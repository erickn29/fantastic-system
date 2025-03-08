from typing import Protocol
from uuid import UUID

from app.apps.interview.dto.user_question import UserQuestionDTO
from app.tools.repository.sql_alchemy.sql_alchemy import SQLAlchemyRepository
from app.tools.repository.sql_alchemy.sql_alchemy_v2 import SARepository
from model.user_question import UserQuestion


class UserQuestionRepositoryProtocol(Protocol):
    async def create_object(self, user_id: UUID, question_id: int):
        """Создает объект пользователя и вопроса"""
        pass

    async def find(self, user_id: UUID, question_id: int) -> UserQuestionDTO | None:
        """Возвращает объект пользователя и вопроса"""
        pass


class SQLAlchemyUserQuestionRepositoryV1(SQLAlchemyRepository):
    model = UserQuestion


class SAUserQuestionRepoV2(SARepository):
    model = UserQuestion

    async def create_object(self, user_id: UUID, question_id: int):
        """Создает объект пользователя и вопроса"""
        async with self:
            await self.stmt(self.model).create(user_id=user_id, question_id=question_id)

    async def find(self, user_id: UUID, question_id: int) -> UserQuestionDTO | None:
        """Возвращает объект пользователя и вопроса"""
        uq: UserQuestionDTO = await self.query(self.model).find(
            user_id=user_id, question_id=question_id, dto=UserQuestionDTO
        )
        return uq
