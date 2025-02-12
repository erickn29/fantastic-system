from app.tools.repository.sql_alchemy.sql_alchemy import SQLAlchemyRepository
from model.user_question import UserQuestion


class SQLAlchemyUserQuestionRepositoryV1(SQLAlchemyRepository):
    model = UserQuestion
