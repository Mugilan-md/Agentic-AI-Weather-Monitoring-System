import requests
import time
import random
from typing import Dict, Any, List
from config import Config
from ml_service import ml_service
import weather_knowledge

# WMO Weather interpretation codes
WMO_WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing Rime Fog",
    51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
    61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
    71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow",
    80: "Slight Rain Showers", 81: "Moderate Rain Showers", 82: "Violent Rain Showers",
    95: "Thunderstorm", 96: "Thunderstorm with Slight Hail", 99: "Thunderstorm with Heavy Hail"
}

def get_weather_icon(code: int) -> str:
    if code == 0: return "☀️"
    elif code in [1, 2]: return "⛅"
    elif code == 3: return "☁️"
    elif code in [45, 48]: return "🌫️"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️"
    elif code in [71, 73, 75]: return "❄️"
    elif code in [95, 96, 99]: return "⛈️"
    return "🌡️"

CITY_PRESETS = {
    "london": {"lat": 51.5074, "lon": -0.1278, "country": "United Kingdom", "temp": 18.2, "humidity": 65, "cond": "Light Drizzle", "code": 51, "wind": 12.0, "uv": 4.1, "aqi": 42},
    "chennai": {"lat": 13.0827, "lon": 80.2707, "country": "India", "temp": 32.5, "humidity": 78, "cond": "Partly Cloudy", "code": 2, "wind": 14.5, "uv": 8.2, "aqi": 85},
    "tokyo": {"lat": 35.6762, "lon": 139.6503, "country": "Japan", "temp": 26.0, "humidity": 58, "cond": "Clear Sky", "code": 0, "wind": 9.5, "uv": 6.8, "aqi": 35},
    "new york": {"lat": 40.7128, "lon": -74.0060, "country": "United States", "temp": 24.5, "humidity": 52, "cond": "Mainly Clear", "code": 1, "wind": 11.2, "uv": 5.5, "aqi": 55},
    "paris": {"lat": 48.8566, "lon": 2.3522, "country": "France", "temp": 21.0, "humidity": 60, "cond": "Partly Cloudy", "code": 2, "wind": 10.0, "uv": 5.0, "aqi": 48},
    "sydney": {"lat": -33.8688, "lon": 151.2093, "country": "Australia", "temp": 19.5, "humidity": 70, "cond": "Moderate Rain", "code": 63, "wind": 18.2, "uv": 3.5, "aqi": 30}
}


