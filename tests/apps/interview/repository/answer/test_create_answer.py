import pytest

from app.apps.interview.dto.answer import AnswerDto
from app.apps.interview.repository.answer import (
    SAAnswerRepoV2,
)
from core.database import DatabaseHelper


@pytest.mark.app
async def test_create_answer(database, init_data):
    answer_repo = SAAnswerRepoV2(DatabaseHelper(url=database))
    answer = await answer_repo.create_answer(
        text="answer",
        user_id=init_data["user"].id,
        question_id=init_data["q_sql_3"].id,
    )
    assert isinstance(answer, AnswerDto)
