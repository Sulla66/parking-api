import pytest
from .models import Client, Parking, ClientParking
from datetime import datetime


@pytest.mark.parametrize('route', [
    '/clients',
    '/clients/1'
])
def test_get_methods(client, route):
    response = client.get(route)
    assert response.status_code == 200


def test_create_client(client):
    data = {
        'name': 'New',
        'surname': 'Client',
        'credit_card': '9876543210987654',
        'car_number': 'X987YZ'
    }
    response = client.post('/clients', json=data)
    assert response.status_code == 201
    assert 'id' in response.json


def test_create_parking(client):
    data = {
        'address': 'New Parking',
        'opened': True,
        'count_places': 20,
        'count_available_places': 20
    }
    response = client.post('/parkings', json=data)
    assert response.status_code == 201
    assert 'id' in response.json


@pytest.mark.parking
def test_enter_parking(client):
    data = {
        'client_id': 1,
        'parking_id': 1
    }
    response = client.post('/client_parkings', json=data)
    assert response.status_code == 201
    assert 'id' in response.json


@pytest.mark.parking
def test_exit_parking(client):
    # First enter parking
    enter_data = {
        'client_id': 1,
        'parking_id': 1
    }
    client.post('/client_parkings', json=enter_data)

    # Then exit
    exit_data = {
        'client_id': 1,
        'parking_id': 1
    }
    response = client.delete('/client_parkings', json=exit_data)
    assert response.status_code == 200
    assert 'message' in response.json


def test_create_client_with_factory(db_session):
    from .factories import ClientFactory
    client = ClientFactory()
    db_session.commit()
    assert client.id is not None


def test_create_parking_with_factory(db_session):
    from .factories import ParkingFactory
    parking = ParkingFactory()
    db_session.commit()
    assert parking.id is not None