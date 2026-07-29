document.addEventListener("DOMContentLoaded", () => {
    let currentUnit = "C";
    let weatherData = null;
    let hourlyChart = null;

    const searchInput = document.getElementById("search-input");
    const searchBtn = document.getElementById("search-btn");
    const autocompleteDropdown = document.getElementById("autocomplete-dropdown");
    const loadingOverlay = document.getElementById("loading-overlay");

    const unitBtnC = document.getElementById("unit-c");
    const unitBtnF = document.getElementById("unit-f");

    // Default load
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

    // Close autocomplete on outside click
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".search-wrapper")) {
            autocompleteDropdown.classList.remove("active");
        }
    });

    // Bookmarks chips
    document.querySelectorAll(".chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const city = chip.getAttribute("data-city");
            searchInput.value = city;
            fetchWeatherData(city);
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
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(err => {
            loadingOverlay.classList.remove("active");
            alert("Network error. Please try again.");
        });
    }

    function updateUI(res) {
        const raw = res.data;
        const curr = raw.current;
        const loc = raw.location;
        const analysis = res.analysis;
        const recs = res.recommendations;
        const logs = res.agent_logs;

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

        // Render Chart
        renderHourlyChart(raw.hourly);
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
});
