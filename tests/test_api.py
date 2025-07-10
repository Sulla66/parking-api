import pytest
from src.models import Client, Parking, ClientParking
from datetime import datetime, timedelta


@pytest.mark.parametrize('route', [
    '/clients',
    '/clients/1'
])
def test_get_methods(client, route):
    """Тестирование GET-эндпоинтов"""
    response = client.get(route)
    assert response.status_code == 200
    if route == '/clients':
        assert isinstance(response.json, list)
    else:
        assert 'name' in response.json
        assert response.json['name'] == 'Test'


def test_create_client(client):
    """Тестирование создания клиента"""
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
    """Тестирование создания парковки"""
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
    """Тестирование въезда на парковку"""
    data = {
        'client_id': 1,
        'parking_id': 1
    }
    response = client.post('/client_parkings', json=data)
    assert response.status_code == 201
    assert 'id' in response.json


@pytest.mark.parking
def test_exit_parking(client, db_session):
    """Тестирование выезда с парковки"""
    # 1. Подготовка данных
    client_data = {
        'name': 'Test',
        'surname': 'User',
        'credit_card': '1234123412341234',
        'car_number': 'A123BC'
    }
    parking_data = {
        'address': 'Test Parking',
        'opened': True,
        'count_places': 10,
        'count_available_places': 5
    }

    # 2. Создаем клиента и парковку
    test_client = Client(**client_data)
    test_parking = Parking(**parking_data)
    db_session.add(test_client)
    db_session.add(test_parking)
    db_session.commit()

    # 3. Занимаем место
    enter_data = {
        'client_id': test_client.id,
        'parking_id': test_parking.id
    }
    enter_response = client.post('/client_parkings', json=enter_data)
    assert enter_response.status_code == 201

    # 4. Проверяем уменьшение мест
    updated_parking = db_session.get(Parking, test_parking.id)
    assert updated_parking.count_available_places == parking_data['count_available_places'] - 1

    # 5. Тестируем выезд
    exit_data = {
        'client_id': test_client.id,
        'parking_id': test_parking.id
    }
    exit_response = client.delete('/client_parkings', json=exit_data)
    assert exit_response.status_code == 200

    # 6. Проверяем освобождение места
    updated_parking = db_session.get(Parking, test_parking.id)
    assert updated_parking.count_available_places == parking_data['count_available_places']


def test_create_client_with_factory(db_session):
    """Тестирование фабрики клиентов"""
    from src.factories import ClientFactory
    client = ClientFactory()
    db_session.commit()
    assert client.id is not None
    assert isinstance(client.name, str)


def test_create_parking_with_factory(db_session):
    """Тестирование фабрики парковок"""
    from src.factories import ParkingFactory
    parking = ParkingFactory()
    db_session.commit()
    assert parking.id is not None
    assert parking.count_available_places <= parking.count_places