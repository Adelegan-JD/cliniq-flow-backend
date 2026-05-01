from pydantic import BaseModel

class BookingCreate(BaseModel):
    property_id: int
    tenant_id: int

class BookingOut(BaseModel):
    id: int
    property_id: int
    tenant_id: int
    status: str

    class Config:
        from_attributes = True
