from datetime import datetime

from flask.testing import FlaskClient

from src.models import Client, db


def test_parking_workflow(client: FlaskClient) -> None:
    # Используем db.session.query вместо Client.query
    test_email = f"testuser_{datetime.now().timestamp()}@testdomain.com"
    client_data = {"name": "Test Client", "email": test_email}

    # Создание клиента
    client_resp = client.post("/clients", json=client_data)
    assert client_resp.status_code == 201
    client_json = client_resp.get_json()
    client_id = client_json["id"]

    # Проверка получения клиента
    get_client_resp = client.get(f"/clients/{client_id}")
    assert get_client_resp.status_code == 200
    assert get_client_resp.get_json()["email"] == test_email
