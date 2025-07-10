from flask import Flask, jsonify, request
from src.models import db, Client, Parking, ClientParking
from datetime import datetime


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/clients', methods=['GET'])
    def get_clients():
        clients = Client.query.all()
        return jsonify([{
            'id': client.id,
            'name': client.name,
            'surname': client.surname,
            'credit_card': client.credit_card,
            'car_number': client.car_number
        } for client in clients])

    @app.route('/clients/<int:client_id>', methods=['GET'])
    def get_client(client_id):
        client = Client.query.get_or_404(client_id)
        return jsonify({
            'id': client.id,
            'name': client.name,
            'surname': client.surname,
            'credit_card': client.credit_card,
            'car_number': client.car_number
        })

    @app.route('/clients', methods=['POST'])
    def create_client():
        data = request.get_json()
        client = Client(
            name=data['name'],
            surname=data['surname'],
            credit_card=data.get('credit_card'),
            car_number=data.get('car_number')
        )
        db.session.add(client)
        db.session.commit()
        return jsonify({'id': client.id}), 201

    @app.route('/parkings', methods=['POST'])
    def create_parking():
        data = request.get_json()
        parking = Parking(
            address=data['address'],
            opened=data.get('opened', True),
            count_places=data['count_places'],
            count_available_places=data['count_available_places']
        )
        db.session.add(parking)
        db.session.commit()
        return jsonify({'id': parking.id}), 201

    @app.route('/client_parkings', methods=['POST'])
    def enter_parking():
        data = request.get_json()
        client = Client.query.get_or_404(data['client_id'])
        parking = Parking.query.get_or_404(data['parking_id'])

        if not parking.opened:
            return jsonify({'error': 'Parking is closed'}), 400

        if parking.count_available_places <= 0:
            return jsonify({'error': 'No available places'}), 400

        parking.count_available_places -= 1
        client_parking = ClientParking(
            client_id=client.id,
            parking_id=parking.id,
            time_in=datetime.now()
        )
        db.session.add(client_parking)
        db.session.commit()
        return jsonify({'id': client_parking.id}), 201

    @app.route('/client_parkings', methods=['DELETE'])
    def exit_parking():
        data = request.get_json()

        # Находим активную запись (где time_out is NULL)
        client_parking = ClientParking.query.filter_by(
            client_id=data['client_id'],
            parking_id=data['parking_id'],
            time_out=None
        ).first_or_404()

        # Освобождаем место
        parking = Parking.query.get_or_404(data['parking_id'])
        parking.count_available_places += 1

        # Фиксируем время выезда
        client_parking.time_out = datetime.now()

        db.session.commit()
        return jsonify({'message': 'Payment processed successfully'}), 200

    return app