from sqlalchemy import Column, String
from app.database import Base


class AutoDataSqlUipath(Base):

    __tablename__ = "AUTO_DATA_SQL_UIPATH"

    SQL_NAME = Column(String(127), primary_key=True)

    DB = Column(String(45))
    SQL_CONTENT = Column(String(10239))