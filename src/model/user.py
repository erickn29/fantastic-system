from datetime import datetime

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base


class User(Base):
    __tablename__ = "user"

    tg_id: Mapped[int] = mapped_column(BigInteger, doc="Telegram ID", nullable=False)
    tg_url: Mapped[str] = mapped_column(String, doc="Telegram URL", nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False, doc="Имя")
    last_name: Mapped[str] = mapped_column(
        String, nullable=True, doc="Фамилия", default=""
    )
    tg_username: Mapped[str] = mapped_column(
        String, nullable=True, doc="username", default=""
    )
    coins: Mapped[int] = mapped_column(BigInteger, doc="Coins", default=0)
    is_active: Mapped[bool] = mapped_column(doc="Активен", default=True)
    is_admin: Mapped[bool] = mapped_column(doc="Админ", default=False)
    subscription: Mapped[datetime] = mapped_column(doc="Подписка до", nullable=True)
    password: Mapped[str] = mapped_column(Text, doc="Пароль", nullable=True)

    user_questions = relationship("UserQuestion", back_populates="user")
    answers = relationship("Answer", back_populates="user")
    ai_assessments = relationship("AIAssessment", back_populates="user")
