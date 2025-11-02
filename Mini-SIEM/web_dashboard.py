# =====================================================
# web_dashboard.py
# Flask web interface for viewing Mini-SIEM alerts
# Features: technical + simplified view, charts, color-coded severity, and clickable filtering.
# Developed by Jørgen A. Fjellstad - 2025
# =====================================================

from flask import Flask, render_template_string
import json, os, time
from collections import Counter

app = Flask(__name__)

# =====================================================
# Simplified explanations for non-technical users
# =====================================================
EXPLANATIONS = {
    "Failed login": "Several failed login attempts - possible password guessing.",
    "Successful login": "A login succeeded after suspicious attempts - verify legitimacy.",
    "Known malicious IP": "Connection with a known threat source was detected.",
    "Brute force attempt": "Multiple login failures from one IP - possible brute-force attack.",
    "Sensitive file modified": "A critical system file was changed - verify it was authorized.",
    "File deletion detected": "A file was deleted from the system - ensure it was intentional.",
    "SQL Injection attempt": "Attempt to manipulate database through input fields.",
    "Ransomware encrypt": "Files encrypted - possible ransomware attack.",
    "Exfiltration": "Data transfer detected - possible data theft.",
    "Heartbeat": "Normal system status update.",
    "Info": "Informational event - no action required unless repeated."
}

# =====================================================
# HTML template with inline CSS + JS
# =====================================================
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="10"> <!-- Auto refresh every 10 seconds -->
<title>Mini-SIEM Threat Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
/* ======= Global layout and colors ======= */
body {
  font-family: Arial, sans-serif;
  background: #101010;
  color: #e0e0e0;
  margin: 0;
  padding: 0;
}
h1 {
  background-color: #1b1b1b;
  padding: 15px;
  text-align: center;
  color: #00bcd4;
  margin: 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.4);
}

/* ======= Top statistics section ======= */
.stats {
  display: flex;
  justify-content: space-around;
  background-color: #141414;
  padding: 15px;
  border-bottom: 1px solid #333;
  flex-wrap: wrap;
}
.card {
  text-align: center;
  padding: 10px 20px;
  border-radius: 10px;
  min-width: 120px;
  margin: 5px;
  transition: transform 0.2s;
  box-shadow: 0 0 8px rgba(0, 188, 212, 0.3);
}
.card:hover { transform: scale(1.05); }

