document.addEventListener("DOMContentLoaded", () => {
    let currentUnit = "C";
    let weatherData = null;
    let hourlyChart = null;
    let lightningHue = 210; // Vivid Deep Electric Blue

    const searchInput = document.getElementById("search-input");
    const searchBtn = document.getElementById("search-btn");
    const autocompleteDropdown = document.getElementById("autocomplete-dropdown");
    const loadingOverlay = document.getElementById("loading-overlay");
    const favStarBtn = document.getElementById("fav-star-btn");
    const hueSlider = document.getElementById("hue-slider");
    const hueValDisplay = document.getElementById("hue-val-display");
    const retrainBtn = document.getElementById("retrain-btn");

    const unitBtnC = document.getElementById("unit-c");
    const unitBtnF = document.getElementById("unit-f");

    const chatInput = document.getElementById("chat-input");
    const chatSendBtn = document.getElementById("chat-send-btn");
    const chatHistory = document.getElementById("chat-history");

    // Initialize 60+ FPS 3-Way Branching WebGL Lightning Background Shader
    initLightningShader();

    // Initialize 3D Parallax Tilt Effects ONLY on Dashboard Content Cards (Excluding Navbar)
    init3DTiltEffects();

    // Initialize 3D Dual-Color Glowing Cursor & Glitter Sparkle Engine
    init3DCursorGlitterEngine();

    // Hue Slider Listener
    if (hueSlider) {
        hueSlider.value = lightningHue;
        hueSlider.addEventListener("input", (e) => {
            lightningHue = parseFloat(e.target.value);
            if (hueValDisplay) hueValDisplay.textContent = `${Math.round(lightningHue)}°`;
        });
    }

    // Retrain Model Button Listener
    if (retrainBtn) {
        retrainBtn.addEventListener("click", () => {
            showToast("Retraining ML Models on updated dataset...", false);
            fetch("/api/ml/retrain", { method: "POST" })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        showToast(`ML Retraining complete! New Accuracy: ${data.result.metrics.accuracy}%`, false);
                        loadMlMetrics();
                    }
                });
        });
    }

    // Toast notification utility
    function showToast(msg, isError = false) {
        const toastContainer = document.getElementById("toast-container") || createToastContainer();
        const toast = document.createElement("div");
        toast.className = "toast";
        toast.style.borderColor = isError ? "var(--accent-rose)" : "var(--primary-cyan)";
        toast.innerHTML = `<span>${isError ? '⚠️' : '⚡'}</span> <span>${msg}</span>`;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    function createToastContainer() {
        const container = document.createElement("div");
        container.id = "toast-container";
        container.className = "toast-container";
        document.body.appendChild(container);
        return container;
    }

    // Load DB Favorites, Analytics & ML Metrics
    loadFavoritesFromDB();
    loadDbAnalytics();
    loadDbHistory();
    loadMlMetrics();

    // Initial city handling (Do NOT load default London report until searched)
    const initialCity = (window.INITIAL_CITY || "").trim();
    if (initialCity) {
        fetchWeatherData(initialCity);
    }

    // Prompt Chips Listener
    document.querySelectorAll(".prompt-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const city = chip.getAttribute("data-city");
            if (city) {
                searchInput.value = city;
                fetchWeatherData(city);
            }
        });
    });

    // Event Listeners
    searchBtn.addEventListener("click", () => {
        const city = searchInput.value.trim();
        if (city) fetchWeatherData(city);
    });

    searchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            const city = searchInput.value.trim();
            if (city) fetchWeatherData(city);
        }
    });

    // Autocomplete handling
    let debounceTimer;
    searchInput.addEventListener("input", (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();
        if (query.length < 2) {
            autocompleteDropdown.classList.remove("active");
            return;
        }
        debounceTimer = setTimeout(() => {
            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    renderAutocomplete(data.results || []);
                }).catch(() => {});
        }, 300);
    });

    function renderAutocomplete(results) {
        if (!results.length) {
            autocompleteDropdown.classList.remove("active");
            return;
        }
        autocompleteDropdown.innerHTML = results.map(item => `
            <div class="autocomplete-item" data-city="${item.name}">
                <span><strong>${item.name}</strong> ${item.admin1 ? ', ' + item.admin1 : ''}</span>
                <span style="color: var(--text-muted); font-size: 0.8rem;">${item.country}</span>
            </div>
        `).join("");
        autocompleteDropdown.classList.add("active");

        document.querySelectorAll(".autocomplete-item").forEach(item => {
            item.addEventListener("click", () => {
                const selectedCity = item.getAttribute("data-city");
                searchInput.value = selectedCity;
                autocompleteDropdown.classList.remove("active");
                fetchWeatherData(selectedCity);
            });
        });
    }

    document.addEventListener("click", (e) => {
        if (!e.target.closest(".search-wrapper")) {
            autocompleteDropdown.classList.remove("active");
        }
    });

    // Favorite Star Button Click
    favStarBtn.addEventListener("click", () => {
        if (!weatherData) return;
        const loc = weatherData.data.location;
        fetch("/api/favorites/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ city: loc.city, country: loc.country })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const isFav = data.is_favorite;
                favStarBtn.textContent = isFav ? "⭐" : "☆";
                showToast(isFav ? `Saved ${loc.city} to DB Favorites!` : `Removed ${loc.city} from Favorites.`);
                loadFavoritesFromDB();
            }
        });
    });

    // Temperature Unit Toggles
    unitBtnC.addEventListener("click", () => {
        if (currentUnit !== "C") {
            currentUnit = "C";
            unitBtnC.classList.add("active");
            unitBtnF.classList.remove("active");
            if (weatherData) updateUI(weatherData);
        }
    });

    unitBtnF.addEventListener("click", () => {
        if (currentUnit !== "F") {
            currentUnit = "F";
            unitBtnF.classList.add("active");
            unitBtnC.classList.remove("active");
            if (weatherData) updateUI(weatherData);
        }
    });

    function cToF(c) {
        return Math.round((c * 9/5) + 32);
    }

    function formatTemp(tempC) {
        return currentUnit === "F" ? `${cToF(tempC)}°F` : `${Math.round(tempC)}°C`;
    }

    // Main Fetch Function
    function fetchWeatherData(city) {
        loadingOverlay.classList.add("active");
        fetch("/api/weather", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ city: city })
        })
        .then(res => res.json())
        .then(data => {
            loadingOverlay.classList.remove("active");
            if (data.success) {
                weatherData = data.result;
                updateUI(weatherData);
                loadDbAnalytics();
                loadDbHistory();
                loadMlMetrics();
            } else {
                showToast(`Error: ${data.error}`, true);
            }
        })
        .catch(err => {
            loadingOverlay.classList.remove("active");
            showToast("Network warning: Switching to local atmospheric mode.", false);
        });
    }

    function updateUI(res) {
        const raw = res.data;
        const curr = raw.current;
        const loc = raw.location;
        const analysis = res.analysis;
        const recs = res.recommendations;
        const logs = res.agent_logs;
        const ml = res.ml_analytics;

        // Toggle Welcome Hero vs Weather Dashboard
        const welcomeHero = document.getElementById("welcome-search-hero");
        const weatherDashboard = document.getElementById("weather-dashboard");
        if (welcomeHero) welcomeHero.style.display = "none";
        if (weatherDashboard) weatherDashboard.style.display = "block";

        // Mode Indicator
        const modeBadge = document.getElementById("mode-badge");
        if (raw.mode === "ONLINE_SATELLITE") {
            modeBadge.innerHTML = "<span>📡</span> Live Satellite Stream";
            modeBadge.style.borderColor = "rgba(16, 185, 129, 0.4)";
            modeBadge.style.color = "var(--accent-emerald)";
        } else {
            modeBadge.innerHTML = "<span>🛡️</span> Resilient Local Mode";
            modeBadge.style.borderColor = "rgba(56, 189, 248, 0.4)";
            modeBadge.style.color = "var(--primary-cyan)";
        }

        // Hero Card Updates
        document.getElementById("location-name").textContent = loc.city;
        document.getElementById("location-country").textContent = `${loc.country} • Lat: ${loc.latitude}, Lon: ${loc.longitude}`;
        
        const safetyBadge = document.getElementById("safety-badge");
        safetyBadge.className = `safety-badge safety-${analysis.status_level.replace(" ", "_")}`;
        safetyBadge.innerHTML = `<span>🛡️</span> ${analysis.status_text} (${analysis.safety_score}/100)`;

        document.getElementById("weather-icon").textContent = curr.icon;
        document.getElementById("temp-display").textContent = formatTemp(curr.temperature);
        document.getElementById("condition-text").textContent = curr.condition;
        document.getElementById("feels-like-text").textContent = `Feels like ${formatTemp(curr.feels_like)}`;

        // Hero Pills
        document.getElementById("pill-uv").textContent = `UV Index: ${curr.uv_index.toFixed(1)}`;
        document.getElementById("pill-aqi").textContent = `US AQI: ${raw.air_quality.us_aqi}`;
        document.getElementById("pill-precip").textContent = `Precip: ${curr.precipitation} mm`;

        // Metric Cards
        document.getElementById("val-humidity").textContent = `${curr.humidity}%`;
        document.getElementById("val-wind").textContent = `${curr.wind_speed} km/h`;
        document.getElementById("val-gusts").textContent = `Gusts: ${curr.wind_gusts} km/h`;
        document.getElementById("val-pressure").textContent = `${Math.round(curr.pressure)} hPa`;
        document.getElementById("val-clouds").textContent = `${curr.cloud_cover}%`;
        document.getElementById("val-uv").textContent = `${curr.uv_index.toFixed(1)}`;
        document.getElementById("val-aqi").textContent = `${raw.air_quality.us_aqi}`;

        // ML Predictions Display
        if (ml) {
            document.getElementById("ml-rain-prob").textContent = `${ml.rainfall_prediction.probability_pct}%`;
            document.getElementById("ml-rain-conf").textContent = `Model Conf: ${ml.rainfall_prediction.confidence_pct}%`;

            document.getElementById("ml-risk-cat").textContent = ml.risk_classification.category;
            document.getElementById("ml-risk-conf").textContent = `Class Conf: ${ml.risk_classification.confidence_pct}%`;

            const anomalyBadge = document.getElementById("ml-anomaly-status");
            if (ml.anomaly_detection.is_anomaly) {
                anomalyBadge.textContent = "🚨 Anomaly Flagged!";
                anomalyBadge.style.color = "var(--accent-rose)";
            } else {
                anomalyBadge.textContent = "✅ Normal Pattern";
                anomalyBadge.style.color = "var(--accent-emerald)";
            }

            document.getElementById("ml-temp-24h").textContent = formatTemp(ml.temperature_forecast.predicted_temp_24h);
            document.getElementById("ml-temp-trend").textContent = `Trend: ${ml.temperature_forecast.trend} (${ml.temperature_forecast.delta > 0 ? '+' : ''}${ml.temperature_forecast.delta}°C)`;

            renderFeatureImportance(ml.feature_importance);
        }

        // Agent Execution Timeline
        const agentTimeline = document.getElementById("agent-timeline");
        agentTimeline.innerHTML = logs.map(log => `
            <div class="agent-step-item">
                <div class="agent-step-header">
                    <span class="agent-name">🤖 ${log.agent}</span>
                    <span class="agent-duration">⏱️ ${log.duration_ms} ms</span>
                </div>
                <div class="agent-thought">${log.thought}</div>
            </div>
        `).join("");

        // Forecast List (7 Days)
        const forecastList = document.getElementById("forecast-list");
        forecastList.innerHTML = raw.daily.map(d => `
            <div class="forecast-item">
                <span class="forecast-date">${d.date.split('-').slice(1).join('/')}</span>
                <span class="forecast-cond">${d.icon} ${d.condition}</span>
                <span class="forecast-temps">${formatTemp(d.max_temp)} / <span style="color: var(--text-muted);">${formatTemp(d.min_temp)}</span></span>
            </div>
        `).join("");

        // Action Recommendations
        document.getElementById("primary-banner").textContent = recs.primary_advisory;
        const actionsList = document.getElementById("actions-list");
        actionsList.innerHTML = recs.detailed_actions.map(act => `
            <div class="action-item-card">
                <div class="action-icon">${act.icon}</div>
                <div>
                    <div class="action-cat">${act.category}</div>
                    <div class="action-text">${act.text}</div>
                </div>
            </div>
        `).join("");

        renderHourlyChart(raw.hourly);
    }

    function renderFeatureImportance(importanceMap) {
        const container = document.getElementById("feature-importance-list");
        if (!container || !importanceMap) return;

        const items = Object.entries(importanceMap).sort((a, b) => b[1] - a[1]);
        container.innerHTML = items.map(([feat, pct]) => `
            <div class="feature-item">
                <div class="feature-info">
                    <span style="text-transform: capitalize; font-weight: 500;">${feat.replace("_", " ")}</span>
                    <span style="color: var(--primary-cyan); font-weight: 600;">${pct}%</span>
                </div>
                <div class="feature-bar-bg">
                    <div class="feature-bar-fill" style="width: ${pct}%;"></div>
                </div>
            </div>
        `).join("");
    }

    function renderHourlyChart(hourlyData) {
        const ctx = document.getElementById("hourlyChart").getContext("2d");
        const labels = hourlyData.map(h => h.time);
        const temps = hourlyData.map(h => currentUnit === "F" ? cToF(h.temp) : Math.round(h.temp));
        const rainProbs = hourlyData.map(h => h.precip_prob);

        if (hourlyChart) {
            hourlyChart.destroy();
        }

        hourlyChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: `Temperature (°${currentUnit})`,
                        data: temps,
                        borderColor: "#38bdf8",
                        backgroundColor: "rgba(56, 189, 248, 0.15)",
                        fill: true,
                        tension: 0.4,
                        yAxisID: "y"
                    },
                    {
                        label: "Precipitation Prob (%)",
                        data: rainProbs,
                        borderColor: "#a855f7",
                        backgroundColor: "rgba(168, 85, 247, 0.15)",
                        fill: true,
                        tension: 0.4,
                        yAxisID: "y1"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: {
                    legend: { labels: { color: "#94a3b8", font: { family: "Inter" } } }
                },
                scales: {
                    x: { ticks: { color: "#64748b" }, grid: { display: false } },
                    y: {
                        type: "linear", display: true, position: "left",
                        ticks: { color: "#38bdf8" }, grid: { color: "rgba(255,255,255,0.05)" }
                    },
                    y1: {
                        type: "linear", display: true, position: "right",
                        ticks: { color: "#a855f7" }, grid: { display: false },
                        min: 0, max: 100
                    }
                }
            }
        });
    }

    // Database & ML Loaders
    function loadFavoritesFromDB() {
        fetch("/api/favorites")
            .then(res => res.json())
            .then(data => {
                if (data.success && data.favorites) {
                    const container = document.getElementById("bookmarks-chips");
                    container.innerHTML = data.favorites.map(f => `
                        <button class="chip" data-city="${f.city}">${f.city}</button>
                    `).join("");

                    container.querySelectorAll(".chip").forEach(chip => {
                        chip.addEventListener("click", () => {
                            const city = chip.getAttribute("data-city");
                            searchInput.value = city;
                            fetchWeatherData(city);
                        });
                    });
                }
            }).catch(() => {});
    }

    function loadDbAnalytics() {
        fetch("/api/analytics")
            .then(res => res.json())
            .then(data => {
                if (data.success && data.analytics) {
                    const a = data.analytics;
                    document.getElementById("stat-total-queries").textContent = a.total_queries;
                    document.getElementById("stat-avg-safety").textContent = `${a.avg_safety_score}/100`;
                    document.getElementById("stat-top-city").textContent = a.top_city;
                    document.getElementById("stat-db-status").textContent = a.db_status;
                }
            }).catch(() => {});
    }

    function loadDbHistory() {
        fetch("/api/history")
            .then(res => res.json())
            .then(data => {
                if (data.success && data.history) {
                    const tbody = document.getElementById("history-table-body");
                    if (!data.history.length) {
                        tbody.innerHTML = `<tr><td colspan="6" style="color: var(--text-muted);">No queries recorded yet.</td></tr>`;
                        return;
                    }
                    tbody.innerHTML = data.history.map(h => `
                        <tr>
                            <td><strong>${h.city}</strong> <span style="color: var(--text-muted); font-size: 0.8rem;">(${h.country})</span></td>
                            <td>${formatTemp(h.temperature)}</td>
                            <td>${h.condition}</td>
                            <td><span class="safety-badge safety-${h.status_level.replace(" ", "_")}" style="padding: 2px 8px; font-size: 0.75rem;">${h.safety_score} / 100</span></td>
                            <td style="color: var(--text-muted);">${h.time_str}</td>
                            <td><button class="requery-btn" data-city="${h.city}">Re-query</button></td>
                        </tr>
                    `).join("");

                    tbody.querySelectorAll(".requery-btn").forEach(btn => {
                        btn.addEventListener("click", () => {
                            const city = btn.getAttribute("data-city");
                            searchInput.value = city;
                            fetchWeatherData(city);
                        });
                    });
                }
            }).catch(() => {});
    }

    function loadMlMetrics() {
        fetch("/api/ml/metrics")
            .then(res => res.json())
            .then(data => {
                if (data.success && data.metrics) {
                    const m = data.metrics;
                    document.getElementById("ml-acc").textContent = `${m.accuracy}%`;
                    document.getElementById("ml-f1").textContent = `${m.f1_score}%`;
                    document.getElementById("ml-mae").textContent = `${m.mae}°C`;
                    document.getElementById("ml-rmse").textContent = `${m.rmse}°C`;
                    document.getElementById("ml-engine-name").textContent = m.engine;
                }
            }).catch(() => {});
    }

    // AI Conversational Assistant Logic
    chatSendBtn.addEventListener("click", sendChatMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendChatMessage();
    });

    document.querySelectorAll(".preset-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            chatInput.value = chip.getAttribute("data-prompt");
            sendChatMessage();
        });
    });

    function sendChatMessage() {
        const query = chatInput.value.trim();
        if (!query) return;

        appendChatBubble("user", query);
        chatInput.value = "";

        fetch("/api/agent/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query, weather_result: weatherData })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                appendChatBubble("ai", data.response.answer);
            } else {
                appendChatBubble("ai", "I'm having trouble analyzing that question right now.");
            }
        })
        .catch(() => {
            appendChatBubble("ai", "Unable to connect to AI reasoning service.");
        });
    }

    function appendChatBubble(role, text) {
        const bubble = document.createElement("div");
        bubble.className = "chat-bubble";
        
        if (role === "user") {
            bubble.innerHTML = `
                <div class="chat-avatar chat-avatar-user">👤</div>
                <div class="chat-content">${text}</div>
            `;
        } else {
            bubble.innerHTML = `
                <div class="chat-avatar chat-avatar-ai">🤖</div>
                <div class="chat-content">${text}</div>
            `;
        }

        chatHistory.appendChild(bubble);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // -------------------------------------------------------------
    // Interactive 3D Parallax Tilt Effect (EXCLUDING Navbar)
    // -------------------------------------------------------------
    function init3DTiltEffects() {
        const cards = document.querySelectorAll(".glass-card, .metric-card");
        cards.forEach(card => {
            // Exclude navbar completely from 3D tilting
            if (card.classList.contains("navbar") || card.classList.contains("navbar-sleek")) return;

            card.addEventListener("mousemove", (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const rotateX = ((y - centerY) / centerY) * -5;
                const rotateY = ((x - centerX) / centerX) * 5;

                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.015, 1.015, 1.015)`;
            });

            card.addEventListener("mouseleave", () => {
                card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)";
            });
        });
    }

    // -------------------------------------------------------------
    // High-FPS 3-Way Branching WebGL Lightning Shader
    // -------------------------------------------------------------
    function initLightningShader() {
        const canvas = document.getElementById("lightning-canvas");
        if (!canvas) return;

        const gl = canvas.getContext("webgl", { alpha: true, antialias: true, preserveDrawingBuffer: false });
        if (!gl) return;

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            gl.viewport(0, 0, canvas.width, canvas.height);
        }
        resize();
        window.addEventListener("resize", resize);

        const vsSource = `
            attribute vec2 aPosition;
            void main() {
                gl_Position = vec4(aPosition, 0.0, 1.0);
            }
        `;

        const fsSource = `
            precision mediump float;
            uniform vec2 iResolution;
            uniform float iTime;
            uniform float uHue;
            
            #define OCTAVE_COUNT 8

            vec3 hsv2rgb(vec3 c) {
                vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0,4.0,2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
                return c.z * mix(vec3(1.0), rgb, c.y);
            }

            float hash12(vec2 p) {
                vec3 p3 = fract(vec3(p.xyx) * .1031);
                p3 += dot(p3, p3.yzx + 33.33);
                return fract((p3.x + p3.y) * p3.z);
            }

            mat2 rotate2d(float theta) {
                float c = cos(theta);
                float s = sin(theta);
                return mat2(c, -s, s, c);
            }

            float noise(vec2 p) {
                vec2 ip = floor(p);
                vec2 fp = fract(p);
                float a = hash12(ip);
                float b = hash12(ip + vec2(1.0, 0.0));
                float c = hash12(ip + vec2(0.0, 1.0));
                float d = hash12(ip + vec2(1.0, 1.0));
                vec2 t = smoothstep(0.0, 1.0, fp);
                return mix(mix(a, b, t.x), mix(c, d, t.x), t.y);
            }

            float fbm(vec2 p) {
                float value = 0.0;
                float amplitude = 0.5;
                for (int i = 0; i < OCTAVE_COUNT; ++i) {
                    value += amplitude * noise(p);
                    p *= rotate2d(0.45);
                    p *= 2.0;
                    amplitude *= 0.5;
                }
                return value;
            }

            float lightningBranch(vec2 uv, vec2 origin, float angle, float time, float noiseScale) {
                vec2 p = uv - origin;
                p = rotate2d(angle) * p;
                float n = fbm(p * noiseScale + vec2(0.0, time * 2.5));
                return abs(p.x + (n - 0.5) * 0.45);
            }

            void main() {
                vec2 uv = gl_FragCoord.xy / iResolution.xy;
                uv = 2.0 * uv - 1.0;
                uv.x *= iResolution.x / iResolution.y;
                
                vec2 nodeOrigin = vec2(0.0, 0.65);
                float time = iTime;
                
                float d1 = lightningBranch(uv, nodeOrigin, -0.55, time, 2.5);
                float d2 = lightningBranch(uv, nodeOrigin,  0.00, time * 1.1, 2.8);
                float d3 = lightningBranch(uv, nodeOrigin,  0.55, time * 0.9, 2.5);
                
                float d4 = lightningBranch(uv, nodeOrigin, -0.28, time * 1.4, 4.0);
                float d5 = lightningBranch(uv, nodeOrigin,  0.28, time * 1.3, 4.0);
                
                float bolt1 = 0.055 / max(d1, 0.001);
                float bolt2 = 0.070 / max(d2, 0.001);
                float bolt3 = 0.055 / max(d3, 0.001);
                float spark4 = 0.025 / max(d4, 0.001);
                float spark5 = 0.025 / max(d5, 0.001);
                
                float totalLightning = bolt1 + bolt2 + bolt3 + spark4 + spark5;
                
                float nodeDist = length(uv - nodeOrigin);
                float nodeGlow = 0.12 / max(nodeDist, 0.01);
                float pulse = 0.85 + 0.15 * sin(time * 6.0);
                nodeGlow *= pulse;
                
                vec3 baseColor = hsv2rgb(vec3(uHue / 360.0, 0.85, 0.98));
                vec3 col = baseColor * (totalLightning * 0.85 + nodeGlow);
                
                gl_FragColor = vec4(col, 0.65);
            }
        `;

        function compileShader(source, type) {
            const s = gl.createShader(type);
            gl.shaderSource(s, source);
            gl.compileShader(s);
            if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
                return null;
            }
            return s;
        }

        const vs = compileShader(vsSource, gl.VERTEX_SHADER);
        const fs = compileShader(fsSource, gl.FRAGMENT_SHADER);
        if (!vs || !fs) return;

        const program = gl.createProgram();
        gl.attachShader(program, vs);
        gl.attachShader(program, fs);
        gl.linkProgram(program);
        gl.useProgram(program);

        const vertices = new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]);
        const buffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
        gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

        const aPosition = gl.getAttribLocation(program, "aPosition");
        gl.enableVertexAttribArray(aPosition);
        gl.vertexAttribPointer(aPosition, 2, gl.FLOAT, false, 0, 0);

        const uResolution = gl.getUniformLocation(program, "iResolution");
        const uTime = gl.getUniformLocation(program, "iTime");
        const uHue = gl.getUniformLocation(program, "uHue");

        const startTime = performance.now();
        function render() {
            gl.uniform2f(uResolution, canvas.width, canvas.height);
            gl.uniform1f(uTime, (performance.now() - startTime) / 1000.0);
            gl.uniform1f(uHue, lightningHue);
            gl.drawArrays(gl.TRIANGLES, 0, 6);
            requestAnimationFrame(render);
        }
        requestAnimationFrame(render);
    }

    /* ==========================================================================
    /* ==========================================================================
       GOLDEN GLITTER SPARKLE PARTICLE ENGINE (MAX FPS)
       ========================================================================== */
    function init3DCursorGlitterEngine() {
        const canvas = document.getElementById("glitter-canvas");
        if (!canvas) return;

        const ctx = canvas.getContext("2d", { alpha: true });
        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;

        window.addEventListener("resize", () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        });

        let mouseX = width / 2;
        let mouseY = height / 2;

        const particles = [];
        const goldColors = [
            { r: 255, g: 215, b: 0 },   // Pure Metallic Gold (#ffd700)
            { r: 255, g: 170, b: 0 },   // Warm Amber Gold (#ffaa00)
            { r: 255, g: 240, b: 160 }  // Champagne Sparkle Gold (#fff0a0)
        ];

        window.addEventListener("mousemove", (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;

            // Spawn 3D glittering particles on mouse movement
            if (particles.length < 50) {
                spawnGlitterParticle(mouseX, mouseY, false);
            }
        });

        // Click burst explosion effect
        window.addEventListener("click", (e) => {
            const burstCount = Math.min(20, 50 - particles.length);
            for (let i = 0; i < burstCount; i++) {
                spawnGlitterParticle(e.clientX, e.clientY, true);
            }
        });

        function spawnGlitterParticle(x, y, isExplosion = false) {
            const col = goldColors[Math.floor(Math.random() * goldColors.length)];

            const speed = isExplosion ? (Math.random() * 4.5 + 1.5) : (Math.random() * 1.5 + 0.4);
            const angle = Math.random() * Math.PI * 2;

            particles.push({
                x: x + (Math.random() * 10 - 5),
                y: y + (Math.random() * 10 - 5),
                z: Math.random() * 160 - 80,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed - (isExplosion ? 0 : 0.4),
                size: Math.random() * 3.5 + 1.8,
                color: col,
                alpha: 1.0,
                decay: Math.random() * 0.03 + 0.02,
                rotation: Math.random() * Math.PI,
                rotSpeed: (Math.random() - 0.5) * 0.15,
                glimmerPhase: Math.random() * Math.PI * 2,
                type: Math.random() > 0.4 ? "diamond" : "star"
            });
        }

        function renderLoop() {
            ctx.clearRect(0, 0, width, height);

            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.z += 0.5;
                p.alpha -= p.decay;
                p.rotation += p.rotSpeed;
                p.glimmerPhase += 0.18;

                if (p.alpha <= 0) {
                    particles.splice(i, 1);
                    continue;
                }

                const perspective = 300 / (300 + p.z);
                const renderSize = p.size * perspective * (0.85 + 0.35 * Math.sin(p.glimmerPhase));

                ctx.save();
                ctx.translate(p.x, p.y);
                ctx.rotate(p.rotation);
                ctx.scale(perspective, perspective);

                const radGlow = ctx.createRadialGradient(0, 0, 0, 0, 0, renderSize * 2.2);
                radGlow.addColorStop(0, `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, ${p.alpha})`);
                radGlow.addColorStop(0.5, `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, ${p.alpha * 0.4})`);
                radGlow.addColorStop(1, `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, 0)`);

                ctx.fillStyle = radGlow;

                if (p.type === "diamond") {
                    ctx.beginPath();
                    ctx.moveTo(0, -renderSize * 1.8);
                    ctx.lineTo(renderSize * 1.2, 0);
                    ctx.lineTo(0, renderSize * 1.8);
                    ctx.lineTo(-renderSize * 1.2, 0);
                    ctx.closePath();
                    ctx.fill();
                } else {
                    ctx.beginPath();
                    for (let s = 0; s < 4; s++) {
                        ctx.lineTo(Math.cos(s * Math.PI / 2) * renderSize * 2, Math.sin(s * Math.PI / 2) * renderSize * 2);
                        ctx.lineTo(Math.cos((s + 0.5) * Math.PI / 2) * (renderSize * 0.5), Math.sin((s + 0.5) * Math.PI / 2) * (renderSize * 0.5));
                    }
                    ctx.closePath();
                    ctx.fill();
                }

                ctx.restore();
            }

            requestAnimationFrame(renderLoop);
        }

        renderLoop();
    }
});
