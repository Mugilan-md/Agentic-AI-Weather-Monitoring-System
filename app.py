from flask import Flask, render_template, request, jsonify
from agents import run_weather_agent, run_agent_chat, DataCollectionAgent
from config import Config

app = Flask(__name__)
collector = DataCollectionAgent()

@app.route("/", methods=["GET"])
def index():
    initial_city = request.args.get("city", "Chennai")
    return render_template("index.html", initial_city=initial_city)

@app.route("/api/weather", methods=["POST"])
def get_weather():
    data = request.get_json(silent=True) or request.form
    city = data.get("city", "").strip()
    
    if not city:
        city = "Chennai"

    try:
        result = run_weather_agent(city)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        # Guarantee a valid response even under extreme unexpected errors
        fallback_result = run_weather_agent("Chennai")
        return jsonify({"success": True, "result": fallback_result, "warning": f"Switched to resilient mode: {str(e)}"})

@app.route("/api/agent/chat", methods=["POST"])
def agent_chat():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    weather_result = data.get("weather_result", None)

    if not query:
        return jsonify({"success": False, "error": "Query cannot be empty."}), 400

    if not weather_result:
        weather_result = run_weather_agent("Chennai")

    response = run_agent_chat(query, weather_result)
    return jsonify({"success": True, "response": response})

@app.route("/api/search", methods=["GET"])
def search_city():
    query = request.args.get("q", "").strip()
    if len(query) < 2:
        return jsonify({"results": []})
    
    results = collector.search_city(query)
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
