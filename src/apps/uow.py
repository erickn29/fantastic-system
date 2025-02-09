from asyncio import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from apps.interview.repository.question import QuestionRepositoryProtocol
from apps.user.repository.user import UserRepositoryProtocol
from core.database import db_conn


class UOWProtocol(Protocol):
    def __init__(
        self,
        question_repo: QuestionRepositoryProtocol,
        user_repo: UserRepositoryProtocol,
    ):
        self._question_repo = question_repo
        self._user_repo = user_repo

    @property
    def question_repo(self) -> QuestionRepositoryProtocol:
        """Возвращает объект для работы с вопросами"""
        return self._question_repo(self._session)  # type: ignore

    @property
    def user_repo(self) -> UserRepositoryProtocol:
        """Возвращает объект для работы с пользователями"""
        return self._user_repo(self._session)  # type: ignore

    async def __aenter__(self) -> "UOWProtocol":
        """Возвращает объект для использования с помощью with"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выполняет коммит и закрывает сессию"""
        pass


class SQLAlchemyUOW:
    def __init__(
        self,
        question_repo: QuestionRepositoryProtocol,
        user_repo: UserRepositoryProtocol,
    ):
        self._session: AsyncSession = db_conn.session_factory()
        self._question_repo = question_repo
        self._user_repo = user_repo

    @property
    def question_repo(self) -> QuestionRepositoryProtocol:
        """Возвращает объект для работы с вопросами"""
        return self._question_repo(self._session)  # type: ignore

    @property
    def user_repo(self) -> UserRepositoryProtocol:
        """Возвращает объект для работы с пользователями"""
        return self._user_repo(self._session)  # type: ignore

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self._session.rollback()
            await self._session.close()
        await self._session.commit()
        await self._session.close()
