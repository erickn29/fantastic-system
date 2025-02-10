from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QuestionDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    complexity: int = 5
    published: bool = False
    created_at: datetime
    updated_at: datetime


class QuestionCreateDto(BaseModel):
    id: int | None = None
    text: str
    complexity: int = 5
    published: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
