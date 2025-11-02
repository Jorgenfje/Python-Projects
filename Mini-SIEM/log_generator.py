# =====================================================
# log_generator.py
# Generates continuous dummy security events for Mini-SIEM.
# Each event is written directly to alerts.json for visualization.
# Developed by Jørgen A. Fjellstad - 2025
# =====================================================

import json
import random
import time
import os

# -----------------------------
# Basic settings
# -----------------------------
ALERTS_FILE = "alerts.json"  # Output file for alerts
MAX_ALERTS = 400             # Keep only the latest 400 alerts

# -----------------------------
# Event types and severity levels
# -----------------------------
EVENTS = {
    "Failed login": "Medium",
    "Known malicious IP": "Critical",
    "Sensitive file modified": "High",
    "File deletion detected": "High",
    "Process start": "High",
    "Privileged escalation": "Critical",
    "SQL Injection attempt": "High",
    "XSS attempt": "High",
    "LFI / Path traversal": "High",
    "Command injection attempt": "High",
    "Port scan detected": "High",
    "Scanner user-agent detected": "High",
    "High request rate": "High",
    "Credential dump": "High",
    "New user created": "High",
    "Scheduled task created": "Medium",
    "Lateral movement": "Medium",
    "Unusual traffic": "Medium",
    "Connection": "Medium",
    "DNS query": "Info",
    "Heartbeat": "Info",
    "Ransomware encrypt": "Critical",
    "Exfiltration": "Critical"
}

# =====================================================
# IP generation (realistic internal and external sources)
# =====================================================

_ACTIVE_HOSTS = []  # Stores recently used IPs for reuse

def random_ip(internal_prob=0.45, reuse_prob=0.25):
    """
    Generate a realistic IP address.
    - 45% chance of being internal (10.x, 192.168.x, or 172.16–31.x)
    - 25% chance of reusing a known IP to simulate recurring hosts
    """
    # Reuse IP occasionally to mimic real-world network patterns
    if _ACTIVE_HOSTS and random.random() < reuse_prob:
        return random.choice(_ACTIVE_HOSTS)

    # Generate internal IPs
    if random.random() < internal_prob:
        private_ranges = [
            ("10.", 0.5),
            ("192.168.", 0.35),
            ("172.16.", 0.15)
        ]
        r = random.random()
        cum = 0
        for prefix, w in private_ranges:
            cum += w
            if r <= cum:
                prefix_choice = prefix
                break
        if prefix_choice == "10.":
            ip = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
        elif prefix_choice == "192.168.":
            ip = f"192.168.{random.randint(0,255)}.{random.randint(1,254)}"
        else:
            ip = f"172.{random.randint(16,31)}.{random.randint(0,255)}.{random.randint(1,254)}"
    else:
        # Simulate public cloud / provider IPs
        subnets = [
            "3.5.140.", "52.95.110.", "104.16.132.", "34.96.152.",
            "185.199.108.", "157.240.0.", "45.77.0.", "88.198.51."
        ]
        ip = f"{random.choice(subnets)}{random.randint(1,254)}"

    # Keep small list of active IPs for reuse
    if ip not in _ACTIVE_HOSTS:
        _ACTIVE_HOSTS.append(ip)
        if len(_ACTIVE_HOSTS) > 40:
            _ACTIVE_HOSTS.pop(0)
    return ip

# =====================================================
# Log message formatting
# =====================================================

def make_log(event_type, ip):
    """Create a log message string for the given event type."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if event_type == "Failed login":
        user = random.choice(["admin", "root", "guest"])
        return f"{timestamp} HOST=web01 EVENT=LOGIN user={user} ip={ip} status=failed reason=invalid_password"
    elif event_type == "SQL Injection attempt":
        return f"{timestamp} HOST=web01 EVENT=HTTP_REQUEST url='/product.php?id=1 OR 1=1' ip={ip} ua='sqlmap/1.6'"
    elif event_type == "Sensitive file modified":
        return f"{timestamp} HOST=app01 EVENT=FILE_CHANGE file=/etc/passwd user=apache action=modified ip={ip}"
    elif event_type == "Ransomware encrypt":
        return f"{timestamp} HOST=file01 EVENT=RANSOMWARE file=/data/payroll.xlsx user=root ip={ip}"
    elif event_type == "Exfiltration":
        dest = random_ip()
        size = random.randint(100_000, 5_000_000)
        return f"{timestamp} HOST=web01 EVENT=EXFILTRATION to={dest} bytes={size}"
    else:
        # Generic format for other events
        return f"{timestamp} HOST=web01 EVENT={event_type.replace(' ', '_').upper()} ip={ip}"

# =====================================================
# Read/write operations for alerts.json
# =====================================================

def load_alerts():
    """Read previous alerts from disk if available."""
    if os.path.exists(ALERTS_FILE):
        try:
            with open(ALERTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_alerts(alerts):
    """Write alerts to disk (only the latest MAX_ALERTS)."""
    alerts = alerts[-MAX_ALERTS:]
    with open(ALERTS_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, ensure_ascii=False, indent=2)

# =====================================================
# Generate and store one alert
# =====================================================

def make_alert():
    """Return a complete alert dictionary (one event)."""
    event_type = random.choice(list(EVENTS.keys()))
    severity = EVENTS[event_type]
    ip = random_ip()
    log_entry = make_log(event_type, ip)
    return {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "severity": severity,
        "type": event_type,
        "ip": ip,
        "log": log_entry
    }

# =====================================================
# Main program loop
# =====================================================
if __name__ == "__main__":
    print("[Mini-SIEM] Live generator running - writing to alerts.json")
    try:
        while True:
            alert = make_alert()
            alerts = load_alerts()
            alerts.append(alert)
            save_alerts(alerts)
            print(f"[{alert['severity']}] {alert['type']} - {alert['ip']} - {alert['time']}")
            time.sleep(random.uniform(2.0, 5.0))
    except KeyboardInterrupt:
        print("\nStopped.")
