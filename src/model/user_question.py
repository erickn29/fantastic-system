from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base


class UserQuestion(Base):
    __tablename__ = "user_question"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, doc="ID пользователя"
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("question.id"), nullable=False, doc="ID вопроса"
    )

    user = relationship("User", back_populates="user_questions", uselist=False)
    question = relationship("Question", back_populates="user_questions", uselist=False)
