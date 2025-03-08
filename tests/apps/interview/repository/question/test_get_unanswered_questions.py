import pytest

from app.apps.interview.dto.question import QuestionDto
from app.apps.interview.repository.question import (
    SAQuestionRepoV2,
)
from core.database import DatabaseHelper


@pytest.mark.app
async def test_get_unanswered_questions_python_sql(database, init_data):
    question_repo = SAQuestionRepoV2(DatabaseHelper(url=database))
    questions = await question_repo.get_unanswered_questions(
        user_id=init_data["user"].id,
        technologies=["python", "sql"],
    )
    assert isinstance(questions, list)
    assert isinstance(questions[0], QuestionDto)
    assert len(questions) == 1
    assert questions[0].id == init_data["q_sql_3"].id
