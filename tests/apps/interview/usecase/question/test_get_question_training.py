from app.apps.interview.dto.question import QuestionDto
from app.apps.interview.entity.question import QuestionEntity
from app.apps.interview.repository.user_question import (
    SQLAlchemyUserQuestionRepositoryV1,
)
from app.apps.interview.usecase.question import QuestionUseCase
from app.tools.cache import cache_service
from app.tools.uow import sqlalchemy_uow


async def test_get_question_training(run_migrations, mocked_session, init_data, mocker):
    cache_service_str = "app.tools.cache.cache_service"
    mocker.patch(f"{cache_service_str}.get_stack", return_value=["python", "sql"])
    mocker.patch(f"{cache_service_str}.set_user_last_question", return_value=None)

    user_question_repo = SQLAlchemyUserQuestionRepositoryV1(mocked_session)

    uc = QuestionUseCase(
        question_entity=QuestionEntity,
        cache_service=cache_service,
        uow=sqlalchemy_uow,
    )
    question = await uc.get_question_training(user_tg_id=init_data["user"].tg_id)
    user_question = await user_question_repo.find(
        user_id=init_data["user"].id, question_id=init_data["q_sql_3"].id
    )
    assert isinstance(question, QuestionDto)
    assert question.id == init_data["q_sql_3"].id
    assert user_question is not None


async def test_get_question_training_all_answered(
    run_migrations, mocked_session, init_data, mocker
):
    cache_service_str = "app.tools.cache.cache_service"
    mocker.patch(f"{cache_service_str}.get_stack", return_value=["python"])
    mocker.patch(f"{cache_service_str}.set_user_last_question", return_value=None)

    user_question_repo = SQLAlchemyUserQuestionRepositoryV1(mocked_session)

    uc = QuestionUseCase(
        question_entity=QuestionEntity,
        cache_service=cache_service,
        uow=sqlalchemy_uow,
    )
    question = await uc.get_question_training(user_tg_id=init_data["user"].tg_id)
    user_question = await user_question_repo.find(
        user_id=init_data["user"].id, question_id=question.id
    )
    assert isinstance(question, QuestionDto)
    assert user_question is not None


async def test_get_question_training_no_user(run_migrations, mocked_session, init_data):
    uc = QuestionUseCase(
        question_entity=QuestionEntity,
        cache_service=cache_service,
        uow=sqlalchemy_uow,
    )
    question = await uc.get_question_training(user_tg_id=None)
    assert question is None
