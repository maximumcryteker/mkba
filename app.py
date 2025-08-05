from flask import Flask, request, send_from_directory, jsonify
import os
import json
import csv
from datetime import datetime

app = Flask(__name__, static_folder='static')
DATA_FOLDER = 'data'

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

@app.route('/')
def index():
    return send_from_directory('static', 'stroop.html')

@app.route('/config/<path:filename>')
def send_config(filename):
    return send_from_directory('config', filename)

@app.route('/save-results', methods=['POST'])
def save_results():
    data = request.get_json()

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    json_filename = os.path.join(DATA_FOLDER, f"results_{timestamp}.json")
    csv_filename = os.path.join(DATA_FOLDER, f"results_{timestamp}.csv")

    # Save JSON
    with open(json_filename, 'w') as f_json:
        json.dump(data, f_json, indent=2)

    # Save CSV (taskResults only)
    try:
        with open(csv_filename, 'w', newline='') as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=['timestamp', 'shape', 'color', 'key', 'time', 'correct'])
            writer.writeheader()
            for row in data.get('taskResults', []):
                row['timestamp'] = data.get('timestamp')
                writer.writerow(row)
    except Exception as e:
        return f"CSV save error: {str(e)}", 500

    return "Saved successfully"
