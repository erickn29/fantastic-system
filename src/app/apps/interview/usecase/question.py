from app.apps.interview.dto.question import QuestionDto
from app.apps.interview.entity.question import QuestionProtocol
from app.tools.protocol.cache import CacheServiceProtocol
from app.tools.repository.sql_alchemy.uow import UOWProtocol


class QuestionUseCase:
    def __init__(
        self,
        question_entity: QuestionProtocol,
        cache_service: CacheServiceProtocol,
        uow: UOWProtocol,
    ):
        self._question_entity = question_entity
        self._cache_service = cache_service
        self._uow = uow

    async def get_question_training(self, user_tg_id: int) -> QuestionDto | None:
        """Возвращает вопрос для тренировки по конкретным технологиям"""
        async with self._uow as uow:
            user = await uow.user_repo.find_user(tg_id=user_tg_id)
        if not user:
            return None
        stack = await self._cache_service.get_stack(user.id) or ["python"]
        async with self._uow as uow:
            questions = await uow.question_repo.get_unanswered_questions(
                user_id=user.id, technologies=stack
            )
            if not questions:
                questions = await uow.question_repo.get_questions(technologies=stack)
        question = self._question_entity.get_random_question(questions)
        if question:
            async with self._uow as uow:
                await uow.question_repo.create_user_question_obj(user.id, question.id)
            await self._cache_service.set_user_last_question(user.id, question.id)
        return question
