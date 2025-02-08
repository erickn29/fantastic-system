import random

from typing import Protocol

from apps.interview.dto.question import QuestionDto


class QuestionProtocol(Protocol):
    def get_random_question(self, questions: list[QuestionDto]) -> QuestionDto | None:
        """Возвращает случайный вопрос"""
        pass

    def _validate(self) -> bool:
        """Проверяет правильность вопроса"""
        pass


class Question[T]:
    def __init__(
        self,
        text: str,
        question_id: int | None = None,
        complexity: int = 5,
        published: bool = False,
    ):
        self._id = question_id
        self._text = text
        self._complexity = complexity
        self._published = published
        self._validate()

    def __str__(self):
        return f"<Question Entity: {self._text[:20]}...>"

    def _validate(self):
        if not self._text:
            raise ValueError("Question text is required")
        if not isinstance(self._text, str):
            raise ValueError("Question text must be a string")

    @staticmethod
    def get_random_question(questions: list[QuestionDto]) -> QuestionDto | None:
        """Возвращает случайный вопрос"""
        question = random.choice(questions) if questions else None
        return question


a: Question = Question(question_id=1, text="10")
