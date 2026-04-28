from sqlalchemy import Boolean, Column, DateTime, Integer, String
from app.database import Base


class ErrorRule(Base):

    __tablename__ = "error_rules"

    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String(255))
    match_text = Column(String(255))
    error_type = Column(String(100))
    root_cause = Column(String(255))
    priority = Column(Integer)
    is_active = Column(Boolean)
    source = Column(String(50))
    created_at = Column(DateTime)
