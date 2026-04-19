from sqlalchemy import Column, BigInteger, String, DateTime
from app.database import Base


class TestComponent(Base):

    __tablename__ = "test_component"

    TEST_COMPONENT_ID = Column(BigInteger, primary_key=True, index=True)

    TEST_COMPONENT_NAME = Column(String(50))
    TEST_COMPONENT_TYPE = Column(String(10))
    TEST_COMPONENT_FILE = Column(String(200))

    REMARK = Column(String(400))

    TENANT_ID = Column(String(6))
    STATE = Column(BigInteger, default=1)

    CREATE_DATE = Column(DateTime)
    EXPIRE_DATE = Column(DateTime)
    UPDATE_DATE = Column(DateTime)