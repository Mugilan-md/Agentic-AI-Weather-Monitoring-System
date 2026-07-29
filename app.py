from flask import Flask, render_template, request, jsonify
from agents import run_weather_agent, DataCollectionAgent
from config import Config

app = Flask(__name__)
collector = DataCollectionAgent()

@app.route("/", methods=["GET"])
def index():
    initial_city = request.args.get("city", "London")
    return render_template("index.html", initial_city=initial_city)

@app.route("/api/weather", methods=["POST"])
def get_weather():
    data = request.get_json(silent=True) or request.form
    city = data.get("city", "").strip()
    
    if not city:
        return jsonify({"success": False, "error": "City name is required."}), 400

    try:
        result = run_weather_agent(city)
        return jsonify({"success": True, "result": result})
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route("/api/search", methods=["GET"])
def search_city():
    query = request.args.get("q", "").strip()
    if len(query) < 2:
        return jsonify({"results": []})
    
    results = collector.search_city(query)
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
