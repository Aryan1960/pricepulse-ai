"""
utils/helpers.py
Shared utility functions for loading model and preparing prediction input.
"""

import os
import joblib
import numpy as np
import pandas as pd


MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "demand_model.pkl")


def load_model():
    """Load the trained demand model. Returns (model, feature_list)."""
    path = os.path.normpath(MODEL_PATH)
    if not os.path.exists(path):
        raise FileNotFoundError(
            "Model not found. Run: python scripts/train_model.py"
        )
    bundle = joblib.load(path)
    return bundle["model"], bundle["features"]


def predict_demand(model, features, inventory, raw_material_cost, competitor_price, price):
    """
    Build a feature row and return predicted demand (single value).
    Uses today's date for seasonal features.
    """
    today = pd.Timestamp.today()
    day_of_year = today.day_of_year
    month = today.month
    price_vs_competitor = price / competitor_price if competitor_price > 0 else 1.0
    margin = price - raw_material_cost

    row = {
        "inventory": inventory,
        "raw_material_cost": raw_material_cost,
        "competitor_price": competitor_price,
        "price": price,
        "day_of_year": day_of_year,
        "month": month,
        "price_vs_competitor": price_vs_competitor,
        "margin": margin,
    }

    X = pd.DataFrame([row])[features]
    prediction = model.predict(X)[0]
    return max(0, round(prediction, 1))


def load_data():
    """Load the raw CSV dataset."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "industry_data.csv")
    return pd.read_csv(os.path.normpath(data_path), parse_dates=["date"])
