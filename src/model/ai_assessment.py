from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base


class AIAssessment(Base):
    __tablename__ = "ai_assessment"

    text: Mapped[str] = mapped_column(Text, nullable=False, doc="Текст оценки")
    user_id: Mapped[int] = mapped_column(
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