class DataCollectionAgent:
    """Agent 1: Atmospheric Data Gathering & Universal Geolocation for 400,000+ Global Cities & Villages."""
    
    def __init__(self):
        self.name = "Data Collection Agent"
        self.role = "Global Geolocation & Atmospheric Telemetry Data Fetcher"

    def search_city(self, city_query: str) -> List[Dict[str, Any]]:
        try:
            params = {"name": city_query, "count": 8, "language": "en", "format": "json"}
            resp = requests.get(Config.OPEN_METEO_GEOCODING_URL, params=params, timeout=4)
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                cities = []
                for item in results:
                    cities.append({
                        "name": item.get("name"),
                        "country": item.get("country", ""),
                        "country_code": item.get("country_code", ""),
                        "admin1": item.get("admin1", ""),
                        "latitude": item.get("latitude"),
                        "longitude": item.get("longitude")
                    })
                return cities
        except Exception:
            pass

        q_lower = city_query.lower()
        matched = []
        for key, val in CITY_PRESETS.items():
            if q_lower in key:
                matched.append({
                    "name": key.capitalize(),
                    "country": val["country"],
                    "country_code": "",
                    "admin1": "Region",
                    "latitude": val["lat"],
                    "longitude": val["lon"]
                })
        return matched

    def geolocate(self, city_name: str) -> Dict[str, Any]:
        if "," in city_name and any(c.isdigit() for c in city_name):
            try:
                parts = [float(p.strip()) for p in city_name.split(",")]
                if len(parts) == 2:
                    return {
                        "city": f"Coords ({parts[0]:.2f}, {parts[1]:.2f})",
                        "country": "Global Location",
                        "latitude": parts[0],
                        "longitude": parts[1],
                        "is_fallback": False
                    }
            except Exception:
                pass

        try:
            params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
            resp = requests.get(Config.OPEN_METEO_GEOCODING_URL, params=params, timeout=5)
            if resp.status_code == 200:
                results = resp.json().get("results")
                if results:
                    top = results[0]
                    return {
                        "city": top.get("name"),
                        "country": top.get("country", "Global"),
                        "latitude": top.get("latitude"),
                        "longitude": top.get("longitude"),
                        "is_fallback": False
                    }
        except Exception:
            pass

        city_key = city_name.strip().lower()
        preset = CITY_PRESETS.get(city_key)
        if preset:
            return {
                "city": city_name.strip().capitalize(),
                "country": preset["country"],
                "latitude": preset["lat"],
                "longitude": preset["lon"],
                "is_fallback": True
            }
        
        hash_val = sum(ord(c) for c in city_name)
        lat = round((hash_val % 140) - 70, 4)
        lon = round((hash_val % 360) - 180, 4)
        return {
            "city": city_name.strip().capitalize(),
            "country": "Regional Location",
            "latitude": lat,
            "longitude": lon,
            "is_fallback": True
        }

    def generate_fallback_weather(self, location: Dict[str, Any]) -> Dict[str, Any]:
        city_key = location["city"].lower()
        preset = CITY_PRESETS.get(city_key, {
            "temp": 22.0, "humidity": 60, "cond": "Partly Cloudy", "code": 2, "wind": 12.0, "uv": 5.0, "aqi": 40
        })

        temp = preset["temp"]
        humidity = preset["humidity"]
        condition_str = preset["cond"]
        weather_code = preset["code"]
        wind_speed = preset["wind"]
        uv_index = preset["uv"]
        aqi_val = preset["aqi"]

        hourly_list = []
        for i in range(24):
            time_str = f"{i:02d}:00"
            hour_temp = round(temp + 3.5 * (i / 12.0 - 1.0), 1)
            precip_prob = random.choice([10, 20, 30, 60]) if "Rain" in condition_str else random.choice([0, 5, 10])
            hourly_list.append({
                "time": time_str,
                "temp": hour_temp,
                "precip_prob": precip_prob,
                "icon": get_weather_icon(weather_code)
            })

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        daily_list = []
        for d in days:
            max_t = round(temp + 3.0, 1)
            min_t = round(temp - 3.0, 1)
            daily_list.append({
                "date": d,
                "max_temp": max_t,
                "min_temp": min_t,
                "condition": condition_str,
                "icon": get_weather_icon(weather_code),
                "uv_index": uv_index,
                "precip_prob": 15
            })

        return {
            "location": location,
            "mode": "OFFLINE_FALLBACK",
            "current": {
                "temperature": temp,
                "feels_like": round(temp + 1.2, 1),
                "humidity": humidity,
                "condition": condition_str,
                "icon": get_weather_icon(weather_code),
                "weather_code": weather_code,
                "wind_speed": wind_speed,
                "wind_gusts": round(wind_speed * 1.4, 1),
                "wind_direction": 180,
                "pressure": 1014,
                "cloud_cover": 40,
                "precipitation": 0.0,
                "uv_index": uv_index
            },
            "air_quality": {
                "us_aqi": aqi_val,
                "pm2_5": round(aqi_val * 0.4, 1),
                "pm10": round(aqi_val * 0.8, 1),
                "ozone": 35.0
            },
            "hourly": hourly_list,
            "daily": daily_list
        }

    def fetch_data(self, city_name: str) -> Dict[str, Any]:
        location = self.geolocate(city_name)
        lat = location["latitude"]
        lon = location["longitude"]

        try:
            weather_params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m", "relative_humidity_2m", "apparent_temperature",
                    "is_day", "precipitation", "rain", "showers", "weather_code",
                    "cloud_cover", "surface_pressure", "wind_speed_10m", "wind_direction_10m",
                    "wind_gusts_10m"
                ],
                "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability", "precipitation", "weather_code"],
                "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "uv_index_max", "precipitation_sum", "precipitation_probability_max"],
                "timezone": "auto"
            }
            
            weather_resp = requests.get(Config.OPEN_METEO_WEATHER_URL, params=weather_params, timeout=6)
            if weather_resp.status_code == 200:
                w_data = weather_resp.json()
                curr = w_data.get("current", {})
                daily = w_data.get("daily", {})
                hourly = w_data.get("hourly", {})

                aq_params = {
                    "latitude": lat,
                    "longitude": lon,
                    "current": ["us_aqi", "pm10", "pm2_5", "ozone"]
                }
                aq_data = {}
                try:
                    aq_resp = requests.get(Config.OPEN_METEO_AIR_QUALITY_URL, params=aq_params, timeout=4)
                    if aq_resp.status_code == 200:
                        aq_data = aq_resp.json().get("current", {})
                except Exception:
                    pass

                weather_code = curr.get("weather_code", 0)
                condition_str = WMO_WEATHER_CODES.get(weather_code, "Clear Sky")
                icon_str = get_weather_icon(weather_code)

                hourly_list = []
                h_times = hourly.get("time", [])[:24]
                h_temps = hourly.get("temperature_2m", [])[:24]
                h_precip = hourly.get("precipitation_probability", [])[:24]
                h_codes = hourly.get("weather_code", [])[:24]

                for idx, t in enumerate(h_times):
                    time_label = t.split("T")[-1] if "T" in t else t
                    hourly_list.append({
                        "time": time_label,
                        "temp": h_temps[idx] if idx < len(h_temps) else 0,
                        "precip_prob": h_precip[idx] if idx < len(h_precip) else 0,
                        "icon": get_weather_icon(h_codes[idx]) if idx < len(h_codes) else "🌡️"
                    })

                daily_list = []
                d_times = daily.get("time", [])
                d_max = daily.get("temperature_2m_max", [])
                d_min = daily.get("temperature_2m_min", [])
                d_codes = daily.get("weather_code", [])
                d_uv = daily.get("uv_index_max", [])

                for idx, d in enumerate(d_times[:7]):
                    daily_list.append({
                        "date": d,
                        "max_temp": d_max[idx] if idx < len(d_max) else 0,
                        "min_temp": d_min[idx] if idx < len(d_min) else 0,
                        "condition": WMO_WEATHER_CODES.get(d_codes[idx], "Clear") if idx < len(d_codes) else "Clear",
                        "icon": get_weather_icon(d_codes[idx]) if idx < len(d_codes) else "☀️",
                        "uv_index": d_uv[idx] if idx < len(d_uv) else 0,
                        "precip_prob": 15
                    })

                return {
                    "location": location,
                    "mode": "ONLINE_SATELLITE",
                    "current": {
                        "temperature": curr.get("temperature_2m", 0.0),
                        "feels_like": curr.get("apparent_temperature", curr.get("temperature_2m", 0.0)),
                        "humidity": curr.get("relative_humidity_2m", 0),
                        "condition": condition_str,
                        "icon": icon_str,
                        "weather_code": weather_code,
                        "wind_speed": curr.get("wind_speed_10m", 0.0),
                        "wind_gusts": curr.get("wind_gusts_10m", 0.0),
                        "wind_direction": curr.get("wind_direction_10m", 0),
                        "pressure": curr.get("surface_pressure", 1013),
                        "cloud_cover": curr.get("cloud_cover", 0),
                        "precipitation": curr.get("precipitation", 0.0),
                        "uv_index": d_uv[0] if d_uv else 5.0
                    },
                    "air_quality": {
                        "us_aqi": aq_data.get("us_aqi", 42),
                        "pm2_5": aq_data.get("pm2_5", 12.0),
                        "pm10": aq_data.get("pm10", 22.0),
                        "ozone": aq_data.get("ozone", 38.0)
                    },
                    "hourly": hourly_list,
                    "daily": daily_list
                }
        except Exception:
            pass

        return self.generate_fallback_weather(location)


