import os
import sys
import pytest
import base64
import hashlib
import hmac
from unittest.mock import MagicMock

# Create a mock for chatbot_integration and sys.modules
mock_chatbot = MagicMock()
mock_chatbot.get_chatbot_response.return_value = "Mock response"
sys.modules['chatbot_integration'] = mock_chatbot

# Set environment variable before importing app
os.environ["ALLOWED_ORIGIN"] = "http://localhost:3000"
os.environ["CHAT_API_SECRET"] = "test-secret"
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def auth_headers():
    payload = base64.b64encode(b"test-session|tester").decode("utf-8")
    signature = hmac.new(
        os.environ["CHAT_API_SECRET"].encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return {
        "Origin": "http://localhost:3000",
        "Authorization": f"Bearer {payload}.{signature}",
    }

def test_allow_explicit_origin(client):
    """Test that an explicitly allowed origin is accepted."""
    response = client.post('/chat', 
                          json={'message': 'hello'},
                          headers=auth_headers())
    assert response.status_code == 200

def test_reject_missing_origin(client):
    """Test that requests missing the Origin header are rejected."""
    response = client.post('/chat', 
                          json={'message': 'hello'})
    assert response.status_code == 403
    assert response.get_json()['error'] == 'Missing Origin header'

def test_reject_disallowed_origin(client):
    """Test that disallowed origins are explicitly rejected."""
    response = client.post('/chat', 
                          json={'message': 'hello'},
                          headers={'Origin': 'http://malicious.com'})
    
    assert response.status_code == 403
    assert response.get_json()['error'] == 'Origin not allowed'


def test_reject_empty_chatbot_message(client):
    response = client.post('/chat', json={'message': '   '}, headers=auth_headers())
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Message cannot be empty.'


def test_reject_oversized_chatbot_message(client):
    response = client.post('/chat', json={'message': 'x' * 501}, headers=auth_headers())
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Message must be 500 characters or fewer.'


def test_reject_malformed_chatbot_request(client):
    response = client.post(
        '/chat',
        data='{bad json',
        content_type='application/json',
        headers=auth_headers(),
    )
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Request body must be valid JSON.'
