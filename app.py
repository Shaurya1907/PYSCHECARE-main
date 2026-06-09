import hmac
import hashlib
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from chatbot_integration import get_chatbot_response
from crisis_detection import detect_crisis_risk, log_crisis_event

app = Flask(__name__)
# ── Global Payload Size Limit ────────────────────────────────────────────────
# Prevent memory exhaustion attacks across the entire app by rejecting payloads
# larger than 5KB (default Flask allows unlimited payload sizes).
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024

# ── CORS ────────────────────────────────────────────────────────────────────
# Read allowed origin from environment variable — fail closed if not set
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN")
if not ALLOWED_ORIGIN:
    raise ValueError(
        "CRITICAL: ALLOWED_ORIGIN environment variable is not set! "
        "Refusing to start with insecure CORS."
    )
CORS(app, origins=[ALLOWED_ORIGIN])

@app.before_request
def verify_origin():
    """Harden CORS by rejecting requests missing or disallowed Origin header."""
    origin = request.headers.get("Origin")
    if not origin:
        return jsonify({"error": "Missing Origin header"}), 403
    if origin != ALLOWED_ORIGIN:
        return jsonify({"error": "Origin not allowed"}), 403

# ── Rate limiting ────────────────────────────────────────────────────────────
limiter = Limiter(get_remote_address, app=app, default_limits=["30 per minute"])

# ── Shared secret for chat token validation ──────────────────────────────────
# Must match the value set in chatBot.php (CHAT_API_SECRET env var).
# If not set, the endpoint refuses ALL requests — fail closed.
CHAT_API_SECRET = os.environ.get("CHAT_API_SECRET", "")


import base64

def _verify_chat_token(token: str) -> str:
    """
    Validate the HMAC chat token and return the extracted session ID.
    Token format: base64(session_id|username).hmac_sha256
    """
    if not CHAT_API_SECRET:
        return None  # Fail closed
    
    if not token or '.' not in token:
        return None
        
    try:
        payload, signature = token.split('.', 1)
        expected_sig = hmac.new(
            CHAT_API_SECRET.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_sig, signature):
            return None
            
        decoded_payload = base64.b64decode(payload).decode('utf-8')
        session_id, username = decoded_payload.split('|', 1)
        return session_id
    except Exception:
        return None


@app.route("/chat", methods=["POST"])
@limiter.limit("30 per minute")
def chat():
    # ── Authentication check ─────────────────────────────────────────────────
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()

    user_id = _verify_chat_token(token)
    if not user_id:
        return jsonify({
            "error": "Unauthorized. Please log in to use the chatbot."
        }), 401

    # ── Payload validation ───────────────────────────────────────────────────
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing message"}), 400

    # ── Advanced: Algorithmic Complexity DoS Protection ──────────────────────
    # NLTK tokenization and the autocorrect Speller() are computationally heavy.
    # An extremely long input will hang the server (ReDoS / exhaustion attack).
    # We enforce a strict 500-character limit per message.
    # Advanced: Algorithmic Complexity DoS Protection
    message = data["message"]
    if not isinstance(message, str) or len(message) > 500:
        return jsonify({
            "error": "Message too long. Maximum length is 500 characters."
        }), 400

    # Use session ID from request or generate a unique one
    user_id = data.get("session_id") or str(uuid.uuid4())

    risk = detect_crisis_risk(data["message"])
    log_crisis_event(risk, user_id)

    response = get_chatbot_response(data["message"], user_id)
    return jsonify({"response": response, "session_id": user_id, "risk": risk})


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