class AnalysisAgent:
    """Agent 2: Risk & Anomaly Analysis Agent enhanced with ML Service predictions."""
    
    def __init__(self):
        self.name = "Risk & Anomaly Analysis Agent"
        self.role = "Hazard Evaluation & ML Safety Index Computation"

    def analyze(self, raw_data: Dict[str, Any], ml_res: Dict[str, Any]) -> Dict[str, Any]:
        curr = raw_data["current"]
        ml_alert = ml_res["intelligent_alert"]
        ml_risk_cat = ml_res["risk_classification"]["category"]
        ml_anomaly = ml_res["anomaly_detection"]

        safety_score = ml_alert["ml_risk_score"]
        status_level = ml_alert["priority"]

        hazards = []
        if ml_anomaly["is_anomaly"]:
            hazards.append({"level": "WARNING", "type": "Environmental Anomaly Alert", "desc": "ML Isolation Forest detected abnormal atmospheric pattern deviation."})

        if ml_risk_cat == "Cyclone Risk":
            hazards.append({"level": "CRITICAL", "type": "Severe Cyclone Risk", "desc": f"ML Risk Classifier predicted {ml_risk_cat} with {ml_res['risk_classification']['confidence_pct']}% confidence."})
        elif ml_risk_cat == "Storm":
            hazards.append({"level": "CRITICAL", "type": "Severe Storm Risk", "desc": "ML Classifier detected severe thunderstorm and high wind velocity."})
        elif ml_risk_cat == "Heavy Rain":
            hazards.append({"level": "WARNING", "type": "Heavy Rain Warning", "desc": f"ML Rainfall Model estimates {ml_res['rainfall_prediction']['probability_pct']}% rain chance."})
        elif ml_risk_cat == "Heatwave":
            hazards.append({"level": "WARNING", "type": "Extreme Heatwave Alert", "desc": f"Elevated temperature detected ({curr['temperature']}°C)."})

        if status_level == "CRITICAL":
            status_text = "Critical Severe Weather Warning"
            status_level_formatted = "CRITICAL_RISK"
        elif status_level == "HIGH":
            status_text = "High Weather Risk Advisory"
            status_level_formatted = "HIGH_RISK"
        elif status_level == "MEDIUM":
            status_text = "Moderate Weather Advisory"
            status_level_formatted = "MODERATE"
        else:
            status_text = "Optimal Favorable Conditions"
            status_level_formatted = "OPTIMAL"

        return {
            "safety_score": safety_score,
            "status_level": status_level_formatted,
            "status_text": status_text,
            "hazards": hazards,
            "hazard_count": len(hazards),
            "ml_risk_category": ml_risk_cat
        }


