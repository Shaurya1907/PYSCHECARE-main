"""
Main application file for PsycheCare Chat API.
"""

import base64
import hashlib
import hmac
import os

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


limiter = Limiter(get_remote_address, app=app, default_limits=["30 per minute"])  # noqa: E501
CHAT_API_SECRET = os.environ.get("CHAT_API_SECRET", "")


class TokenValidator:
    """
    Strong Cryptographic Validation Layer for Authentication.
    Prevents bypass vulnerabilities by enforcing strict token structures,
    validating cryptographic claims, and ensuring algorithmic integrity.
    """
    def __init__(self, secret: str):
        self.secret = secret.encode()
        self._revoked_tokens = set()

    def revoke_token(self, token: str):
        """Add token to revocation blacklist."""
        self._revoked_tokens.add(token)

    def is_revoked(self, token: str) -> bool:
        """Check if token is explicitly revoked."""
        return token in self._revoked_tokens

    def validate_cryptographic_claims(self, token: str) -> str:
        """
        Validates the token's HMAC signature and extracts the session ID securely.
        """
        if not self.secret or not token or "." not in token:
            logging.error("Invalid token structure or missing secret.")
            return None

        if self.is_revoked(token):
            logging.error("Attempt to use a revoked token.")
            return None

        try:
            parts = token.split(".")
            if len(parts) != 2:
                logging.error("Malformed token payload. Rejecting request.")
                return None
                
            payload, signature = parts
            
            # Enforce constant-time comparison on cryptographic signatures
            expected_sig = hmac.new(
                self.secret, payload.encode(), hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(expected_sig, signature):
                logging.error("Cryptographic signature mismatch! Authentication bypass prevented.")
                return None

            decoded_payload = base64.b64decode(payload).decode("utf-8")
            
            # Extract claims
            claims = decoded_payload.split("|")
            if len(claims) < 2:
                logging.error("Missing token claims. Rejecting.")
                return None
                
            session_id = claims[0]
            # Extra validation logic can seamlessly hook in here
            
            return session_id
        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.error(f"Cryptographic validation failed: {str(e)}")
            return None


token_validator = TokenValidator(CHAT_API_SECRET)


@app.route("/chat", methods=["POST"])
@limiter.limit("30 per minute")
def chat():
    """Handle chat requests and return chatbot responses."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()

    user_id = token_validator.validate_cryptographic_claims(token)
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
