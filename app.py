from flask import Flask, render_template, request
from agents import run_weather_agent

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        city = request.form["city"]
        result = run_weather_agent(city)

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