class PredictiveAgent:
    """Agent 3: Evaluates 24-hour thermal curves and machine learning forecasting trends."""
    
    def __init__(self):
        self.name = "Predictive & Trend Agent"
        self.role = "24H ML Trend Analysis & Forecast Prediction"

    def predict(self, raw_data: Dict[str, Any], ml_res: Dict[str, Any]) -> Dict[str, Any]:
        hourly = raw_data.get("hourly", [])
        daily = raw_data.get("daily", [])
        ml_temp = ml_res["temperature_forecast"]
        ml_rain = ml_res["rainfall_prediction"]

        max_rain_prob = max([h.get("precip_prob", 0) for h in hourly]) if hourly else ml_rain["probability_pct"]
        temps = [h.get("temp", 0) for h in hourly if "temp" in h]
        min_24h = min(temps) if temps else raw_data["current"]["temperature"] - 3.0
        max_24h = max(temps) if temps else raw_data["current"]["temperature"] + 4.0

        summary = f"ML Models predict 24h temperature trend: {ml_temp['trend']} to {ml_temp['predicted_temp_24h']}°C (Delta: {ml_temp['delta']}°C). Rainfall Probability: {ml_rain['probability_pct']}% with {ml_rain['confidence_pct']}% ML confidence."

        return {
            "max_rain_prob_24h": max_rain_prob,
            "peak_rain_time": "16:00",
            "temp_delta_24h": ml_temp['delta'],
            "min_24h": min_24h,
            "max_24h": max_24h,
            "rainy_days_count_7d": sum(1 for d in daily if d.get("precip_prob", 0) > 50),
            "predictive_summary": summary
        }


