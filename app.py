from flask import Flask, jsonify
import requests
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

# Define version
APP_VERSION = "0.0.1"

# List of senseBox IDs
SENSEBOX_IDS = [
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c"
]

def fetch_recent_temperature(box_id):
    """Fetch recent temperature from a given senseBox ID."""
    url = f"https://api.opensensemap.org/boxes/{box_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for sensor in data.get('sensors', []):
            if 'temp' in sensor['title'].lower():
                measurement = sensor.get('lastMeasurement')
                if not measurement:
                    continue
                value = float(measurement['value'])
                timestamp = datetime.fromisoformat(measurement['createdAt'].replace('Z', '+00:00'))

                # Check if the reading is from the last 1 hour
                if datetime.now(timezone.utc) - timestamp <= timedelta(hours=1):
                    return value
    except Exception as e:
        print(f"Error fetching from box {box_id}: {e}")
    return None

@app.route("/version")
def version():
    """Return current app version."""
    return jsonify({"version": APP_VERSION})

@app.route("/temperature")
def temperature():
    """Return average temperature from 3 senseBox sensors."""
    temps = []
    for box_id in SENSEBOX_IDS:
        temp = fetch_recent_temperature(box_id)
        if temp is not None:
            temps.append(temp)

    if not temps:
        return jsonify({"error": "No recent temperature data available"}), 503

    avg_temp = sum(temps) / len(temps)
    return jsonify({"average_temperature": round(avg_temp, 2)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)