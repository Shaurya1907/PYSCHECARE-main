import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path


RISK_LEVELS = ("LOW", "MODERATE", "HIGH", "CRITICAL")

RISK_PHRASES = {
    "MODERATE": [
        # English
        "depressed",
        "hopeless",
        "panic attack",
        "worthless",
        # Spanish
        "deprimido",
        "deprimida",
        "sin esperanza",
        "desesperado",
        "desesperada",
        "ataque de pánico",
        # French
        "déprimé",
        "déprimée",
        "sans espoir",
        "désespéré",
        "désespérée",
        "crise de panique",
        # Hindi
        "उदास",
        "निराश",
        "हताश",
        "तनाव",
        "घबराहट",
    ],
    "HIGH": [
        # English
        "self harm",
        "hurt myself",
        "cut myself",
        "want to die",
        # Spanish
        "hacerme daño",
        "lastimarme",
        "cortarme",
        "querer morir",
        "quiero morir",
        # French
        "me faire du mal",
        "me blesser",
        "me couper",
        "vouloir mourir",
        "veux mourir",
        # Hindi
        "चोट पहुंचाना",
        "नुकसान पहुंचाना",
        "मरना चाहता",
        "मरना चाहती",
    ],
    "CRITICAL": [
        # English
        "kill myself",
        "end my life",
        "suicide",
        "overdose",
        # Spanish
        "suicidarme",
        "suicidarse",
        "suicidio",
        "matarme",
        "quitarme la vida",
        # French
        "me suicider",
        "se suicider",
        "suicide",
        "me tuer",
        "mettre fin à mes jours",
        # Hindi
        "आत्महत्या",
        "सुसाइड",
        "खुद को मारना",
        "जान दे देना",
        "जान देना",
    ],
}

DEFAULT_EVENT_LOG = Path(__file__).resolve().parent / "crisis_events.json"
_crisis_log_lock = threading.Lock()


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
        path.write_text(json.dumps(events, indent=2), encoding="utf-8")
