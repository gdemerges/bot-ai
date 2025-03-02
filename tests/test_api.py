import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_status():
    """Test que l'endpoint /status retourne une réponse valide"""
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"status": "API en ligne"}

def test_health():
    """Test que l'endpoint /health fonctionne"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_chat():
    """Test l'endpoint /chat avec un message"""
    response = client.post("/chat", json={"message": "Hello"})
    assert response.status_code == 200
    assert "response" in response.json()
