from flask import Flask, render_template, request, jsonify
from agents import run_weather_agent, run_agent_chat, DataCollectionAgent
from ml_service import ml_service
from config import Config
import database

app = Flask(__name__)
collector = DataCollectionAgent()

# Initialize SQLite Database
database.init_db()

@app.route("/", methods=["GET"])
def index():
    initial_city = request.args.get("city", "London")
    return render_template("index.html", initial_city=initial_city)

@app.route("/api/weather", methods=["POST"])
def get_weather():
    data = request.get_json(silent=True) or request.form
    city = data.get("city", "").strip()
    
    if not city:
        city = "London"

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
        fallback_result = run_weather_agent("London")
        return jsonify({"success": True, "result": fallback_result, "warning": f"Switched to resilient mode: {str(e)}"})

@app.route("/api/agent/chat", methods=["POST"])
def agent_chat():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    weather_result = data.get("weather_result", None)

    if not query:
        return jsonify({"success": False, "error": "Query cannot be empty."}), 400

    if not weather_result:
        weather_result = run_weather_agent("London")

    response = run_agent_chat(query, weather_result)
    return jsonify({"success": True, "response": response})

@app.route("/api/search", methods=["GET"])
def search_city():
    query = request.args.get("q", "").strip()
    if len(query) < 2:
        return jsonify({"results": []})
    
    results = collector.search_city(query)
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

# Machine Learning REST Endpoints
@app.route("/api/ml/metrics", methods=["GET"])
def get_ml_metrics():
    metrics = ml_service.performance_metrics
    return jsonify({"success": True, "metrics": metrics, "logs": ml_service.prediction_logs})

@app.route("/api/ml/retrain", methods=["POST"])
def retrain_ml_model():
    retrain_res = ml_service.retrain_pipeline()
    return jsonify({"success": True, "result": retrain_res})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
