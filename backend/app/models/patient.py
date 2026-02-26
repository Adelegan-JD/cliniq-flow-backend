from sqlalchemy import Column, String, Date
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Patient(BaseModel):
    __tablename__ = "patients"

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    address = Column(String, nullable=True)

    visits = relationship("Visit", back_populates="patient")
