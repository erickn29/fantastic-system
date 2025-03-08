from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserQuestionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    question_id: int