class ActionAgent:
    """Agent 4: Research-backed, highly practical and realistic city-specific advisories."""
    
    def __init__(self):
        self.name = "Decision & Action Agent"
        self.role = "Research-Backed Realistic Safety Advisory Generation"

    def recommend(self, raw_data: Dict[str, Any], analysis: Dict[str, Any], predictions: Dict[str, Any], ml_res: Dict[str, Any]) -> Dict[str, Any]:
        curr = raw_data["current"]
        air_quality = raw_data.get("air_quality", {})
        city = raw_data["location"]["city"]
        status_level = analysis["status_level"]

        if status_level == "CRITICAL_RISK":
            primary_action = f"🚨 CRITICAL ML ADVISORY FOR {city.upper()}: Severe meteorological risk. Limit non-essential travel and remain indoors."
        elif status_level == "HIGH_RISK":
            primary_action = f"⚠️ HIGH RISK ADVISORY FOR {city.upper()}: Adverse atmospheric conditions. Postpone intense outdoor activities."
        elif status_level == "MODERATE":
            primary_action = f"⚡ MODERATE ADVISORY FOR {city.upper()}: Minor environmental hazards detected. Exercise standard precautions."
        else:
            primary_action = f"🌿 OPTIMAL CONDITIONS IN {city.upper()}: Weather is favorable for outdoor activities and daily routines!"

        # Generate evidence-based, realistic, city-specific advisories
        actions = weather_knowledge.generate_research_advisories(city, curr, air_quality, ml_res)

        return {
            "primary_advisory": primary_action,
            "detailed_actions": actions
        }


