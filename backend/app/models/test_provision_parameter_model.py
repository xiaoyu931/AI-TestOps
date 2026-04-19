from sqlalchemy import Column, Integer, String
from app.database import Base


class TestProvisionParameter(Base):

    __tablename__ = "TEST_PROVISION_PARAMETER"

    provision_seq_id = Column(Integer, primary_key=True, index=True)

    action_id = Column(Integer)
    platform_code = Column(String(20))
    provision_type = Column(String(200))

    provision_Mandatory_aram = Column(String(1000))
    provision_optional_aram = Column(String(1000))

    state = Column(String(2))

    ext1 = Column(String(1000))
    ext2 = Column(String(1000))
    ext3 = Column(String(1000))

    product_line = Column(String(20))
    veris_code_status = Column(String(20))
    platform = Column(String(20))