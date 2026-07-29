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

    // Initialize Full-Page Cinematic Scroll-Driven Weather Engine
    initCinematicWeatherEngine();

    // Initialize 3D Parallax Tilt Effects on Cards
    init3DTiltEffects();

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

    // Default load (London)
    const initialCity = window.INITIAL_CITY || "London";
    fetchWeatherData(initialCity);

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
    // Interactive 3D Parallax Tilt Effect
    // -------------------------------------------------------------
    function init3DTiltEffects() {
        const cards = document.querySelectorAll(".glass-card, .metric-card");
        cards.forEach(card => {
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

    // =========================================================================
    // FULL-PAGE CINEMATIC SCROLL-DRIVEN WEATHER ENGINE (60 FPS GPU ACCELERATED)
    // =========================================================================
    function initCinematicWeatherEngine() {
        const canvas = document.getElementById("cinematic-weather-canvas");
        const sunOverlay = document.getElementById("sun-god-rays");
        const frostOverlay = document.getElementById("frost-vignette");
        const snowBottom = document.getElementById("snow-bottom-layer");

        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        let width = (canvas.width = window.innerWidth);
        let height = (canvas.height = window.innerHeight);

        window.addEventListener("resize", () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        });

        // Target vs Current Scroll Ratio for 100% Smooth Lerp Interpolation
        let currentScroll = 0;
        let targetScroll = 0;

        function updateScroll() {
            const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
            targetScroll = Math.min(1, Math.max(0, window.scrollY / maxScroll));
        }
        window.addEventListener("scroll", updateScroll, { passive: true });
        updateScroll();

        // -------------------------------------------------------------
        // Particle Systems & Asset Objects
        // -------------------------------------------------------------
        
        // 1. Rain Drops Pool (300 Drops)
        const rainDrops = [];
        for (let i = 0; i < 350; i++) {
            rainDrops.push({
                x: Math.random() * width,
                y: Math.random() * height,
                length: Math.random() * 25 + 15,
                speed: Math.random() * 18 + 12,
                depth: Math.random() * 0.8 + 0.2,
                opacity: Math.random() * 0.7 + 0.3
            });
        }

        // 2. Snowflakes Pool (300 Flakes)
        const snowflakes = [];
        for (let i = 0; i < 300; i++) {
            snowflakes.push({
                x: Math.random() * width,
                y: Math.random() * height,
                radius: Math.random() * 3.5 + 1.2,
                speed: Math.random() * 1.8 + 0.8,
                swayOffset: Math.random() * Math.PI * 2,
                opacity: Math.random() * 0.8 + 0.2
            });
        }

        // 3. Sun Dust & God Ray Dust Particles (120 Particles)
        const sunParticles = [];
        for (let i = 0; i < 120; i++) {
            sunParticles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                radius: Math.random() * 2.5 + 0.8,
                speedY: Math.random() * -0.5 - 0.2,
                speedX: Math.random() * 0.4 - 0.2,
                opacity: Math.random() * 0.6 + 0.2
            });
        }

        // 4. Volumetric Cloud Layers (6 Clouds)
        const clouds = [
            { x: width * 0.1, y: height * 0.15, radius: 180, speed: 0.25 },
            { x: width * 0.4, y: height * 0.08, radius: 240, speed: 0.18 },
            { x: width * 0.75, y: height * 0.18, radius: 210, speed: 0.22 },
            { x: width * 0.25, y: height * 0.28, radius: 190, speed: 0.30 },
            { x: width * 0.6, y: height * 0.32, radius: 220, speed: 0.20 }
        ];

        // 5. Parallax Distant Birds (3 Birds)
        const birds = [
            { x: -50, y: height * 0.20, speed: 1.5, scale: 0.8 },
            { x: -120, y: height * 0.25, speed: 1.2, scale: 0.6 },
            { x: -200, y: height * 0.18, speed: 1.8, scale: 0.9 }
        ];

        // Lightning State for Scene 1
        let lightningFlashOpacity = 0;

        // Color Helper Interpolation
        function hexToRgb(hex) {
            let c = hex.replace("#", "");
            if (c.length === 3) c = c.split("").map(x => x + x).join("");
            const num = parseInt(c, 16);
            return [num >> 16, (num >> 8) & 255, num & 255];
        }

        function interpolateColor(color1, color2, factor) {
            const rgb1 = hexToRgb(color1);
            const rgb2 = hexToRgb(color2);
            const r = Math.round(rgb1[0] + factor * (rgb2[0] - rgb1[0]));
            const g = Math.round(rgb1[1] + factor * (rgb2[1] - rgb1[1]));
            const b = Math.round(rgb1[2] + factor * (rgb2[2] - rgb1[2]));
            return `rgb(${r}, ${g}, ${b})`;
        }

        // Main Render Loop (60 FPS)
        let startTime = performance.now();
        function renderCinematicLoop(now) {
            const time = (now - startTime) / 1000.0;

            // Smooth Scroll Interpolation (Lerp 0.08)
            currentScroll += (targetScroll - currentScroll) * 0.08;

            ctx.clearRect(0, 0, width, height);

            // Calculate Scene Blends based on Scroll Ratio (0.0 -> 1.0)
            let skyColorTop, skyColorBottom;
            let lightningIntensity = 0;
            let sunIntensity = 0;
            let rainIntensity = 0;
            let snowIntensity = 0;

            if (currentScroll < 0.28) {
                // Scene 1: Thunderstorm (0.00 - 0.28)
                const s = currentScroll / 0.28;
                skyColorTop = interpolateColor("#030712", "#0f172a", s);
                skyColorBottom = interpolateColor("#0f172a", "#1e293b", s);
                lightningIntensity = 1.0 - s * 0.7;
            } else if (currentScroll < 0.38) {
                // Transition 1: Thunderstorm -> Sunny Day (0.28 - 0.38)
                const t = (currentScroll - 0.28) / 0.10;
                skyColorTop = interpolateColor("#0f172a", "#0284c7", t);
                skyColorBottom = interpolateColor("#1e293b", "#38bdf8", t);
                lightningIntensity = 0.3 * (1.0 - t);
                sunIntensity = t;
            } else if (currentScroll < 0.62) {
                // Scene 2: Bright Sunny Day (0.38 - 0.62)
                skyColorTop = "#0284c7";
                skyColorBottom = "#38bdf8";
                sunIntensity = 1.0;
            } else if (currentScroll < 0.72) {
                // Transition 2: Sunny Day -> Continuous Rain (0.62 - 0.72)
                const t = (currentScroll - 0.62) / 0.10;
                skyColorTop = interpolateColor("#0284c7", "#1e293b", t);
                skyColorBottom = interpolateColor("#38bdf8", "#334155", t);
                sunIntensity = 1.0 - t;
                rainIntensity = t * 0.6;
            } else if (currentScroll < 0.86) {
                // Scene 3: Continuous Rain (0.72 - 0.86)
                skyColorTop = "#1e293b";
                skyColorBottom = "#334155";
                rainIntensity = 1.0;
            } else if (currentScroll < 0.92) {
                // Transition 3: Continuous Rain -> Winter Snow (0.86 - 0.92)
                const t = (currentScroll - 0.86) / 0.06;
                skyColorTop = interpolateColor("#1e293b", "#0f172a", t);
                skyColorBottom = interpolateColor("#334155", "#1e1b4b", t);
                rainIntensity = 1.0 - t;
                snowIntensity = t;
            } else {
                // Scene 4: Winter Snow (0.92 - 1.00)
                skyColorTop = "#0f172a";
                skyColorBottom = "#1e1b4b";
                snowIntensity = 1.0;
            }

            // Draw Background Sky Gradient
            const gradient = ctx.createLinearGradient(0, 0, 0, height);
            gradient.addColorStop(0, skyColorTop);
            gradient.addColorStop(1, skyColorBottom);
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, width, height);

            // Handle Overlays (Sun God Rays & Sub-Zero Frost)
            if (sunIntensity > 0.3) {
                sunOverlay.classList.add("active");
                sunOverlay.style.opacity = (sunIntensity - 0.3) / 0.7;
            } else {
                sunOverlay.classList.remove("active");
            }

            if (snowIntensity > 0.4) {
                frostOverlay.classList.add("active");
                snowBottom.classList.add("active");
                frostOverlay.style.opacity = (snowIntensity - 0.4) / 0.6;
                snowBottom.style.opacity = (snowIntensity - 0.4) / 0.6;
            } else {
                frostOverlay.classList.remove("active");
                snowBottom.classList.remove("active");
            }

            // -------------------------------------------------------------
            // Scene 1: Thunderstorm Lightning Flashes & Clouds
            // -------------------------------------------------------------
            if (lightningIntensity > 0) {
                if (Math.random() < 0.03 * lightningIntensity) {
                    lightningFlashOpacity = Math.random() * 0.45 * lightningIntensity;
                } else {
                    lightningFlashOpacity *= 0.88;
                }

                if (lightningFlashOpacity > 0.02) {
                    ctx.fillStyle = `rgba(56, 189, 248, ${lightningFlashOpacity})`;
                    ctx.fillRect(0, 0, width, height);
                }
            }

            // Volumetric Cloud Layer (Scenes 1 & 2)
            if (currentScroll < 0.65) {
                ctx.fillStyle = currentScroll < 0.35 
                    ? "rgba(15, 23, 42, 0.45)" 
                    : "rgba(248, 250, 252, 0.18)";

                clouds.forEach(c => {
                    c.x += c.speed;
                    if (c.x - c.radius > width) c.x = -c.radius;

                    ctx.beginPath();
                    ctx.arc(c.x, c.y, c.radius, 0, Math.PI * 2);
                    ctx.arc(c.x + c.radius * 0.5, c.y - c.radius * 0.2, c.radius * 0.7, 0, Math.PI * 2);
                    ctx.arc(c.x - c.radius * 0.5, c.y - c.radius * 0.2, c.radius * 0.7, 0, Math.PI * 2);
                    ctx.fill();
                });
            }

            // -------------------------------------------------------------
            // Scene 2: Bright Sunny Day Birds & Dust Particles
            // -------------------------------------------------------------
            if (sunIntensity > 0) {
                // Flying Birds
                ctx.strokeStyle = `rgba(255, 255, 255, ${0.6 * sunIntensity})`;
                ctx.lineWidth = 2;
                birds.forEach(b => {
                    b.x += b.speed;
                    if (b.x > width + 100) b.x = -100;

                    ctx.beginPath();
                    const wingSway = Math.sin(time * 6 + b.x * 0.05) * 8;
                    ctx.moveTo(b.x - 12 * b.scale, b.y + wingSway);
                    ctx.quadraticCurveTo(b.x, b.y - 6 * b.scale, b.x + 12 * b.scale, b.y + wingSway);
                    ctx.stroke();
                });

                // Sun Particles
                ctx.fillStyle = `rgba(253, 224, 71, ${0.4 * sunIntensity})`;
                sunParticles.forEach(p => {
                    p.y += p.speedY;
                    p.x += p.speedX;
                    if (p.y < 0) p.y = height;
                    if (p.x < 0) p.x = width;
                    if (p.x > width) p.x = 0;

                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                    ctx.fill();
                });
            }

            // -------------------------------------------------------------
            // Scene 3: Continuous Rain Particles
            // -------------------------------------------------------------
            if (rainIntensity > 0) {
                ctx.strokeStyle = "rgba(186, 230, 253, 0.65)";
                ctx.lineWidth = 1.2;

                rainDrops.forEach(drop => {
                    drop.y += drop.speed;
                    drop.x += Math.sin(time) * 0.8;

                    if (drop.y > height) {
                        drop.y = -drop.length;
                        drop.x = Math.random() * width;
                    }

                    ctx.beginPath();
                    ctx.moveTo(drop.x, drop.y);
                    ctx.lineTo(drop.x - 2, drop.y + drop.length * rainIntensity);
                    ctx.stroke();
                });
            }

            // -------------------------------------------------------------
            // Scene 4: Winter Snow Particles
            // -------------------------------------------------------------
            if (snowIntensity > 0) {
                ctx.fillStyle = `rgba(248, 250, 252, ${0.85 * snowIntensity})`;

                snowflakes.forEach(flake => {
                    flake.y += flake.speed;
                    flake.x += Math.sin(time + flake.swayOffset) * 1.2;

                    if (flake.y > height) {
                        flake.y = -5;
                        flake.x = Math.random() * width;
                    }

                    ctx.beginPath();
                    ctx.arc(flake.x, flake.y, flake.radius * snowIntensity, 0, Math.PI * 2);
                    ctx.fill();
                });
            }

            requestAnimationFrame(renderCinematicLoop);
        }

        requestAnimationFrame(renderCinematicLoop);
    }
});
