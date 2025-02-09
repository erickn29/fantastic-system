from sqlalchemy import Boolean, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base
from model.question_technology import QuestionTechnologyTable


# from model import QuestionTechnology


class Question(Base):
    __tablename__ = "question"

    text: Mapped[str] = mapped_column(Text, nullable=False, doc="Текст вопроса")
    complexity: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, doc="Сложность", default=5, comment="1-9"
    )
    published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, doc="Опубликован", default=False
    )

    ai_assessments = relationship("AIAssessment", back_populates="question")
    answers = relationship("Answer", back_populates="question")
    question_technologies = relationship(
        "QuestionTechnology", back_populates="question"
    )
    user_questions = relationship("UserQuestion", back_populates="question")
    technologies = relationship(
        "Technology",
        secondary=QuestionTechnologyTable,
        # back_populates="questions"
    )
