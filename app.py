"""
Main application file for PsycheCare Chat API.
"""

import base64
import hashlib
import hmac
import os
import sqlite3
import math

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from chatbot_integration import get_chatbot_response
from crisis_detection import detect_crisis_risk, log_crisis_event
from validation import validate_chat_payload

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.sqlite")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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

    response = get_chatbot_response(data["message"], user_id)

    # Save to chat_history
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_messages (user_id, sender, message) VALUES (?, ?, ?)",
            (user_id, "user", data["message"])
        )
        cursor.execute(
            "INSERT INTO chat_messages (user_id, sender, message) VALUES (?, ?, ?)",
            (user_id, "bot", response)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        app.logger.error(f"Failed to save chat history: {e}")

    return jsonify({"response": response, "session_id": user_id, "risk": risk})

@app.route("/chat/history", methods=["GET"])
@limiter.limit("30 per minute")
def chat_history():
    """Retrieve paginated chat history for the logged-in user."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()

    user_id = _verify_chat_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        if page < 1 or limit < 1:
            return jsonify({"error": "Invalid pagination parameters"}), 400
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    offset = (page - 1) * limit

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get total items
        cursor.execute("SELECT COUNT(*) FROM chat_messages WHERE user_id = ?", (user_id,))
        total_items = cursor.fetchone()[0]
        
        # Get messages for the page (ordered by created_at DESC to get newest first, then we can reverse if needed)
        # Usually history is loaded newest first for pagination, but displayed oldest first.
        cursor.execute(
            "SELECT id, sender, message, created_at FROM chat_messages WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (user_id, limit, offset)
        )
        rows = cursor.fetchall()
        conn.close()

        messages = [dict(row) for row in rows]
        
        total_pages = math.ceil(total_items / limit) if total_items > 0 else 1

        return jsonify({
            "data": messages,
            "meta": {
                "currentPage": page,
                "pageSize": limit,
                "totalItems": total_items,
                "totalPages": total_pages,
                "hasNextPage": page < total_pages,
                "hasPreviousPage": page > 1
            }
        })

    except Exception as e:
        app.logger.error(f"Database error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(413)
def payload_too_large(_error):
    """Handle 413 error."""
    return jsonify({"error": "Request body is too large."}), 413


@app.errorhandler(400)
def bad_request(_error):
    """Handle 400 Bad Request error."""
    return jsonify({"error": "Invalid request."}), 400


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
