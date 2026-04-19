from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# T0
# DATABASE_URL = "mysql+pymysql://autotest_data:auto1234@10.1.248.187:3306/autotest_data"
# Local
DATABASE_URL = "mysql+pymysql://root:Yuhongyi850623!@localhost:3306/autotest_data"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()