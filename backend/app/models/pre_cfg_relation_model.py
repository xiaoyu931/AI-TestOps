from sqlalchemy import Column, String
from app.database import Base


class PreCfgRelation(Base):

    __tablename__ = "pre_cfg_relation"

    preCfgId = Column(String(50), primary_key=True)
    cfgId = Column(String(50), primary_key=True)