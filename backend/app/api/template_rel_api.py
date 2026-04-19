from fastapi import APIRouter, HTTPException
from sqlalchemy import asc, desc
from datetime import datetime

from app.database import SessionLocal
from app.models.test_case_template_rel_model import TestCaseTemplateRel
from app.schemas.template_rel_schema import (
    TemplateRelCreateRequest,
    TemplateRelUpdateRequest,
    TemplateRelListResponse,
    TemplateRelDetailResponse
)

router = APIRouter(prefix="/template-relations", tags=["Template Relations"])


@router.post("")
def create_template_relation(req: TemplateRelCreateRequest):
    db = SessionLocal()
    try:
        obj = TestCaseTemplateRel(
            TEST_CASE_TEMPLATE_ID=req.test_case_template_id,
            PRE_TEST_CASE_TEMPLATE_ID=req.pre_test_case_template_id,
            TENANT_ID=req.tenant_id,
            STATE=req.state,
            CREATE_DATE=datetime.now(),
            EXPIRE_DATE=datetime(2099, 12, 31, 23, 59, 59)
        )

        db.add(obj)
        db.commit()
        db.refresh(obj)

        return {
            "message": "success",
            "rel_id": obj.TEST_CASE_TEMPLATE_REL_ID
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("", response_model=TemplateRelListResponse)
def get_template_relations(
    rel_id: int = None,
    test_case_template_id: int = None,
    pre_test_case_template_id: int = None,
    page: int = 1,
    page_size: int = 10,
    sort_field: str = "rel_id",
    sort_order: str = "desc"
):
    db = SessionLocal()
    try:
        query = db.query(TestCaseTemplateRel)

        if rel_id:
            query = query.filter(
                TestCaseTemplateRel.TEST_CASE_TEMPLATE_REL_ID == rel_id
            )

        if test_case_template_id:
            query = query.filter(
                TestCaseTemplateRel.TEST_CASE_TEMPLATE_ID == test_case_template_id
            )

        if pre_test_case_template_id:
            query = query.filter(
                TestCaseTemplateRel.PRE_TEST_CASE_TEMPLATE_ID == pre_test_case_template_id
            )

        sort_column = {
            "rel_id": TestCaseTemplateRel.TEST_CASE_TEMPLATE_REL_ID,
            "test_case_template_id": TestCaseTemplateRel.TEST_CASE_TEMPLATE_ID,
            "pre_test_case_template_id": TestCaseTemplateRel.PRE_TEST_CASE_TEMPLATE_ID,
            "tenant_id": TestCaseTemplateRel.TENANT_ID,
            "state": TestCaseTemplateRel.STATE,
            "create_date": TestCaseTemplateRel.CREATE_DATE
        }.get(sort_field.lower(), TestCaseTemplateRel.TEST_CASE_TEMPLATE_REL_ID)

        if sort_order == "asc":
            query = query.order_by(
                asc(sort_column),
                asc(TestCaseTemplateRel.TEST_CASE_TEMPLATE_REL_ID)
            )
        else:
            query = query.order_by(
                desc(sort_column),
                desc(TestCaseTemplateRel.TEST_CASE_TEMPLATE_REL_ID)
            )

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        result = []
        for x in items:
            result.append({
                "rel_id": x.TEST_CASE_TEMPLATE_REL_ID,
                "test_case_template_id": x.TEST_CASE_TEMPLATE_ID,
                "pre_test_case_template_id": x.PRE_TEST_CASE_TEMPLATE_ID,
                "tenant_id": x.TENANT_ID,
                "state": x.STATE or 0,
                "create_date": x.CREATE_DATE
            })

        return {
            "total": total,
            "data": result
        }

    finally:
        db.close()


@router.get("/{rel_id}", response_model=TemplateRelDetailResponse)
def get_template_relation_detail(rel_id: int):
    db = SessionLocal()
    try:
        x = db.query(TestCaseTemplateRel).filter(
            TestCaseTemplateRel.TEST_CASE_TEMPLATE_REL_ID == rel_id
        ).first()

        if not x:
            raise HTTPException(status_code=404, detail="Relation not found")

        return {
            "rel_id": x.TEST_CASE_TEMPLATE_REL_ID,
            "test_case_template_id": x.TEST_CASE_TEMPLATE_ID,
            "pre_test_case_template_id": x.PRE_TEST_CASE_TEMPLATE_ID,
            "tenant_id": x.TENANT_ID,
            "state": x.STATE or 0,
            "create_date": x.CREATE_DATE
        }

    finally:
        db.close()


@router.put("/{rel_id}")
def update_template_relation(rel_id: int, req: TemplateRelUpdateRequest):
    db = SessionLocal()
    try:
        x = db.query(TestCaseTemplateRel).filter(
            TestCaseTemplateRel.TEST_CASE_TEMPLATE_REL_ID == rel_id
        ).first()

        if not x:
            raise HTTPException(status_code=404, detail="Relation not found")

        x.TEST_CASE_TEMPLATE_ID = req.test_case_template_id
        x.PRE_TEST_CASE_TEMPLATE_ID = req.pre_test_case_template_id
        x.TENANT_ID = req.tenant_id
        x.STATE = req.state

        db.commit()

        return {
            "message": "updated",
            "rel_id": rel_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.delete("/{rel_id}")
def delete_template_relation(rel_id: int):
    db = SessionLocal()
    try:
        x = db.query(TestCaseTemplateRel).filter(
            TestCaseTemplateRel.TEST_CASE_TEMPLATE_REL_ID == rel_id
        ).first()

        if not x:
            raise HTTPException(status_code=404, detail="Relation not found")

        db.delete(x)
        db.commit()

        return {
            "message": "deleted",
            "rel_id": rel_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()