from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# PythonAnywhere MySQL config
USERNAME = "maximumcryteker"
PASSWORD = "MKBA1MKBA1"
HOST = "maximumcryteker.mysql.pythonanywhere-services.com"
DBNAME = "maximumcryteker$mkba_database"

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DBNAME}"
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

@app.route("/upload_all", methods=["POST"])
def upload_all():
    data = request.get_json()
    questionnaire = data.get("questionnaire", {})
    results = data.get("results", [])

    # Save questionnaire answers
    q_entry = QuestionnaireResponse(answers_json=str(questionnaire))
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

if __name__ == "__main__":
    app.run()
