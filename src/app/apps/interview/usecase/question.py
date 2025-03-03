from app.apps.interview.dto.question import QuestionDto
from app.apps.interview.entity.question import QuestionProtocol
from app.apps.interview.repository.question import QuestionRepositoryProtocol
from app.apps.interview.repository.user_question import UserQuestionRepositoryProtocol
from app.apps.user.repository.user import UserRepositoryProtocol
from app.tools.cache import CacheServiceProtocol


class QuestionUseCase:
    def __init__(
        self,
        question_entity: QuestionProtocol,
        cache_service: CacheServiceProtocol,
        user_repo: UserRepositoryProtocol,
        question_repo: QuestionRepositoryProtocol,
        user_question_repo: UserQuestionRepositoryProtocol,
    ):
        self._question_entity = question_entity
        self._cache_service = cache_service
        self._user_repo = user_repo
        self._question_repo = question_repo
        self._user_question_repo = user_question_repo

    async def get_question_training(self, user_tg_id: int) -> QuestionDto | None:
        """Возвращает вопрос для тренировки по конкретным технологиям"""
        user = await self._user_repo.find_user(tg_id=user_tg_id)
        if not user:
            return None
        stack = await self._cache_service.get_stack(user.id) or ["python"]
        questions = await self._question_repo.get_questions_for_user(user.id, stack)
        question = self._question_entity.get_random_question(questions)
        if question:
            await self._user_question_repo.create_object(user.id, question.id)
            await self._cache_service.set_user_last_question(user.id, question.id)
        return question
