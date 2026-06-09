import os
import sys
import pytest
from unittest.mock import MagicMock

# Create a mock for chatbot_integration and sys.modules
mock_chatbot = MagicMock()
mock_chatbot.get_chatbot_response.return_value = "Mock response"
sys.modules['chatbot_integration'] = mock_chatbot

# Set environment variable before importing app
os.environ["ALLOWED_ORIGIN"] = "http://localhost:3000"
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_allow_explicit_origin(client):
    """Test that an explicitly allowed origin is accepted."""
    response = client.post('/chat', 
                          json={'message': 'hello'},
                          headers={'Origin': 'http://localhost:3000'})
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
