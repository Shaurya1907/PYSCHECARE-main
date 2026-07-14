import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path


RISK_LEVELS = ("LOW", "MODERATE", "HIGH", "CRITICAL")

RISK_PHRASES = {
    "MODERATE": [
        "depressed",
        "hopeless",
        "panic attack",
        "worthless",
    ],
    "HIGH": [
    "self harm",
    "hurt myself",
    "cut myself",
    "want to die",

    # Hindi
    "मरना चाहता हूँ",

    # Spanish
    "quiero morir",

    # French
    "je veux mourir",
   ],
    "CRITICAL": [
    "kill myself",
    "end my life",
    "suicide",
    "overdose",

    # Spanish
    "quiero suicidarme",

    # French
    "je veux me suicider",

    # Hindi
    "मैं खुद को मारना चाहता हूँ",
    "आत्महत्या",
    ],
}

DEFAULT_EVENT_LOG = Path(__file__).resolve().parent / "crisis_events.json"
_crisis_log_lock = threading.Lock()

MAX_EVENTS = 10_000
def _matches_phrase(message: str, phrase: str) -> bool:
    phrase = phrase.lower().strip()
    if " " in phrase:
        return phrase in message
    return re.search(rf"\b{re.escape(phrase)}\b", message) is not None


def detect_crisis_risk(message: str) -> dict:
    """Return simple keyword-based crisis risk metadata for a user message."""
    normalized = (message or "").lower()
    matches_by_level = {
        level: [
            phrase
            for phrase in phrases
            if _matches_phrase(normalized, phrase)
        ]
        for level, phrases in RISK_PHRASES.items()
    }

    for level in ("CRITICAL", "HIGH", "MODERATE"):
        if matches_by_level[level]:
            return {
                "level": level,
                "detected_keywords": matches_by_level[level],
            }

    return {"level": "LOW", "detected_keywords": []}


def log_crisis_event(risk: dict, session_id: str, log_path: Path | str = DEFAULT_EVENT_LOG) -> None:
    """Append a minimal crisis event to a local JSON file."""
    if risk.get("level") == "LOW":
        return

    path = Path(log_path)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "risk_level": risk.get("level", "LOW"),
        "detected_keywords": risk.get("detected_keywords", []),
        "session_id": session_id,
    }

    with _crisis_log_lock:
        try:
            events = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
            if not isinstance(events, list):
                events = []
        except (json.JSONDecodeError, OSError):
            events = []

        events.append(event)
        events = events[-MAX_EVENTS:]
        path.write_text(json.dumps(events, indent=2), encoding="utf-8")

# ADD this function at the bottom of crisis_detection.py

def get_crisis_response_for_frontend(crisis_result: dict) -> dict:
    """
    Sanitizes crisis detection results before sending to the browser.

    NEVER expose the raw psychiatric classification label (e.g., 'suicidal_ideation')
    to the frontend. Only return a boolean flag and a pre-written support message.

    Args:
        crisis_result: Raw internal result from the crisis classifier

    Returns:
        dict: Safe response for browser consumption
    """
    if crisis_result.get('is_crisis', False):
        return {
            'needs_support': True,
            'support_message': (
                'It sounds like you\'re going through a really difficult time. '
                'You are not alone, and help is available right now.'
            ),
            'emergency_contacts': [
                {
                    'name': 'iCall (India)',
                    'number': '9152987821',
                    'hours': 'Mon–Sat, 8am–10pm'
                },
                {
                    'name': 'Vandrevala Foundation',
                    'number': '1860-2662-345',
                    'hours': '24/7'
                },
                {
                    'name': 'SNEHI',
                    'number': '044-24640050',
                    'hours': '24/7'
                },
            ],
            'show_sos_button': True,
            # NOTE: 'crisis_type', 'severity', 'classification' are
            # intentionally OMITTED — stored server-side only
        }

    return {
        'needs_support': False,
        'support_message': None,
        'show_sos_button': False,
    }


def log_crisis_event_server_side(user_id: int, crisis_type: str, severity: str) -> None:
    """
    Stores crisis classification in the database, accessible only to
    authorized healthcare staff. This function is called from app.py
    and the result is NEVER forwarded to the client.

    Args:
        user_id: ID of the user whose message triggered crisis detection
        crisis_type: Internal classification (e.g., 'suicidal_ideation') — server only
        severity: Severity level — server only
    """
    # TODO: implement encrypted DB write when DB layer is available
    # Example:
    # db.execute(
    #     "INSERT INTO crisis_events (user_id, crisis_type, severity, detected_at) "
    #     "VALUES (?, ?, ?, NOW())",
    #     (user_id, crisis_type, severity)
    # )
    import logging
    logger = logging.getLogger('psychecare.crisis')
    logger.warning(
        f"[CRISIS EVENT] user_id={user_id} "
        f"type={crisis_type} "
        f"severity={severity} "
        f"[stored server-side, not sent to client]"
    )