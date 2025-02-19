from app.apps.interview.dto.answer import AnswerDto
from app.apps.interview.dto.question import QuestionDto
from app.apps.user.dto.user import UserDto
from app.tools.uow import UOWProtocol


class AnswerUseCase:
    def __init__(
        self,
        uow: UOWProtocol,
    ):
        self._uow = uow

    async def process_user_answer(
        self, question_id: int, user_tg_id: int, text: str = ""
    ) -> tuple[UserDto, QuestionDto, AnswerDto] | None:
        """Обрабатывает ответ пользователя на вопрос"""
        async with self._uow as uow:
            user = await uow.user_repo.find_user(tg_id=user_tg_id)
            question = await uow.question_repo.find_question(id=question_id)

        if not question or not user:
            return None

        async with self._uow as uow:
            answer = await uow.answer_repo.create_answer(
                text=text, user_id=user.id, question_id=question.id
            )
        return user, question, answer
