"""
Main application file for PsycheCare Chat API.
"""

import base64
import hashlib
import hmac
import os

from flask import Flask, jsonify, request, session, redirect
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# from chatbot_integration import get_chatbot_response  # temporarily disabled
from crisis_detection import detect_crisis_risk, log_crisis_event
from validation import validate_chat_payload

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024

ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN")
if not ALLOWED_ORIGIN:
    raise ValueError(
        "CRITICAL: ALLOWED_ORIGIN environment variable is not set! "
        "Refusing to start with insecure CORS."
    )
CORS(app, origins=[ALLOWED_ORIGIN])


@app.before_request
def verify_origin():
    """Verify that the Origin header matches ALLOWED_ORIGIN."""
    origin = request.headers.get("Origin")
    if not origin:
        return jsonify({"error": "Missing Origin header"}), 403
    if origin != ALLOWED_ORIGIN:
        return jsonify({"error": "Origin not allowed"}), 403
    return None


limiter = Limiter(
    get_remote_address, app=app, default_limits=["30 per minute"]
)  # noqa: E501
CHAT_API_SECRET = os.environ.get("CHAT_API_SECRET", "")


def _verify_chat_token(token: str) -> str:
    """Validate chat token and return session ID."""
    if not CHAT_API_SECRET or not token or "." not in token:
        return None

    try:
        payload, signature = token.split(".", 1)
        expected_sig = hmac.new(
            CHAT_API_SECRET.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_sig, signature):
            return None

        decoded_payload = base64.b64decode(payload).decode("utf-8")
        session_id, _ = decoded_payload.split("|", 1)
        return session_id
    except Exception:  # pylint: disable=broad-exception-caught
        return None


@app.route("/chat", methods=["POST"])
@limiter.limit("30 per minute")
def chat():
    """Handle chat requests and return chatbot responses."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()

    user_id = _verify_chat_token(token)
    if not user_id:
        return (
            jsonify(
                {"error": "Unauthorized. Please log in to use the chatbot."}
            ),  # noqa: E501
            401,
        )

    data = request.get_json(silent=True)
    validation_error = validate_chat_payload(data)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    risk = detect_crisis_risk(data["message"])
    log_crisis_event(risk, user_id)

    response = "Chatbot temporarily disabled"
    return jsonify({"response": response, "session_id": user_id, "risk": risk})


@app.errorhandler(413)
def payload_too_large(_error):
    """Handle 413 error."""
    return jsonify({"error": "Request body is too large."}), 413


@app.errorhandler(400)
def bad_request(_error):
    """Handle 400 Bad Request error."""
    return jsonify({"error": "Invalid request."}), 400


# ========== MOOD ANALYTICS API (Issue #320) ==========
@app.route('/api/mood-history', methods=['GET'])
def get_mood_history():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    
    # Example SQLite query – adjust your database name and table/columns
    import sqlite3
    conn = sqlite3.connect('your_database.db')   # change to your actual DB
    cursor = conn.cursor()
    
    query = "SELECT date, mood, rating FROM mood_entries WHERE 1=1"
    params = []
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    query += " ORDER BY date ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    data = [{'date': row[0], 'mood': row[1], 'rating': row[2]} for row in rows]
    return jsonify(data)
if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    # Provide a warning that app.run is insecure for production
    import logging

    logging.warning(
        "You are using the development server. For production, "
        "use wsgi.py to ensure bounded thread scaling and "
        "prevent memory leaks."
    )
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)

from datetime import datetime, timedelta

@app.route('/api/mood-data', methods=['GET'])
def get_mood_data():
    """Fetch mood entries (replace with your actual DB query)"""
    import random
# --- DUMMY DATA - REPLACE WITH YOUR MODEL ---
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
    # --- END DUMMY ---
    return jsonify(data)

@app.route('/dashboard/mood')
def mood_dashboard():
    return render_template('mood_dashboard.html')

@app.route('/api/mood-data', methods=['GET'])
def get_mood_data():
    """Fetch mood entries (replace with your actual DB query)"""
    import random
# --- DUMMY DATA - REPLACE WITH YOUR MODEL ---
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
    # --- END DUMMY ---
    return jsonify(data)

@app.route('/dashboard/mood')
def mood_dashboard():
    return render_template('mood_dashboard.html')








@app.route('/test-login')
def test_login():
    from flask import session, redirect
    # Set a dummy user ID (use 1 or any valid ID)
    session['user_id'] = 1
    return redirect('/dashboard/mood')
