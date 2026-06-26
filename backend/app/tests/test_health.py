from sqlalchemy import text


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_db_connection(db_session):
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1
