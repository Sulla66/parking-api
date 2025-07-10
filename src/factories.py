import factory
from factory.alchemy import SQLAlchemyModelFactory
from .models import db, Client, Parking
from faker import Faker

fake = Faker()


class ClientFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    credit_card = factory.LazyAttribute(lambda x: fake.credit_card_number() if fake.boolean() else None)
    car_number = factory.LazyAttribute(lambda x: fake.license_plate())


class ParkingFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = factory.Faker('address')
    opened = factory.Faker('boolean')
    count_places = factory.Faker('random_int', min=5, max=50)
    count_available_places = factory.LazyAttribute(lambda o: o.count_places)