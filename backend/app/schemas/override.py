from pydantic import BaseModel
from uuid import UUID


class OverrideCreate(BaseModel):
    visit_id: UUID
    overridden_field: str
    original_value: str | None = None
    new_value: str | None = None
    reason: str | None = None
    doctor_id: str | None = None
