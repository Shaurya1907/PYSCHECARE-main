import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from chatbot_integration import get_chatbot_response

app = Flask(__name__)

# ── CORS ────────────────────────────────────────────────────────────────────
# Read allowed origin from environment variable — never hardcode or use wildcard
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "http://localhost:3000")
CORS(app, origins=[ALLOWED_ORIGIN])

# ── Rate limiting ────────────────────────────────────────────────────────────
limiter = Limiter(get_remote_address, app=app, default_limits=["30 per minute"])

@app.route("/chat", methods=["POST"])
@limiter.limit("30 per minute")
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing message"}), 400
    
    # Use session ID from request or generate a unique one
    user_id = data.get("session_id") or str(uuid.uuid4())
    
    response = get_chatbot_response(data["message"], user_id)
    return jsonify({"response": response, "session_id": user_id})

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