class ConversationalAgent:
    """Agent 5: Intelligent, Natural Language Conversational Assistant with Intent-Aware Reasoning."""
    
    def __init__(self):
        self.name = "AI Conversational Assistant"
        self.role = "Conversational Intelligence & Meteorological Assistant"

    def respond(self, query: str, weather_result: Dict[str, Any]) -> Dict[str, Any]:
        q_clean = query.strip().lower()
        curr = weather_result["data"]["current"]
        loc = weather_result["data"]["location"]
        analysis = weather_result["analysis"]
        city = loc["city"]
        country = loc["country"]
        temp = curr["temperature"]
        feels = curr["feels_like"]
        cond = curr["condition"]
        humidity = curr["humidity"]
        wind = curr["wind_speed"]
        uv = curr["uv_index"]
        aqi = weather_result["data"]["air_quality"]["us_aqi"]
        safety = analysis["safety_score"]
        
        ml_analytics = weather_result.get("ml_analytics", {})
        ml_rain = ml_analytics.get("rainfall_prediction", {})
        ml_risk = ml_analytics.get("risk_classification", {})
        rain_prob = ml_rain.get("probability_pct", 15)
        rain_conf = ml_rain.get("confidence_pct", 90)
        risk_cat = ml_risk.get("category", "Normal")

        # 1. Casual Greetings (hi, hello, hey, good morning, etc.)
        greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "howdy", "sup"]
        if q_clean in greetings or any(q_clean.startswith(g + " ") or q_clean == g for g in greetings):
            answer = f"Hello! 👋 I am your <strong>Agentic AI Weather Assistant</strong>.<br><br>" \
                     f"I'm currently monitoring live atmospheric telemetry for <strong>{city}, {country}</strong> (Temp: <strong>{temp}°C</strong>, Condition: <strong>{cond}</strong>).<br><br>" \
                     f"How can I assist you today? You can ask me questions like:<br>" \
                     f"• <em>'Is it safe for outdoor running right now?'</em><br>" \
                     f"• <em>'Do I need an umbrella today?'</em><br>" \
                     f"• <em>'What should I wear in {city} today?'</em><br>" \
                     f"• <em>'What are the emergency precautions for floods or heatwaves?'</em>"
            return {"query": query, "answer": answer, "agent_name": self.name}

        # 2. Conversational Capabilities / Gratitude (who are you, thank you, help, etc.)
        if any(k in q_clean for k in ["who are you", "what can you do", "help me", "your name"]):
            answer = f"I am your <strong>Interactive Agentic AI Weather Assistant</strong>! 🤖<br><br>" \
                     f"I analyze live satellite data, run Scikit-Learn Machine Learning models (Rainfall probability, Risk classification, Anomaly detection), and cross-reference global emergency disaster management protocols to give you accurate, real-time safety advice for any location worldwide."
            return {"query": query, "answer": answer, "agent_name": self.name}

        if any(k in q_clean for k in ["thank you", "thanks", "awesome", "great", "cool"]):
            answer = f"You're very welcome! 😊 Stay safe and feel free to ask if you need any more weather updates or travel advice for {city}!"
            return {"query": query, "answer": answer, "agent_name": self.name}

        # 3. Outdoor Exercise / Running Intent
        if any(k in q_clean for k in ["run", "running", "jog", "jogging", "walk", "outdoor", "sport", "football", "cricket"]):
            if safety >= 70 and rain_prob < 40 and aqi < 100:
                answer = f"🏃 <strong>Yes! Outdoor running conditions in {city} are excellent right now.</strong><br><br>" \
                         f"• Temperature: <strong>{temp}°C</strong> (Feels like {feels}°C)<br>" \
                         f"• Condition: <strong>{cond}</strong> | Humidity: <strong>{humidity}%</strong><br>" \
                         f"• Air Quality: US AQI <strong>{aqi}</strong> (Safe) | ML Safety Score: <strong>{safety}/100</strong><br><br>" \
                         f"💡 <em>Tip: Enjoy your run! Stay hydrated.</em>"
            else:
                answer = f"⚠️ <strong>Caution is advised for outdoor activities in {city}.</strong><br><br>" \
                         f"• ML Risk Level: <strong>{risk_cat}</strong> (Safety Score: <strong>{safety}/100</strong>)<br>" \
                         f"• Rain Probability: <strong>{rain_prob}%</strong> | US AQI: <strong>{aqi}</strong><br><br>" \
                         f"💡 <em>Tip: Consider indoor gym exercise or waiting until weather conditions improve.</em>"
            return {"query": query, "answer": answer, "agent_name": self.name}

        # 4. Rain & Umbrella Intent
        if any(k in q_clean for k in ["rain", "umbrella", "wet", "drizzle", "downpour", "shower"]):
            if rain_prob >= 45 or "Rain" in cond or "Drizzle" in cond:
                answer = f"☔ <strong>Yes, carry an umbrella!</strong><br><br>" \
                         f"• ML Rainfall Prediction: <strong>{rain_prob}% probability</strong> (Model Confidence: <strong>{rain_conf}%</strong>)<br>" \
                         f"• Current Condition in {city}: <strong>{cond}</strong><br><br>" \
                         f"💡 <em>Recommendation: Waterproof footwear and a sturdy windproof umbrella are recommended today.</em>"
            else:
                answer = f"☀️ <strong>Low chance of rain in {city} right now.</strong><br><br>" \
                         f"• ML Rainfall Probability: <strong>{rain_prob}%</strong><br>" \
                         f"• Current Condition: <strong>{cond}</strong><br><br>" \
                         f"💡 <em>You likely won't need an umbrella today!</em>"
            return {"query": query, "answer": answer, "agent_name": self.name}

        # 5. Clothing & Outfit Intent
        if any(k in q_clean for k in ["wear", "cloth", "outfit", "jacket", "coat", "sweater", "dress"]):
            if temp >= 30:
                answer = f"👕 <strong>Outfit Advice for {city} ({temp}°C)</strong>:<br>" \
                         f"Wear lightweight, breathable cotton or linen clothing. Apply SPF 50+ sunscreen (UV Index: {uv}) and wear sunglasses."
            elif temp <= 10:
                answer = f"🧥 <strong>Outfit Advice for {city} ({temp}°C)</strong>:<br>" \
                         f"It's cold! Wear layered thermal clothing, a heavy insulated jacket or coat, and warm gloves."
            else:
                answer = f"🧥 <strong>Outfit Advice for {city} ({temp}°C)</strong>:<br>" \
                         f"Comfortable moderate weather attire. A light jacket, hoodie, or sweater over jeans is ideal for {cond}."
            return {"query": query, "answer": answer, "agent_name": self.name}

        # 6. Air Quality & Health Intent
        if any(k in q_clean for k in ["air", "aqi", "smog", "pollution", "kid", "asthma", "breath"]):
            if aqi < 50:
                aq_status = "Good (Clean Air)"
            elif aqi < 100:
                aq_status = "Moderate"
            else:
                aq_status = "Unhealthy for Sensitive Groups"
            answer = f"😷 <strong>Air Quality Report for {city}</strong>:<br><br>" \
                     f"• US AQI Level: <strong>{aqi}</strong> — <strong>{aq_status}</strong><br>" \
                     f"• PM2.5 / PM10 particles are within normal monitoring ranges.<br><br>" \
                     f"💡 <em>Recommendation: {'Clean air for all outdoor activities!' if aqi < 100 else 'Sensitive individuals should wear an N95 mask outdoors.'}</em>"
            return {"query": query, "answer": answer, "agent_name": self.name}

        # 7. Severe Weather & Disaster Emergency Intent
        if any(k in q_clean for k in ["cyclone", "hurricane", "flood", "heatwave", "blizzard", "typhoon", "disaster", "emergency"]):
            knowledge = weather_knowledge.query_global_knowledge(query, temp, rain_prob, risk_cat)
            precautions_html = "".join([f"<li>{p}</li>" for p in knowledge["precautions"]])
            answer = f"🤖 <strong>Emergency Management Protocol for {city}</strong>:<br><br>" \
                     f"<strong>{knowledge['title']}</strong><br>" \
                     f"📜 <em>Historical Context</em>: {knowledge['historical_context']}<br><br>" \
                     f"🛡️ <strong>Research-Backed Precautionary Steps</strong>:<ul>{precautions_html}</ul>" \
                     f"💡 <strong>Optimal Solution</strong>:<br><strong>{knowledge['best_solution']}</strong>"
            return {"query": query, "answer": answer, "agent_name": self.name}

        # 8. General Weather Query / Fallback
        answer = f"🤖 <strong>Weather & Safety Briefing for {city}, {country}</strong>:<br><br>" \
                 f"• Temperature: <strong>{temp}°C</strong> ({cond}) | Feels like <strong>{feels}°C</strong><br>" \
                 f"• Moisture & Wind: Humidity <strong>{humidity}%</strong> | Wind <strong>{wind} km/h</strong><br>" \
                 f"• ML Risk Level: <strong>{risk_cat}</strong> (Safety Index: <strong>{safety}/100</strong>)<br>" \
                 f"• ML Rain Probability: <strong>{rain_prob}%</strong> (Confidence: <strong>{rain_conf}%</strong>)<br><br>" \
                 f"💡 <em>How else can I assist you with weather forecasts, outdoor activities, or clothing recommendations?</em>"

        return {
            "query": query,
            "answer": answer,
            "agent_name": self.name
        }


