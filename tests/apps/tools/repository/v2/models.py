import uuid

from datetime import date

from sqlalchemy import (
    UUID,
    Boolean,
    CheckConstraint,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tests.apps.tools.repository.v2.base import Base, uuid_pk


class Driver(Base):
    __tablename__ = "driver"
    verbose_name = "Водитель"

    id: Mapped[uuid_pk]
    first_name: Mapped[str] = mapped_column(String(16), nullable=False)
    last_name: Mapped[str] = mapped_column(String(16), nullable=False)
    patronymic: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    birth_date: Mapped[date] = mapped_column(
        Date,
        CheckConstraint("birth_date <= '2006-01-01'", name="ck_birth_date"),
        nullable=False,
        name="birth_date",
    )
    phone_number: Mapped[str] = mapped_column(
        String(12), unique=True, nullable=False, name="phone_number"
    )
    list_field: Mapped[list] = mapped_column(ARRAY(String), default=[])

    license = relationship(
        "License",
        back_populates="driver",
        uselist=False,
        cascade="all, delete-orphan",
    )
    cars = relationship(
        "Car",
        back_populates="driver",
        cascade="all, delete-orphan",
    )


class License(Base):
    __tablename__ = "license"
    __table_args__ = (UniqueConstraint("series", "number", name="uq_series_number"),)
    verbose_name = "Водительское удостоверение"

    id: Mapped[uuid_pk]
    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("driver.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        name="driver_id",
    )
    series: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("series >= 1000 AND series <= 9999", name="ck_series"),
        nullable=False,
        name="series",
    )
    number: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("number >= 100000 AND number <= 999999", name="ck_number"),
        nullable=False,
        name="number",
    )

    driver = relationship(
        "Driver",
        back_populates="license",
        uselist=False,
    )


class Car(Base):
    __tablename__ = "car"
    verbose_name = "Автомобиль"

    id: Mapped[uuid_pk]
    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("driver.id", ondelete="CASCADE"), nullable=False
    )
    vendor: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str] = mapped_column(String(32), nullable=False)
    year: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("year >= 2014 AND year <= 2024", name="ck_year"),
        nullable=False,
        name="year",
    )
    color: Mapped[str] = mapped_column(String(32), nullable=True)
    is_broken: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cost: Mapped[float] = mapped_column(
        Float,
        CheckConstraint("cost >= 100000 AND cost <= 100000000", name="ck_cost"),
        name="cost",
    )

    driver = relationship(
        "Driver",
        back_populates="cars",
    )


class Route(Base):
    __tablename__ = "route"
    verbose_name = "Маршрут"

    id: Mapped[uuid_pk]
    city_from: Mapped[str] = mapped_column(String(32), nullable=False)
    city_to: Mapped[str] = mapped_column(String(32), nullable=False)


class DriverRoute(Base):
    __tablename__ = "driver_route"
    verbose_name = "Маршруты и водители"

    id: Mapped[uuid_pk]
    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("driver.id", ondelete="CASCADE"), nullable=False
    )
    route_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("route.id", ondelete="CASCADE"), nullable=False
    )
