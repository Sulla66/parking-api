from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ClientParking(db.Model):
    __tablename__ = 'client_parking'
    __table_args__ = (
        db.UniqueConstraint('client_id', 'parking_id', name='unique_client_parking_active'),
        {'sqlite_autoincrement': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    parking_id = db.Column(db.Integer, db.ForeignKey('parking.id'))
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime)

class Parking(db.Model):
    __tablename__ = 'parking'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)
    clients = db.relationship('ClientParking', backref='parking', lazy=True)
