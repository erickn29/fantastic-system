import random

from typing import Protocol

from apps.interview.dto.question import QuestionDto


class QuestionProtocol(Protocol):
    def get_random_question(self, questions: list[QuestionDto]) -> QuestionDto | None:
        """Возвращает случайный вопрос"""
        pass


class Question:
    @staticmethod
    def get_random_question(questions: list[QuestionDto]) -> QuestionDto | None:
        """Возвращает случайный вопрос"""
        question = random.choice(questions) if questions else None
        return question
