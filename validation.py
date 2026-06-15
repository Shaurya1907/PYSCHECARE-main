MAX_CHAT_MESSAGE_LENGTH = 500
MAX_SESSION_ID_LENGTH = 128


def required(value):
    return isinstance(value, str) and value.strip() != ""


def max_length(value, limit):
    return isinstance(value, str) and len(value) <= limit


def validate_chat_payload(data):
    if not isinstance(data, dict):
        return "Request body must be valid JSON."

    message = data.get("message")
    if not isinstance(message, str):
        return "Message is required."
    if not required(message):
        return "Message cannot be empty."
    if not max_length(message, MAX_CHAT_MESSAGE_LENGTH):
        return f"Message must be {MAX_CHAT_MESSAGE_LENGTH} characters or fewer."

    session_id = data.get("session_id")
    if session_id is not None and (
        not isinstance(session_id, str) or not max_length(session_id, MAX_SESSION_ID_LENGTH)
    ):
        return f"Session ID must be {MAX_SESSION_ID_LENGTH} characters or fewer."

    return None
