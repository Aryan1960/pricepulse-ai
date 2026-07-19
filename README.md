# PricePulse AI

> AI-powered operational intelligence system for MSMEs and small-scale industries.

PricePulse AI helps small factories, textile units, food producers, and workshops make smarter decisions around **demand forecasting**, **production planning**, and **pricing strategy** — powered by machine learning.

---

##  Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/pricepulse-ai.git
cd pricepulse-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate synthetic data
```bash
python scripts/generate_data.py
```

### 4. Train the AI model
```bash
python scripts/train_model.py
```

### 5. Launch the dashboard
```bash
streamlit run app.py
```

---

##  Project Structure

```
pricepulse-ai/
├── app.py                  ← Streamlit dashboard (4 tabs)
├── data/
│   └── industry_data.csv   ← Synthetic MSME dataset (400 rows)
├── models/
│   └── demand_model.pkl    ← Trained RandomForest model
├── scripts/
│   ├── generate_data.py    ← Synthetic data generator
│   ├── train_model.py      ← Model training script
│   └── optimization.py     ← Rule-based recommendation engine
├── utils/
│   └── helpers.py          ← Shared utilities
└── requirements.txt
```

---

##  How It Works

1. **Synthetic Data** — 400 rows of realistic industrial data with seasonal demand patterns, price elasticity, and raw material cost trends.
2. **AI Model** — `RandomForestRegressor` predicts demand based on inventory, pricing, competitor prices, and seasonal features.
3. **Optimizer** — Rule-based engine converts predictions into actionable production and pricing recommendations.
4. **Dashboard** — Real-time Streamlit UI with 4 tabs: AI Analysis, Charts, Recommendations, and About.

---

##  SDG Alignment

| SDG | Contribution |
|-----|-------------|
| SDG 8 — Economic Growth | Helps MSMEs optimize profits |
| SDG 9 — Industry & Innovation | Democratizes AI for small businesses |
| SDG 12 — Responsible Production | Reduces overproduction waste |
| SDG 13 — Climate Action | Efficient production = lower resource use |

---

##  Tech Stack

- **Backend/AI**: Python, Scikit-learn, Pandas, NumPy
- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Model**: RandomForestRegressor

---

##  Features

-  Real-time demand prediction
-  Inventory risk assessment
-  Pricing recommendations vs competitor
-  Production capacity optimization
-  Profit outlook comparison
- 📊 Interactive historical trend charts

---

*Built as a hackathon prototype — PricePulse AI*
