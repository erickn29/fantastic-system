from collections.abc import Iterable
from typing import Protocol
from uuid import UUID

from sqlalchemy import select

from apps.interview.dto.question import QuestionDto
from apps.interview.repository.sql_alchemy import SQLAlchemyRepository
from model.question import Question
from model.question_technology import QuestionTechnology
from model.technology import Technology
from model.user_question import UserQuestion


class QuestionRepositoryProtocol(Protocol):
    async def get_questions(self, technologies: list[str]) -> list[QuestionDto]:
        """Возвращает все вопросы по технологии"""
        pass

    async def get_unanswered_questions(
        self, user_id: UUID, technologies: list[str] | None = None
    ) -> list[QuestionDto] | None:
        """Возвращает все неотвеченные вопросы по технологии"""
        pass

    async def create_user_question_object(self, user_id: UUID, question_id: int):
        """Связывает пользователя с вопросом"""
        pass


class SQLAlchemyQuestionRepositoryV1(SQLAlchemyRepository):
    model = Question

    async def get_questions(self, technologies: Iterable[str]) -> list[QuestionDto]:
        """Возвращает все вопросы по технологии"""
        sub_query_technologies = select(Technology.id).where(
            Technology.name.in_(technologies)
        )
        query = (
            select(self.model)
            .join(QuestionTechnology, QuestionTechnology.question_id == self.model.id)
            .where(
                QuestionTechnology.technology_id.in_(sub_query_technologies),
            )
            .distinct(self.model.id, self.model.created_at)
            .order_by(self.model.created_at)
        )
        result = await self.session.scalars(query)
        questions = result.all()
        return [QuestionDto.model_validate(question) for question in questions]

    async def get_unanswered_questions(
        self, user_id: UUID, technologies: Iterable[str] | None = None
    ) -> list[QuestionDto] | None:
        """Возвращает все неотвеченные вопросы по технологии"""
        technologies = technologies or []
        sub_query_technologies = select(Technology.id).where(
            Technology.name.in_(technologies)
        )
        sub_query_user_questions = select(UserQuestion.question_id).where(
            UserQuestion.user_id == user_id
        )
        query = (
            select(self.model)
            .join(QuestionTechnology)
            .where(
                QuestionTechnology.technology_id.in_(sub_query_technologies),
                QuestionTechnology.question_id == self.model.id,
                self.model.id.not_in(sub_query_user_questions),
                self.model.published == True,
            )
            .distinct(self.model.id, self.model.created_at)
            .order_by(self.model.created_at)
        )
        result = await self.session.scalars(query)
        questions = result.all()
        return [QuestionDto.model_validate(question) for question in questions]

    async def create_user_question_object(self, user_id: UUID, question_id: int):
        """Связывает пользователя с вопросом"""
        user_question_object = UserQuestion(user_id=user_id, question_id=question_id)
        self.session.add(user_question_object)
        await self.session.flush()
