from app.apps.interview.dto.answer import AnswerDto
from app.apps.interview.dto.question import QuestionDto
from app.apps.interview.repository.answer import AnswerRepositoryProtocol
from app.apps.interview.repository.question import QuestionRepositoryProtocol
from app.apps.user.dto.user import UserDto
from app.apps.user.repository.user import UserRepositoryProtocol


class AnswerUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryProtocol,
        question_repo: QuestionRepositoryProtocol,
        answer_repo: AnswerRepositoryProtocol,
    ):
        self._user_repo = user_repo
        self._question_repo = question_repo
        self._answer_repo = answer_repo

    async def process_user_answer(
        self, question_id: int, user_tg_id: int, text: str = ""
    ) -> tuple[UserDto, QuestionDto, AnswerDto] | None:
        """Обрабатывает ответ пользователя на вопрос"""
        user = await self._user_repo.find_user(tg_id=user_tg_id)
        question = await self._question_repo.find_question(id=question_id)

        if not question or not user:
            return None

        answer = await self._answer_repo.create_answer(text, user.id, question.id)
        return user, question, answer
