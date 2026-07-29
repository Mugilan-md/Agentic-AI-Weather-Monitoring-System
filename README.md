# 🌦️ Agentic AI Weather Monitoring System

An autonomous, multi-agent AI system designed to monitor real-time atmospheric conditions, evaluate weather hazards, forecast 24-hour and 7-day environmental trends, and generate personalized safety advisories.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg)
![API](https://img.shields.io/badge/Weather_API-Open--Meteo-cyan.svg)

---

## 🚀 Features

- 🤖 **Multi-Agent AI Architecture**: 4 specialized AI agents working together in a synchronized pipeline.
- ⚡ **Zero Setup Required**: Uses Open-Meteo free real-time weather & geocoding APIs. No API key signup required out-of-the-box!
- 🔍 **City Search & Autocomplete**: Instant city search suggestion dropdown with worldwide coordinate geocoding.
- 📊 **Interactive Weather Visualizations**: 24-hour temperature and precipitation probability charts powered by Chart.js.
- 🛡️ **Multi-Parameter Hazard Scoring**: Real-time evaluation of heatwaves, storms, high wind gusts, UV index, and US AQI (Air Quality Index).
- 🧠 **Autonomous Agent Reasoning Log**: Live UI step-by-step trace showing each agent's execution duration, thoughts, and output decisions.
- 🌡️ **Unit Toggle (°C / °F)**: Dynamic temperature unit switching.
- 🎨 **Modern Glassmorphic Dashboard**: Sleek dark-mode aesthetic with micro-animations, quick-access city chips, and metric cards.

---

## 🧠 Multi-Agent Architecture

```
                    ┌──────────────────────────────┐
                    │    User City Query (Input)    │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                   ┌────────────────────────────────┐
                   │    Data Collection Agent       │
                   │  - Geocoding & Coordinates     │
                   │  - Atmospheric Data Fetcher    │
                   └──────────────┬─────────────────┘
                                  │
                                  ▼
                   ┌────────────────────────────────┐
                   │ Risk & Anomaly Analysis Agent  │
                   │  - Hazard Level Assessment     │
                   │  - Safety Score Calculation    │
                   └──────────────┬─────────────────┘
                                  │
                                  ▼
                   ┌────────────────────────────────┐
                   │   Predictive & Trend Agent     │
                   │  - 24H Rain Probability Window │
                   │  - Thermal Swing Calculation   │
                   └──────────────┬─────────────────┘
                                  │
                                  ▼
                   ┌────────────────────────────────┐
                   │   Decision & Action Agent      │
                   │  - Actionable Advisories       │
                   │  - Emergency Guidance          │
                   └──────────────┬─────────────────┘
                                  │
                                  ▼
                 ┌───────────────────────────────────┐
                 │  Agentic Orchestrator (Final UI)  │
                 └───────────────────────────────────┘
```

1. **Data Collection Agent**: Resolves city coordinates via Open-Meteo Geocoding API and retrieves real-time weather, 24h hourly forecast, 7-day daily forecast, and US Air Quality Index metrics.
2. **Risk & Anomaly Analysis Agent**: Computes an overall **Safety Index Score (0-100)** by analyzing temperature extremes, storm risks, high wind velocity, UV exposure, and particulate air pollution.
3. **Predictive & Trend Agent**: Identifies upcoming 24-hour hazard windows (e.g. peak rain timing, temperature drops) and 7-day weather patterns.
4. **Decision & Action Agent**: Formulates clear, categorized advice (Hydration, Thermal Gear, Sun Protection, Respiratory Care, Travel Guidance).
5. **Agentic Orchestrator**: Coordinates execution flow and constructs detailed reasoning logs for full system transparency.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.14, Flask, Requests, Python-Dotenv
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism), JavaScript (ES6+ AJAX)
- **Data & Charts**: Open-Meteo Free Weather & Air Quality APIs, Chart.js CDN
- **Fonts**: Google Fonts (Inter & Outfit)

---

## 💻 Installation & Local Execution Guide

### Prerequisites
- Python 3.9+ installed on your system.
- Git installed.

### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Mugilan-md/Agentic-AI-Weather-Monitoring-System.git
   cd Agentic-AI-Weather-Monitoring-System
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Open in Browser**:
   Navigate to `http://127.0.0.1:5000` in your web browser.

---

## 📡 API Endpoints

### 1. `POST /api/weather`
Executes the multi-agent pipeline for a specified city.

**Request Body**:
```json
{
  "city": "London"
}
```

**Response**:
```json
{
  "success": true,
  "result": {
    "data": { ... },
    "analysis": {
      "safety_score": 90,
      "status_level": "OPTIMAL",
      "status_text": "Safe & Favorable Conditions"
    },
    "predictions": { ... },
    "recommendations": { ... },
    "agent_logs": [ ... ]
  }
}
```

### 2. `GET /api/search?q={query}`
Returns city autocomplete suggestions.

---

## 📄 License
This project is licensed under the MIT License.
