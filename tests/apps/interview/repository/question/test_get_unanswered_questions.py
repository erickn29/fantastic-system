from app.apps.interview.dto.question import QuestionDto
from app.apps.interview.repository.question import SQLAlchemyQuestionRepositoryV1


async def test_get_unanswered_questions_python_sql(run_migrations, session, init_data):
    async with session:
        question_repo = SQLAlchemyQuestionRepositoryV1(session)
        questions = await question_repo.get_unanswered_questions(
            user_id=init_data["user"].id,
            technologies=["python", "sql"],
        )
    assert isinstance(questions, list)
    assert isinstance(questions[0], QuestionDto)
    assert len(questions) == 1
    assert questions[0].id == init_data["q_sql_3"].id
