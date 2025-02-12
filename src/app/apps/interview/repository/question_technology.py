from app.tools.repository.sql_alchemy.sql_alchemy import SQLAlchemyRepository
from model.question_technology import QuestionTechnology


class SQLAlchemyQuestionTechnologyRepositoryV1(SQLAlchemyRepository):
    model = QuestionTechnology
