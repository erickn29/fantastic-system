from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import db_conn
from model.base import Base


class Error(Base):
    __tablename__ = "error"

    text: Mapped[str] = mapped_column(Text, nullable=False, doc="Текст ошибки")


async def create_error(text: str):
    session = db_conn.session_factory()
    async with session.begin():
        error = Error(text=text)
        session.add(error)
        await session.commit()
