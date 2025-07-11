import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

fake = Faker()


class ClientFactory(SQLAlchemyModelFactory):
    class Meta:
        model = None
        sqlalchemy_session = None

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    credit_card = factory.LazyAttribute(
        lambda x: fake.credit_card_number() if fake.boolean() else None
    )
    car_number = factory.LazyAttribute(lambda x: fake.license_plate())


class ParkingFactory(SQLAlchemyModelFactory):
    class Meta:
        model = None
        sqlalchemy_session = None

    address = factory.Faker("address")
    opened = factory.Faker("boolean")
    count_places = factory.Faker("random_int", min=5, max=50)
    count_available_places = factory.LazyAttribute(lambda o: o.count_places)
