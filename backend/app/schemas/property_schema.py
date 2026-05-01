from pydantic import BaseModel

class PropertyCreate(BaseModel):
    title: str
    location: str
    price: int
    image_url: str | None = None

class PropertyOut(PropertyCreate):
    id: int
    agent_id: int

    class Config:
        from_attributes = True
