from sqlalchemy import Column, BigInteger, String, DateTime, Text
from app.database import Base


class TestDispatcherData(Base):

    __tablename__ = "test_dispatcher_data"

    DISPATCHER_PLAN_ID = Column(BigInteger, primary_key=True, index=True)

    QUE_NAME = Column(String(100))
    EXE_MACHINE = Column(String(100))
    PLAN_ID = Column(BigInteger, default=0)

    BATCH_NAME = Column(String(100))

    SEND_EMAIL = Column(BigInteger)
    PASS_RATE_SWITCH = Column(BigInteger)
    PASS_RATE = Column(String(6))

    DEFAULT_MSG_TO_LIST = Column(String(255))
    MSG_CC_LIST = Column(String(255))
    MSG_TO_LIST = Column(String(255))

    CASE_LIST = Column(Text)
    ACTUAL_CASE_LIST = Column(Text)

    EXPLANATION = Column(String(100))

    CREATE_DATE = Column(DateTime)
    EXPIRE_DATE = Column(DateTime)

    UPDATE_JIRA = Column(String(10))
    CREATE_BUG = Column(String(6))

    UIPATH_EXE_MACHONE = Column(String(20))