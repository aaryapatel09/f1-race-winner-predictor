"""Train an XGBoost classifier that predicts P(winner) for a single driver-race.

Features are all available before the race starts: grid, constructor, circuit,
driver's rolling form (last-5 finishing positions), and driver/constructor
historical win rates computed only from *prior* races to avoid leakage.
"""
from __future__ import annotations

import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(HERE, "data", "model.joblib")
META_PATH = os.path.join(HERE, "data", "model_meta.joblib")

FEATURES = [
    "grid",
    "driver_form_5",
    "driver_career_winrate",
    "constructor_recent_winrate",
    "circuit_mean_winner_grid",
    "driver_constructor_age",
]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["season", "round"]).reset_index(drop=True).copy()
    df["is_winner"] = (df["position"] == 1).astype(int)

    # Rolling last-5-race finishing position per driver (prior to this race)
    df["driver_form_5"] = (
        df.groupby("driver_id")["position"].transform(
            lambda s: s.shift(1).rolling(5, min_periods=1).mean()
        )
    )

    # Expanding career win rate per driver, computed only from races before this one
    df["driver_career_winrate"] = (
        df.groupby("driver_id")["is_winner"].transform(
            lambda s: s.shift(1).expanding(min_periods=1).mean()
        )
    )

    # 10-race rolling win rate per constructor (recent form of the car)
    df["constructor_recent_winrate"] = (
        df.groupby("constructor_id")["is_winner"].transform(
            lambda s: s.shift(1).rolling(20, min_periods=1).mean()
        )
    )

    # Per-circuit mean winner grid (how often does pole convert here) — prior seasons only
    df["circuit_mean_winner_grid"] = df.apply(
        lambda r: _circuit_prior(df, r["circuit_id"], r["season"]), axis=1
    )

    # Proxy for driver-constructor partnership duration: count of races together
    df["driver_constructor_age"] = (
        df.groupby(["driver_id", "constructor_id"]).cumcount()
    )

    defaults = {
        "driver_form_5": 10.0,
        "driver_career_winrate": 0.0,
        "constructor_recent_winrate": 0.0,
        "circuit_mean_winner_grid": 5.0,
    }
    for col, val in defaults.items():
        df[col] = df[col].fillna(val)

    return df


def _circuit_prior(df: pd.DataFrame, circuit: str, season: int) -> float:
    prior = df[(df["circuit_id"] == circuit) & (df["season"] < season) & (df["position"] == 1)]
    if len(prior) == 0:
        return 5.0
    return float(prior["grid"].mean())


def train(df: pd.DataFrame) -> dict:
    feats = build_features(df).dropna(subset=["position"])
    X, y = feats[FEATURES], feats["is_winner"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # class imbalance ≈ 1:19 winners:non-winners; per-sample weights rebalance it
    pos_weight = len(y_tr[y_tr == 0]) / max(1, len(y_tr[y_tr == 1]))
    sample_weight = np.where(y_tr == 1, pos_weight, 1.0)

    clf = HistGradientBoostingClassifier(
        max_iter=300,
        max_depth=4,
        learning_rate=0.05,
        random_state=42,
    )
    clf.fit(X_tr, y_tr, sample_weight=sample_weight)
    auc = roc_auc_score(y_te, clf.predict_proba(X_te)[:, 1])

    # Permutation importance on the held-out test fold: how much does each
    # feature's contribution to ROC-AUC drop when that column is shuffled?
    # Averaged over 10 permutations. Using the test fold avoids giving credit
    # for features the model merely memorised on the train fold.
    imp = permutation_importance(
        clf, X_te, y_te, n_repeats=10, random_state=42, scoring="roc_auc", n_jobs=-1
    )
    importance = {
        f: {"mean": float(m), "std": float(s)}
        for f, m, s in zip(FEATURES, imp.importances_mean, imp.importances_std)
    }

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(clf, MODEL_PATH)

    meta = {
        "driver_career_winrate": feats.groupby("driver_id")["driver_career_winrate"].last().to_dict(),
        "driver_form_5": feats.groupby("driver_id")["driver_form_5"].last().to_dict(),
        "constructor_recent_winrate": feats.groupby("constructor_id")["constructor_recent_winrate"].last().to_dict(),
        "circuit_mean_winner_grid": feats.groupby("circuit_id")["circuit_mean_winner_grid"].last().to_dict(),
        "driver_constructor_age": feats.groupby(["driver_id", "constructor_id"])["driver_constructor_age"].last().to_dict(),
        "driver_names": dict(zip(feats["driver_id"], feats["driver_name"])),
        "feature_importance": importance,
        "test_auc": float(auc),
    }
    joblib.dump(meta, META_PATH)

    return {"auc": float(auc), "n_train": len(y_tr), "n_test": len(y_te), "winners": int(y.sum())}


def load_or_train(df: pd.DataFrame):
    if os.path.exists(MODEL_PATH) and os.path.exists(META_PATH):
        return joblib.load(MODEL_PATH), joblib.load(META_PATH)
    stats = train(df)
    print(f"Test ROC-AUC = {stats['auc']:.3f} on {stats['n_test']} rows")
    return joblib.load(MODEL_PATH), joblib.load(META_PATH)


def predict_row(clf, meta: dict, driver_id: str, constructor_id: str, circuit_id: str, grid: int) -> float:
    row = pd.DataFrame([{
        "grid": int(grid),
        "driver_form_5": meta["driver_form_5"].get(driver_id, 10.0),
        "driver_career_winrate": meta["driver_career_winrate"].get(driver_id, 0.0),
        "constructor_recent_winrate": meta["constructor_recent_winrate"].get(constructor_id, 0.0),
        "circuit_mean_winner_grid": meta["circuit_mean_winner_grid"].get(circuit_id, 5.0),
        "driver_constructor_age": meta["driver_constructor_age"].get((driver_id, constructor_id), 0),
    }])
    return float(clf.predict_proba(row[FEATURES])[0, 1])


if __name__ == "__main__":
    import fetch_data
    df = fetch_data.load_or_fetch(range(2019, 2025))
    print(train(df))
