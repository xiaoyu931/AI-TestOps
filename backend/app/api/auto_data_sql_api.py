from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models.auto_data_sql_uipath_model import AutoDataSqlUipath
from app.schemas.auto_data_sql_schema import (
    AutoSqlCreateRequest,
    AutoSqlListResponse,
    AutoSqlDetailResponse
)

router = APIRouter(prefix="/auto-sql", tags=["Auto SQL"])


@router.post("")
def create_sql(req: AutoSqlCreateRequest):

    db = SessionLocal()

    try:
        existing = db.query(AutoDataSqlUipath).filter(
            AutoDataSqlUipath.SQL_NAME == req.sql_name
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="SQL_NAME already exists")

        new_sql = AutoDataSqlUipath(
            SQL_NAME=req.sql_name,
            DB=req.db,
            SQL_CONTENT=req.sql_content
        )

        db.add(new_sql)
        db.commit()

        return {"message": "created"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

@router.get("", response_model=AutoSqlListResponse)
def get_sql_list():

    db = SessionLocal()

    try:
        items = db.query(AutoDataSqlUipath).all()

        result = []

        for i in items:
            result.append({
                "sql_name": i.SQL_NAME,
                "db": i.DB,
                "sql_content": i.SQL_CONTENT
            })

        return {
            "total": len(result),
            "data": result
        }

    finally:
        db.close()

@router.get("/{sql_name}", response_model=AutoSqlDetailResponse)
def get_sql(sql_name: str):

    db = SessionLocal()

    try:
        item = db.query(AutoDataSqlUipath).filter(
            AutoDataSqlUipath.SQL_NAME == sql_name
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Not found")

        return {
            "sql_name": item.SQL_NAME,
            "db": item.DB,
            "sql_content": item.SQL_CONTENT
        }

    finally:
        db.close()