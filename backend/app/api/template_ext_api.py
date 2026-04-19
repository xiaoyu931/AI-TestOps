from fastapi import APIRouter
from app.database import SessionLocal
from app.models.test_case_template_model import TestCaseTemplate

router = APIRouter(prefix="/template-ext")


@router.delete("/{template_id}")
def delete_template(template_id: int):

    db = SessionLocal()

    try:
        db.query(TestCaseTemplate).filter(
            TestCaseTemplate.TEST_CASE_TEMPLATE_ID == template_id
        ).delete()

        db.commit()

        return {"message": "deleted"}

    finally:
        db.close()