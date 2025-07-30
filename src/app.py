from typing import Any, Dict, Tuple

from flask import Flask, jsonify, request
from werkzeug.wrappers import Response

from .models import Client, ClientParking, Parking, db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    db.init_app(app)

    @app.route("/clients", methods=["GET", "POST"])
    def handle_clients() -> Tuple[Response, int]:
        if request.method == "GET":
            clients = db.session.query(Client).all()
            return jsonify({"clients": [client.to_dict() for client in clients]}), 200

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        try:
            client = Client(name=data["name"], email=data["email"])
            db.session.add(client)
            db.session.commit()
            return jsonify(client.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

    @app.route("/parkings", methods=["POST"])
    def handle_parkings() -> Tuple[Response, int]:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        try:
            parking = Parking(
                number=data["number"],
                address=data["address"],
                count_places=data["count_places"],
            )
            db.session.add(parking)
            db.session.commit()
            return jsonify(parking.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

    @app.route("/client_parkings", methods=["POST"])
    def handle_client_parkings() -> Tuple[Response, int]:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        try:
            client_parking = ClientParking(
                client_id=data["client_id"], parking_id=data["parking_id"]
            )
            db.session.add(client_parking)
            db.session.commit()
            return jsonify(client_parking.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

    @app.route("/clients/<int:client_id>", methods=["GET"])
    def get_client(client_id: int) -> Tuple[Response, int]:
        client = db.session.query(Client).get(client_id)
        if not client:
            return jsonify({"error": "Client not found"}), 404

        return jsonify(client.to_dict()), 200

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
