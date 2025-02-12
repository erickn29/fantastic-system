from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base, int_pk


class Technology(Base):
    __tablename__ = "technology"

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String, nullable=False, doc="Название технологии")

    question_technologies = relationship(
        "QuestionTechnology", back_populates="technology"
    )
