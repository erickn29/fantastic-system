from sqlalchemy import Column, ForeignKey, Integer, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base


class QuestionTechnology(Base):
    __tablename__ = "question_technology"
    __table_args__ = (UniqueConstraint("question_id", "technology_id"),)

    question_id: Mapped[int] = mapped_column(
        ForeignKey("question.id"), nullable=False, doc="Вопрос", name="question_id"
    )
    technology_id: Mapped[int] = mapped_column(
        ForeignKey("technology.id"),
        nullable=False,
        doc="Технология",
        name="technology_id",
    )

    question = relationship(
        "Question",
        back_populates="question_technologies",
        uselist=False,
    )
    technology = relationship(
        "Technology",
        back_populates="question_technologies",
        uselist=False,
    )


QuestionTechnologyTable = Table(
    "question_technology",
    Base.metadata,
    Column(
        "question_id",
        Integer,
        ForeignKey("question.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "technology_id",
        Integer,
        ForeignKey("technology.id", ondelete="CASCADE"),
        nullable=False,
    ),
    extend_existing=True,
)
