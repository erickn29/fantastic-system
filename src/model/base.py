import uuid

from datetime import datetime
from typing import Annotated

from sqlalchemy import TIMESTAMP, UUID, BigInteger
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


TIMESTAMP_WITH_TIMEZONE = TIMESTAMP(timezone=True)

uuid_pk = Annotated[
    uuid.UUID,
    mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    ),
]
int_pk = Annotated[
    int,
    mapped_column(BigInteger, primary_key=True, autoincrement=True, unique=True),
]
created_at = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP_WITH_TIMEZONE,
        default=datetime.now,
        nullable=False,
        doc="Дата создания",
    ),
]
updated_at = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP_WITH_TIMEZONE,
        default=datetime.now,
        nullable=False,
        onupdate=datetime.now,
        doc="Дата изменения",
    ),
]


class Base(DeclarativeBase):
    id: Mapped[int_pk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    @classmethod
    def ordering(cls):
        return [cls.created_at]
