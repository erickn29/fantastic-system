from app.apps.interview.dto.ai_assessment import AIAssessmentDTO
from app.apps.interview.dto.answer import AnswerDto
from app.apps.interview.dto.question import QuestionDto
from app.apps.interview.entity import ai_assessment
from app.apps.interview.repository.ai_assessment import AIAssessmentRepositoryProtocol
from app.apps.user.dto.user import UserDto
from app.tools.cache import CacheServiceProtocol


class AIAssessmentUseCase:
    def __init__(
        self,
        cache_service: CacheServiceProtocol,
        ai_assessment_repo: AIAssessmentRepositoryProtocol,
        temperature: float = 0.7,
        max_tokens: int = -1,
        stream: bool = False,
    ):
        self._cache_service = cache_service
        self._ai_assessment_repo = ai_assessment_repo
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._stream = stream

    async def get_ai_assessment(
        self,
        user: UserDto,
        question: QuestionDto,
        answer: AnswerDto,
        to_markdown: bool = True,
    ) -> AIAssessmentDTO | None:
        stack = await self._cache_service.get_stack(user.id)
        if not any([question, answer, user, stack]):
            return None
        response_dict = await self._ai_assessment_repo.get_ai_response(
            answer=answer,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            stream=self._stream,
        )
        if not response_dict:
            return None
        text = ai_assessment.extract_text_from_llm_response(response_dict)
        if not text:
            return None
        if to_markdown:
            text = ai_assessment.normalize_text_to_markdown(text)
        score = ai_assessment.get_score(text)
        return await self._ai_assessment_repo.create_ai_assessment(
            text=text,
            user_id=user.id,
            question_id=question.id,
            answer_id=answer.id,
            score=score,
        )
