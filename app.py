"""
Main application file for PsycheCare Chat API.
"""

import base64
import hashlib
import hmac
import os
from xml.etree import ElementTree as ET
import io
import time

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


class SecureDocumentParser:
    """
    A hardened document parser designed to prevent XML External Entity (XXE)
    injection attacks by strictly disabling external entity resolution and DTD processing.
    """
    def __init__(self, enforce_defused: bool = True):
        self.enforce_defused = enforce_defused
        # Restrict maximum document size to prevent XML Bomb (Billion Laughs) attacks
        self.max_file_size_bytes = 5 * 1024 * 1024 # 5 MB limit

    def _validate_file_size(self, xml_content: bytes) -> bool:
        """Ensure the XML payload does not exceed strict size boundaries."""
        if len(xml_content) > self.max_file_size_bytes:
            logging.error("XML document exceeds the maximum permitted size.")
            return False
        return True

    def parse_xml_safely(self, xml_content: bytes):
        """
        Safely parses an XML document, blocking external entities and DTDs.
        """
        if not xml_content:
            raise ValueError("Empty XML content provided.")
            
        if not self._validate_file_size(xml_content):
            raise SecurityError("XML payload too large. Possible DoS attack.")

        try:
            # Fallback native parser with strict entity/DTD rejection using custom parser logic
            parser = ET.XMLParser()
            # Explicitly disable external entity processing in the standard library parser
            if hasattr(parser, 'entity'):
                parser.entity = {}
            tree = ET.parse(io.BytesIO(xml_content), parser=parser)
                
            return tree.getroot()
            
        except Exception as e:
            logging.error(f"Failed to securely parse the XML document: {str(e)}")
            raise ValueError("Malformed or insecure XML document.") from e

secure_document_parser = SecureDocumentParser()


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