/* Card colors match table + charts */
.card.Critical { border:1px solid #ff5252; color:#ff5252; box-shadow:0 0 10px rgba(255,82,82,0.4); }
.card.High { border:1px solid #ffb74d; color:#ffb74d; box-shadow:0 0 10px rgba(255,183,77,0.4); }
.card.Medium { border:1px solid #4db6ac; color:#4db6ac; box-shadow:0 0 10px rgba(77,182,172,0.4); }
.card.Info { border:1px solid #555; color:#aaa; box-shadow:0 0 10px rgba(255,255,255,0.05); }

/* ======= Table formatting ======= */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
  table-layout: fixed;
  display: block;
  max-height: 600px;
  overflow-y: auto;
}
thead, tbody tr { display: table; width: 100%; table-layout: fixed; }
th, td {
  padding: 10px;
  border-bottom: 1px solid #333;
  text-align: left;
  vertical-align: top;
  word-wrap: break-word;
}
tr:nth-child(even) { background-color: #151515; }
tr:nth-child(odd) { background-color: #0f0f0f; }
tr:hover { background-color: #222; }

/* Column width definitions */
th:nth-child(1), td:nth-child(1) { width: 12%; white-space: nowrap; }
th:nth-child(2), td:nth-child(2) { width: 10%; }
th:nth-child(3), td:nth-child(3) { width: 18%; }
th:nth-child(4), td:nth-child(4) { width: 12%; }
th:nth-child(5), td:nth-child(5) { width: 48%; }

/* Only the severity column is colored */
td:nth-child(2).Critical { color: #ff5252; font-weight: bold; }
td:nth-child(2).High { color: #ffb74d; font-weight: bold; }
td:nth-child(2).Medium { color: #4db6ac; font-weight: bold; }
td:nth-child(2).Info { color: #aaa; }

/* Buttons and footer */
.toggle { text-align:center; padding:10px; background:#1b1b1b; }
.toggle button {
  background-color:#00bcd4; color:#fff; border:none;
  padding:8px 16px; font-size:14px; border-radius:6px; cursor:pointer;
}
.toggle button:hover { background-color:#0097a7; }

footer {
  text-align:center; padding:10px; font-size:0.8em;
  color:#777; border-top:1px solid #333;
}

/* Status line under title */
.update-line {
  text-align:center; color:#999; font-size:13px;
  padding:4px; background:#111; border-bottom:1px solid #333;
}
.blink { color:#4db6ac; animation: blink 1s infinite alternate; }
@keyframes blink { from{opacity:1;} to{opacity:0.3;} }
</style>

<!-- ======= Chart toggle (defined early so it's global) ======= -->
<script>
function toggleCharts() {
  const chartContainer = document.getElementById('chartContainer');
  if (!chartContainer) return;
  let chartsVisible = localStorage.getItem('chartsVisible') !== 'false';
  chartsVisible = !chartsVisible;
  chartContainer.style.display = chartsVisible ? 'flex' : 'none';
  localStorage.setItem('chartsVisible', chartsVisible);
}
</script>
</head>

<body>
  <h1>Mini-SIEM Threat Dashboard</h1>

  <!-- Top status bar showing update time and total alerts -->
  <div class="update-line">
    <span class="blink">●</span> Last update: {{ stats.last_update }} | Total alerts loaded: {{ stats.total }}
  </div>

  {% if stats %}
  <!-- ======= Stats cards section ======= -->
  <div class="stats">
    <!-- Clickable cards that filter table rows -->
    <div class="card Info" onclick="filterBySeverity('All')">
      Total Alerts<br><strong>{{ stats.total }}</strong>
    </div>
    <div class="card Critical" onclick="filterBySeverity('Critical')">
      Critical<br><strong>{{ stats.critical }}</strong>
    </div>
    <div class="card High" onclick="filterBySeverity('High')">
      High<br><strong>{{ stats.high }}</strong>
    </div>
    <div class="card Medium" onclick="filterBySeverity('Medium')">
      Medium<br><strong>{{ stats.medium }}</strong>
    </div>
    <div class="card Info">
      Top IPs<br>
      {% if stats.top_ips %}
        {% for ip,count in stats.top_ips %}
          {{ ip }} ({{ count }})<br>
        {% endfor %}
      {% else %}
        No recurring IPs detected
      {% endif %}
    </div>
  </div>

  <!-- ======= Charts section ======= -->
  <div style="text-align:center; margin-top:10px;">
    <button onclick="toggleCharts()" style="background-color:#00bcd4;color:white;border:none;padding:6px 12px;border-radius:6px;cursor:pointer;">
      Toggle Charts
    </button>
  </div>

  <div id="chartContainer" style="display:flex; justify-content:center; gap:20px; flex-wrap:wrap; margin:10px auto;">
    <div style="max-width:400px;">
      <canvas id="severityChart" width="400" height="150"></canvas>
    </div>
    <div style="max-width:400px;">
      <canvas id="topEventsChart" width="400" height="150"></canvas>
    </div>
  </div>

  <!-- ======= ChartJS initialization ======= -->
  <script>
  const chartContainer = document.getElementById('chartContainer');
  const ctx1 = document.getElementById('severityChart');
  const ctx2 = document.getElementById('topEventsChart');
  let chartsVisible = localStorage.getItem('chartsVisible') !== 'false';
  chartContainer.style.display = chartsVisible ? 'flex' : 'none';

  // Doughnut chart for severity distribution
  new Chart(ctx1, {
    type: 'doughnut',
    data: {
      labels: ['Critical', 'High', 'Medium'],
      datasets: [{ data: [{{ stats.critical }}, {{ stats.high }}, {{ stats.medium }}],
                   backgroundColor: ['#ff5252', '#ffb74d', '#4db6ac'] }]
    },
    options: { plugins: { legend: { labels: { color: '#fff' } } } }
  });

  // Bar chart for most frequent event types
  let topEvents = {};
  {% for a in alerts %}
  if ("{{ a.type }}" !== "Heartbeat" && "{{ a.severity }}" !== "Info") {
    topEvents["{{ a.type }}"] = (topEvents["{{ a.type }}"] || 0) + 1;
  }
  {% endfor %}
  let sortedTypes = Object.entries(topEvents).sort((a,b) => b[1]-a[1]).slice(0,5);
  let labels = sortedTypes.map(e => e[0]);
  let values = sortedTypes.map(e => e[1]);
  new Chart(ctx2, {
    type: 'bar',
    data: { labels, datasets: [{ label: 'Most Frequent Events', data: values, backgroundColor: '#00bcd4' }] },
    options: {
  scales: {
    x: {
      ticks: { color: '#fff' },
      grid: { color: '#333' }
    },
    y: {
      ticks: { color: '#fff' },
      grid: { color: '#333' },
      beginAtZero: true,
      max: 40,           // upper limit on Y-axis
    }
  },
  plugins: { legend: { labels: { color: '#fff' } } }
}
  });
  </script>
  {% endif %}

  <!-- ======= View toggle button (technical / simplified) ======= -->
  <div class="toggle">
    <button id="toggleBtn">Switch to Simplified View</button>
  </div>

  <!-- ======= Technical (Advanced) view ======= -->
  <div id="advanced">
  {% if alerts %}
  <table>
    <thead><tr><th>Time</th><th>Severity</th><th>Type</th><th>IP</th><th>Details</th></tr></thead>
    <tbody>
    {% for a in alerts %}
    <tr class="{{ a.severity }}">
      <td>{{ a.time }}</td>
      <td class="{{ a.severity }}">{{ a.severity }}</td>
      <td>{{ a.type }}</td>
      <td>{{ a.ip or "-" }}</td>
      <td>{{ a.log }}</td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p style="text-align:center;">No alerts found.</p>
  {% endif %}
  </div>

  <!-- ======= Simplified (executive) view ======= -->
  <div id="executive" style="display:none;">
  {% if alerts %}
  <table>
    <thead><tr><th>Time</th><th>Severity</th><th>Type</th><th>IP</th><th>Explanation</th></tr></thead>
    <tbody>
    {% for a in alerts %}
    <tr class="{{ a.severity }}">
      <td>{{ a.time }}</td>
      <td class="{{ a.severity }}">{{ a.severity }}</td>
      <td>{{ a.type }}</td>
      <td>{{ a.ip or "-" }}</td>
      <td>{{ a.description or "No explanation available." }}</td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p style="text-align:center;">No alerts found.</p>
  {% endif %}
  </div>

  <footer>Developed by Jørgen A. Fjellstad - 2025</footer>

  <!-- ======= Toggle simplified / technical view ======= -->
  <script>
  document.addEventListener('DOMContentLoaded', () => {
    const adv = document.getElementById('advanced');
    const exec = document.getElementById('executive');
    const btn = document.getElementById('toggleBtn');
    let simplified = localStorage.getItem('simplifiedView') === 'true';

    function applyViewState() {
      if (simplified) {
        adv.style.display = 'none';
        exec.style.display = '';
        btn.innerText = 'Switch to Technical View';
      } else {
        adv.style.display = '';
        exec.style.display = 'none';
        btn.innerText = 'Switch to Simplified View';
      }
    }

    btn.addEventListener('click', () => {
      simplified = !simplified;
      localStorage.setItem('simplifiedView', simplified);
      applyViewState();
    });
    applyViewState();
  });
  </script>

  <!-- ======= Filter by clicking severity cards ======= -->
  <script>
  function filterBySeverity(level) {
    const allRows = document.querySelectorAll('tbody tr');
    allRows.forEach(row => {
      if (level === 'All') row.style.display = '';
      else row.style.display = row.classList.contains(level) ? '' : 'none';
    });
  }
  </script>
</body>
</html>
"""

# =====================================================
# Flask route: loads data and renders dashboard
# =====================================================
@app.route("/")
def dashboard():
    """Load alerts from alerts.json and build dashboard statistics."""
    if not os.path.exists("alerts.json"):
        return render_template_string(TEMPLATE, alerts=[], stats=None)

    with open("alerts.json", "r", encoding="utf-8") as f:
        alerts = json.load(f)

    # Add descriptions for simplified view
    for a in alerts:
        a["description"] = EXPLANATIONS.get(a["type"], "No explanation available.")

    # Sort newest first
    alerts.sort(key=lambda x: x.get("time", ""), reverse=True)

    # Collect counts and top IPs
    total = len(alerts)
    severities = Counter(a["severity"] for a in alerts)
    ip_counter = Counter(a.get("ip") for a in alerts if a.get("ip"))
    top_ips = [(ip, count) for ip, count in ip_counter.most_common(5) if count > 1]

    stats = {
        "total": total,
        "critical": severities.get("Critical", 0),
        "high": severities.get("High", 0),
        "medium": severities.get("Medium", 0),
        "top_ips": top_ips,
        "last_update": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    return render_template_string(TEMPLATE, alerts=alerts, stats=stats)

# =====================================================
# Run Flask web server
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)
