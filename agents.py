import requests

API_KEY = "YOUR_OPENWEATHER_API_KEY"

# -------------------------------
# Data Collection Agent
# -------------------------------
def data_collection_agent(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    weather_info = {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind": data["wind"]["speed"]
    }
    return weather_info


# -------------------------------
# Analysis Agent
# -------------------------------
def analysis_agent(weather):
    risk = "Normal"

    if weather["temperature"] > 35:
        risk = "High Temperature"
    elif "rain" in weather["condition"]:
        risk = "Rain Alert"
    elif weather["wind"] > 15:
        risk = "Strong Wind"

    return risk


# -------------------------------
# Decision Agent
# -------------------------------
def decision_agent(risk):
    if risk == "High Temperature":
        return "Heat Alert"
    elif risk == "Rain Alert":
        return "Rain Warning"
    elif risk == "Strong Wind":
        return "Wind Alert"
    else:
        return "Weather is Normal"


# -------------------------------
# Action Agent
# -------------------------------
def action_agent(decision):
    if decision == "Heat Alert":
        return "Stay hydrated and avoid outdoor activities."
    elif decision == "Rain Warning":
        return "Carry an umbrella and avoid low areas."
    elif decision == "Wind Alert":
        return "Avoid travel and secure loose objects."
    else:
        return "Have a nice day!"


# -------------------------------
# Main Agent Controller
# -------------------------------
def run_weather_agent(city):
    weather = data_agent(city)
    status = analysis_agent(weather)
    decision = decision_agent(status)
    action = action_agent(decision)

    return {
        "weather": weather,
        "decision": decision,
        "action": action
    }
