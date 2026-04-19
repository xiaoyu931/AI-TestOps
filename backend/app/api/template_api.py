from fastapi import APIRouter, HTTPException
from sqlalchemy import asc, desc
from app.database import SessionLocal
from datetime import datetime

from app.models.test_case_template_model import TestCaseTemplate
from app.models.test_case_component_model import TestCaseComponent
from app.schemas.template_schema import TemplateCreateRequest, TemplateUpdateRequest

router = APIRouter(tags=["Template"])


@router.post("/templates")
def create_template(req: TemplateCreateRequest):
    db = SessionLocal()

    try:
        if not req.components:
            raise HTTPException(status_code=400, detail="components cannot be empty")

        template = TestCaseTemplate(
            TEST_CASE_NAME=req.template_name,
            TEST_CASE_TYPE=req.test_case_type,
            MODULE=req.module,
            IS_BROWSER=req.is_browser,
            REMARK=req.remark,
            TENANT_ID=req.tenant_id,
            STATE=req.state,
            CREATE_DATE=datetime.now(),
            EXPIRE_DATE=datetime(2099, 12, 31, 23, 59, 59),
            UPDATE_DATE=datetime.now()
        )

        db.add(template)
        db.flush()

        for comp in req.components:
            relation = TestCaseComponent(
                TEST_CASE_TEMPLATE_ID=template.TEST_CASE_TEMPLATE_ID,
                TEST_COMPONENT_ID=comp.component_id,
                SORT=comp.sort,
                WAIT_TIME=comp.wait_time,
                LOOP_NUM=comp.loop_num,
                IS_SUSPEND=comp.is_suspend,
                REMARK=comp.remark,
                TENANT_ID=req.tenant_id,
                STATE=req.state,
                CREATE_DATE=datetime.now(),
                EXPIRE_DATE=datetime(2099, 12, 31, 23, 59, 59),
                UPDATE_DATE=datetime.now()
            )
            db.add(relation)

        db.commit()

        return {
            "message": "Template created successfully",
            "template_id": template.TEST_CASE_TEMPLATE_ID
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/templates")
def get_templates(
    template_id: int = None,
    template_name: str = None,
    module: str = None,
    test_case_type: str = None,
    page: int = 1,
    page_size: int = 10,
    sort_field: str = "template_id",
    sort_order: str = "desc"
):
    db = SessionLocal()

    try:
        query = db.query(TestCaseTemplate)

        if template_id:
            query = query.filter(TestCaseTemplate.TEST_CASE_TEMPLATE_ID == template_id)

        if template_name:
            query = query.filter(TestCaseTemplate.TEST_CASE_NAME.like(f"%{template_name}%"))

        if module:
            query = query.filter(TestCaseTemplate.MODULE.like(f"%{module}%"))

        if test_case_type:
            query = query.filter(TestCaseTemplate.TEST_CASE_TYPE == test_case_type)

        sort_column = {
            "template_id": TestCaseTemplate.TEST_CASE_TEMPLATE_ID,
            "template_name": TestCaseTemplate.TEST_CASE_NAME,
            "module": TestCaseTemplate.MODULE,
            "test_case_type": TestCaseTemplate.TEST_CASE_TYPE,
            "state": TestCaseTemplate.STATE,
            "create_date": TestCaseTemplate.CREATE_DATE
        }.get(sort_field.lower(), TestCaseTemplate.TEST_CASE_TEMPLATE_ID)

        if sort_order == "asc":
            query = query.order_by(asc(sort_column), asc(TestCaseTemplate.TEST_CASE_TEMPLATE_ID))
        else:
            query = query.order_by(desc(sort_column), desc(TestCaseTemplate.TEST_CASE_TEMPLATE_ID))

        total = query.count()
        templates = query.offset((page - 1) * page_size).limit(page_size).all()

        result = []

        for t in templates:
            result.append({
                "template_id": t.TEST_CASE_TEMPLATE_ID,
                "template_name": t.TEST_CASE_NAME,
                "test_case_type": t.TEST_CASE_TYPE,
                "module": t.MODULE,
                "is_browser": t.IS_BROWSER,
                "tenant_id": t.TENANT_ID,
                "state": t.STATE,
                "remark": t.REMARK,
                "create_date": t.CREATE_DATE
            })

        return {
            "total": total,
            "data": result
        }

    finally:
        db.close()


@router.get("/templates/{template_id}")
def get_template_detail(template_id: int):
    db = SessionLocal()

    try:
        template = db.query(TestCaseTemplate).filter(
            TestCaseTemplate.TEST_CASE_TEMPLATE_ID == template_id
        ).first()

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        components = db.query(TestCaseComponent).filter(
            TestCaseComponent.TEST_CASE_TEMPLATE_ID == template_id
        ).order_by(TestCaseComponent.SORT.asc()).all()

        component_list = []

        for c in components:
            component_list.append({
                "test_case_component_id": c.TEST_CASE_COMPONENT_ID,
                "component_id": c.TEST_COMPONENT_ID,
                "sort": c.SORT,
                "wait_time": c.WAIT_TIME,
                "loop_num": c.LOOP_NUM,
                "is_suspend": c.IS_SUSPEND,
                "remark": c.REMARK
            })

        return {
            "template_id": template.TEST_CASE_TEMPLATE_ID,
            "template_name": template.TEST_CASE_NAME,
            "test_case_type": template.TEST_CASE_TYPE,
            "module": template.MODULE,
            "is_browser": template.IS_BROWSER,
            "remark": template.REMARK,
            "tenant_id": template.TENANT_ID,
            "state": template.STATE,
            "create_date": template.CREATE_DATE,
            "components": component_list
        }

    finally:
        db.close()


@router.put("/templates/{template_id}")
def update_template(template_id: int, req: TemplateUpdateRequest):
    db = SessionLocal()

    try:
        template = db.query(TestCaseTemplate).filter(
            TestCaseTemplate.TEST_CASE_TEMPLATE_ID == template_id
        ).first()

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        template.TEST_CASE_NAME = req.template_name
        template.TEST_CASE_TYPE = req.test_case_type
        template.MODULE = req.module
        template.IS_BROWSER = req.is_browser
        template.REMARK = req.remark
        template.TENANT_ID = req.tenant_id
        template.STATE = req.state
        template.UPDATE_DATE = datetime.now()

        db.query(TestCaseComponent).filter(
            TestCaseComponent.TEST_CASE_TEMPLATE_ID == template_id
        ).delete()

        for comp in req.components:
            relation = TestCaseComponent(
                TEST_CASE_TEMPLATE_ID=template_id,
                TEST_COMPONENT_ID=comp.component_id,
                SORT=comp.sort,
                WAIT_TIME=comp.wait_time,
                LOOP_NUM=comp.loop_num,
                IS_SUSPEND=comp.is_suspend,
                REMARK=comp.remark,
                TENANT_ID=req.tenant_id,
                STATE=req.state,
                CREATE_DATE=datetime.now(),
                EXPIRE_DATE=datetime(2099, 12, 31, 23, 59, 59),
                UPDATE_DATE=datetime.now()
            )
            db.add(relation)

        db.commit()

        return {"message": "updated", "template_id": template_id}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.delete("/templates/{template_id}")
def delete_template(template_id: int):
    db = SessionLocal()

    try:
        template = db.query(TestCaseTemplate).filter(
            TestCaseTemplate.TEST_CASE_TEMPLATE_ID == template_id
        ).first()

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        db.query(TestCaseComponent).filter(
            TestCaseComponent.TEST_CASE_TEMPLATE_ID == template_id
        ).delete()

        db.delete(template)
        db.commit()

        return {"message": "deleted", "template_id": template_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()