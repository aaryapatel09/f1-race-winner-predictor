"""F1 Race Winner Predictor — Streamlit UI.

First run fetches F1 race results from the Jolpica API (~1 minute for six
seasons) and trains a gradient-boosted classifier. Subsequent runs load from
the cache in ``data/``.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

import fetch_data
import model as mlmodel

SEASONS = range(2019, 2025)

st.set_page_config(page_title="F1 Race Winner Predictor", page_icon="🏎️", layout="wide")


@st.cache_data(show_spinner="Loading F1 race data…")
def _data() -> pd.DataFrame:
    return fetch_data.load_or_fetch(SEASONS)


@st.cache_resource(show_spinner="Training model…")
def _model():
    return mlmodel.load_or_train(_data())


st.title("🏎️ F1 Race Winner Predictor")

try:
    df = _data()
    clf, meta = _model()
except Exception as e:
    st.error(
        "Could not fetch training data from the Jolpica F1 API. Check your "
        "network connection and try again — the first run needs internet "
        f"access. Raw error: `{e}`"
    )
    st.stop()

year_lo, year_hi = int(df["season"].min()), int(df["season"].max())
st.caption(
    f"Trained on {len(df):,} driver-race rows from {year_lo}–{year_hi}, "
    "sourced from the [Jolpica F1 API](https://api.jolpi.ca/ergast/f1/) (the maintained Ergast replacement)."
)

recent = df[df["season"] == df["season"].max()]
drivers = sorted(recent["driver_id"].unique())
circuits = sorted(df["circuit_id"].unique())
constructors = sorted(recent["constructor_id"].unique())


def _driver_label(d: str) -> str:
    return meta["driver_names"].get(d, d)


def _last_team(d: str) -> str:
    return df[df["driver_id"] == d]["constructor_id"].iloc[-1]


tab1, tab2, tab3, tab4 = st.tabs(["Single prediction", "What-if grid", "Model", "Data"])

# ---- Tab 1: single driver-race ----
with tab1:
    st.subheader("Predict a single driver's chance of winning")

    c1, c2, c3 = st.columns(3)
    with c1:
        driver = st.selectbox("Driver", drivers, format_func=_driver_label)
    with c2:
        default_team = _last_team(driver)
        idx = constructors.index(default_team) if default_team in constructors else 0
        constructor = st.selectbox("Constructor", constructors, index=idx)
    with c3:
        idx = circuits.index("monaco") if "monaco" in circuits else 0
        circuit = st.selectbox("Circuit", circuits, index=idx)

    grid = st.slider("Starting grid position", 1, 20, 3)

    if st.button("Predict", type="primary"):
        p = mlmodel.predict_row(clf, meta, driver, constructor, circuit, grid)
        st.metric("Win probability", f"{p * 100:.1f}%")
        st.progress(min(1.0, p))

# ---- Tab 2: what-if grid editor ----
with tab2:
    st.subheader("What-if grid editor")
    st.caption(
        "Edit the starting grid directly — change a driver, swap teams, move someone "
        "up or down. Probabilities update on every edit and normalise so they sum to 1."
    )

    whatif_circuit = st.selectbox(
        "Circuit", circuits, key="whatif_circuit",
        index=circuits.index("monaco") if "monaco" in circuits else 0,
    )

    starter_drivers = drivers[: min(10, len(drivers))]
    default_rows = [
        {"Grid": i + 1, "Driver": d, "Constructor": _last_team(d)}
        for i, d in enumerate(starter_drivers)
    ]
    if "whatif_df" not in st.session_state or st.session_state.get("whatif_circuit_last") != whatif_circuit:
        st.session_state["whatif_df"] = pd.DataFrame(default_rows)
        st.session_state["whatif_circuit_last"] = whatif_circuit

    edited = st.data_editor(
        st.session_state["whatif_df"],
        key="whatif_editor",
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Grid": st.column_config.NumberColumn(min_value=1, max_value=30, step=1),
            "Driver": st.column_config.SelectboxColumn(options=drivers, required=True),
            "Constructor": st.column_config.SelectboxColumn(options=constructors, required=True),
        },
        hide_index=True,
    )
    st.session_state["whatif_df"] = edited

    valid = edited.dropna(subset=["Grid", "Driver", "Constructor"])
    if len(valid) == 0:
        st.info("Add at least one row with a Grid, Driver, and Constructor filled in.")
    else:
        raw = [
            mlmodel.predict_row(clf, meta, r["Driver"], r["Constructor"], whatif_circuit, int(r["Grid"]))
            for _, r in valid.iterrows()
        ]
        total = sum(raw) or 1.0
        result = valid.copy()
        result["Driver name"] = result["Driver"].map(_driver_label)
        result["P(win)"] = [p / total for p in raw]
        result = result.sort_values("P(win)", ascending=False).reset_index(drop=True)
        result["P(win)"] = result["P(win)"].map(lambda v: f"{v * 100:.1f}%")
        st.dataframe(
            result[["Grid", "Driver name", "Constructor", "P(win)"]],
            use_container_width=True,
            hide_index=True,
        )

# ---- Tab 3: model internals ----
with tab3:
    st.subheader("What the model actually uses")
    st.caption(
        "Permutation importance on the held-out test fold: how much does each feature's "
        "contribution to ROC-AUC drop when that column is shuffled? Higher = more load-bearing. "
        f"Test ROC-AUC on this model: **{meta.get('test_auc', float('nan')):.3f}**."
    )

    importance = meta.get("feature_importance") or {}
    if not importance:
        st.info("This model was trained before feature importance was captured. Delete data/model.joblib and rerun to regenerate.")
    else:
        imp_rows = sorted(
            (
                {"Feature": f, "Importance": v["mean"], "Std": v["std"]}
                for f, v in importance.items()
            ),
            key=lambda r: r["Importance"],
            reverse=True,
        )
        imp_df = pd.DataFrame(imp_rows)
        st.bar_chart(imp_df.set_index("Feature")["Importance"], use_container_width=True)
        display_df = imp_df.copy()
        display_df["Importance"] = display_df["Importance"].map(lambda v: f"{v:+.4f}")
        display_df["Std"] = display_df["Std"].map(lambda v: f"{v:.4f}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# ---- Tab 4: raw data ----
with tab4:
    st.subheader("Training data")
    st.caption(f"{len(df):,} rows · {df['driver_id'].nunique()} drivers · {df['circuit_id'].nunique()} circuits")
    st.dataframe(df.tail(100), use_container_width=True, hide_index=True)
