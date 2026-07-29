import requests
import time
from typing import Dict, Any, List
from config import Config

# Weather Code Mapping (WMO Weather interpretation codes)
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


class DataCollectionAgent:
    """Agent 1: Responsible for location geocoding and real-time/forecast atmospheric data retrieval."""
    
    def __init__(self):
        self.name = "Data Collection Agent"
        self.role = "Atmospheric Data Gathering & Geolocation"

    def search_city(self, city_query: str) -> List[Dict[str, Any]]:
        """Search cities matching name query for autocomplete."""
        try:
            params = {"name": city_query, "count": 5, "language": "en", "format": "json"}
            resp = requests.get(Config.OPEN_METEO_GEOCODING_URL, params=params, timeout=5)
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
        return []

    def geolocate(self, city_name: str) -> Dict[str, Any]:
        """Resolves city name to latitude and longitude."""
        params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
        resp = requests.get(Config.OPEN_METEO_GEOCODING_URL, params=params, timeout=8)
        if resp.status_code != 200:
            raise ValueError(f"Geolocation API request failed with status code {resp.status_code}")
        
        data = resp.json()
        results = data.get("results")
        if not results:
            raise ValueError(f"Location '{city_name}' could not be found. Please check spelling.")
        
        top = results[0]
        return {
            "city": top.get("name"),
            "country": top.get("country", ""),
            "latitude": top.get("latitude"),
            "longitude": top.get("longitude"),
            "timezone": top.get("timezone", "UTC")
        }

    def fetch_data(self, city_name: str) -> Dict[str, Any]:
        location = self.geolocate(city_name)
        lat = location["latitude"]
        lon = location["longitude"]

        # Fetch Weather
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
        
        weather_resp = requests.get(Config.OPEN_METEO_WEATHER_URL, params=weather_params, timeout=10)
        if weather_resp.status_code != 200:
            raise ValueError(f"Weather API request failed for {city_name}")
        
        w_data = weather_resp.json()
        curr = w_data.get("current", {})
        daily = w_data.get("daily", {})
        hourly = w_data.get("hourly", {})

        # Fetch Air Quality
        aq_params = {
            "latitude": lat,
            "longitude": lon,
            "current": ["european_aqi", "us_aqi", "pm10", "pm2_5", "ozone"]
        }
        aq_data = {}
        try:
            aq_resp = requests.get(Config.OPEN_METEO_AIR_QUALITY_URL, params=aq_params, timeout=5)
            if aq_resp.status_code == 200:
                aq_data = aq_resp.json().get("current", {})
        except Exception:
            pass

        weather_code = curr.get("weather_code", 0)
        condition_str = WMO_WEATHER_CODES.get(weather_code, "Unknown")
        icon_str = get_weather_icon(weather_code)

        # Process Hourly (next 24 hours)
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

        # Process Daily (7 days)
        daily_list = []
        d_times = daily.get("time", [])
        d_max = daily.get("temperature_2m_max", [])
        d_min = daily.get("temperature_2m_min", [])
        d_codes = daily.get("weather_code", [])
        d_uv = daily.get("uv_index_max", [])
        d_precip_prob = daily.get("precipitation_probability_max", [])

        for idx, d in enumerate(d_times[:7]):
            daily_list.append({
                "date": d,
                "max_temp": d_max[idx] if idx < len(d_max) else 0,
                "min_temp": d_min[idx] if idx < len(d_min) else 0,
                "condition": WMO_WEATHER_CODES.get(d_codes[idx], "Clear") if idx < len(d_codes) else "Clear",
                "icon": get_weather_icon(d_codes[idx]) if idx < len(d_codes) else "☀️",
                "uv_index": d_uv[idx] if idx < len(d_uv) else 0,
                "precip_prob": d_precip_prob[idx] if idx < len(d_precip_prob) else 0
            })

        max_uv = d_uv[0] if d_uv else 0.0

        return {
            "location": location,
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
                "uv_index": max_uv
            },
            "air_quality": {
                "us_aqi": aq_data.get("us_aqi", 35),
                "pm2_5": aq_data.get("pm2_5", 10.0),
                "pm10": aq_data.get("pm10", 20.0),
                "ozone": aq_data.get("ozone", 40.0)
            },
            "hourly": hourly_list,
            "daily": daily_list
        }


