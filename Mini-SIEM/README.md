### 🛡️ Mini-SIEM Dashboard  
Developed by Jørgen A. Fjellstad - November 2025

____________________________________________________________________________________________________________

A Python-based prototype that simulates a Security Information and Event Management (SIEM) system.  
It visualizes real-time threat data, event logs, and network anomalies in a clean Flask web dashboard.

____________________________________________________________________________________________________________

### 📊 Features
- **Live dashboard** with auto-refresh and blinking status indicator  
- **Dual view modes:**  
  - *Technical View* - detailed log data for analysts  
  - *Simplified View* - human-readable summaries for executives  
- **Interactive charts:** Severity distribution + most frequent event types  
- **Filter & sort:** Filter by severity or sort directly by clicking cards  
- **Persistent storage:** Alerts automatically written to `alerts.json`  
- **Minimal design:** Optimized for readability and realism  

____________________________________________________________________________________________________________

### 🧠 How It Works
- `log_generator.py` continuously generates randomized but realistic alerts  
- Alerts are saved in `alerts.json`  
- `web_dashboard.py` reads and displays them dynamically using Flask  
- The dashboard automatically updates every 10 seconds  
- User preferences (simplified/technical view, visible charts, filters) are stored in browser `localStorage`

____________________________________________________________________________________________________________

### ▶️ Usage
```bash
# 1. Install Flask
pip install flask

# 2. Run the log generator
python log_generator.py

# 3. Start the web dashboard
python web_dashboard.py

# 4. Then open your browser and go to:
http://127.0.0.1:5000
```

### 🧰 Technologies Used

- Python 3
- Flask - lightweight backend web framework
- Chart.js - dynamic data visualization
- HTML, CSS, JavaScript - modern dashboard frontend


