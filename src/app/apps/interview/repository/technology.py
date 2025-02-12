from app.tools.repository.sql_alchemy.sql_alchemy import SQLAlchemyRepository
from model.technology import Technology


class SQLAlchemyTechnologyRepositoryV1(SQLAlchemyRepository):
    model = Technology
