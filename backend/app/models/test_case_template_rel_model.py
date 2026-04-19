from sqlalchemy import Column, Integer, DateTime
from app.database import Base


class TestCaseTemplateRel(Base):
    __tablename__ = "test_case_template_rel"

    TEST_CASE_TEMPLATE_REL_ID = Column(Integer, primary_key=True, index=True)
    TEST_CASE_TEMPLATE_ID = Column(Integer)
    PRE_TEST_CASE_TEMPLATE_ID = Column(Integer)
    TENANT_ID = Column(Integer)
    STATE = Column(Integer)
    CREATE_DATE = Column(DateTime)
    EXPIRE_DATE = Column(DateTime)