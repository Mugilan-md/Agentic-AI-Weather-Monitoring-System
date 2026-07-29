from typing import Dict, Any, List

GLOBAL_WEATHER_KNOWLEDGE = {
    "cyclone": {
        "title": "🌀 Cyclone, Typhoon & Hurricane Emergency Management",
        "historical_context": "Tropical cyclones (e.g. Hurricane Katrina, Cyclone Nargis, Typhoon Tip) generate devastating wind velocities exceeding 120 km/h and massive storm surges.",
        "precautions": [
            "Secure all windows and doors with storm shutters or heavy 5/8-inch exterior plywood.",
            "Stock an emergency supply kit with 3 days of non-perishable food, water (4L/person/day), first aid, flashlight, and power banks.",
            "Charge all mobile devices and monitor official emergency broadcasts (NOAA / IMD / JMA)."
        ],
        "best_solution": "If located in a low-lying coastal zone under a mandatory evacuation order, evacuate immediately along designated emergency routes. Do not attempt to drive through flooded roads."
    },
    "heatwave": {
        "title": "🌡️ Extreme Heatwave & Thermal Risk Management",
        "historical_context": "Record heatwaves (e.g., European Heatwave 2003, South Asian Summer 2022) cause severe heat exhaustion, wet-bulb temperature stress, and power grid failures.",
        "precautions": [
            "Maintain high hydration by drinking electrolyte-rich water (at least 3-4 liters daily).",
            "Avoid direct sun exposure during peak solar hours between 11:00 AM and 16:00 PM.",
            "Wear loose, light-colored, breathable cotton clothing and UV 400 blocking sunglasses."
        ],
        "best_solution": "Remain indoors in air-conditioned or well-ventilated shade. Apply cold compresses to wrist and neck pulse points if experiencing heat fatigue."
    },
    "flood": {
        "title": "🌊 Torrential Rain & Flash Flood Management",
        "historical_context": "Flash flooding from sudden cloudbursts and stalled monsoonal troughs can inundate urban areas within minutes.",
        "precautions": [
            "Move valuable electronics and documents to upper floors.",
            "Never walk or drive through moving floodwaters ('Turn Around, Don't Drown'). As little as 15 cm of moving water can knock a person down.",
            "Disconnect main electrical switches if floodwaters enter the building."
        ],
        "best_solution": "Move to higher ground immediately. Avoid storm drains, culverts, and low-lying underpasses."
    },
    "blizzard": {
        "title": "❄️ Sub-Zero Freeze & Blizzard Management",
        "historical_context": "Arctic polar vortex outbreaks cause rapid temperature drops, dangerous wind chills, hypothermia, and widespread frostbite.",
        "precautions": [
            "Dress in multiple warm synthetic or wool layers rather than a single heavy coat.",
            "Keep home heating pipes insulated to prevent bursting.",
            "Equip vehicles with emergency blankets, ice scrapers, sand, and jumper cables."
        ],
        "best_solution": "Stay sheltered indoors. If outdoor travel is unavoidable, cover all exposed skin to prevent frostbite within minutes."
    },
    "pollution": {
        "title": "😷 Hazardous Air Quality & Smog Protocol",
        "historical_context": "High particulate pollution (PM2.5 / PM10) from crop burning, industrial emissions, and temperature inversions increases respiratory hazards.",
        "precautions": [
            "Wear tightly fitted N95 or KN95 masks when stepping outdoors.",
            "Run indoor HEPA air purifiers and keep windows closed during peak AQI spikes.",
            "Postpone strenuous outdoor exercise and jogging when AQI exceeds 150."
        ],
        "best_solution": "Minimize outdoor exposure for children, elderly, and individuals with asthma. Utilize indoor ventilation filtration."
    }
}

