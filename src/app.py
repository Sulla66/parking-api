from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from flask import Flask, jsonify, request
from werkzeug.wrappers import Response

from .models import Client, ClientParking, Parking, db


def create_app(test_config: Optional[Dict[str, Any]] = None) -> Flask:
    """Фабрика для создания Flask приложения."""
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        PROPAGATE_EXCEPTIONS=True,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    @app.route("/clients", methods=["GET", "POST"])
    def handle_clients() -> Tuple[Response, int]:
        """Обработчик для работы с клиентами."""
        if request.method == "GET":
            clients = db.session.scalars(db.select(Client)).all()
            return jsonify([client.to_dict() for client in clients]), 200

        data = request.get_json()
        if not data or "name" not in data or "email" not in data:
            return jsonify({"error": "Name and email are required"}), 400

        try:
            client = Client(**data)
            db.session.add(client)
            db.session.commit()
            return jsonify(client.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

    @app.route("/parkings", methods=["POST"])
    def handle_parkings() -> Tuple[Response, int]:
        """Создание новой парковки."""
        data = request.get_json()
        required_fields = ["number", "address", "count_places"]
        if not data or any(field not in data for field in required_fields):
            return (
                jsonify({"error": f"Required fields: {', '.join(required_fields)}"}),
                400,
            )

        try:
            parking = Parking(**data)
            db.session.add(parking)
            db.session.commit()
            return jsonify(parking.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

    @app.route("/client_parkings", methods=["POST"])
    def handle_client_parkings() -> Tuple[Response, int]:
        """Связь клиента с парковкой."""
        data = request.get_json()
        if not data or "client_id" not in data or "parking_id" not in data:
            return jsonify({"error": "client_id and parking_id are required"}), 400

        try:
            client_parking = ClientParking(**data)
            db.session.add(client_parking)
            db.session.commit()
            return jsonify(client_parking.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

    @app.route("/clients/<int:client_id>", methods=["GET"])
    def get_client(client_id: int) -> Tuple[Response, int]:
        """Получение информации о клиенте."""
        client = db.session.get(Client, client_id)  # SQLAlchemy 2.0 style
        if not client:
            return jsonify({"error": "Client not found"}), 404
        return jsonify(client.to_dict()), 200

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