class AnalysisAgent:
    """Agent 2: Analyzes atmospheric risk parameters, anomalies, and safety thresholds."""
    
    def __init__(self):
        self.name = "Risk & Anomaly Analysis Agent"
        self.role = "Hazard Evaluation & Safety Index Computation"

    def analyze(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        curr = raw_data["current"]
        aqi = raw_data["air_quality"].get("us_aqi", 30)

        temp = curr["temperature"]
        wind = curr["wind_speed"]
        gusts = curr["wind_gusts"]
        uv = curr["uv_index"]
        precip = curr["precipitation"]
        condition = curr["condition"].lower()

        hazards = []
        safety_deductions = 0

        # Temperature Analysis
        if temp >= 40:
            hazards.append({"level": "CRITICAL", "type": "Extreme Heatwave Alert", "desc": f"Dangerous heat detected ({temp}°C). High heatstroke risk."})
            safety_deductions += 40
        elif temp >= 35:
            hazards.append({"level": "WARNING", "type": "High Heat Warning", "desc": f"Elevated temperature ({temp}°C). Outdoor exertion cautioned."})
            safety_deductions += 20
        elif temp <= 0:
            hazards.append({"level": "WARNING", "type": "Freezing Conditions", "desc": f"Sub-zero temperature ({temp}°C). Black ice & frost risk."})
            safety_deductions += 25

        # Storm / Rain Analysis
        if "thunderstorm" in condition or curr["weather_code"] in [95, 96, 99]:
            hazards.append({"level": "CRITICAL", "type": "Thunderstorm & Lightning Alert", "desc": "Active severe thunderstorm cell in region."})
            safety_deductions += 35
        elif precip > 10.0 or "heavy rain" in condition:
            hazards.append({"level": "WARNING", "type": "Torrential Downpour Alert", "desc": f"High rainfall volume ({precip} mm/h). Risk of localized flooding."})
            safety_deductions += 25
        elif "rain" in condition or "drizzle" in condition:
            hazards.append({"level": "INFO", "type": "Precipitation Alert", "desc": "Active rainfall present."})
            safety_deductions += 10

        # Wind Analysis
        if gusts > 50 or wind > 35:
            hazards.append({"level": "CRITICAL", "type": "Gale Force Wind Warning", "desc": f"Severe wind gusts up to {gusts} km/h."})
            safety_deductions += 30
        elif wind > 25:
            hazards.append({"level": "WARNING", "type": "Strong Wind Advisory", "desc": f"High wind velocity detected ({wind} km/h)."})
            safety_deductions += 15

        # UV Index Analysis
        if uv >= 10:
            hazards.append({"level": "CRITICAL", "type": "Extreme UV Radiation", "desc": f"UV Index {uv}. Sunburn can occur in under 10 minutes."})
            safety_deductions += 20
        elif uv >= 7:
            hazards.append({"level": "WARNING", "type": "High UV Index", "desc": f"UV Index {uv}. UV protection required."})
            safety_deductions += 10

        # Air Quality Analysis
        if aqi > 150:
            hazards.append({"level": "CRITICAL", "type": "Unhealthy Air Quality", "desc": f"US AQI {aqi}. High particulate pollution."})
            safety_deductions += 30
        elif aqi > 100:
            hazards.append({"level": "WARNING", "type": "Moderate Pollution Alert", "desc": f"US AQI {aqi}. Sensitive groups affected."})
            safety_deductions += 15

        safety_score = max(0, min(100, 100 - safety_deductions))

        if safety_score >= 85:
            status_level = "OPTIMAL"
            status_text = "Safe & Favorable Conditions"
        elif safety_score >= 65:
            status_level = "MODERATE"
            status_text = "Moderate Weather Advisory"
        elif safety_score >= 40:
            status_level = "HIGH RISK"
            status_text = "Elevated Weather Hazard Alert"
        else:
            status_level = "CRITICAL RISK"
            status_text = "Severe Weather Emergency Warning"

        return {
            "safety_score": safety_score,
            "status_level": status_level,
            "status_text": status_text,
            "hazards": hazards,
            "hazard_count": len(hazards)
        }


class PredictiveAgent:
    """Agent 3: Evaluates multi-hour atmospheric trends and forecasts peak hazard windows."""
    
    def __init__(self):
        self.name = "Predictive & Trend Agent"
        self.role = "24H Trend Analysis & Forecast Prediction"

    def predict(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        hourly = raw_data.get("hourly", [])
        daily = raw_data.get("daily", [])

        # Find peak rain probability in next 24h
        max_rain_prob = 0
        peak_rain_time = "N/A"
        for h in hourly:
            prob = h.get("precip_prob", 0)
            if prob > max_rain_prob:
                max_rain_prob = prob
                peak_rain_time = h.get("time", "N/A")

        # Temperature swing in next 24h
        temps = [h.get("temp", 0) for h in hourly if "temp" in h]
        min_24h = min(temps) if temps else 0
        max_24h = max(temps) if temps else 0
        temp_delta = round(max_24h - min_24h, 1)

        # 7-Day Trend summary
        rain_days = sum(1 for d in daily if d.get("precip_prob", 0) > 50)

        predictive_summary = ""
        if max_rain_prob > 70:
            predictive_summary = f"High likelihood of precipitation ({max_rain_prob}%) expected around {peak_rain_time}."
        elif max_rain_prob > 40:
            predictive_summary = f"Moderate chance of rain ({max_rain_prob}%) in the upcoming hours."
        else:
            predictive_summary = "Stable weather expected over the next 24 hours with low precipitation risk."

        return {
            "max_rain_prob_24h": max_rain_prob,
            "peak_rain_time": peak_rain_time,
            "temp_delta_24h": temp_delta,
            "min_24h": min_24h,
            "max_24h": max_24h,
            "rainy_days_count_7d": rain_days,
            "predictive_summary": predictive_summary
        }


class ActionAgent:
    """Agent 4: Recommends specific mitigation steps, safety protocols, and lifestyle advice."""
    
    def __init__(self):
        self.name = "Decision & Action Agent"
        self.role = "Actionable Advisory & Emergency Guidance Generation"

    def recommend(self, raw_data: Dict[str, Any], analysis: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
        curr = raw_data["current"]
        status_level = analysis["status_level"]
        temp = curr["temperature"]
        precip = curr["precipitation"]
        uv = curr["uv_index"]
        wind = curr["wind_speed"]

        actions = []

        # Primary Emergency Action
        if status_level == "CRITICAL RISK":
            primary_action = "CRITICAL ADVISORY: Seek secure shelter immediately. Limit all non-essential outdoor travel and monitor official emergency broadcasts."
        elif status_level == "HIGH RISK":
            primary_action = "HIGH RISK: Exercise extreme caution outdoors. Postpone outdoor sports or heavy physical activity."
        elif status_level == "MODERATE":
            primary_action = "MODERATE ADVISORY: Weather conditions require minor precautions. Stay informed of local forecast updates."
        else:
            primary_action = "OPTIMAL CONDITIONS: Excellent weather for outdoor activities, travel, and sports. Enjoy your day!"

        # Specific Advisories
        if temp >= 35:
            actions.append({"category": "Hydration & Heat", "icon": "💧", "text": "Drink plenty of water (at least 3L/day). Avoid direct sun between 11 AM - 4 PM."})
        elif temp <= 5:
            actions.append({"category": "Thermal Gear", "icon": "🧥", "text": "Wear layered thermal clothing, heavy coats, and insulated gloves."})
        
        if precip > 0 or predictions["max_rain_prob_24h"] > 50:
            actions.append({"category": "Rain Gear", "icon": "☔", "text": f"Carry a waterproof umbrella or raincoat. High rain probability expected."})
        
        if uv >= 7:
            actions.append({"category": "Sun Protection", "icon": "🕶️", "text": f"Apply SPF 50+ broad-spectrum sunscreen and wear UV-blocking sunglasses."})

        if wind >= 25:
            actions.append({"category": "Wind Safety", "icon": "💨", "text": "Secure loose outdoor furniture, avoid parking under trees or loose power lines."})

        if raw_data["air_quality"].get("us_aqi", 0) > 100:
            actions.append({"category": "Respiratory Care", "icon": "😷", "text": "Wear N95 masks outdoors to guard against PM2.5 particulate pollution."})

        if not actions:
            actions.append({"category": "General Advice", "icon": "😊", "text": "Ideal weather conditions. Perfect for walking, running, or outdoor gatherings."})

        return {
            "primary_advisory": primary_action,
            "detailed_actions": actions
        }


class AgenticWeatherSystem:
    """Orchestrator Agent: Coordinates execution across all sub-agents and captures reasoning logs."""
    
    def __init__(self):
        self.collector = DataCollectionAgent()
        self.analyzer = AnalysisAgent()
        self.predictor = PredictiveAgent()
        self.actioner = ActionAgent()

    def run_pipeline(self, city_name: str) -> Dict[str, Any]:
        logs = []
        
        # Step 1: Data Collection Agent
        t0 = time.time()
        raw_data = self.collector.fetch_data(city_name)
        dt1 = round((time.time() - t0) * 1000, 2)
        logs.append({
            "agent": self.collector.name,
            "role": self.collector.role,
            "status": "SUCCESS",
            "duration_ms": dt1,
            "thought": f"Resolved location coordinates ({raw_data['location']['latitude']}, {raw_data['location']['longitude']}) for '{raw_data['location']['city']}'. Successfully retrieved atmospheric metrics, 24h hourly forecast, 7d daily forecast, and air quality index.",
            "key_outputs": {
                "Temperature": f"{raw_data['current']['temperature']} °C",
                "Humidity": f"{raw_data['current']['humidity']}%",
                "Condition": raw_data['current']['condition']
            }
        })

        # Step 2: Risk Analysis Agent
        t0 = time.time()
        analysis = self.analyzer.analyze(raw_data)
        dt2 = round((time.time() - t0) * 1000, 2)
        logs.append({
            "agent": self.analyzer.name,
            "role": self.analyzer.role,
            "status": "SUCCESS",
            "duration_ms": dt2,
            "thought": f"Evaluated multi-parameter risk metrics. Safety Score calculated at {analysis['safety_score']}/100 ({analysis['status_level']}). Identified {analysis['hazard_count']} weather hazards.",
            "key_outputs": {
                "Safety Index": f"{analysis['safety_score']} / 100",
                "Status Level": analysis['status_level'],
                "Detected Hazards": analysis['hazard_count']
            }
        })

        # Step 3: Predictive Agent
        t0 = time.time()
        predictions = self.predictor.predict(raw_data)
        dt3 = round((time.time() - t0) * 1000, 2)
        logs.append({
            "agent": self.predictor.name,
            "role": self.predictor.role,
            "status": "SUCCESS",
            "duration_ms": dt3,
            "thought": f"Analyzed 24-hour thermal and precipitation curves. {predictions['predictive_summary']}",
            "key_outputs": {
                "24H Rain Probability": f"{predictions['max_rain_prob_24h']}%",
                "Peak Rain Window": predictions['peak_rain_time'],
                "24H Temp Swing": f"{predictions['min_24h']}°C to {predictions['max_24h']}°C"
            }
        })

        # Step 4: Action Agent
        t0 = time.time()
        recommendations = self.actioner.recommend(raw_data, analysis, predictions)
        dt4 = round((time.time() - t0) * 1000, 2)
        logs.append({
            "agent": self.actioner.name,
            "role": self.actioner.role,
            "status": "SUCCESS",
            "duration_ms": dt4,
            "thought": f"Synthesized safety advisory protocols. Generated {len(recommendations['detailed_actions'])} tailored action recommendations.",
            "key_outputs": {
                "Primary Action": recommendations['primary_advisory'][:60] + "..."
            }
        })

        return {
            "data": raw_data,
            "analysis": analysis,
            "predictions": predictions,
            "recommendations": recommendations,
            "agent_logs": logs,
            "total_execution_ms": round(dt1 + dt2 + dt3 + dt4, 2)
        }


# Convenience function for simple execution
def run_weather_agent(city: str) -> Dict[str, Any]:
    orchestrator = AgenticWeatherSystem()
    return orchestrator.run_pipeline(city)
