"""Fetch F1 race results from the Jolpica API (the maintained Ergast replacement).

Produces ``data/races.csv`` with one row per (season, round, driver) containing
the grid position, finishing position, constructor, and circuit. Polite about
rate limits — sleeps between requests.
"""
from __future__ import annotations

import os
import time
from typing import Iterator

import pandas as pd
import requests

API = "https://api.jolpi.ca/ergast/f1"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "data", "races.csv")


def _get(path: str, *, retries: int = 3, backoff: float = 2.0) -> dict:
    for attempt in range(retries):
        try:
            r = requests.get(f"{API}/{path}", timeout=20)
            if r.status_code == 429:
                time.sleep(backoff * (attempt + 1))
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(backoff * (attempt + 1))
    raise RuntimeError("unreachable")


def iter_season(year: int) -> Iterator[dict]:
    offset = 0
    while True:
        data = _get(f"{year}/results.json?limit=100&offset={offset}")
        races = data["MRData"]["RaceTable"]["Races"]
        if not races:
            return
        for race in races:
            for res in race["Results"]:
                yield {
                    "season": int(race["season"]),
                    "round": int(race["round"]),
                    "race_name": race["raceName"],
                    "circuit_id": race["Circuit"]["circuitId"],
                    "driver_id": res["Driver"]["driverId"],
                    "driver_name": f"{res['Driver']['givenName']} {res['Driver']['familyName']}",
                    "constructor_id": res["Constructor"]["constructorId"],
                    "grid": int(res["grid"]),
                    "position": int(res.get("position") or 0) or None,
                    "status": res.get("status"),
                    "points": float(res.get("points") or 0),
                }
        total = int(data["MRData"]["total"])
        offset += int(data["MRData"]["limit"])
        if offset >= total:
            return


def fetch(seasons: range) -> pd.DataFrame:
    rows: list[dict] = []
    for y in seasons:
        print(f"fetching {y}…", flush=True)
        rows.extend(iter_season(y))
        time.sleep(0.4)
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"wrote {len(df)} rows to {DATA_PATH}")
    return df


def load_or_fetch(seasons: range) -> pd.DataFrame:
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return fetch(seasons)


if __name__ == "__main__":
    fetch(range(2019, 2025))
