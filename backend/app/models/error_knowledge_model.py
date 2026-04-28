from sqlalchemy import Column, DateTime, Integer, String, Text
from app.database import Base


class ErrorKnowledge(Base):

    __tablename__ = "error_knowledge"

    id = Column(Integer, primary_key=True, index=True)
    error_type = Column(String(100))
    root_cause = Column(String(255))
    solution = Column(Text)
    category = Column(String(100))
    confidence = Column(String(20))
    source = Column(String(50))
    created_at = Column(DateTime)
