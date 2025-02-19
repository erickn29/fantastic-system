from asyncio import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.apps.interview.repository.answer import (
    AnswerRepositoryProtocol,
    SQLAlchemyAnswerRepositoryV1,
)
from app.apps.interview.repository.question import (
    QuestionRepositoryProtocol,
    SQLAlchemyQuestionRepositoryV1,
)
from app.apps.user.repository.user import (
    SQLAlchemyUserRepositoryV1,
    UserRepositoryProtocol,
)
from core.database import db_conn


class UOWProtocol(Protocol):
    def __init__(
        self,
        question_repo: QuestionRepositoryProtocol,
        user_repo: UserRepositoryProtocol,
        answer_repo: AnswerRepositoryProtocol,
    ):
        self._question_repo = question_repo
        self._user_repo = user_repo
        self._answer_repo = answer_repo

    @property
    def question_repo(self) -> QuestionRepositoryProtocol:
        """Возвращает объект для работы с вопросами"""
        return self._question_repo(self._session)  # type: ignore

    @property
    def user_repo(self) -> UserRepositoryProtocol:
        """Возвращает объект для работы с пользователями"""
        return self._user_repo(self._session)  # type: ignore

    @property
    def answer_repo(self) -> AnswerRepositoryProtocol:
        """Возвращает объект для работы с ответами"""
        return self._answer_repo(self._session)  # type: ignore

    async def __aenter__(self) -> "UOWProtocol":
        """Возвращает объект для использования с помощью with"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выполняет коммит и закрывает сессию"""
        pass


class SQLAlchemyUOW:
    def __init__(
        self,
        question_repo: type[QuestionRepositoryProtocol],
        user_repo: type[UserRepositoryProtocol],
        answer_repo: type[AnswerRepositoryProtocol],
    ):
        self._session = None
        self._question_repo = question_repo
        self._user_repo = user_repo
        self._answer_repo = answer_repo

    def _check_session(self):
        if not self._session:
            raise ValueError("Вызов возможен только внутри контекстного менеджера")

    @property
    def question_repo(self) -> QuestionRepositoryProtocol:
        """Возвращает объект для работы с вопросами"""
        self._check_session()
        return self._question_repo(self._session)  # type: ignore

    @property
    def user_repo(self) -> UserRepositoryProtocol:
        """Возвращает объект для работы с пользователями"""
        self._check_session()
        return self._user_repo(self._session)  # type: ignore

    @property
    def answer_repo(self) -> AnswerRepositoryProtocol:
        """Возвращает объект для работы с ответами"""
        self._check_session()
        return self._answer_repo(self._session)  # type: ignore

    async def __aenter__(self):
        self._session: AsyncSession = db_conn.session_factory()
        await self._session.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self._session.rollback()
            await self._session.close()
            self._session = None
            return
        await self._session.commit()
        await self._session.close()
        self._session = None


sqlalchemy_uow = SQLAlchemyUOW(
    question_repo=SQLAlchemyQuestionRepositoryV1,
    user_repo=SQLAlchemyUserRepositoryV1,
    answer_repo=SQLAlchemyAnswerRepositoryV1,
)
