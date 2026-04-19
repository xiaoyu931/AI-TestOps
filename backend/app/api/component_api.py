from fastapi import APIRouter, HTTPException
from sqlalchemy import asc, desc
from app.database import SessionLocal
from app.models.test_component_model import TestComponent
from app.schemas.component_schema import (
    ComponentCreateRequest,
    ComponentUpdateRequest,
    ComponentListResponse,
    ComponentDetailResponse
)
from datetime import datetime

router = APIRouter(prefix="/components", tags=["Components"])


@router.post("")
def create_component(req: ComponentCreateRequest):
    db = SessionLocal()

    try:
        new_component = TestComponent(
            TEST_COMPONENT_NAME=req.component_name,
            TEST_COMPONENT_TYPE=req.component_type,
            TEST_COMPONENT_FILE=req.component_file,
            REMARK=req.remark,
            TENANT_ID=req.tenant_id,
            STATE=req.state,
            CREATE_DATE=datetime.now(),
            EXPIRE_DATE=datetime(2099, 12, 31, 23, 59, 59)
        )

        db.add(new_component)
        db.commit()
        db.refresh(new_component)

        return {
            "message": "success",
            "component_id": new_component.TEST_COMPONENT_ID
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("", response_model=ComponentListResponse)
def get_components(
    component_id: int = None,
    component_name: str = None,
    component_type: str = None,
    component_file: str = None,
    page: int = 1,
    page_size: int = 10,
    sort_field: str = "component_id",
    sort_order: str = "desc"
):
    db = SessionLocal()

    try:
        query = db.query(TestComponent)

        if component_id:
            query = query.filter(TestComponent.TEST_COMPONENT_ID == component_id)

        if component_name:
            query = query.filter(TestComponent.TEST_COMPONENT_NAME.like(f"%{component_name}%"))

        if component_type:
            query = query.filter(TestComponent.TEST_COMPONENT_TYPE.like(f"%{component_type}%"))

        if component_file:
            query = query.filter(TestComponent.TEST_COMPONENT_FILE.like(f"%{component_file}%"))

        sort_column = {
            "component_id": TestComponent.TEST_COMPONENT_ID,
            "component_name": TestComponent.TEST_COMPONENT_NAME,
            "component_type": TestComponent.TEST_COMPONENT_TYPE,
            "component_file": TestComponent.TEST_COMPONENT_FILE,
            "state": TestComponent.STATE,
            "create_date": TestComponent.CREATE_DATE
        }.get(sort_field.lower(), TestComponent.TEST_COMPONENT_ID)

        if sort_order == "asc":
            query = query.order_by(asc(sort_column), asc(TestComponent.TEST_COMPONENT_ID))
        else:
            query = query.order_by(desc(sort_column), desc(TestComponent.TEST_COMPONENT_ID))

        total = query.count()

        tasks = query.offset((page - 1) * page_size).limit(page_size).all()

        result = []
        for c in tasks:
            result.append({
                "component_id": c.TEST_COMPONENT_ID,
                "component_name": c.TEST_COMPONENT_NAME,
                "component_type": c.TEST_COMPONENT_TYPE,
                "component_file": c.TEST_COMPONENT_FILE,
                "remark": c.REMARK,
                "tenant_id": c.TENANT_ID,
                "state": c.STATE,
                "active": c.STATE == 1,
                "create_date": c.CREATE_DATE
            })

        return {"total": total, "data": result}

    finally:
        db.close()


@router.get("/{component_id}", response_model=ComponentDetailResponse)
def get_component_detail(component_id: int):
    db = SessionLocal()

    try:
        c = db.query(TestComponent).filter(
            TestComponent.TEST_COMPONENT_ID == component_id
        ).first()

        if not c:
            raise HTTPException(status_code=404, detail="Component not found")

        return {
            "component_id": c.TEST_COMPONENT_ID,
            "component_name": c.TEST_COMPONENT_NAME,
            "component_type": c.TEST_COMPONENT_TYPE,
            "component_file": c.TEST_COMPONENT_FILE,
            "remark": c.REMARK,
            "tenant_id": c.TENANT_ID,
            "state": c.STATE,
            "create_date": c.CREATE_DATE,
            "update_date": c.UPDATE_DATE
        }

    finally:
        db.close()


@router.put("/{component_id}")
def update_component(component_id: int, req: ComponentUpdateRequest):
    db = SessionLocal()

    try:
        c = db.query(TestComponent).filter(
            TestComponent.TEST_COMPONENT_ID == component_id
        ).first()

        if not c:
            raise HTTPException(status_code=404, detail="Component not found")

        c.TEST_COMPONENT_NAME = req.component_name
        c.TEST_COMPONENT_TYPE = req.component_type
        c.TEST_COMPONENT_FILE = req.component_file
        c.REMARK = req.remark
        c.TENANT_ID = req.tenant_id
        c.STATE = req.state
        c.UPDATE_DATE = datetime.now()

        db.commit()

        return {"message": "updated", "component_id": component_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.delete("/{component_id}")
def delete_component(component_id: int):
    db = SessionLocal()

    try:
        c = db.query(TestComponent).filter(
            TestComponent.TEST_COMPONENT_ID == component_id
        ).first()

        if not c:
            raise HTTPException(status_code=404, detail="Component not found")

        db.delete(c)
        db.commit()

        return {"message": "deleted", "component_id": component_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()