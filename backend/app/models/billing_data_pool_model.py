from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from app.database import Base


class BillingTestDataPool(Base):

    __tablename__ = "Billing_test_data_pool"

    id = Column(BigInteger, primary_key=True, index=True)

    cfg_id = Column(String(50), index=True)

    testCaseName_str = Column(String(200))

    cust_id = Column(String(50), unique=True)
    account_id = Column(String(50))
    order_id = Column(String(50))

    status = Column(Integer, default=0)

    create_time = Column(DateTime)
    update_time = Column(DateTime)
    used_time = Column(DateTime)