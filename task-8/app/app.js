const ws = new WebSocket("ws://localhost:5000/ws");
const dot = document.getElementById("dot");
const connStatus = document.getElementById("conn-status");

const MAX_ROWS = 10;

ws.onopen = () => {
    dot.classList.add("connected");
    connStatus.textContent = "Connected";
};

ws.onerror = () => {
    dot.classList.add("error");
    connStatus.textContent = "Error";
};

ws.onclose = () => {
    dot.classList.remove("connected");
    dot.classList.add("error");
    connStatus.textContent = "Disconnected";
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateTable(data);
    updateStats(data);
    checkAlerts(data);
    updateCharts(data);
};

function updateTable(data) {
    const tbody = document.getElementById("data-table");
    const row = document.createElement("tr");
    row.innerHTML = `
        <td>${data.timestamp}</td>
        <td>${data.sensor_id}</td>
        <td>${data.temperature}</td>
        <td>${data.vibration}</td>
    `;
    tbody.prepend(row);
    if (tbody.rows.length > MAX_ROWS) tbody.deleteRow(MAX_ROWS);
}

function updateStats(data) {
    const s = data.sensor_id;
    document.getElementById(`${s}-avg-temp`).textContent = data.avg_temp.toFixed(2);
    document.getElementById(`${s}-avg-vibration`).textContent = data.avg_vibration.toFixed(3);
    document.getElementById(`${s}-z-temp`).textContent = data.z_temp.toFixed(2);
    document.getElementById(`${s}-z-vibration`).textContent = data.z_vibration.toFixed(2);
}

function checkAlerts(data) {
    const alertsDiv = document.getElementById("alerts");
    const noAlerts = alertsDiv.querySelector(".no-alerts");

    const messages = [];
    if (Math.abs(data.z_temp) > 2.5) messages.push(`${data.sensor_id} — Temp z-score: ${data.z_temp.toFixed(2)}`);
    if (Math.abs(data.z_vibration) > 2.5) messages.push(`${data.sensor_id} — Vibration z-score: ${data.z_vibration.toFixed(2)}`);

    messages.forEach(msg => {
        if (noAlerts) noAlerts.remove();
        const item = document.createElement("div");
        item.className = "alert-item";
        item.textContent = `[${data.timestamp}] ${msg}`;
        alertsDiv.prepend(item);
    });
}

const MAX_POINTS = 30;

const chartConfigs = {
    "T1-temp":      { label: "T1 Temperature",  raw: "temperature", avg: "avg_temp",      min: 15, max: 120 },
    "T2-temp":      { label: "T2 Temperature",  raw: "temperature", avg: "avg_temp",      min: 15, max: 120 },
    "T1-vibration": { label: "T1 Vibration",    raw: "vibration",   avg: "avg_vibration", min: 0,  max: 0.8 },
    "T2-vibration": { label: "T2 Vibration",    raw: "vibration",   avg: "avg_vibration", min: 0,  max: 0.8 },
};

const charts = {};

function initCharts() {
    for (const [id, config] of Object.entries(chartConfigs)) {
        const ctx = document.getElementById(`chart-${id}`);
        charts[id] = new Chart(ctx, {
            type: "line",
            data: {
                labels: [],
                datasets: [
                    {
                        label: "Raw",
                        data: [],
                        borderColor: "#2563eb",
                        borderWidth: 1.5,
                        pointRadius: 0,
                        tension: 0.2,
                    },
                    {
                        label: "Moving Avg",
                        data: [],
                        borderColor: "#dc2626",
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.4,
                        borderDash: [5, 3],
                    }
                ]
            },
            options: {
                animation: false,
                responsive: true,
                plugins: { legend: { display: true } },
                scales: {
                    x: { ticks: { maxTicksLimit: 6 } },
                    y: { min: config.min, max: config.max }
                }
            }
        });
    }
}

function updateCharts(data) {
    const sid = data.sensor_id;

    for (const metric of ["temp", "vibration"]) {
        const id = `${sid}-${metric}`;
        const chart = charts[id];
        const config = chartConfigs[id];

        chart.data.labels.push(data.timestamp);
        chart.data.datasets[0].data.push(data[config.raw]);
        chart.data.datasets[1].data.push(data[config.avg]);

        if (chart.data.labels.length > MAX_POINTS) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
            chart.data.datasets[1].data.shift();
        }

        chart.update();
    }
}

initCharts();
