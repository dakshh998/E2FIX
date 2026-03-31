"""
E2FIX - Core Engine
Handles all API calls, data processing, and score calculations.
"""

import requests
import random
import math
from config import (
    AQICN_API_KEY, OPENWEATHER_API_KEY,
    CARBON_FACTORS, SCORE_BANDS
)
import database as db
import json

def geocode(query: str) -> tuple[float, float, str]:
    """Geocode a text query to lat, lon, and full display name using Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "E2FIX_Environment_App/1.0"}
    params = {"q": query, "format": "json", "limit": 1}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        data = r.json()
        if not data:
            return None, None, query
        return float(data[0]["lat"]), float(data[0]["lon"]), data[0]["display_name"]
    except Exception:
        return None, None, query

def reverse_geocode(lat: float, lon: float) -> str:
    """Get location name from coordinates."""
    url = "https://nominatim.openstreetmap.org/reverse"
    headers = {"User-Agent": "E2FIX_Environment_App/1.0"}
    params = {"lat": lat, "lon": lon, "format": "json"}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        data = r.json()
        return data.get("display_name", f"{lat:.4f}, {lon:.4f}")
    except Exception:
        return f"{lat:.4f}, {lon:.4f}"

def _is_demo_mode():
    return (
        AQICN_API_KEY == "YOUR_AQICN_API_KEY_HERE" or
        OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY_HERE"
    )

def fetch_aqi(lat: float, lon: float, display_name: str) -> dict:
    """Fetch AQI data from AQICN API using coordinates."""
    if _is_demo_mode():
        random.seed(display_name)
        base_aqi = random.randint(30, 250)
        noise = random.uniform(-5, 5)
        aqi = max(0, base_aqi + noise)
        res = {
            "aqi": aqi,
            "pm25": round(aqi * 0.55 + random.uniform(-5, 5), 1),
            "pm10": round(aqi * 0.85 + random.uniform(-5, 5), 1),
            "co":   round(random.uniform(0.5, 3.0), 2),
            "no2":  round(random.uniform(10, 80), 1),
            "source": "demo",
        }
        random.seed() # reset
        return res

    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={AQICN_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        d = r.json()
        if d["status"] != "ok":
            raise ValueError(d.get("data", "Unknown AQICN error"))
        iaqi = d["data"].get("iaqi", {})
        return {
            "aqi":  d["data"]["aqi"],
            "pm25": iaqi.get("pm25", {}).get("v", None),
            "pm10": iaqi.get("pm10", {}).get("v", None),
            "co":   iaqi.get("co",   {}).get("v", None),
            "no2":  iaqi.get("no2",  {}).get("v", None),
            "source": "live",
        }
    except Exception as e:
        raise RuntimeError(f"AQI API error: {e}")

def fetch_weather(lat: float, lon: float, display_name: str) -> dict:
    """Fetch weather data from OpenWeatherMap using coordinates."""
    if _is_demo_mode():
        random.seed(display_name + "_weather")
        base_temp = random.randint(15, 40)
        res = {
            "temperature": round(base_temp + random.uniform(-1, 1), 1),
            "feels_like":  round(base_temp + random.uniform(0, 3), 1),
            "humidity":    random.randint(30, 90),
            "wind_speed":  round(random.uniform(2, 20), 1),
            "description": random.choice(["Clear", "Haze", "Partly Cloudy", "Humid", "Smoggy"]),
            "pressure":    random.randint(1005, 1020),
            "source": "demo",
        }
        random.seed()
        return res

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    try:
        r = requests.get(url, timeout=10)
        d = r.json()
        if d.get("cod") != 200:
            raise ValueError(d.get("message", "Unknown weather error"))
        main = d["main"]
        return {
            "temperature": main["temp"],
            "feels_like":  main["feels_like"],
            "humidity":    main["humidity"],
            "wind_speed":  d["wind"]["speed"],
            "description": d["weather"][0]["description"].title(),
            "pressure":    main["pressure"],
            "source": "live",
        }
    except Exception as e:
        raise RuntimeError(f"Weather API error: {e}")


# ─────────────────────────────────────────────
# CALCULATIONS
# ─────────────────────────────────────────────

def calc_heat_index(temp_c: float, humidity: float) -> float:
    """Steadman heat index approximation."""
    T = temp_c * 9 / 5 + 32  # to Fahrenheit
    H = humidity
    HI = (-42.379 + 2.04901523*T + 10.14333127*H
          - 0.22475541*T*H - 0.00683783*T*T
          - 0.05481717*H*H + 0.00122874*T*T*H
          + 0.00085282*T*H*H - 0.00000199*T*T*H*H)
    return round((HI - 32) * 5 / 9, 1)  # back to Celsius


def calc_green_impact(aqi: float, temp: float) -> float:
    """
    Estimate green coverage impact (0-100, higher = more green).
    Cities with lower AQI and moderate temp tend to have more greenery.
    """
    aqi_factor  = max(0, 100 - aqi) / 100
    temp_factor = max(0, 1 - abs(temp - 22) / 30)
    score = (aqi_factor * 0.7 + temp_factor * 0.3) * 100
    return round(min(100, max(0, score + random.uniform(-5, 5))), 1)


def calc_noise_impact(aqi: float, wind: float) -> float:
    """
    Estimate noise pollution (0-100, higher = more noise).
    Higher AQI cities tend to have more traffic → more noise.
    """
    base = min(100, aqi * 0.5 + random.uniform(10, 30))
    wind_reduction = min(15, wind * 0.5)
    return round(max(0, base - wind_reduction), 1)


def calc_water_stress(temp: float, humidity: float) -> float:
    """
    Estimate water stress (0-100, higher = more stress).
    High temp + low humidity = more water stress.
    """
    temp_stress  = min(100, max(0, (temp - 20) * 3))
    humid_relief = humidity * 0.4
    stress = max(0, temp_stress - humid_relief + random.uniform(-5, 5))
    return round(min(100, stress), 1)


def calc_waste_pressure(aqi: float, temp: float) -> float:
    """
    Estimate waste management pressure (0-100).
    Proxy: higher AQI often correlates with poor waste management.
    """
    base = min(100, aqi * 0.4 + temp * 0.8 + random.uniform(-10, 10))
    return round(max(0, min(100, base)), 1)


def aqi_to_score(aqi: float) -> float:
    """Convert AQI (0-500+) to a 0-100 health sub-score (inverted)."""
    return max(0, 100 - min(100, aqi / 5))


def heat_to_score(heat_index: float) -> float:
    """Convert heat index to health sub-score."""
    if heat_index < 27:   return 100
    if heat_index < 32:   return 80
    if heat_index < 38:   return 60
    if heat_index < 45:   return 35
    return 10


def calc_health_score(params: dict) -> tuple[float, str]:
    """
    Combine all parameters into a single Environmental Health Score.
    Returns (score: float, label: str)
    """
    sub = {
        "aqi":   aqi_to_score(params["aqi"]),
        "heat":  heat_to_score(params["heat_index"]),
        "green": params["green_impact"],               # already 0-100 health proxy
        "noise": 100 - params["noise_impact"],         # invert: less noise = better
        "water": 100 - params["water_stress"],         # invert
        "waste": 100 - params["waste_pressure"],       # invert
    }

    w_str = db.get_setting("score_weights")
    if w_str:
        try:
            w = json.loads(w_str)
        except Exception:
            w = {"aqi": 0.35, "heat": 0.20, "green": 0.15, "noise": 0.10, "water": 0.10, "waste": 0.10}
    else:
        w = {"aqi": 0.35, "heat": 0.20, "green": 0.15, "noise": 0.10, "water": 0.10, "waste": 0.10}

    score = sum(sub[k] * w.get(k, 0) for k in w)
    score += params.get("bonus_score", 0)
    score = round(min(100, max(0, score)), 1)

    label = "Unknown"
    for lo, hi, lbl, _ in SCORE_BANDS:
        if lo <= score <= hi:
            label = lbl
            break

    return score, label, sub


def score_color(score: float) -> str:
    for lo, hi, _, color in SCORE_BANDS:
        if lo <= score <= hi:
            return color
    return "#94a3b8"


def get_action_plan(params: dict) -> list[dict]:
    """Generate context-aware action plan based on environmental parameters."""
    actions = []

    if params["aqi"] > 100:
        actions.append({
            "icon": "🌬️",
            "priority": "High",
            "area": "Air Quality",
            "action": "Reduce vehicle usage and switch to public transport or carpooling.",
            "impact": "High",
        })
        actions.append({
            "icon": "🚭",
            "priority": "High",
            "area": "Air Quality",
            "action": "Strictly ban open waste burning in industrial and residential zones.",
            "impact": "High",
        })

    if params["aqi"] > 150:
        actions.append({
            "icon": "😷",
            "priority": "Urgent",
            "area": "Public Health",
            "action": "Issue air quality advisory — vulnerable groups should stay indoors.",
            "impact": "Critical",
        })

    if params["heat_index"] > 35:
        actions.append({
            "icon": "🌳",
            "priority": "Medium",
            "area": "Heat Reduction",
            "action": "Plant shade trees and install green roofs to reduce urban heat island effect.",
            "impact": "Medium",
        })
        actions.append({
            "icon": "💧",
            "priority": "Medium",
            "area": "Heat Reduction",
            "action": "Set up public cooling centers and mist sprayers in high-footfall areas.",
            "impact": "Medium",
        })

    if params["waste_pressure"] > 60:
        actions.append({
            "icon": "♻️",
            "priority": "High",
            "area": "Waste Management",
            "action": "Launch segregated waste collection drives — separate organic, plastic, and metal waste.",
            "impact": "High",
        })
        actions.append({
            "icon": "🏭",
            "priority": "Medium",
            "area": "Industry",
            "action": "Incentivize industries to adopt zero-waste manufacturing practices.",
            "impact": "High",
        })

    if params["water_stress"] > 55:
        actions.append({
            "icon": "🌧️",
            "priority": "High",
            "area": "Water Conservation",
            "action": "Install rooftop rainwater harvesting systems in residential and commercial buildings.",
            "impact": "Medium",
        })
        actions.append({
            "icon": "🚿",
            "priority": "Medium",
            "area": "Water Conservation",
            "action": "Run awareness campaigns on water-efficient practices and fix leaking infrastructure.",
            "impact": "Medium",
        })

    if params["green_impact"] < 40:
        actions.append({
            "icon": "🌱",
            "priority": "Medium",
            "area": "Green Cover",
            "action": "Organize tree plantation drives targeting at least 1 tree per 5 residents.",
            "impact": "Long-term",
        })
        actions.append({
            "icon": "🏞️",
            "priority": "Low",
            "area": "Green Cover",
            "action": "Convert vacant urban land into micro-gardens and community green spaces.",
            "impact": "Medium",
        })

    if params["noise_impact"] > 65:
        actions.append({
            "icon": "🔇",
            "priority": "Medium",
            "area": "Noise Pollution",
            "action": "Enforce noise ordinances in residential zones; install sound barriers near highways.",
            "impact": "Medium",
        })

    if not actions:
        actions.append({
            "icon": "✅",
            "priority": "Low",
            "area": "General",
            "action": "Environment is in good condition! Continue current practices and monitor regularly.",
            "impact": "Maintenance",
        })

    return actions


# ─────────────────────────────────────────────
# CARBON CREDIT ENGINE
# ─────────────────────────────────────────────

def calc_carbon_savings(waste_type: str, quantity_kg: float) -> dict:
    factor = CARBON_FACTORS.get(waste_type, 1.0)
    carbon_saved = quantity_kg * factor
    credits = carbon_saved / 1000
    try:
        price = float(db.get_setting("carbon_credit_price", 1500))
    except Exception:
        price = 1500.0
    revenue = credits * price
    bonus = min(carbon_saved / 50, 5)  # max +5 pts to health score
    return {
        "waste_type":      waste_type,
        "quantity_kg":     quantity_kg,
        "carbon_factor":   factor,
        "carbon_saved_kg": round(carbon_saved, 4),
        "carbon_credits":  round(credits, 6),
        "revenue_inr":     round(revenue, 2),
        "bonus_score":     round(bonus, 2),
    }


def predict_next_aqi(history: list) -> float:
    """Predict next AQI using simple average of the last 7 entries."""
    if not history:
        return None
    recent = history[:7] 
    valid_aqi = [float(h["aqi"]) for h in recent if h.get("aqi") is not None]
    if not valid_aqi:
        return None
    return sum(valid_aqi) / len(valid_aqi)

def get_all_env_data(lat: float, lon: float, display_name: str) -> dict:
    """Fetch + process everything for a given coordinate."""
    aqi_data     = fetch_aqi(lat, lon, display_name)
    weather_data = fetch_weather(lat, lon, display_name)

    aqi  = float(aqi_data["aqi"])
    temp = weather_data["temperature"]
    hum  = weather_data["humidity"]
    wind = weather_data["wind_speed"]

    heat_idx      = calc_heat_index(temp, hum)
    green_impact  = calc_green_impact(aqi, temp)
    noise_impact  = calc_noise_impact(aqi, wind)
    water_stress  = calc_water_stress(temp, hum)
    waste_pressure = calc_waste_pressure(aqi, temp)

    params = {
        "aqi":           aqi,
        "temperature":   temp,
        "humidity":      hum,
        "wind_speed":    wind,
        "heat_index":    heat_idx,
        "green_impact":  green_impact,
        "noise_impact":  noise_impact,
        "water_stress":  water_stress,
        "waste_pressure": waste_pressure,
        "bonus_score":   0,
        "description":   weather_data["description"],
        "feels_like":    weather_data["feels_like"],
        "pressure":      weather_data["pressure"],
        "pm25":          aqi_data.get("pm25"),
        "pm10":          aqi_data.get("pm10"),
        "co":            aqi_data.get("co"),
        "no2":           aqi_data.get("no2"),
        "data_source":   aqi_data["source"],
    }

    score, label, sub_scores = calc_health_score(params)
    params["health_score"] = score
    params["score_label"]  = label
    params["sub_scores"]   = sub_scores
    params["action_plan"]  = get_action_plan(params)

    return params
