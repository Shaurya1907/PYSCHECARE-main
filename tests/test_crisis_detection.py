import json

from crisis_detection import detect_crisis_risk, log_crisis_event


def test_low_risk_message():
    risk = detect_crisis_risk("I had a calm day and want to talk.")

    assert risk["level"] == "LOW"
    assert risk["detected_keywords"] == []


def test_moderate_risk_message():
    risk = detect_crisis_risk("I feel hopeless lately.")

    assert risk["level"] == "MODERATE"
    assert risk["detected_keywords"] == ["hopeless"]


def test_high_risk_message():
    risk = detect_crisis_risk("I want to hurt myself tonight.")

    assert risk["level"] == "HIGH"
    assert risk["detected_keywords"] == ["hurt myself"]


def test_critical_risk_message():
    risk = detect_crisis_risk("I might kill myself.")

    assert risk["level"] == "CRITICAL"
    assert risk["detected_keywords"] == ["kill myself"]


def test_crisis_event_logging(tmp_path):
    log_path = tmp_path / "crisis_events.json"
    risk = detect_crisis_risk("I am thinking about suicide.")

    log_crisis_event(risk, "session-123", log_path)

    events = json.loads(log_path.read_text(encoding="utf-8"))
    assert len(events) == 1
    assert events[0]["risk_level"] == "CRITICAL"
    assert events[0]["detected_keywords"] == ["suicide"]
    assert events[0]["session_id"] == "session-123"
    assert "timestamp" in events[0]


def test_multilingual_crisis_messages():
    # Spanish crisis detection
    risk_es = detect_crisis_risk("Quiero suicidarme hoy.")
    assert risk_es["level"] == "CRITICAL"
    assert "suicidarme" in risk_es["detected_keywords"]

    # French crisis detection
    risk_fr = detect_crisis_risk("Je veux me suicider ce soir.")
    assert risk_fr["level"] == "CRITICAL"
    assert "suicider" in risk_fr["detected_keywords"]

    # Hindi crisis detection
    risk_hi = detect_crisis_risk("मैं खुद को मारना चाहता हूँ।")
    assert risk_hi["level"] == "CRITICAL"
    assert "खुद को मारना" in risk_hi["detected_keywords"]

