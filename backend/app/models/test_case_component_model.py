from sqlalchemy import Column, BigInteger, String, DateTime
from app.database import Base


class TestCaseComponent(Base):

    __tablename__ = "test_case_component"

    TEST_CASE_COMPONENT_ID = Column(BigInteger, primary_key=True, autoincrement=True)

    TEST_CASE_TEMPLATE_ID = Column(BigInteger)
    TEST_COMPONENT_ID = Column(BigInteger)

    SORT = Column(BigInteger)
    WAIT_TIME = Column(BigInteger)
    LOOP_NUM = Column(BigInteger)

    IS_SUSPEND = Column(String(10))
    REMARK = Column(String(400))
    TENANT_ID = Column(String(6))
    STATE = Column(BigInteger)

    CREATE_DATE = Column(DateTime)
    EXPIRE_DATE = Column(DateTime)
    UPDATE_DATE = Column(DateTime)