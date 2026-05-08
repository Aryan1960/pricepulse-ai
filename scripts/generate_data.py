"""
scripts/generate_data.py
Generates realistic synthetic MSME operational data.
Run: python scripts/generate_data.py
"""

import numpy as np
import pandas as pd
import os

def generate_industry_data(n_rows=400, seed=42):
    np.random.seed(seed)
    
    # --- Time axis: ~16 months of daily data ---
    dates = pd.date_range(start="2023-01-01", periods=n_rows, freq="D")
    
    # --- Seasonal demand signal (peaks at month 3, 9 = festive/harvest cycles) ---
    day_of_year = np.array([d.timetuple().tm_yday for d in dates])
    seasonal = (
        np.sin(2 * np.pi * day_of_year / 365) * 30   # annual cycle
        + np.sin(4 * np.pi * day_of_year / 365) * 10  # bi-annual bump
    )

    # --- Raw material cost: upward trend with noise ---
    raw_material_cost = (
        50
        + np.linspace(0, 20, n_rows)             # gradual cost increase
        + np.random.normal(0, 3, n_rows)          # daily noise
        + seasonal * 0.15                          # slight seasonal pressure
    ).clip(40, 90)

    # --- Competitor price: loosely tracks raw cost + their own margin ---
    competitor_price = (
        raw_material_cost * 1.6
        + np.random.normal(0, 5, n_rows)
        + seasonal * 0.4
    ).clip(80, 160)

    # --- Our selling price: we try to stay slightly below competitor ---
    price = (
        competitor_price * 0.93
        + np.random.normal(0, 3, n_rows)
    ).clip(75, 150)

    # --- Inventory: oscillates as we produce/sell ---
    inventory = (
        500
        - seasonal * 1.2
        + np.random.normal(0, 40, n_rows)
        + np.sin(np.linspace(0, 8 * np.pi, n_rows)) * 60  # production cycles
    ).clip(50, 900)

    # --- Demand: driven by price (inverse), season, competitor price, inventory signal ---
    demand = (
        300
        + seasonal * 1.8                           # seasonal lift
        - (price - price.mean()) * 1.5             # price elasticity
        + (competitor_price - competitor_price.mean()) * 1.2  # competitor spillover
        - (inventory - inventory.mean()) * 0.1     # high inventory → we reduce push
        + np.random.normal(0, 15, n_rows)           # random market noise
    ).clip(80, 600).round(0)

    df = pd.DataFrame({
        "date": dates,
        "inventory": inventory.round(1),
        "raw_material_cost": raw_material_cost.round(2),
        "competitor_price": competitor_price.round(2),
        "price": price.round(2),
        "demand": demand.astype(int),
    })

    return df


if __name__ == "__main__":
    df = generate_industry_data(n_rows=400)
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "industry_data.csv")
    out_path = os.path.normpath(out_path)
    df.to_csv(out_path, index=False)
    print(f"✅ Dataset saved → {out_path}")
    print(df.describe().round(2))
