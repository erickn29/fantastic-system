from sqlalchemy import ForeignKey, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base


class Answer(Base):
    __tablename__ = "answer"

    text: Mapped[str] = mapped_column(Text, nullable=False, doc="Текст ответа")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, doc="ID пользователя"
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("question.id"), nullable=False, doc="ID вопроса"
    )
    score: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, doc="Оценка ответа"
    )

    user = relationship("User", back_populates="answers", uselist=False)
    question = relationship("Question", back_populates="answers", uselist=False)
    ai_assessment = relationship("AIAssessment", back_populates="answer", uselist=False)
