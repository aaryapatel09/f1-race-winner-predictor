"""F1 Race Winner Predictor — Streamlit UI.

First run fetches 6 seasons of F1 results from the Jolpica API (~1 minute) and
trains an XGBoost model. Subsequent runs load from the cache.
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


df = _data()
clf, meta = _model()

st.title("🏎️ F1 Race Winner Predictor")
st.caption(
    f"Trained on {len(df):,} driver-race rows from {SEASONS.start}–{SEASONS.stop - 1}, "
    "sourced from the [Jolpica F1 API](https://api.jolpi.ca/ergast/f1/) (the maintained Ergast replacement)."
)

tab1, tab2, tab3 = st.tabs(["Single prediction", "Simulate a race", "Data"])

# ---- Tab 1: single driver-race ----
with tab1:
    st.subheader("Predict a single driver's chance of winning")

    recent = df[df["season"] == df["season"].max()]
    drivers = sorted(recent["driver_id"].unique())
    circuits = sorted(df["circuit_id"].unique())
    constructors = sorted(recent["constructor_id"].unique())

    c1, c2, c3 = st.columns(3)
    with c1:
        driver = st.selectbox("Driver", drivers, format_func=lambda d: meta["driver_names"].get(d, d))
    with c2:
        default_team = df[df["driver_id"] == driver]["constructor_id"].iloc[-1]
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

# ---- Tab 2: simulate whole race ----
with tab2:
    st.subheader("Simulate a full grid")
    st.caption("Pick a circuit and the starting order of the most-recent season's drivers. Model predicts win probability for each, then normalises so they sum to 1.")

    circuit2 = st.selectbox("Circuit", circuits, key="sim_circuit", index=circuits.index("monaco") if "monaco" in circuits else 0)
    grid_order = st.multiselect(
        "Starting grid (in order — pole first)",
        drivers,
        default=drivers[: min(10, len(drivers))],
        format_func=lambda d: meta["driver_names"].get(d, d),
    )
    if st.button("Simulate", type="primary") and grid_order:
        rows = []
        for pos, d in enumerate(grid_order, start=1):
            team = df[df["driver_id"] == d]["constructor_id"].iloc[-1]
            p = mlmodel.predict_row(clf, meta, d, team, circuit2, pos)
            rows.append({"Grid": pos, "Driver": meta["driver_names"].get(d, d), "Constructor": team, "raw_p": p})
        sim = pd.DataFrame(rows)
        total = sim["raw_p"].sum() or 1.0
        sim["P(win)"] = (sim["raw_p"] / total).map(lambda v: f"{v * 100:.1f}%")
        st.dataframe(
            sim.drop(columns=["raw_p"]).sort_values("P(win)", ascending=False).reset_index(drop=True),
            use_container_width=True,
        )

# ---- Tab 3: raw data ----
with tab3:
    st.subheader("Training data")
    st.caption(f"{len(df):,} rows · {df['driver_id'].nunique()} drivers · {df['circuit_id'].nunique()} circuits")
    st.dataframe(df.tail(100), use_container_width=True, hide_index=True)
