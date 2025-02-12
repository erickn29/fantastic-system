from app.apps.interview.dto.question import QuestionDto
from app.apps.interview.repository.question import SQLAlchemyQuestionRepositoryV1


async def test_get_questions_python(run_migrations, session, init_data):
    async with session:
        question_repo = SQLAlchemyQuestionRepositoryV1(session)
        questions = await question_repo.get_questions(["python"])
    assert isinstance(questions, list)
    assert isinstance(questions[0], QuestionDto)
    assert len(questions) == 3


async def test_get_questions_sql(run_migrations, session, init_data):
    async with session:
        question_repo = SQLAlchemyQuestionRepositoryV1(session)
        questions = await question_repo.get_questions(["sql"])
    assert isinstance(questions, list)
    assert isinstance(questions[0], QuestionDto)
    assert len(questions) == 3


async def test_get_questions_all(run_migrations, session, init_data):
    async with session:
        question_repo = SQLAlchemyQuestionRepositoryV1(session)
        questions = await question_repo.get_questions(["sql", "python"])
    assert isinstance(questions, list)
    assert isinstance(questions[0], QuestionDto)
    assert len(questions) == 6


async def test_get_questions_empty_stack(run_migrations, session, init_data):
    async with session:
        question_repo = SQLAlchemyQuestionRepositoryV1(session)
        questions = await question_repo.get_questions([])
    assert isinstance(questions, list)
    assert len(questions) == 0


async def test_get_questions_wrong_stack(run_migrations, session, init_data):
    async with session:
        question_repo = SQLAlchemyQuestionRepositoryV1(session)
        questions = await question_repo.get_questions(["_wrong_"])
    assert isinstance(questions, list)
    assert len(questions) == 0
