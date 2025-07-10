import pytest
from .app import create_app
from .models import db, Client, Parking, ClientParking
from datetime import datetime, timedelta


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()

        # Создаём тестового клиента с картой
        client = Client(
            name='Test',
            surname='User',
            credit_card='1234567890123456',  # Убедимся, что карта есть
            car_number='A123BC'
        )

        # Создаём парковку с 10 местами (5 свободных)
        parking = Parking(
            address='Test Address',
            opened=True,  # Парковка открыта
            count_places=10,
            count_available_places=5  # Достаточно свободных мест
        )

        db.session.add(client)
        db.session.add(parking)
        db.session.commit()

        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session