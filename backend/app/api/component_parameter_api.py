from fastapi import APIRouter, HTTPException
from sqlalchemy import asc, desc
from app.database import SessionLocal
from app.models.test_component_parameter_model import TestComponentParameter
from app.schemas.component_parameter_schema import (
    ComponentParameterCreateRequest,
    ComponentParameterUpdateRequest,
    ComponentParameterListResponse,
    ComponentParameterDetailResponse
)
from datetime import datetime

router = APIRouter(prefix="/component-parameters", tags=["Component Parameters"])


@router.post("")
def create_component_parameter(req: ComponentParameterCreateRequest):
    db = SessionLocal()

    try:
        new_item = TestComponentParameter(
            TEST_COMPONENT_ID=req.component_id,
            TEST_PARAMETER_ID=req.parameter_id,
            SORT=req.sort,
            REMARK=req.remark,
            TENANT_ID=req.tenant_id,
            STATE=req.state,
            CREATE_DATE=datetime.now(),
            EXPIRE_DATE=datetime(2099, 12, 31, 23, 59, 59)
        )

        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        return {
            "message": "success",
            "id": new_item.TEST_COMPONENT_PARAMETER_ID
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("", response_model=ComponentParameterListResponse)
def get_component_parameters(
    id: int = None,
    component_id: int = None,
    parameter_id: int = None,
    page: int = 1,
    page_size: int = 10,
    sort_field: str = "id",
    sort_order: str = "desc"
):
    db = SessionLocal()

    try:
        query = db.query(TestComponentParameter)

        if id:
            query = query.filter(TestComponentParameter.TEST_COMPONENT_PARAMETER_ID == id)

        if component_id:
            query = query.filter(TestComponentParameter.TEST_COMPONENT_ID == component_id)

        if parameter_id:
            query = query.filter(TestComponentParameter.TEST_PARAMETER_ID == parameter_id)

        sort_column = {
            "id": TestComponentParameter.TEST_COMPONENT_PARAMETER_ID,
            "component_id": TestComponentParameter.TEST_COMPONENT_ID,
            "parameter_id": TestComponentParameter.TEST_PARAMETER_ID,
            "sort": TestComponentParameter.SORT,
            "state": TestComponentParameter.STATE,
            "create_date": TestComponentParameter.CREATE_DATE
        }.get(sort_field.lower(), TestComponentParameter.TEST_COMPONENT_PARAMETER_ID)

        if sort_order == "asc":
            query = query.order_by(asc(sort_column), asc(TestComponentParameter.TEST_COMPONENT_PARAMETER_ID))
        else:
            query = query.order_by(desc(sort_column), desc(TestComponentParameter.TEST_COMPONENT_PARAMETER_ID))

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        result = []
        for i in items:
            result.append({
                "id": i.TEST_COMPONENT_PARAMETER_ID,
                "component_id": i.TEST_COMPONENT_ID,
                "parameter_id": i.TEST_PARAMETER_ID,
                "sort": i.SORT,
                "remark": i.REMARK,
                "tenant_id": i.TENANT_ID,
                "state": i.STATE,
                "active": i.STATE == 1,
                "create_date": i.CREATE_DATE
            })

        return {"total": total, "data": result}

    finally:
        db.close()


@router.get("/{id}", response_model=ComponentParameterDetailResponse)
def get_component_parameter(id: int):
    db = SessionLocal()

    try:
        item = db.query(TestComponentParameter).filter(
            TestComponentParameter.TEST_COMPONENT_PARAMETER_ID == id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Not found")

        return {
            "id": item.TEST_COMPONENT_PARAMETER_ID,
            "component_id": item.TEST_COMPONENT_ID,
            "parameter_id": item.TEST_PARAMETER_ID,
            "sort": item.SORT,
            "remark": item.REMARK,
            "tenant_id": item.TENANT_ID,
            "state": item.STATE,
            "create_date": item.CREATE_DATE,
            "update_date": item.UPDATE_DATE
        }

    finally:
        db.close()


@router.put("/{id}")
def update_component_parameter(id: int, req: ComponentParameterUpdateRequest):
    db = SessionLocal()

    try:
        item = db.query(TestComponentParameter).filter(
            TestComponentParameter.TEST_COMPONENT_PARAMETER_ID == id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Not found")

        item.TEST_COMPONENT_ID = req.component_id
        item.TEST_PARAMETER_ID = req.parameter_id
        item.SORT = req.sort
        item.REMARK = req.remark
        item.TENANT_ID = req.tenant_id
        item.STATE = req.state
        item.UPDATE_DATE = datetime.now()

        db.commit()

        return {"message": "updated", "id": id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.delete("/{id}")
def delete_component_parameter(id: int):
    db = SessionLocal()

    try:
        item = db.query(TestComponentParameter).filter(
            TestComponentParameter.TEST_COMPONENT_PARAMETER_ID == id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Not found")

        db.delete(item)
        db.commit()

        return {"message": "deleted", "id": id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()