from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models.test_dispatcher_model import TestDispatcherData

router = APIRouter(prefix="/dispatcher-ext")


@router.put("/{plan_id}")
def update_dispatcher(plan_id: int, data: dict):

    db = SessionLocal()

    try:
        item = db.query(TestDispatcherData).filter(
            TestDispatcherData.DISPATCHER_PLAN_ID == plan_id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Not found")

        for k, v in data.items():
            if hasattr(item, k):
                setattr(item, k, v)

        db.commit()

        return {"message": "updated"}

    finally:
        db.close()