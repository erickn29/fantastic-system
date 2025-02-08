import asyncio

from apps.interview.dto.question import QuestionDto
from apps.interview.entity.question import Question, QuestionProtocol
from apps.interview.repository.question import (
    QuestionRepositoryProtocol,
    SQLAlchemyQuestionRepositoryV1,
)


async def get_question_for_training(
    user_tg_id: int,
    question_entity: QuestionProtocol,
    question_repo: QuestionRepositoryProtocol,
) -> QuestionDto | None:
    """Возвращает вопрос для тренировки по конкретным технологиям для пользователя"""
    questions = await question_repo.get_unanswered_questions(
        user_id=user_tg_id, technologies=["python"]
    )
    if not questions:
        questions = await question_repo.get_questions(technologies=["python"])
    question = question_entity.get_random_question(questions)
    if question:
        pass
    return question


async def main():
    print(
        await get_question_for_training(1, Question, SQLAlchemyQuestionRepositoryV1())
    )


if __name__ == "__main__":
    asyncio.run(main())
