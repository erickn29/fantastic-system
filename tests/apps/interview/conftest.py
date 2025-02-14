import pytest

from app.apps.interview.repository.question import SQLAlchemyQuestionRepositoryV1
from app.apps.interview.repository.question_technology import (
    SQLAlchemyQuestionTechnologyRepositoryV1,
)
from app.apps.interview.repository.technology import SQLAlchemyTechnologyRepositoryV1
from app.apps.interview.repository.user_question import (
    SQLAlchemyUserQuestionRepositoryV1,
)
from app.apps.user.repository.user import SQLAlchemyUserRepositoryV1


@pytest.fixture(scope="function")
async def init_data(session):
    async with session.begin():
        question_repo = SQLAlchemyQuestionRepositoryV1(session)
        user_repo = SQLAlchemyUserRepositoryV1(session)
        tech_repo = SQLAlchemyTechnologyRepositoryV1(session)
        question_tech_repo = SQLAlchemyQuestionTechnologyRepositoryV1(session)
        user_question_repo = SQLAlchemyUserQuestionRepositoryV1(session)

        user = await user_repo.create(
            tg_id=123,
            tg_url="url",
            first_name="user",
        )

        python = await tech_repo.create(name="python")
        sql = await tech_repo.create(name="sql")

        q_python_1 = await question_repo.create(
            text="q_python_1",
            published=True,
        )
        q_python_2 = await question_repo.create(
            text="q_python_2",
            published=True,
        )
        q_python_3 = await question_repo.create(
            text="q_python_3",
            published=True,
        )
        await question_repo.create(
            text="q_python_4",
            published=False,
        )
        q_sql_1 = await question_repo.create(
            text="q_sql_1",
            published=True,
        )
        q_sql_2 = await question_repo.create(
            text="q_sql_2",
            published=True,
        )
        q_sql_3 = await question_repo.create(
            text="q_sql_3",
            published=True,
        )

        await user_question_repo.create(user_id=user.id, question_id=q_python_1.id)
        await user_question_repo.create(user_id=user.id, question_id=q_python_2.id)
        await user_question_repo.create(user_id=user.id, question_id=q_python_3.id)
        await user_question_repo.create(user_id=user.id, question_id=q_sql_1.id)
        await user_question_repo.create(user_id=user.id, question_id=q_sql_2.id)

        await question_tech_repo.create(
            question_id=q_python_1.id,
            technology_id=python.id,
        )
        await question_tech_repo.create(
            question_id=q_python_2.id,
            technology_id=python.id,
        )
        await question_tech_repo.create(
            technology_id=python.id,
            question_id=q_python_3.id,
        )

        await question_tech_repo.create(
            technology_id=sql.id,
            question_id=q_sql_1.id,
        )
        await question_tech_repo.create(
            technology_id=sql.id,
            question_id=q_sql_2.id,
        )
        await question_tech_repo.create(
            question_id=q_sql_3.id,
            technology_id=sql.id,
        )

        return {
            "user": user,
            "python": python,
            "sql": sql,
            "q_python_1": q_python_1,
            "q_python_2": q_python_2,
            "q_python_3": q_python_3,
            "q_sql_1": q_sql_1,
            "q_sql_2": q_sql_2,
            "q_sql_3": q_sql_3,
        }
