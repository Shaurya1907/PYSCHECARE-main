from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import random

app = Flask(__name__)

@app.route('/dashboard/mood')
def mood_dashboard():
    return render_template('mood_dashboard.html')

@app.route('/api/mood-data', methods=['GET'])
def get_mood_data():
    print("API called - generating dummy data")
    moods = ['happy', 'sad', 'angry', 'anxious', 'neutral', 'excited']
    data = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        data.append({
            'date': date,
            'mood': random.choice(moods),
            'intensity': random.randint(1, 10),
            'note': f'Feeling {random.choice(moods)} on {date}'
        })
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
