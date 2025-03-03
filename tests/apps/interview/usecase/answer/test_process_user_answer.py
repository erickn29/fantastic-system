import pytest

from app.apps.interview.dto.answer import AnswerDto
from app.apps.interview.dto.question import QuestionDto
from app.apps.interview.usecase.answer import AnswerUseCase
from app.apps.user.dto.user import UserDto
from app.tools.uow import sqlalchemy_uow


@pytest.mark.app
async def test_process_user_answer(run_migrations, mocked_session, init_data):
    uc = AnswerUseCase(uow=sqlalchemy_uow)
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
async def test_process_user_answer_no_user(run_migrations, mocked_session, init_data):
    uc = AnswerUseCase(uow=sqlalchemy_uow)
    processed_data = await uc.process_user_answer(
        question_id=init_data["q_sql_3"].id,
        user_tg_id=100,
        text="answer",
    )
    assert processed_data is None


@pytest.mark.app
async def test_process_user_answer_no_question(
    run_migrations, mocked_session, init_data
):
    uc = AnswerUseCase(uow=sqlalchemy_uow)
    processed_data = await uc.process_user_answer(
        question_id=999,
        user_tg_id=init_data["user"].tg_id,
        text="answer",
    )
    assert processed_data is None
