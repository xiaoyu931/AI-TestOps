from sqlalchemy import Column, BigInteger, String, DateTime
from app.database import Base


class TestComponentParameter(Base):

    __tablename__ = "test_component_parameter"

    TEST_COMPONENT_PARAMETER_ID = Column(BigInteger, primary_key=True, index=True)

    TEST_COMPONENT_ID = Column(BigInteger)
    TEST_PARAMETER_ID = Column(BigInteger)

    SORT = Column(BigInteger)

    REMARK = Column(String(400))

    TENANT_ID = Column(String(6))
    STATE = Column(BigInteger, default=1)

    CREATE_DATE = Column(DateTime)
    EXPIRE_DATE = Column(DateTime)
    UPDATE_DATE = Column(DateTime)