import asyncio

from apps.interview.dto.question import QuestionDto
from apps.interview.entity.question import Question, QuestionProtocol
from apps.interview.repository.question import (
    QuestionRepositoryProtocol,
    SQLAlchemyQuestionRepositoryV1,
)
from apps.user.repository.user import UserRepositoryProtocol, UserRepositoryV1
from core.cache import cache


class QuestionForTrainingUseCase:
    def __init__(
        self,
        question_entity: QuestionProtocol,
        question_repo: QuestionRepositoryProtocol,
        user_repo: UserRepositoryProtocol,
    ):
        self._question_entity = question_entity
        self._question_repo = question_repo
        self._user_repo = user_repo

    async def get(self, user_tg_id: int) -> QuestionDto | None:
        """Возвращает вопрос для тренировки по конкретным технологиям"""
        stack = await self._user_repo.get_stack(user_tg_id)
        questions = await self._question_repo.get_unanswered_questions(
            user_id=user_tg_id, technologies=stack
        )
        if not questions:
            questions = await self._question_repo.get_questions(technologies=["python"])
        question = self._question_entity.get_random_question(questions)
        if question:
            pass
        return question


async def main():
    uc = QuestionForTrainingUseCase(
        question_entity=Question,
        question_repo=SQLAlchemyQuestionRepositoryV1,
        user_repo=UserRepositoryV1(cache_service=cache),
    )
    print(await uc.get(user_tg_id=1))


if __name__ == "__main__":
    asyncio.run(main())
