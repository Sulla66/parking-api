import sys
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

from src.app import create_app
from src.models import Client, ClientParking, Parking, db

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="module")
def app() -> Generator[Flask, None, None]:
    """Фикстура инициализации Flask-приложения."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False,
    }

    app = create_app(config=test_config)

    with app.app_context():
        db.create_all()
        _create_test_data(db)
        yield app
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> Generator[FlaskClient, None, None]:
    """Фикстура тестового клиента."""
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client


@pytest.fixture
def db_session(app: Flask) -> Generator[Session, None, None]:
    """Фикстура сессии базы данных."""
    with app.app_context():
        yield db.session


def _create_test_data(db):
    """Создание тестовых данных."""
    test_client = Client(
        name="Test",
        surname="User",
        credit_card="1234567890123456",
        car_number="A123BC",
    )
    test_parking = Parking(
        address="Test Address",
        opened=True,
        count_places=10,
        count_available_places=5,
    )
    db.session.add_all([test_client, test_parking])
    db.session.commit()

    client_parking = ClientParking(
        client_id=test_client.id,
        parking_id=test_parking.id,
        time_in=datetime.now(),
    )
    db.session.add(client_parking)
    db.session.commit()
