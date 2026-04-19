from fastapi import APIRouter, HTTPException
from sqlalchemy import asc, desc
from app.database import SessionLocal
from app.models.test_parameter_model import TestParameter
from app.schemas.parameter_schema import (
    ParameterCreateRequest,
    ParameterUpdateRequest,
    ParameterListResponse,
    ParameterDetailResponse
)
from datetime import datetime

router = APIRouter(prefix="/parameters", tags=["Parameters"])


@router.post("")
def create_parameter(req: ParameterCreateRequest):
    db = SessionLocal()

    try:
        new_param = TestParameter(
            TEST_PARAMETER_NAME=req.parameter_name,
            PARAMETER_PATH=req.parameter_path,
            TEST_PARAMETER_TYPE=req.parameter_type,
            DEFAULT_VALUE=req.default_value,
            REMARK=req.remark,
            TENANT_ID=req.tenant_id,
            STATE=req.state,
            CREATE_DATE=datetime.now(),
            EXPIRE_DATE=datetime(2099, 12, 31, 23, 59, 59)
        )

        db.add(new_param)
        db.commit()
        db.refresh(new_param)

        return {
            "message": "success",
            "parameter_id": new_param.TEST_PARAMETER_ID
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("", response_model=ParameterListResponse)
def get_parameters(
    parameter_id: int = None,
    parameter_name: str = None,
    parameter_path: str = None,
    parameter_type: str = None,
    page: int = 1,
    page_size: int = 10,
    sort_field: str = "parameter_id",
    sort_order: str = "desc"
):
    db = SessionLocal()

    try:
        query = db.query(TestParameter)

        if parameter_id:
            query = query.filter(TestParameter.TEST_PARAMETER_ID == parameter_id)

        if parameter_name:
            query = query.filter(TestParameter.TEST_PARAMETER_NAME.like(f"%{parameter_name}%"))

        if parameter_path:
            query = query.filter(TestParameter.PARAMETER_PATH.like(f"%{parameter_path}%"))

        if parameter_type:
            query = query.filter(TestParameter.TEST_PARAMETER_TYPE.like(f"%{parameter_type}%"))

        sort_column = {
            "parameter_id": TestParameter.TEST_PARAMETER_ID,
            "parameter_name": TestParameter.TEST_PARAMETER_NAME,
            "parameter_path": TestParameter.PARAMETER_PATH,
            "parameter_type": TestParameter.TEST_PARAMETER_TYPE,
            "state": TestParameter.STATE,
            "create_date": TestParameter.CREATE_DATE
        }.get(sort_field.lower(), TestParameter.TEST_PARAMETER_ID)

        if sort_order == "asc":
            query = query.order_by(asc(sort_column), asc(TestParameter.TEST_PARAMETER_ID))
        else:
            query = query.order_by(desc(sort_column), desc(TestParameter.TEST_PARAMETER_ID))

        total = query.count()

        items = query.offset((page - 1) * page_size).limit(page_size).all()

        result = []
        for p in items:
            result.append({
                "parameter_id": p.TEST_PARAMETER_ID,
                "parameter_name": p.TEST_PARAMETER_NAME,
                "parameter_path": p.PARAMETER_PATH,
                "parameter_type": p.TEST_PARAMETER_TYPE,
                "default_value": p.DEFAULT_VALUE,
                "remark": p.REMARK,
                "tenant_id": p.TENANT_ID,
                "state": p.STATE,
                "active": p.STATE == 1,
                "create_date": p.CREATE_DATE
            })

        return {"total": total, "data": result}

    finally:
        db.close()


@router.get("/{parameter_id}", response_model=ParameterDetailResponse)
def get_parameter_detail(parameter_id: int):
    db = SessionLocal()

    try:
        p = db.query(TestParameter).filter(
            TestParameter.TEST_PARAMETER_ID == parameter_id
        ).first()

        if not p:
            raise HTTPException(status_code=404, detail="Parameter not found")

        return {
            "parameter_id": p.TEST_PARAMETER_ID,
            "parameter_name": p.TEST_PARAMETER_NAME,
            "parameter_path": p.PARAMETER_PATH,
            "parameter_type": p.TEST_PARAMETER_TYPE,
            "default_value": p.DEFAULT_VALUE,
            "remark": p.REMARK,
            "tenant_id": p.TENANT_ID,
            "state": p.STATE or 0,
            "create_date": p.CREATE_DATE,
            "update_date": p.UPDATE_DATE
        }

    finally:
        db.close()


@router.put("/{parameter_id}")
def update_parameter(parameter_id: int, req: ParameterUpdateRequest):
    db = SessionLocal()

    try:
        p = db.query(TestParameter).filter(
            TestParameter.TEST_PARAMETER_ID == parameter_id
        ).first()

        if not p:
            raise HTTPException(status_code=404, detail="Parameter not found")

        p.TEST_PARAMETER_NAME = req.parameter_name
        p.PARAMETER_PATH = req.parameter_path
        p.TEST_PARAMETER_TYPE = req.parameter_type
        p.DEFAULT_VALUE = req.default_value
        p.REMARK = req.remark
        p.TENANT_ID = req.tenant_id
        p.STATE = req.state
        p.UPDATE_DATE = datetime.now()

        db.commit()

        return {"message": "updated", "parameter_id": parameter_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.delete("/{parameter_id}")
def delete_parameter(parameter_id: int):
    db = SessionLocal()

    try:
        p = db.query(TestParameter).filter(
            TestParameter.TEST_PARAMETER_ID == parameter_id
        ).first()

        if not p:
            raise HTTPException(status_code=404, detail="Parameter not found")

        db.delete(p)
        db.commit()

        return {"message": "deleted", "parameter_id": parameter_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()