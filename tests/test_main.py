from fastapi.testclient import TestClient

from app.main import app


def test_health_check():
    """
    Test the health check endpoint.
    """
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_api_docs():
    """
    Test that the API docs are accessible.
    """
    client = TestClient(app)
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
