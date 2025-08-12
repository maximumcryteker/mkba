import os
import json
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
    timestamp = db.Column(db.String(50))
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
    
    # Get all unique question keys from all rows
    all_questions = set()
    for r in responses:
        ans = json.loads(r.answers_json)
        all_questions.update(ans.keys())
    all_questions = sorted(all_questions)

    # Create CSV dynamically
    def generate():
        # header
        yield ",".join(["id", "timestamp"] + all_questions) + "\n"
        # rows
        for r in responses:
            ans = json.loads(r.answers_json)
            row = [str(r.id), r.timestamp] + [ans.get(q, "") for q in all_questions]
            yield ",".join(row) + "\n"

    date = datetime.now()
    return Response(generate(), mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=combined_results_{date}.csv"})

if __name__ == "__main__":
    app.run()
