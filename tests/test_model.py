"""Unit tests for the F1 predictor's feature pipeline and prediction code.

These run against a tiny hand-written fixture DataFrame, so they do not need
network access or the full Jolpica dataset.
"""
from __future__ import annotations

import pandas as pd
import pytest

import model


def _fixture() -> pd.DataFrame:
    # Two drivers, two constructors, one circuit, four races. Driver A wins
    # races 1 and 3; driver B wins race 2; race 4 is the "prediction target".
    rows = []
    for r, winner in enumerate([("A", "red"), ("B", "blue"), ("A", "red"), ("A", "red")], start=1):
        for driver, team in [("A", "red"), ("B", "blue")]:
            pos = 1 if (driver, team) == winner else 2
            rows.append({
                "season": 2024,
                "round": r,
                "race_name": f"R{r}",
                "circuit_id": "testtrack",
                "driver_id": driver,
                "driver_name": driver,
                "constructor_id": team,
                "grid": 1 if pos == 1 else 2,
                "position": pos,
                "status": "Finished",
                "points": 25 if pos == 1 else 18,
            })
    return pd.DataFrame(rows)


def test_feature_pipeline_no_leakage():
    df = _fixture()
    feats = model.build_features(df)
    # Career win rate at round 1 must be NaN-imputed to the default (0),
    # not 1.0 — otherwise the pipeline is peeking at the current-row label.
    first = feats[feats["round"] == 1].iloc[0]
    assert first["driver_career_winrate"] == 0.0


def test_train_and_predict(tmp_path, monkeypatch):
    # Train on the tiny fixture. We only check plumbing, not AUC — the fixture
    # is too small to learn from, but predict_row must still return [0, 1].
    monkeypatch.setattr(model, "MODEL_PATH", str(tmp_path / "m.joblib"))
    monkeypatch.setattr(model, "META_PATH", str(tmp_path / "meta.joblib"))
    df = _fixture()
    stats = model.train(df)
    assert 0.0 <= stats["auc"] <= 1.0
    assert stats["winners"] > 0

    import joblib
    clf = joblib.load(str(tmp_path / "m.joblib"))
    meta = joblib.load(str(tmp_path / "meta.joblib"))
    p = model.predict_row(clf, meta, "A", "red", "testtrack", 1)
    assert 0.0 <= p <= 1.0
    assert "A" in meta["driver_names"]


def test_predict_row_missing_ids_uses_defaults(tmp_path, monkeypatch):
    # Unknown driver + unknown circuit should still return a finite probability
    # rather than raising, because meta.get(...) falls back to the default.
    monkeypatch.setattr(model, "MODEL_PATH", str(tmp_path / "m.joblib"))
    monkeypatch.setattr(model, "META_PATH", str(tmp_path / "meta.joblib"))
    model.train(_fixture())
    import joblib
    clf = joblib.load(str(tmp_path / "m.joblib"))
    meta = joblib.load(str(tmp_path / "meta.joblib"))
    p = model.predict_row(clf, meta, "unknown_driver", "unknown_team", "unknown_track", 5)
    assert 0.0 <= p <= 1.0
