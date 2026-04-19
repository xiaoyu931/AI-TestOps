from sqlalchemy import Column, BigInteger, String, DateTime
from app.database import Base


class TestParameter(Base):

    __tablename__ = "test_parameter"

    TEST_PARAMETER_ID = Column(BigInteger, primary_key=True, index=True)

    TEST_PARAMETER_NAME = Column(String(50))
    PARAMETER_PATH = Column(String(200))

    TEST_PARAMETER_TYPE = Column(String(10))
    DEFAULT_VALUE = Column(String(100))

    REMARK = Column(String(400))

    TENANT_ID = Column(String(6))
    STATE = Column(BigInteger, default=1)

    CREATE_DATE = Column(DateTime)
    EXPIRE_DATE = Column(DateTime)
    UPDATE_DATE = Column(DateTime)