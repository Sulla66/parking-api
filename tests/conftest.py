import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app import create_app
from src.models import db, Client, Parking
import pytest

@pytest.fixture(scope='module')
def app():
    """Фикстура инициализации Flask-приложения"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    with app.app_context():
        db.create_all()
        # Добавляем тестовые данные
        test_client = Client(
            name='Test',
            surname='User',
            credit_card='1234567890123456',
            car_number='A123BC'
        )
        test_parking = Parking(
            address='Test Address',
            opened=True,
            count_places=10,
            count_available_places=5
        )
        db.session.add(test_client)
        db.session.add(test_parking)
        db.session.commit()

        yield app

        db.drop_all()


@pytest.fixture
def client(app):
    """Фикстура тестового клиента"""
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client


@pytest.fixture
def db_session(app):
    """Фикстура сессии базы данных"""
    with app.app_context():
        yield db.session