from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Property(Base):
    __tablename__ = 'properties'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    location = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=False)
