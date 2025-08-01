from datetime import datetime
from typing import Any, Dict

from flask import Response


def test_parking_workflow(client: Any) -> None:
    """Тест workflow работы с парковками."""
    test_email = f"testuser_{datetime.now().timestamp()}@testdomain.com"
    client_data: Dict[str, str] = {"name": "Test Client", "email": test_email}

    # Проверяем, что маршрут существует
    assert client.application.url_map.bind("").match("/clients", method="POST")

    # Создание клиента
    client_resp: Response = client.post("/clients", json=client_data)
    assert client_resp.status_code == 201, (
        f"Expected 201, got {client_resp.status_code}."
        f" Response: {client_resp.data.decode()}"
    )

    client_json = client_resp.get_json()
    client_id = client_json["id"]

    # Проверка получения клиента
    get_client_resp: Response = client.get(f"/clients/{client_id}")
    assert get_client_resp.status_code == 200
    assert get_client_resp.get_json()["email"] == test_email
