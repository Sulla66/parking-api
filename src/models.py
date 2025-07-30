from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Type

from email_validator import EmailNotValidError, validate_email
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.orm import relationship, validates

db = SQLAlchemy()

if TYPE_CHECKING:
    # Для проверки типов создаем заглушку
    class BaseModel:
        pass

else:
    BaseModel = db.Model


class BaseModel(db.Model):  # type: ignore[name-defined]
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            c.name: (
                getattr(self, c.name).isoformat()
                if isinstance(getattr(self, c.name), datetime)
                else getattr(self, c.name)
            )
            for c in self.__table__.columns
        }


class Client(BaseModel):
    __tablename__ = "clients"

    name: "Column[str]" = Column(String(80), nullable=False)
    email: "Column[str]" = Column(String(120), unique=True, nullable=False)
    parkings = relationship("ClientParking", back_populates="client")

    def __init__(self, name: str, email: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.name = name  # type: ignore[assignment]
        self.email = email  # type: ignore[assignment]

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["parkings"] = [cp.parking.to_dict() for cp in self.parkings]
        return data


class Parking(BaseModel):
    __tablename__ = "parkings"

    number: "Column[str]" = Column(String(20), unique=True, nullable=False)
    address: "Column[str]" = Column(String(200), nullable=False)
    opened: "Column[bool]" = Column(Boolean, default=True)
    count_places: "Column[int]" = Column(Integer, nullable=False)
    count_available_places: "Column[int]" = Column(Integer, nullable=False)
    clients = relationship("ClientParking", back_populates="parking")

    def __init__(self, number: str, address: str, count_places: int, **kwargs: Any):
        super().__init__(**kwargs)
        self.number = number  # type: ignore[assignment]
        self.address = address  # type: ignore[assignment]
        self.count_places = count_places  # type: ignore[assignment]
        self.count_available_places = count_places  # type: ignore[assignment]

    def to_dict(self) -> Dict[str, Any]:
        return super().to_dict()


class ClientParking(db.Model):  # type: ignore[name-defined]
    __tablename__ = "client_parkings"

    id = Column(Integer, primary_key=True)
    client_id: "Column[int]" = Column(
        Integer, ForeignKey("clients.id", ondelete="CASCADE")
    )
    parking_id: "Column[int]" = Column(
        Integer, ForeignKey("parkings.id", ondelete="CASCADE")
    )
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("client_id", "parking_id", name="_client_parking_uc"),
    )

    client = relationship("Client", back_populates="parkings")
    parking = relationship("Parking", back_populates="clients")

    def __init__(self, client_id: int, parking_id: int, **kwargs: Any):
        super().__init__(**kwargs)
        self.client_id = client_id  # type: ignore[assignment]
        self.parking_id = parking_id  # type: ignore[assignment]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "client_id": self.client_id,
            "parking_id": self.parking_id,
            "created_at": self.created_at.isoformat(),
        }
