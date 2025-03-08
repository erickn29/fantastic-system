from typing import Protocol
from uuid import UUID

from app.apps.interview.dto.answer import AnswerDto
from app.tools.repository.sql_alchemy.sql_alchemy import SQLAlchemyRepository
from app.tools.repository.sql_alchemy.sql_alchemy_v2 import SARepository
from model import Answer


class AnswerRepositoryProtocol(Protocol):

    async def create_answer(
        self, text: str, user_id: UUID, question_id: int
    ) -> AnswerDto:
        """Создает ответ пользователя на вопрос"""
        pass


class SQLAlchemyAnswerRepositoryV1(SQLAlchemyRepository):
    model = Answer

    async def create_answer(
        self, text: str, user_id: UUID, question_id: int
    ) -> AnswerDto:
        """Создает ответ пользователя на вопрос"""
        answer = await self.create(text=text, user_id=user_id, question_id=question_id)
        return AnswerDto.model_validate(answer)


class SAAnswerRepoV2(SARepository):
    model = Answer

    async def create_answer(
        self, text: str, user_id: UUID, question_id: int
    ) -> AnswerDto:
        """Создает ответ пользователя на вопрос"""
        async with self:
            answer = await self.stmt(self.model).create(
                text=text, user_id=user_id, question_id=question_id
            )
        return AnswerDto.model_validate(answer)
