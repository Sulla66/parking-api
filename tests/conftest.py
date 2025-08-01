from typing import Any, Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient


@pytest.fixture
def app() -> Generator[Flask, Any, None]:
    """Фикстура создания Flask приложения."""
    from src.app import create_app

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        from src.models import db

        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> Generator[FlaskClient, Any, None]:
    """Фикстура тестового клиента."""
    with app.test_client() as test_client:
        yield test_client
