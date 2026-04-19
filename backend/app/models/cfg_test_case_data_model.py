from sqlalchemy import Column, BigInteger, String, DateTime, Text
from app.database import Base


class TestCaseData(Base):

    __tablename__ = "cfg_test_case_data"

    CFG_DATA_ID = Column(BigInteger, primary_key=True, index=True)

    CFG_ID = Column(BigInteger)

    TEST_CASE_TEMPLATE_ID = Column(BigInteger)

    TEST_DATA = Column(Text)

    TENANT_ID = Column(String(6))
    STATE = Column(BigInteger)

    UIPATH_FLAG = Column(BigInteger)

    CREATE_DATE = Column(DateTime)
    EXPIRE_DATE = Column(DateTime)