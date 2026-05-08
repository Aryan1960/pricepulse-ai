"""
scripts/train_model.py
Trains a RandomForestRegressor on the synthetic dataset and saves the model.
Run: python scripts/train_model.py
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

def train_demand_model():
    # --- Load data ---
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "industry_data.csv")
    df = pd.read_csv(data_path, parse_dates=["date"])

    # --- Feature engineering ---
    df["day_of_year"] = df["date"].dt.dayofyear
    df["month"] = df["date"].dt.month
    df["price_vs_competitor"] = df["price"] / df["competitor_price"]
    df["margin"] = df["price"] - df["raw_material_cost"]

    # --- Features and target ---
    features = [
        "inventory",
        "raw_material_cost",
        "competitor_price",
        "price",
        "day_of_year",
        "month",
        "price_vs_competitor",
        "margin",
    ]
    X = df[features]
    y = df["demand"]

    # --- Train/test split ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # --- Train model ---
    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # --- Evaluate ---
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"✅ Model trained  |  MAE: {mae:.2f}  |  R²: {r2:.4f}")

    # --- Save model ---
    model_path = os.path.join(os.path.dirname(__file__), "..", "models", "demand_model.pkl")
    model_path = os.path.normpath(model_path)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump({"model": model, "features": features}, model_path)
    print(f"✅ Model saved → {model_path}")

    return model, features

if __name__ == "__main__":
    train_demand_model()
