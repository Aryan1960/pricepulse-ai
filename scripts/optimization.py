"""
scripts/optimization.py
Rule-based optimization engine.
Takes predicted demand + user inputs → production & pricing recommendations.
"""

def get_recommendations(
    predicted_demand,
    inventory,
    price,
    raw_material_cost,
    competitor_price,
    production_capacity,
):
    """
    Returns a dict of recommendations and insights.
    """
    recommendations = {}
    reasons = []

    # --- Derived metrics ---
    margin = price - raw_material_cost
    margin_pct = (margin / price) * 100 if price > 0 else 0
    inventory_days = inventory / predicted_demand if predicted_demand > 0 else 999
    price_vs_competitor = price / competitor_price if competitor_price > 0 else 1.0

    # -----------------------------------------------
    # PRODUCTION RECOMMENDATION
    # -----------------------------------------------
    if predicted_demand > production_capacity * 0.85:
        prod_change_pct = min(20, round((predicted_demand / production_capacity - 1) * 100 + 5))
        recommendations["production_action"] = "INCREASE"
        recommendations["production_change_pct"] = prod_change_pct
        reasons.append("Predicted demand is approaching or exceeding current production capacity.")
    elif inventory_days > 30:
        recommendations["production_action"] = "DECREASE"
        recommendations["production_change_pct"] = -10
        reasons.append(f"Inventory covers {inventory_days:.0f} days of demand — overstock risk is high.")
    else:
        recommendations["production_action"] = "MAINTAIN"
        recommendations["production_change_pct"] = 0
        reasons.append("Production levels are balanced with current demand forecasts.")

    # -----------------------------------------------
    # PRICING RECOMMENDATION
    # -----------------------------------------------
    if price_vs_competitor < 0.88:
        # We're too cheap — can raise price
        suggested_price = round(price * 1.05, 2)
        recommendations["pricing_action"] = "INCREASE"
        recommendations["suggested_price"] = suggested_price
        reasons.append(
            f"Your price (₹{price:.0f}) is significantly below competitor (₹{competitor_price:.0f}). "
            "There is room to increase price without losing customers."
        )
    elif price_vs_competitor > 1.05:
        # We're more expensive — risk losing customers
        suggested_price = round(competitor_price * 0.96, 2)
        recommendations["pricing_action"] = "DECREASE"
        recommendations["suggested_price"] = suggested_price
        reasons.append(
            f"Your price (₹{price:.0f}) exceeds competitor (₹{competitor_price:.0f}). "
            "Reducing price may recover lost demand."
        )
    elif margin_pct < 20:
        # Margin too thin even at current price
        suggested_price = round(raw_material_cost * 1.28, 2)
        recommendations["pricing_action"] = "INCREASE"
        recommendations["suggested_price"] = suggested_price
        reasons.append(
            f"Margin is only {margin_pct:.1f}%. Raising price is needed to stay profitable."
        )
    else:
        recommendations["pricing_action"] = "MAINTAIN"
        recommendations["suggested_price"] = round(price, 2)
        reasons.append("Current pricing maintains a healthy margin and competitive position.")

    # -----------------------------------------------
    # INVENTORY RISK
    # -----------------------------------------------
    if inventory_days < 7:
        recommendations["inventory_risk"] = "HIGH"
        reasons.append("⚠️ Inventory may run out within a week. Accelerate restocking.")
    elif inventory_days > 45:
        recommendations["inventory_risk"] = "HIGH"
        reasons.append("⚠️ Excess inventory ties up capital. Consider slowing production.")
    elif inventory_days < 14:
        recommendations["inventory_risk"] = "MEDIUM"
        reasons.append("Inventory is getting low. Monitor closely over next 2 weeks.")
    else:
        recommendations["inventory_risk"] = "LOW"

    # -----------------------------------------------
    # PROFIT ESTIMATE
    # -----------------------------------------------
    current_profit = (price - raw_material_cost) * predicted_demand
    suggested_price_val = recommendations["suggested_price"]
    future_demand_estimate = predicted_demand * (
        1 + recommendations["production_change_pct"] / 200
    )
    future_profit = (suggested_price_val - raw_material_cost) * future_demand_estimate

    profit_change_pct = (
        ((future_profit - current_profit) / abs(current_profit)) * 100
        if current_profit != 0
        else 0
    )
    recommendations["current_profit_estimate"] = round(current_profit, 2)
    recommendations["future_profit_estimate"] = round(future_profit, 2)
    recommendations["profit_change_pct"] = round(profit_change_pct, 1)

    # -----------------------------------------------
    # SUMMARY
    # -----------------------------------------------
    recommendations["reasons"] = reasons
    recommendations["inventory_days"] = round(inventory_days, 1)
    recommendations["margin_pct"] = round(margin_pct, 1)
    recommendations["predicted_demand"] = round(predicted_demand, 0)

    return recommendations