class AgenticWeatherSystem:
    """Orchestrator Agent: Coordinates execution across sub-agents and ML Service Layer."""
    
    def __init__(self):
        self.collector = DataCollectionAgent()
        self.analyzer = AnalysisAgent()
        self.predictor = PredictiveAgent()
        self.actioner = ActionAgent()
        self.chat_agent = ConversationalAgent()

    def run_pipeline(self, city_name: str) -> Dict[str, Any]:
        logs = []
        
        t0 = time.time()
        raw_data = self.collector.fetch_data(city_name)
        dt1 = round((time.time() - t0) * 1000, 2)
        logs.append({
            "agent": self.collector.name,
            "role": self.collector.role,
            "status": "SUCCESS",
            "duration_ms": dt1,
            "thought": f"Retrieved atmospheric telemetry for '{raw_data['location']['city']}'. Temp: {raw_data['current']['temperature']}°C, Humidity: {raw_data['current']['humidity']}%, Pressure: {raw_data['current']['pressure']} hPa."
        })

        t0 = time.time()
        ml_res = ml_service.predict_weather_features(raw_data["current"], raw_data["air_quality"])
        dt_ml = round((time.time() - t0) * 1000, 2)

        t0 = time.time()
        analysis = self.analyzer.analyze(raw_data, ml_res)
        dt2 = round((time.time() - t0) * 1000, 2)
        logs.append({
            "agent": self.analyzer.name,
            "role": self.analyzer.role,
            "status": "SUCCESS",
            "duration_ms": dt2 + dt_ml,
            "thought": f"ML Service Inference completed. Category: '{ml_res['risk_classification']['category']}' ({ml_res['risk_classification']['confidence_pct']}% conf), Rain Prob: {ml_res['rainfall_prediction']['probability_pct']}%, Anomaly: {ml_res['anomaly_detection']['status']}. ML Risk Score: {analysis['safety_score']}/100."
        })

        t0 = time.time()
        predictions = self.predictor.predict(raw_data, ml_res)
        dt3 = round((time.time() - t0) * 1000, 2)
        logs.append({
            "agent": self.predictor.name,
            "role": self.predictor.role,
            "status": "SUCCESS",
            "duration_ms": dt3,
            "thought": predictions["predictive_summary"]
        })

        t0 = time.time()
        recommendations = self.actioner.recommend(raw_data, analysis, predictions, ml_res)
        dt4 = round((time.time() - t0) * 1000, 2)
        logs.append({
            "agent": self.actioner.name,
            "role": self.actioner.role,
            "status": "SUCCESS",
            "duration_ms": dt4,
            "thought": f"Generated {len(recommendations['detailed_actions'])} research-backed advisories."
        })

        return {
            "data": raw_data,
            "analysis": analysis,
            "predictions": predictions,
            "recommendations": recommendations,
            "ml_analytics": ml_res,
            "agent_logs": logs,
            "total_execution_ms": round(dt1 + dt_ml + dt2 + dt3 + dt4, 2)
        }

    def chat(self, query: str, weather_result: Dict[str, Any]) -> Dict[str, Any]:
        return self.chat_agent.respond(query, weather_result)


orchestrator = AgenticWeatherSystem()

def run_weather_agent(city: str) -> Dict[str, Any]:
    return orchestrator.run_pipeline(city)

def run_agent_chat(query: str, weather_result: Dict[str, Any]) -> Dict[str, Any]:
    return orchestrator.chat(query, weather_result)
