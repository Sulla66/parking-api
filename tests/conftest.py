from typing import Any, Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.app import create_app
from src.models import db


@pytest.fixture
def app() -> Generator[Flask, Any, None]:
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()
