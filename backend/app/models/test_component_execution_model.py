from sqlalchemy import Column, BigInteger, String, DateTime, Text
from app.database import Base


class TestComponentExecution(Base):

    __tablename__ = "test_component_execution"

    TEST_COMPONENT_EXE_ID = Column(BigInteger, primary_key=True, index=True)

    TEST_CASE_EXE_ID = Column(BigInteger, index=True)
    TEST_CASE_TEMPLATE_ID = Column(BigInteger)

    TEST_COMPONENT_ID = Column(BigInteger)
    TEST_COMPONENT_NAME = Column(String(50))

    STATE = Column(BigInteger)

    COMPONENT_IN_PARAM = Column(Text)
    COMPONENT_RESULT_DATA = Column(Text)

    PYTHON_ERROR_MESSAGE = Column(Text)
    SYSTEM_ERROR_MESSAGE = Column(Text)

    TENANT_ID = Column(String(6))

    CREATE_DATE = Column(DateTime)
    FINISH_DATE = Column(DateTime)