# ============================================================
# E2FIX Configuration File
# Replace the values below with your actual API keys
# ============================================================

# Get your FREE key at: https://aqicn.org/data-platform/token/
AQICN_API_KEY = "c6353295f0c486653f16f943bfddbbd8517b8556"

# Get your FREE key at: https://openweathermap.org/api
OPENWEATHER_API_KEY = "4698436bf13a8430546ab2558aa5f0ae"

# Carbon credit market price in INR per credit
CARBON_CREDIT_PRICE_INR = 1500

# Carbon factors (kg CO2 saved per kg of waste recycled)
CARBON_FACTORS = {
    "Plastic": 2.5,
    "Metal": 3.0,
    "Paper": 1.5,
    "Organic": 0.5,
    "Other": 1.0,
}

# Environmental Health Score thresholds
SCORE_BANDS = [
    (80, 100, "🟢 Healthy", "#22c55e"),
    (60, 79, "🟡 Moderate", "#eab308"),
    (40, 59, "🟠 Unhealthy", "#f97316"),
    (0,  39, "🔴 Dangerous", "#ef4444"),
]

# Weights for Environmental Health Score (must sum to 1.0)
SCORE_WEIGHTS = {
    "aqi":         0.35,
    "heat":        0.20,
    "green":       0.15,
    "noise":       0.10,
    "water":       0.10,
    "waste":       0.10,
}
