from sqlalchemy import Column, BigInteger, String, DateTime, Text
from app.database import Base


class TestCaseExecution(Base):

    __tablename__ = "test_case_execution"

    TEST_CASE_EXE_ID = Column(BigInteger, primary_key=True, index=True)

    REL_CASE_EXE_ID = Column(BigInteger)
    CFG_ID = Column(BigInteger)
    TEST_CASE_TEMPLATE_ID = Column(BigInteger)

    TEST_CASE_NAME = Column(String(100))
    TEST_INST_ID = Column(String(50))

    EXECUTION_ENVIRONMENT = Column(String(10))
    EXECUTION_MACHINE = Column(String(20))

    IS_PRE_TASK = Column(BigInteger)
    STATE = Column(BigInteger)

    OMP_BATCH_ID = Column(BigInteger)

    SOURCE_DATA = Column(Text)
    TEST_RESULT_DATA = Column(Text)
    ERROR_MESSAGE = Column(Text)

    TENANT_ID = Column(String(6))

    CREATE_DATE = Column(DateTime)
    FINISH_DATE = Column(DateTime)

    CASE_ID = Column(BigInteger)
    PLAN_ID = Column(BigInteger)
    TASK_STATUS = Column(BigInteger)