from sqlalchemy import Column, BigInteger, String, DateTime
from app.database import Base


class TestCaseTask(Base):

    __tablename__ = "cfg_test_case_task"

    CFG_ID = Column(BigInteger, primary_key=True, index=True)

    TEST_CASE_TEMPLATE_ID = Column(BigInteger)
    TEST_CASE_NAME = Column(String(200))

    VERIFY_TEST_CASE_TEMPLATE_ID = Column(BigInteger)
    VERIFY_TEST_CASE_NAME = Column(String(50))

    TRIGGER_MODE = Column(BigInteger)
    CRON_EXPRESSION = Column(String(20))

    TASK_STATUS = Column(BigInteger)

    TENANT_ID = Column(String(6))
    STATE = Column(BigInteger)

    CREATE_DATE = Column(DateTime)
    EXPIRE_DATE = Column(DateTime)

    TEST_INST_ID = Column(String(50))

    EXECUTION_ENVIRONMENT = Column(String(10))
    EXECUTION_MACHINE = Column(String(20))

    UIPATH_ENTRY = Column(String(200))
    UIPATH_CASE_NAME = Column(String(100))

    CASE_ID = Column(String(100))