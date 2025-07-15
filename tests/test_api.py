import pytest

from src.models import db


@pytest.fixture
def sample_client_data():
    return {
        "name": "Test",
        "surname": "User",
        "credit_card": "1234123412341234",
        "car_number": "A123BC",
    }


@pytest.fixture
def sample_parking_data():
    return {
        "address": "Test Parking",
        "opened": True,
        "count_places": 20,
        "count_available_places": 20,
    }


@pytest.mark.parametrize(
    "route,expected_fields",
    [("/clients", ["id", "name"]), ("/clients/1", ["id", "name", "surname"])],
)
def test_get_methods(client, route, expected_fields):
    """Тестирование GET-эндпоинтов."""
    response = client.get(route)
    assert response.status_code == 200
    if isinstance(response.json, list):
        assert all(
            field in item
            for item in response.json()
            for field in expected_fields
        )
    else:
        assert all(field in response.json for field in expected_fields)


def test_create_client(client, sample_client_data):
    """Тестирование создания клиента."""
    response = client.post("/clients", json=sample_client_data)
    assert response.status_code == 201
    assert "id" in response.json


def test_create_parking(client, sample_parking_data):
    """Тестирование создания парковки."""
    response = client.post("/parkings", json=sample_parking_data)
    assert response.status_code == 201
    assert "id" in response.json


def test_enter_exit_parking_flow(
    client, db_session, sample_client_data, sample_parking_data
):
    """Тестирование полного цикла въезда-выезда."""
    client_obj = db.models.Client(**sample_client_data)
    parking = db.models.Parking(**sample_parking_data)
    db_session.add_all([client_obj, parking])
    db_session.commit()

    enter_data = {"client_id": client_obj.id, "parking_id": parking.id}
    enter_response = client.post("/client_parkings", json=enter_data)
    assert enter_response.status_code == 201
    assert parking.count_available_places == 19

    exit_response = client.delete("/client_parkings", json=enter_data)
    assert exit_response.status_code == 200
    assert parking.count_available_places == 20
