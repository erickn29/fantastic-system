from app.apps.interview.dto.answer import AnswerDto
from app.apps.interview.repository.answer import SQLAlchemyAnswerRepositoryV1


async def test_create_answer(run_migrations, session, init_data):
    async with session:
        answer_repo = SQLAlchemyAnswerRepositoryV1(session)
        answer = await answer_repo.create_answer(
            text="answer",
            user_id=init_data["user"].id,
            question_id=init_data["q_sql_3"].id,
        )
    assert isinstance(answer, AnswerDto)
