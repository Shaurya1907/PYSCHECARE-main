"""
Main application file for PsycheCare Chat API.
"""

import base64
import hashlib
import hmac
import time
import json
import os
import logging

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from chatbot_integration import get_chatbot_response
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

class SecureSessionManager:
    """
    Prevents Insecure Deserialization by utilizing strict JSON parsing
    with cryptographic signature verification, completely avoiding the use
    of unsafe native serialization methods like Python's `pickle`.
    """
    def __init__(self, secret_key: str):
        if not secret_key or len(secret_key) < 32:
            logging.warning("A strong cryptographic key is recommended for secure session management.")
        self.secret_key = secret_key.encode('utf-8')
        
    def _sign_payload(self, payload: str) -> str:
        """Generates an HMAC-SHA256 signature for the session payload."""
        return hmac.new(self.secret_key, payload.encode('utf-8'), hashlib.sha256).hexdigest()

    def serialize_session(self, state: dict) -> str:
        """
        Safely serializes the session state to JSON and attaches a cryptographic signature.
        """
        if not isinstance(state, dict):
            raise TypeError("Session state must be a dictionary.")
            
        # Inject timestamp to enforce session expiration at the data layer
        state['_issued_at'] = int(time.time())
        
        # Use secure JSON serialization, avoiding unsafe pickle objects
        json_payload = json.dumps(state, separators=(',', ':'))
        encoded_payload = base64.b64encode(json_payload.encode('utf-8')).decode('utf-8')
        
        signature = self._sign_payload(encoded_payload)
        return f"{encoded_payload}.{signature}"

    def deserialize_session(self, token: str, max_age_seconds: int = 3600) -> dict:
        """
        Safely reconstructs the session state only after cryptographic verification
        and strict JSON structural validation.
        """
        if not token or "." not in token:
            logging.error("Invalid session token format.")
            return {}
            
        try:
            encoded_payload, signature = token.split(".", 1)
            expected_signature = self._sign_payload(encoded_payload)
            
            # Constant-time comparison prevents timing attacks
            if not hmac.compare_digest(expected_signature, signature):
                logging.error("Session signature mismatch! Possible tampering detected.")
                return {}
                
            json_payload = base64.b64decode(encoded_payload).decode('utf-8')
            
            # Strictly use JSON parser; never evaluate or unpickle the payload
            state = json.loads(json_payload)
            
            if not isinstance(state, dict):
                logging.error("Invalid session structure decoded.")
                return {}
                
            issued_at = state.get('_issued_at', 0)
            if int(time.time()) - issued_at > max_age_seconds:
                logging.warning("Session token has expired.")
                return {}
                
            return state
            
        except (ValueError, json.JSONDecodeError, TypeError) as e:
            logging.error(f"Insecure deserialization attempt prevented: {str(e)}")
            return {}

secure_session_manager = SecureSessionManager(os.environ.get("CHAT_API_SECRET", "fallback_secret_must_be_thirty_two_chars_long"))

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
    return jsonify({"response": response, "session_id": user_id, "risk": risk})


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
