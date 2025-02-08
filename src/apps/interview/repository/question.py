from typing import Protocol

from apps.interview.dto.question import QuestionDto
from apps.interview.repository.sql_alchemy import SQLAlchemyRepository


class QuestionRepositoryProtocol(Protocol):
    async def get_questions(self, technologies: list[str]) -> list[QuestionDto]:
        """Возвращает все вопросы по технологии"""
        pass

    async def get_unanswered_questions(
        self, user_id: int, technologies: list[str]
    ) -> list[QuestionDto]:
        """Возвращает все неотвеченные вопросы по технологии"""
        pass


class SQLAlchemyQuestionRepositoryV1(SQLAlchemyRepository):
    async def get_questions(self, technologies: list[str]) -> list[QuestionDto]:
        """Возвращает все вопросы по технологии"""
        return []

    async def get_unanswered_questions(
        self, user_id: int, technologies: list[str]
    ) -> list[QuestionDto]:
        """Возвращает все неотвеченные вопросы по технологии"""
        return []
