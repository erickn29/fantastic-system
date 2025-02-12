from datetime import datetime

import pytz

from app.apps.interview.dto.question import QuestionDto
from app.apps.interview.entity.question import Question


async def test_get_random_question():
    questions = [
        QuestionDto(
            id=1,
            text="q_python_1",
            complexity=5,
            published=True,
            created_at=datetime(2023, 1, 1, 8, 0, tzinfo=pytz.utc),
            updated_at=datetime(2023, 1, 1, 8, 0, tzinfo=pytz.utc),
        ),
        QuestionDto(
            id=2,
            text="q_python_2",
            complexity=5,
            published=True,
            created_at=datetime(2023, 1, 1, 8, 0, tzinfo=pytz.utc),
            updated_at=datetime(2023, 1, 1, 8, 0, tzinfo=pytz.utc),
        ),
        QuestionDto(
            id=3,
            text="q_python_3",
            complexity=5,
            published=True,
            created_at=datetime(2023, 1, 1, 8, 0, tzinfo=pytz.utc),
            updated_at=datetime(2023, 1, 1, 8, 0, tzinfo=pytz.utc),
        ),
    ]

    question = Question.get_random_question(questions)
    assert isinstance(question, QuestionDto)


async def test_get_random_question_empty_questions():
    questions = []
    question = Question.get_random_question(questions)
    assert question is None
