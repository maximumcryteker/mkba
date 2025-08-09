from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define a simple model (optional)
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.Text)

@app.route('/')
def index():
    return "Hello, your Flask app is running!"

@app.route('/save-results', methods=['POST'])
def save_results():
    data = request.get_json()
    # Just print or save the data to DB here
    result = Result(data=str(data))
    db.session.add(result)
    db.session.commit()
    return jsonify({"message": "Results saved"}), 200

if __name__ == "__main__":
    app.run(debug=True)
