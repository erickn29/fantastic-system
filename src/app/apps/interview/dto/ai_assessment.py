from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AIAssessmentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    user_id: UUID
    question_id: int
    answer_id: int
    score: int
    created_at: datetime
    updated_at: datetime
