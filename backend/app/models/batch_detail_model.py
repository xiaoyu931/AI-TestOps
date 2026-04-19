from sqlalchemy import Column, Integer, DateTime
from app.database import Base


class BatchDetail(Base):

    __tablename__ = "batch_detail"

    BATCH_DETAIL_ID = Column(Integer, primary_key=True, index=True)

    BATCH_ID = Column(Integer)
    CFG_ID = Column(Integer)

    UIPATH_CASE_EXE_ID = Column(Integer)
    ORDER_CASE_EXE_ID = Column(Integer)
    VERIFY_CASE_EXE_ID = Column(Integer)

    STATUS = Column(Integer)
    TASK_STATUS = Column(Integer)

    CREATE_DATE = Column(DateTime)
    FINISH_DATE = Column(DateTime)