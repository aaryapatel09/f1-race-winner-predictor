# F1 Race Winner Predictor

Streamlit app that predicts Formula 1 race winners from driver form, constructor, circuit history, and grid position. Trained on ~6 seasons of race results from the [Jolpica F1 API](https://api.jolpi.ca/ergast/f1/) (the maintained drop-in replacement for the retired Ergast service).

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

First launch fetches 2019–2024 results from Jolpica (~1 min) and trains a gradient-boosted classifier. Both the CSV and the trained model cache to `data/`, so subsequent starts are instant.

## Model

- **Target:** `position == 1` (binary win/no-win per driver-race)
- **Features:**
  - `grid` — starting grid position
  - `driver_form_5` — mean finishing position over the driver's last 5 races
  - `driver_career_winrate` — expanding win rate (leakage-free, shifted by one)
  - `constructor_recent_winrate` — 20-race rolling win rate for the team
  - `circuit_mean_winner_grid` — at this circuit, what grid slot do winners typically come from
  - `driver_constructor_age` — how many races the driver has run with this team
- **Classifier:** sklearn `HistGradientBoostingClassifier`, `max_iter=300`, `max_depth=4`, per-sample weights rebalance the ~1:19 win/no-win ratio
- **Evaluation:** 80/20 stratified split; on 2021–2024 data the test ROC-AUC is **0.954**

All features are strictly pre-race: rolling/expanding windows are shifted by one step so no label information leaks in.

## UI

- **Single prediction** — pick a driver, team, circuit, and grid slot, get a win probability
- **Simulate a race** — pick a circuit and starting order, get normalised win probabilities across the grid
- **Data** — browse the last 100 rows of the fetched dataset

## Why the rewrite

The previous repo had two parallel frameworks (FastAPI `main.py` + Streamlit `src/web/app.py`), three duplicated predictor classes (`predictor.py`, `model.py`, `ensemble_model.py`), an `sklearn.neural_networks` typo that prevented import, training targets of raw finish position (1–20) being fed to classifiers, and a scraper pointed at Ergast — which went offline in 2024. This collapse is a single Streamlit app hitting the live Jolpica replacement API.
