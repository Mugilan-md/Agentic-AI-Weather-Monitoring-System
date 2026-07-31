# Agentic AI Weather Monitoring System - Vercel Production Gateway
from flask import Flask, render_template, request, jsonify
from agents import run_weather_agent, run_agent_chat, DataCollectionAgent
from ml_service import ml_service
from config import Config
import database

import os

base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, "templates"),
    static_folder=os.path.join(base_dir, "static")
)

# Lazy collector instance for request handling
collector = None

def get_collector():
    global collector
    if collector is None:
        try:
            collector = DataCollectionAgent()
        except Exception:
            collector = None
    return collector

@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
@app.route("/api/index", methods=["GET"])
@app.route("/api/index.py", methods=["GET"])
def index():
    initial_city = request.args.get("city", "").strip()
    return render_template("index.html", initial_city=initial_city)

@app.route("/api/weather", methods=["POST"])
def get_weather():
    data = request.get_json(silent=True) or request.form
    city = data.get("city", "").strip()
    
    if not city:
        return jsonify({"success": False, "error": "Please enter a city, town, or village name to search weather data."}), 400

    try:
        result = run_weather_agent(city)
        raw = result["data"]
        analysis = result["analysis"]
        
        # Log query to SQLite Database
        database.log_search(
            city=raw["location"]["city"],
            country=raw["location"]["country"],
            temp=raw["current"]["temperature"],
            condition=raw["current"]["condition"],
            safety_score=analysis["safety_score"],
            status_level=analysis["status_level"]
        )
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": f"Unable to fetch weather data for '{city}': {str(e)}"})

@app.route("/api/agent/chat", methods=["POST"])
def agent_chat():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    weather_result = data.get("weather_result", None)

    if not query:
        return jsonify({"success": False, "error": "Query cannot be empty."}), 400

    if not weather_result:
        # Construct clean default context without forcing a specific city report
        weather_result = {
            "data": {
                "current": {"temperature": 22.0, "feels_like": 22.0, "humidity": 60, "condition": "Clear", "wind_speed": 10.0, "uv_index": 5.0, "pressure": 1013},
                "location": {"city": "Global Location", "country": "Earth"},
                "air_quality": {"us_aqi": 35}
            },
            "analysis": {"safety_score": 90, "status_level": "OPTIMAL"},
            "ml_analytics": {
                "rainfall_prediction": {"probability_pct": 10, "confidence_pct": 95},
                "risk_classification": {"category": "Normal", "confidence_pct": 98}
            }
        }

    response = run_agent_chat(query, weather_result)
    return jsonify({"success": True, "response": response})

@app.route("/api/search", methods=["GET"])
def search_city():
    query = request.args.get("q", "").strip()
    if len(query) < 2:
        return jsonify({"results": []})
    
    try:
        agent = get_collector() or DataCollectionAgent()
        results = agent.search_city(query)
    except Exception:
        results = []
    return jsonify({"results": results})

# Database REST Endpoints
@app.route("/api/history", methods=["GET"])
def get_history():
    history = database.get_recent_history(limit=8)
    return jsonify({"success": True, "history": history})

@app.route("/api/favorites", methods=["GET"])
def get_favorites():
    favorites = database.get_favorites()
    return jsonify({"success": True, "favorites": favorites})

@app.route("/api/favorites/toggle", methods=["POST"])
def toggle_favorite():
    data = request.get_json(silent=True) or {}
    city = data.get("city", "").strip()
    country = data.get("country", "").strip()
    
    if not city:
        return jsonify({"success": False, "error": "City name required"}), 400
        
    is_fav = database.toggle_favorite(city, country)
    return jsonify({"success": True, "is_favorite": is_fav})

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    analytics = database.get_db_analytics()
    return jsonify({"success": True, "analytics": analytics})

@app.route("/api/analytics/historical", methods=["GET"])
def get_historical_analytics():
    city = request.args.get("city", "London").strip()
    records = database.get_historical_city_analytics(city, limit=24)
    return jsonify({"success": True, "city": city, "records": records})

# Machine Learning REST Endpoints
@app.route("/api/ml/metrics", methods=["GET"])
def get_ml_metrics():
    metrics = ml_service.performance_metrics
    return jsonify({"success": True, "metrics": metrics, "logs": ml_service.prediction_logs})

@app.route("/api/ml/retrain", methods=["POST"])
def retrain_ml_model():
    retrain_res = ml_service.retrain_pipeline()
    return jsonify({"success": True, "result": retrain_res})

@app.errorhandler(Exception)
def handle_global_exception(e):
    return jsonify({"success": False, "error": f"Serverless Function Notice: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
