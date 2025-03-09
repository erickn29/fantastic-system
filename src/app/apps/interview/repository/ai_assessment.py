from typing import Protocol
from uuid import UUID

from app.apps.interview.dto.ai_assessment import AIAssessmentDTO
from app.apps.interview.dto.answer import AnswerDto
from app.apps.interview.utils.request_service import RequestServiceProtocol
from app.tools.repository.sql_alchemy.sql_alchemy_v2 import SARepository
from core.database import DatabaseHelper
from model import AIAssessment


class AIAssessmentRepositoryProtocol(Protocol):
    def __init__(
        self,
        system_prompt_assessment: str,
        system_prompt_help: str,
        llm_request_service: RequestServiceProtocol,
    ):
        pass

    async def get_ai_response(
        self,
        answer: AnswerDto,
        temperature: float = 0.7,
        max_tokens: int = -1,
        stream: bool = False,
    ) -> dict | None:
        """Возвращает оценку ответа пользователя на вопрос"""
        pass

    async def create_ai_assessment(
        self,
        text: str,
        user_id: UUID,
        question_id: int,
        answer_id: int,
        score: int = 1,
    ) -> AIAssessmentDTO | None:
        """Создает оценку ответа пользователя на вопрос"""
        pass


class AIAssessmentRepository(SARepository):
    model = AIAssessment

    def __init__(
        self,
        system_prompt_assessment: str,
        system_prompt_help: str,
        llm_request_service: RequestServiceProtocol,
        connection: DatabaseHelper,
    ):
        super().__init__(connection=connection)
        self._system_prompt_assessment = system_prompt_assessment
        self._system_prompt_help = system_prompt_help
        self._llm_request_service = llm_request_service

    async def get_ai_response(
        self,
        answer: AnswerDto,
        temperature: float = 0.7,
        max_tokens: int = -1,
        stream: bool = False,
    ) -> dict | None:
        """Возвращает оценку ответа пользователя на вопрос"""
        response = await self._llm_request_service.send_request_llm(
            data={
                "messages": [
                    {"role": "system", "content": self._system_prompt_assessment},
                    {"role": "user", "content": answer.text},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
            },
        )
        return response

    async def create_ai_assessment(
        self,
        text: str,
        user_id: UUID,
        question_id: int,
        answer_id: int,
        score: int = 1,
    ) -> AIAssessmentDTO | None:
        """Создает оценку ответа пользователя на вопрос"""
        return await self.stmt(self.model).create(
            text=text,
            user_id=user_id,
            question_id=question_id,
            answer_id=answer_id,
            score=score,
            dto=AIAssessmentDTO,
        )
