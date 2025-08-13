import os
import json
import io
import csv
from sqlalchemy import text
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, static_folder='static')
DATA_FOLDER = 'data'

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# PythonAnywhere MySQL config
USERNAME = "maximumcryteker"
PASSWORD = "MKBA1MKBA1"
HOST = "maximumcryteker.mysql.pythonanywhere-services.com"
DBNAME = "maximumcryteker$mkba_database"

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{USERNAME}:{PASSWORD}@{HOST}/{DBNAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Table for questionnaire answers
class QuestionnaireResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    answers_json = db.Column(db.Text)  # store as JSON string

# Table for Stroop game results
class StroopResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey("questionnaire_response.id"), nullable=False)
    shape = db.Column(db.String(50))
    color = db.Column(db.String(50))
    key = db.Column(db.String(10))
    time = db.Column(db.Float)
    correct = db.Column(db.Boolean)

# Create tables if not exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return send_from_directory('static', 'stroop.html')

@app.route('/config/<path:filename>')
def send_config(filename):
    return send_from_directory('config', filename)

@app.route("/upload_all", methods=["POST"])
def upload_all():
    data = request.get_json()
    questionnaire = data.get("questionnaire", {})
    results = data.get("results", [])

    # Save questionnaire answers
    q_entry = QuestionnaireResponse(
        timestamp=datetime.now().isoformat(),
        answers_json=json.dumps(questionnaire, ensure_ascii=False)
    )
    db.session.add(q_entry)
    db.session.commit()  # commit so q_entry.id is available

    # Save Stroop results linked to questionnaire
    for r in results:
        entry = StroopResult(
            questionnaire_id=q_entry.id,
            shape=r.get("shape"),
            color=r.get("color"),
            key=r.get("key"),
            time=r.get("time"),
            correct=r.get("correct")
        )
        db.session.add(entry)

    db.session.commit()
    return jsonify({"status": "success", "questionnaire_id": q_entry.id}), 201

@app.route("/export-csv")
def export_csv():
    responses = QuestionnaireResponse.query.all()

    # Get all unique questionnaire question keys
    all_questions = set()
    max_game_trials = 0
    stroop_by_qid = {}  # Map questionnaire_id -> list of trials

    for r in responses:
        # Parse questionnaire
        try:
            ans = json.loads(r.answers_json) if r.answers_json else {}
            all_questions.update(ans.keys())
        except Exception as e:
            print(f"Error parsing answers for row {r.id}: {e}")
            ans = {}

        # Fetch stroop results linked to this questionnaire
        trials = StroopResult.query.filter_by(questionnaire_id=r.id).all()
        stroop_by_qid[r.id] = trials
        max_game_trials = max(max_game_trials, len(trials))

    all_questions = sorted(all_questions)

    # Create CSV headers
    headers = ["id", "timestamp"] + all_questions
    for i in range(1, max_game_trials + 1):
        headers += [
            f"trial{i}_shape",
            f"trial{i}_color",
            f"trial{i}_key",
            f"trial{i}_time",
            f"trial{i}_correct"
        ]

    # Write CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)

    for r in responses:
        ans = json.loads(r.answers_json) if r.answers_json else {}
        row = [r.id, r.timestamp]
        row += [ans.get(q, "") for q in all_questions]

        trials = stroop_by_qid.get(r.id, [])
        for i in range(max_game_trials):
            if i < len(trials):
                t = trials[i]
                row += [t.shape, t.color, t.key, t.time, t.correct]
            else:
                row += ["", "", "", "", ""]

        writer.writerow(row)

    csv_data = output.getvalue()
    output.close()

    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=combined_results_{date}.csv"}
    )

if __name__ == "__main__":
    app.run()
