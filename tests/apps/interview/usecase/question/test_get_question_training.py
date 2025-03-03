import pytest

from app.apps.interview.dto.question import QuestionDto
from app.apps.interview.entity.question import QuestionEntity
from app.apps.interview.repository.question import (
    SQLAlchemyQuestionRepositoryV2,
)
from app.apps.interview.repository.user_question import (
    SQLAlchemyUserQuestionRepositoryV1,
    SQLAlchemyUserQuestionRepositoryV2,
)
from app.apps.interview.usecase.question import QuestionUseCase
from app.apps.user.repository.user import SQLAlchemyUserRepositoryV2
from app.tools.cache import cache_service
from core.database import DatabaseHelper


@pytest.mark.app
async def test_get_question_training(
    database, run_migrations, mocked_session, init_data, mocker
):
    cache_service_str = "app.tools.cache.cache_service"
    mocker.patch(f"{cache_service_str}.get_stack", return_value=["python", "sql"])
    mocker.patch(f"{cache_service_str}.set_user_last_question", return_value=None)

    user_question_repo = SQLAlchemyUserQuestionRepositoryV1(mocked_session)

    uc = QuestionUseCase(
        question_entity=QuestionEntity,
        cache_service=cache_service,
        user_repo=SQLAlchemyUserRepositoryV2(DatabaseHelper(url=database)),
        question_repo=SQLAlchemyQuestionRepositoryV2(DatabaseHelper(url=database)),
        user_question_repo=SQLAlchemyUserQuestionRepositoryV2(
            DatabaseHelper(url=database)
        ),
    )
    question = await uc.get_question_training(user_tg_id=init_data["user"].tg_id)
    user_question = await user_question_repo.find(
        user_id=init_data["user"].id, question_id=init_data["q_sql_3"].id
    )
    assert isinstance(question, QuestionDto)
    assert question.id == init_data["q_sql_3"].id
    assert user_question is not None


@pytest.mark.app
async def test_get_question_training_all_answered(
    database, run_migrations, mocked_session, init_data, mocker
):
    cache_service_str = "app.tools.cache.cache_service"
    mocker.patch(f"{cache_service_str}.get_stack", return_value=["python"])
    mocker.patch(f"{cache_service_str}.set_user_last_question", return_value=None)

    user_question_repo = SQLAlchemyUserQuestionRepositoryV1(mocked_session)

    uc = QuestionUseCase(
        question_entity=QuestionEntity,
        cache_service=cache_service,
        user_repo=SQLAlchemyUserRepositoryV2(DatabaseHelper(url=database)),
        question_repo=SQLAlchemyQuestionRepositoryV2(DatabaseHelper(url=database)),
        user_question_repo=SQLAlchemyUserQuestionRepositoryV2(
            DatabaseHelper(url=database)
        ),
    )
    question = await uc.get_question_training(user_tg_id=init_data["user"].tg_id)
    user_question = await user_question_repo.find(
        user_id=init_data["user"].id, question_id=question.id
    )
    assert isinstance(question, QuestionDto)
    assert user_question is not None


@pytest.mark.app
async def test_get_question_training_no_user(
    database, run_migrations, mocked_session, init_data
):
    uc = QuestionUseCase(
        question_entity=QuestionEntity,
        cache_service=cache_service,
        user_repo=SQLAlchemyUserRepositoryV2(DatabaseHelper(url=database)),
        question_repo=SQLAlchemyQuestionRepositoryV2(DatabaseHelper(url=database)),
        user_question_repo=SQLAlchemyUserQuestionRepositoryV2(
            DatabaseHelper(url=database)
        ),
    )
    question = await uc.get_question_training(user_tg_id=None)
    assert question is None
