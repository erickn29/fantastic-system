from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base, int_pk


class AIAssessment(Base):
    __tablename__ = "ai_assessment"

    id: Mapped[int_pk]
    text: Mapped[str] = mapped_column(Text, nullable=False, doc="Текст оценки")
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=1, doc="Оценка")
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"), nullable=False, doc="ID пользователя"
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("question.id"), nullable=False, doc="ID вопроса"
    )
    answer_id: Mapped[int] = mapped_column(
        ForeignKey("answer.id"), nullable=False, doc="ID ответа"
    )

    user = relationship("User", back_populates="ai_assessments", uselist=False)
    question = relationship("Question", back_populates="ai_assessments")
    answer = relationship("Answer", back_populates="ai_assessment", uselist=False)
