from collections.abc import Iterable
from typing import Protocol
from uuid import UUID

from sqlalchemy import select

from app.apps.interview.dto.question import QuestionDto
from app.tools.repository.sql_alchemy.sql_alchemy import SQLAlchemyRepository
from app.tools.repository.sql_alchemy.sql_alchemy_v2 import SARepository
from model.question import Question
from model.question_technology import QuestionTechnology
from model.technology import Technology
from model.user_question import UserQuestion


class QuestionRepositoryProtocol(Protocol):
    async def find_question(self, id: int) -> QuestionDto | None:
        """Возвращает вопрос по id"""
        pass

    async def get_questions(self, technologies: list[str]) -> list[QuestionDto]:
        """Возвращает все вопросы по технологии"""
        pass

    async def get_unanswered_questions(
        self, user_id: UUID, technologies: list[str] | None = None
    ) -> list[QuestionDto] | None:
        """Возвращает все неотвеченные вопросы по технологии"""
        pass

    async def get_questions_for_user(
        self, user_id: UUID, technologies: list[str] | None = None
    ) -> list[QuestionDto]:
        """Возвращает вопросы для пользователя"""
        pass

    async def create_user_question_obj(self, user_id: UUID, question_id: int):
        """Связывает пользователя с вопросом"""
        pass


class SQLAlchemyQuestionRepositoryV1(SQLAlchemyRepository):
    model = Question

    async def find_question(self, id: int) -> QuestionDto | None:
        """Возвращает вопрос по id"""
        question = await self.find(id=id)
        if not question:
            return None
        return QuestionDto.model_validate(question)

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
                self.model.published == True,
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

    async def create_user_question_obj(self, user_id: UUID, question_id: int):
        """Связывает пользователя с вопросом"""
        user_question_object = UserQuestion(user_id=user_id, question_id=question_id)
        self.session.add(user_question_object)
        await self.session.flush()


class SAQuestionRepoV2(SARepository):
    model = Question

    async def find_question(self, id: int) -> QuestionDto | None:
        """Возвращает вопрос по id"""
        question = await self.query(self.model).find(id=id)
        if not question:
            return None
        return QuestionDto.model_validate(question)

    async def get_questions(self, technologies: Iterable[str]) -> list[QuestionDto]:
        sub_query_technologies = select(Technology.id).where(
            Technology.name.in_(technologies)
        )
        query = (
            select(self.model)
            .join(QuestionTechnology, QuestionTechnology.question_id == self.model.id)
            .where(
                QuestionTechnology.technology_id.in_(sub_query_technologies),
                self.model.published == True,
            )
            .distinct(self.model.id, self.model.created_at)
            .order_by(self.model.created_at)
        )
        result = await self.execute(query)
        questions = result.scalars().all()
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
        result = await self.execute(query)
        questions = result.scalars().all()
        return [QuestionDto.model_validate(question) for question in questions]

    async def get_questions_for_user(
        self, user_id: UUID, technologies: Iterable[str] | None = None
    ) -> list[QuestionDto]:
        """Возвращает вопросы для пользователя"""
        return await self.get_unanswered_questions(
            user_id=user_id, technologies=technologies
        ) or await self.get_questions(technologies=technologies)
