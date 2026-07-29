from typing import Dict, Any, List

GLOBAL_WEATHER_KNOWLEDGE = {
    "cyclone": {
        "title": "🌀 Cyclone, Typhoon & Hurricane Emergency Management",
        "historical_context": "Tropical cyclones (e.g. Hurricane Katrina, Cyclone Nargis, Typhoon Tip) generate devastating wind velocities exceeding 120 km/h and massive storm surges.",
        "precautions": [
            "Secure all windows and doors with storm shutters or heavy plywood.",
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

REGIONAL_CLIMATE_PATTERNS = {
    "asia": "Influenced by South-East Monsoons (June-Sept), Siberian Cold Highs (Dec-Feb), and West Pacific Typhoons.",
    "europe": "Westerlies tempered by Gulf Stream currents, experiencing North Atlantic maritime lows and summer Mediterranean heat.",
    "americas": "Vulnerable to Tornado Alley convective storms, Atlantic/Gulf Hurricanes, and Canadian Arctic Polar Outbreaks.",
    "oceania": "Driven by El Niño-Southern Oscillation (ENSO) cycles, severe summer bushfire dynamics, and Southern Ocean squalls."
}

def query_global_knowledge(query: str, current_temp: float, precip_prob: float, risk_cat: str) -> Dict[str, Any]:
    q_lower = query.lower()
    
    # Intent Match
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
        # Dynamic topic selection based on current live weather risk
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