# Research-Backed Action Advisories Generator for ActionAgent
def generate_research_advisories(city: str, current: Dict[str, Any], air_quality: Dict[str, Any], ml_analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
    temp = current.get("temperature", 22.0)
    feels = current.get("feels_like", temp)
    humidity = current.get("humidity", 60)
    wind = current.get("wind_speed", 12.0)
    pressure = current.get("pressure", 1013)
    uv = current.get("uv_index", 5.0)
    aqi = air_quality.get("us_aqi", 42)
    
    ml_rain = ml_analytics.get("rainfall_prediction", {})
    ml_risk = ml_analytics.get("risk_classification", {})
    ml_anomaly = ml_analytics.get("anomaly_detection", {})
    rain_prob = ml_rain.get("probability_pct", 15)
    risk_cat = ml_risk.get("category", "Normal")

    advisories = []

    # 1. Hydration & Heat Stress (Wet-Bulb Heat Index Thresholds)
    if temp >= 35 or feels >= 38:
        advisories.append({
            "category": "Thermoregulatory Heat Safety",
            "icon": "💧",
            "text": f"High thermal load detected in {city} ({temp}°C, feels like {feels}°C). Drink 500ml of electrolyte water every hour. Avoid intense outdoor physical exertion between 11 AM - 4 PM."
        })
    elif temp >= 30:
        advisories.append({
            "category": "Moderate Thermal Exertion",
            "icon": "🥤",
            "text": f"Warm conditions in {city} ({temp}°C). Maintain adequate hydration (2.5L-3L daily) and rest in shaded or air-conditioned environments."
        })
    elif temp <= 5:
        advisories.append({
            "category": "Sub-Zero Thermal Insulation",
            "icon": "🧥",
            "text": f"Freezing temperatures in {city} ({temp}°C). Wear three-layer thermal insulation (base moisture-wicking layer, fleece mid-layer, windproof outer shell) to prevent hypothermia."
        })

    # 2. Air Quality & Respiratory Protection (WHO PM2.5 Guidelines)
    if aqi >= 150:
        advisories.append({
            "category": "Severe Air Quality Alert",
            "icon": "😷",
            "text": f"US AQI level in {city} is Hazardous ({aqi}). Wear an N95/KN95 respirator outdoors. Run indoor HEPA air purifiers and keep windows closed."
        })
    elif aqi >= 100:
        advisories.append({
            "category": "Moderate Respiratory Advisory",
            "icon": "🍃",
            "text": f"Elevated AQI in {city} ({aqi}). Sensitive groups (children, seniors, asthma sufferers) should reduce prolonged outdoor exertion."
        })

    # 3. Wind Velocity & Structural Dynamics (Beaufort Scale Analysis)
    if wind >= 45 or risk_cat == "Storm":
        advisories.append({
            "category": "Gale-Force Wind Hazards",
            "icon": "💨",
            "text": f"High wind speeds in {city} ({wind} km/h). Secure loose outdoor furniture, avoid standing near large trees or power lines, and drive with extra vehicle stability caution."
        })

    # 4. Precipitation & Rain Gear (Hydro-Meteorological Risk)
    if rain_prob >= 60 or risk_cat == "Heavy Rain":
        advisories.append({
            "category": "Precipitation Preparedness",
            "icon": "☔",
            "text": f"ML Rainfall Model predicts {rain_prob}% rain probability for {city}. Carry a sturdy windproof umbrella and waterproof footwear."
        })
    elif rain_prob >= 35:
        advisories.append({
            "category": "Chance of Light Rain",
            "icon": "🌧️",
            "text": f"Moderate rain chance in {city} ({rain_prob}%). Keep a compact rain jacket or umbrella accessible."
        })

    # 5. Solar UV Dose (Erythemal Exposure Guidelines)
    if uv >= 8.0:
        advisories.append({
            "category": "Very High UV Radiation",
            "icon": "☀️",
            "text": f"Extreme UV Index in {city} ({uv.toFixed(1) if hasattr(uv, 'toFixed') else round(uv,1)}). Apply broad-spectrum SPF 50+ sunscreen every 2 hours and wear broad-brimmed hats."
        })

    # 6. Environmental Anomaly Flag
    if ml_anomaly.get("is_anomaly", False):
        advisories.append({
            "category": "Atmospheric Pattern Anomaly",
            "icon": "🚨",
            "text": f"ML Isolation Forest flagged unusual pressure/wind anomalies in {city}. Monitor local emergency bulletins for rapid weather shifts."
        })

    # Fallback optimal baseline if weather is ideal
    if not advisories:
        advisories.append({
            "category": "Optimal Outdoor Conditions",
            "icon": "🌿",
            "text": f"Weather in {city} is favorable ({temp}°C, {current.get('condition', 'Clear')}). Excellent conditions for outdoor walks, sports, and daily activities."
        })

    return advisories

def query_global_knowledge(query: str, current_temp: float, precip_prob: float, risk_cat: str) -> Dict[str, Any]:
    q_lower = query.lower()
    
    if any(k in q_lower for k in ["cyclone", "hurricane", "typhoon", "storm", "gale"]):
        topic = "cyclone"
    elif any(k in q_lower for k in ["heat", "hot", "heatwave", "sunstroke", "summer"]):
        topic = "heatwave"
    elif any(k in q_lower for k in ["flood", "heavy rain", "downpour", "cloudburst"]):
        topic = "flood"
    elif any(k in q_lower for k in ["snow", "freeze", "cold", "blizzard", "frost"]):
        topic = "blizzard"
    elif any(k in q_lower for k in ["air", "aqi", "smog", "pollution", "smoke"]):
        topic = "pollution"
    else:
        if risk_cat in ["Cyclone Risk", "Storm"]:
            topic = "cyclone"
        elif risk_cat == "Heatwave" or current_temp >= 36:
            topic = "heatwave"
        elif risk_cat == "Heavy Rain" or precip_prob >= 60:
            topic = "flood"
        elif current_temp <= 2:
            topic = "blizzard"
        else:
            topic = "heatwave" if current_temp > 28 else "flood"

    info = GLOBAL_WEATHER_KNOWLEDGE[topic]
    return info
