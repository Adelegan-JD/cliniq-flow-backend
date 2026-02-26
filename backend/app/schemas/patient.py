from pydantic import BaseModel
from datetime import date
from uuid import UUID


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    phone_number: str | None = None
    address: str | None = None


class PatientResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    phone_number: str | None
    address: str | None

    class Config:
        from_attributes = True
