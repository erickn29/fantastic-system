import pytest

from app.apps.interview.dto.question import QuestionDto
from app.apps.interview.repository.question import (
    SAQuestionRepoV2,
)
from core.database import DatabaseHelper


@pytest.mark.app
async def test_get_questions_python(database, init_data):
    question_repo = SAQuestionRepoV2(DatabaseHelper(url=database))
    questions = await question_repo.get_questions(["python"])
    assert isinstance(questions, list)
    assert isinstance(questions[0], QuestionDto)
    assert len(questions) == 3


@pytest.mark.app
async def test_get_questions_sql(database, init_data):
    question_repo = SAQuestionRepoV2(DatabaseHelper(url=database))
    questions = await question_repo.get_questions(["sql"])
    assert isinstance(questions, list)
    assert isinstance(questions[0], QuestionDto)
    assert len(questions) == 3


@pytest.mark.app
async def test_get_questions_all(database, init_data):
    question_repo = SAQuestionRepoV2(DatabaseHelper(url=database))
    questions = await question_repo.get_questions(["sql", "python"])
    assert isinstance(questions, list)
    assert isinstance(questions[0], QuestionDto)
    assert len(questions) == 6


@pytest.mark.app
async def test_get_questions_empty_stack(database, init_data):
    question_repo = SAQuestionRepoV2(DatabaseHelper(url=database))
    questions = await question_repo.get_questions([])
    assert isinstance(questions, list)
    assert len(questions) == 0


@pytest.mark.app
async def test_get_questions_wrong_stack(database, init_data):
    question_repo = SAQuestionRepoV2(DatabaseHelper(url=database))
    questions = await question_repo.get_questions(["_wrong_"])
    assert isinstance(questions, list)
    assert len(questions) == 0
