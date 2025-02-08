from pydantic import BaseModel


class QuestionDto(BaseModel):
    id: int | None = None
    text: str
    complexity: int = 5
    published: bool = False
