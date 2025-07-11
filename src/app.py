from datetime import datetime

from flask import Flask, jsonify, request

from src.models import db


def create_app():
    app = Flask(__name__)
    app.config.update(
        {
            "SQLALCHEMY_DATABASE_URI": "sqlite:///parking.db",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "JSONIFY_PRETTYPRINT_REGULAR": True,
            "WTF_CSRF_ENABLED": False,
        }
    )
    db.init_app(app)

    def _client_to_dict(client):
        """Конвертирует объект Client в словарь."""
        return {
            "id": client.id,
            "name": client.name,
            "surname": client.surname,
            "credit_card": client.credit_card,
            "car_number": client.car_number,
        }

    @app.route("/clients", methods=["GET"])
    def get_clients():
        """Получение списка всех клиентов."""
        clients = db.session.query(db.models.Client).all()
        return jsonify([_client_to_dict(c) for c in clients])

    @app.route("/clients/<int:client_id>", methods=["GET"])
    def get_client(client_id):
        """Получение конкретного клиента по ID."""
        client = db.session.query(db.models.Client).get_or_404(client_id)
        return jsonify(_client_to_dict(client))

    @app.route("/clients", methods=["POST"])
    def create_client():
        """Создание нового клиента."""
        data = request.get_json()
        if not all(k in data for k in ["name", "surname"]):
            return jsonify({"error": "Missing required fields"}), 400

        client = db.models.Client(
            name=data["name"],
            surname=data["surname"],
            credit_card=data.get("credit_card"),
            car_number=data.get("car_number"),
        )
        db.session.add(client)
        db.session.commit()
        return jsonify({"id": client.id}), 201

    @app.route("/parkings", methods=["POST"])
    def create_parking():
        """Создание новой парковки."""
        data = request.get_json()
        if not all(k in data for k in ["address", "count_places"]):
            return jsonify({"error": "Missing required fields"}), 400

        parking = db.models.Parking(
            address=data["address"],
            opened=data.get("opened", True),
            count_places=data["count_places"],
            count_available_places=data.get(
                "count_available_places", data["count_places"]
            ),
        )
        db.session.add(parking)
        db.session.commit()
        return jsonify({"id": parking.id}), 201

    @app.route("/client_parkings", methods=["POST"])
    def enter_parking():
        """Регистрация въезда на парковку."""
        data = request.get_json()
        if not all(k in data for k in ["client_id", "parking_id"]):
            return jsonify({"error": "Missing required fields"}), 400

        client = db.session.query(db.models.Client).get_or_404(data["client_id"])
        parking = db.session.query(db.models.Parking).get_or_404(data["parking_id"])

        if not parking.opened:
            return jsonify({"error": "Parking is closed"}), 400
        if parking.count_available_places <= 0:
            return jsonify({"error": "No available places"}), 400

        parking.count_available_places -= 1
        client_parking = db.models.ClientParking(
            client_id=client.id, parking_id=parking.id, time_in=datetime.now()
        )
        db.session.add(client_parking)
        db.session.commit()
        return jsonify({"id": client_parking.id}), 201

    @app.route("/client_parkings", methods=["DELETE"])
    def exit_parking():
        """Регистрация выезда с парковки."""
        data = request.get_json()
        if not all(k in data for k in ["client_id", "parking_id"]):
            return jsonify({"error": "Missing required fields"}), 400

        client_parking = (
            db.session.query(db.models.ClientParking)
            .filter_by(
                client_id=data["client_id"],
                parking_id=data["parking_id"],
                time_out=None,
            )
            .first_or_404()
        )

        parking = db.session.query(db.models.Parking).get_or_404(data["parking_id"])
        parking.count_available_places += 1
        client_parking.time_out = datetime.now()

        db.session.commit()
        return jsonify({"message": "Success"}), 200

    return app
