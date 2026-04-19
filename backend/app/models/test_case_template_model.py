from sqlalchemy import Column, BigInteger, String, DateTime
from app.database import Base


class TestCaseTemplate(Base):

    __tablename__ = "test_case_template"

    TEST_CASE_TEMPLATE_ID = Column(BigInteger, primary_key=True, autoincrement=True)

    TEST_CASE_NAME = Column(String(50))
    TEST_CASE_TYPE = Column(String(10))
    MODULE = Column(String(50))
    IS_BROWSER = Column(BigInteger)
    REMARK = Column(String(400))
    TENANT_ID = Column(String(6))
    STATE = Column(BigInteger)

    CREATE_DATE = Column(DateTime)
    EXPIRE_DATE = Column(DateTime)
    UPDATE_DATE = Column(DateTime)