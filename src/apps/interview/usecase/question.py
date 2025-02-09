import asyncio

from apps.dependencies.protocol.cache_service import CacheServiceProtocol
from apps.interview.dto.question import QuestionDto
from apps.interview.entity.question import Question, QuestionProtocol
from apps.interview.repository.question import (
    QuestionRepositoryProtocol,
    SQLAlchemyQuestionRepositoryV1,
)
from apps.user.repository.user import UserRepositoryProtocol, UserRepositoryV1
from core.cache import cache


class QuestionUseCase:
    def __init__(
        self,
        question_entity: QuestionProtocol,
        question_repo: QuestionRepositoryProtocol,
        user_repo: UserRepositoryProtocol,
        cache_service: CacheServiceProtocol,
    ):
        self._question_entity = question_entity
        self._question_repo = question_repo
        self._user_repo = user_repo
        self._cache_service = cache_service

    async def get_question_training(self, user_tg_id: int) -> QuestionDto | None:
        """Возвращает вопрос для тренировки по конкретным технологиям"""
        user = await self._user_repo.find_user(tg_id=user_tg_id)
        if not user:
            return None
        stack = await self._cache_service.get_stack(user.id) or ["python"]
        questions = await self._question_repo.get_unanswered_questions(
            user_id=user.id, technologies=stack
        )
        if not questions:
            questions = await self._question_repo.get_questions(technologies=["python"])
        question = self._question_entity.get_random_question(questions)
        if question:
            await self._question_repo.create_user_question(user.id, question.id)
            await self._cache_service.set_user_last_question(user.id, question.id)
        return question


async def main():
    uc = QuestionUseCase(
        question_entity=Question,
        question_repo=SQLAlchemyQuestionRepositoryV1,
        user_repo=UserRepositoryV1,
        cache_service=cache,
    )
    print(await uc.get_question_training(user_tg_id=1))


if __name__ == "__main__":
    asyncio.run(main())
