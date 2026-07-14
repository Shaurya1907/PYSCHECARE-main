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
from werkzeug.middleware.proxy_fix import ProxyFix

from chatbot_integration import get_chatbot_response
from crisis_detection import detect_crisis_risk, log_crisis_event
from validation import validate_chat_payload

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
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

# ================================================================
# APPOINTMENT ROUTES
# Implements: POST /api/appointment/book
#             GET  /api/appointment/my
#             PUT  /api/appointment/<id>/cancel
#             GET  /api/appointment/therapists
# ================================================================

from datetime import datetime, timedelta

@app.route('/api/appointment/therapists', methods=['GET'])
def get_therapists():
    """
    Returns all active therapists for the booking dropdown.
    This endpoint is public (no login required) so the booking page
    can populate the therapist list before the user logs in.
    """
    # Adapt to your existing DB helper
    # therapists = db.execute("SELECT id, name, specialty FROM therapists WHERE is_active = 1")
    # return jsonify({'therapists': therapists})

    # Placeholder until DB is wired:
    sample_therapists = [
        {'id': 1, 'name': 'Dr. Priya Sharma',  'specialty': 'Anxiety & Depression'},
        {'id': 2, 'name': 'Dr. Arjun Mehta',   'specialty': 'Trauma & PTSD'},
        {'id': 3, 'name': 'Dr. Sunita Rao',    'specialty': 'Relationship Counselling'},
        {'id': 4, 'name': 'Dr. Kavya Nair',    'specialty': 'Youth Mental Health'},
    ]
    return jsonify({'therapists': sample_therapists})


@app.route('/api/appointment/book', methods=['POST'])
def book_appointment():
    """
    Books a therapy appointment for the logged-in user.

    Expected JSON body:
    {
        "therapist_id": 1,
        "appointment_date": "2025-09-15",
        "appointment_time": "14:00",
        "session_type": "video",
        "notes": "First session, feeling anxious about opening up"
    }
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required. Please log in.'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # ── Validate required fields ──────────────────────────────────
    required_fields = ['therapist_id', 'appointment_date', 'appointment_time', 'session_type']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({
            'error': f'Missing required fields: {", ".join(missing)}'
        }), 400

    # ── Validate session type ─────────────────────────────────────
    valid_types = {'video', 'audio', 'text'}
    if data['session_type'] not in valid_types:
        return jsonify({
            'error': f'Invalid session_type. Must be one of: {", ".join(valid_types)}'
        }), 400

    # ── Parse and validate appointment datetime ───────────────────
    try:
        appt_dt_str = f"{data['appointment_date']} {data['appointment_time']}"
        appt_dt     = datetime.strptime(appt_dt_str, '%Y-%m-%d %H:%M')
    except ValueError:
        return jsonify({
            'error': 'Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time.'
        }), 400

    now = datetime.utcnow()

    # Must be in the future
    if appt_dt <= now:
        return jsonify({'error': 'Appointment must be scheduled in the future.'}), 400

    # Cannot book more than 90 days ahead
    if appt_dt > now + timedelta(days=90):
        return jsonify({'error': 'Cannot book more than 90 days in advance.'}), 400

    # Must be within business hours (8 AM – 9 PM)
    if not (8 <= appt_dt.hour < 21):
        return jsonify({'error': 'Appointments must be between 8:00 AM and 9:00 PM.'}), 400

    # ── Validate therapist_id is a positive integer ───────────────
    try:
        therapist_id = int(data['therapist_id'])
        if therapist_id <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid therapist_id.'}), 400

    # ── Truncate notes to 500 characters ─────────────────────────
    notes = str(data.get('notes', '')).strip()[:500]

    # ── Build appointment record ──────────────────────────────────
    appointment = {
        'user_id':               session['user_id'],
        'therapist_id':          therapist_id,
        'appointment_datetime':  appt_dt.strftime('%Y-%m-%d %H:%M:%S'),
        'session_type':          data['session_type'],
        'notes':                 notes,
        'status':                'pending',
        'created_at':            now.strftime('%Y-%m-%d %H:%M:%S'),
    }

    # ── Save to database ──────────────────────────────────────────
    # Uncomment and adapt when DB layer is available:
    #
    # try:
    #     cursor = db.execute(
    #         """INSERT INTO appointments
    #            (user_id, therapist_id, appointment_datetime, session_type, notes, status)
    #            VALUES (%s, %s, %s, %s, %s, 'pending')""",
    #         (appointment['user_id'], appointment['therapist_id'],
    #          appointment['appointment_datetime'], appointment['session_type'],
    #          appointment['notes'])
    #     )
    #     appointment['id'] = cursor.lastrowid
    #     db.commit()
    # except IntegrityError:
    #     return jsonify({
    #         'error': 'This time slot is already booked. Please choose another time.'
    #     }), 409

    return jsonify({
        'success':     True,
        'message':     'Appointment booked successfully! You will receive a confirmation shortly.',
        'appointment': appointment,
    }), 201


@app.route('/api/appointment/my', methods=['GET'])
def get_my_appointments():
    """
    Returns all upcoming appointments for the logged-in user.
    Query params:
        include_past=true  — also return past appointments
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required.'}), 401

    include_past = request.args.get('include_past', 'false').lower() == 'true'

    # Uncomment when DB is available:
    #
    # query = """
    #     SELECT a.*, t.name AS therapist_name, t.specialty
    #     FROM appointments a
    #     JOIN therapists t ON a.therapist_id = t.id
    #     WHERE a.user_id = %s
    # """
    # params = [session['user_id']]
    # if not include_past:
    #     query += " AND a.appointment_datetime > NOW()"
    # query += " ORDER BY a.appointment_datetime ASC"
    # appointments = db.execute(query, params).fetchall()

    return jsonify({
        'appointments': [],   # Replace [] with query results when DB is wired
        'count':        0,
    })


@app.route('/api/appointment/<int:appt_id>/cancel', methods=['PUT'])
def cancel_appointment(appt_id):
    """
    Cancels a specific appointment.
    Users can only cancel their own appointments.
    Cancellation is not allowed within 2 hours of the appointment.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required.'}), 401

    data = request.get_json() or {}
    cancellation_reason = str(data.get('reason', '')).strip()[:500]

    # Uncomment when DB is available:
    #
    # appt = db.execute(
    #     "SELECT * FROM appointments WHERE id = %s AND user_id = %s",
    #     (appt_id, session['user_id'])
    # ).fetchone()
    #
    # if not appt:
    #     return jsonify({'error': 'Appointment not found.'}), 404
    #
    # if appt['status'] in ('cancelled', 'completed'):
    #     return jsonify({'error': f'Appointment is already {appt["status"]}.'}), 400
    #
    # appt_dt = datetime.strptime(str(appt['appointment_datetime']), '%Y-%m-%d %H:%M:%S')
    # if appt_dt - datetime.utcnow() < timedelta(hours=2):
    #     return jsonify({
    #         'error': 'Cannot cancel an appointment within 2 hours of the session start time.'
    #     }), 400
    #
    # db.execute(
    #     "UPDATE appointments SET status = 'cancelled', cancellation_reason = %s WHERE id = %s",
    #     (cancellation_reason, appt_id)
    # )
    # db.commit()

    return jsonify({
        'success': True,
        'message': 'Appointment cancelled successfully.',
        'appointment_id': appt_id,
    })


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
