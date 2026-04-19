from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from app.database import Base


class TestPlan(Base):

    __tablename__ = "test_plan"

    BATCH_ID = Column(Integer, primary_key=True, index=True)

    BATCH_NAME = Column(String(100))

    TASK_STATUS = Column(Integer)
    STATUS = Column(Integer)

    SEND_EMAIL = Column(Integer)

    PLAN_ID = Column(BigInteger, default=0)
    OMP_BATCH_ID = Column(BigInteger, default=0)

    PASS_RATE_SWITCH = Column(BigInteger, default=0)
    PASS_RATE = Column(String(6))

    RE_RUN = Column(BigInteger, default=0)

    DEFAULT_MSG_TO_LIST = Column(String(255))
    MSG_CC_LIST = Column(String(255))
    MSG_TO_LIST = Column(String(255))

    EXECUTION_MACHINE = Column(String(20))

    CREATE_DATE = Column(DateTime)
    FINISH_DATE = Column(DateTime)

    update_jira = Column(String(10))
    billing_issue = Column(Integer, default=0)

    CREATE_BUG = Column(String(10))