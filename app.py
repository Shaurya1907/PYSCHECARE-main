"""
Main application file for PsycheCare Chat API.
"""

import base64
import hashlib
import hmac
import os
import time
from urllib.parse import urlparse
import socket
import ipaddress
import requests
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

class SecurityError(Exception):
    pass

class SecureExternalAPIProxy:
    """
    A strictly isolated proxy handler designed to safely fetch external resources
    while explicitly blocking Server-Side Request Forgery (SSRF) attacks.
    """
    def __init__(self):
        self.allowed_domains = ["api.mentalhealth.org", "cdn.pyschecare.com", "oauth.google.com"]
        self.timeout = 5
        
    def _resolve_and_validate_ip(self, hostname: str) -> bool:
        """
        Resolves the hostname and checks if the resulting IP is internal/private.
        """
        try:
            ip_str = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip_str)
            # Block all loopback, private, and reserved IP ranges
            if ip_obj.is_loopback or ip_obj.is_private or ip_obj.is_reserved:
                return False
            return True
        except socket.gaierror:
            return False

    def fetch_resource(self, url: str):
        """
        Safely fetches a resource after comprehensive URL validation.
        """
        if not url or not isinstance(url, str):
            raise ValueError("Invalid URL provided to the proxy.")
            
        parsed = urlparse(url)
        
        # 1. Enforce HTTPS only
        if parsed.scheme != "https":
            logging.error(f"SSRF Blocked: Attempted to use non-HTTPS scheme '{parsed.scheme}'")
            raise SecurityError("Only HTTPS URLs are permitted.")
            
        hostname = parsed.hostname
        if not hostname:
            raise SecurityError("Malformed URL structure.")
            
        # 2. Domain Allowlisting
        if hostname not in self.allowed_domains:
            logging.error(f"SSRF Blocked: Domain '{hostname}' is not in the trusted allowlist.")
            raise SecurityError("Access to the requested domain is strictly forbidden.")
            
        # 3. DNS Resolution & Private IP Blacklisting
        if not self._resolve_and_validate_ip(hostname):
            logging.error(f"SSRF Blocked: Domain '{hostname}' resolves to an internal or private IP address.")
            raise SecurityError("Access to internal network resources is blocked.")
            
        try:
            # 4. Enforce strict timeouts and prevent redirects to internal IPs
            response = requests.get(url, timeout=self.timeout, allow_redirects=False)
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"External API proxy failed to fetch resource: {str(e)}")
            raise

secure_api_proxy = SecureExternalAPIProxy()


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
