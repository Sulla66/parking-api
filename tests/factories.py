# mypy: ignore-errors

import factory
from factory.alchemy import SQLAlchemyModelFactory

from src.models import Client, Parking, db


class ClientFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker("name")  # type: ignore[attr-defined, no-untyped-call]
    email = factory.Faker("email")  # type: ignore[attr-defined, no-untyped-call]


class ParkingFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    number = factory.Faker(
        "bothify", text="??-##"
    )  # type: ignore[attr-defined, no-untyped-call]
    address = factory.Faker("address")  # type: ignore[attr-defined, no-untyped-call]
    opened = factory.Faker("boolean")  # type: ignore[attr-defined, no-untyped-call]
    count_places = factory.Faker(
        "random_int", min=5, max=50
    )  # type: ignore[attr-defined, no-untyped-call]
    count_available_places = factory.LazyAttribute(
        lambda o: o.count_places
    )  # type: ignore[attr-defined, no-untyped-call]
