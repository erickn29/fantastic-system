import pytest

from app.apps.interview.dto.answer import AnswerDto
from app.apps.interview.dto.question import QuestionDto
from app.apps.interview.repository.answer import SAAnswerRepoV2
from app.apps.interview.repository.question import SAQuestionRepoV2
from app.apps.interview.usecase.answer import AnswerUseCase
from app.apps.user.dto.user import UserDto
from app.apps.user.repository.user import SAUserRepositoryV2
from core.database import DatabaseHelper


@pytest.mark.app
async def test_process_user_answer(init_data, database):
    uc = AnswerUseCase(
        user_repo=SAUserRepositoryV2(DatabaseHelper(url=database)),
        question_repo=SAQuestionRepoV2(DatabaseHelper(url=database)),
        answer_repo=SAAnswerRepoV2(DatabaseHelper(url=database)),
    )
    processed_data = await uc.process_user_answer(
        question_id=init_data["q_sql_3"].id,
        user_tg_id=init_data["user"].tg_id,
        text="answer",
    )
    assert isinstance(processed_data, tuple)
    assert len(processed_data) == 3
    assert isinstance(processed_data[0], UserDto)
    assert isinstance(processed_data[1], QuestionDto)
    assert isinstance(processed_data[2], AnswerDto)


@pytest.mark.app
async def test_process_user_answer_no_user(init_data, database):
    uc = AnswerUseCase(
        user_repo=SAUserRepositoryV2(DatabaseHelper(url=database)),
        question_repo=SAQuestionRepoV2(DatabaseHelper(url=database)),
        answer_repo=SAAnswerRepoV2(DatabaseHelper(url=database)),
    )
    processed_data = await uc.process_user_answer(
        question_id=init_data["q_sql_3"].id,
        user_tg_id=100,
        text="answer",
    )
    assert processed_data is None


@pytest.mark.app
async def test_process_user_answer_no_question(init_data, database):
    uc = AnswerUseCase(
        user_repo=SAUserRepositoryV2(DatabaseHelper(url=database)),
        question_repo=SAQuestionRepoV2(DatabaseHelper(url=database)),
        answer_repo=SAAnswerRepoV2(DatabaseHelper(url=database)),
    )
    processed_data = await uc.process_user_answer(
        question_id=999,
        user_tg_id=init_data["user"].tg_id,
        text="answer",
    )
    assert processed_data is None
