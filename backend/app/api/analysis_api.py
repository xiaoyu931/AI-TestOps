from fastapi import APIRouter
from app.database import SessionLocal
from app.models.batch_detail_model import BatchDetail

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get("/batch/{batch_id}")
def analyze_batch(batch_id: int):

    db = SessionLocal()

    try:
        items = db.query(BatchDetail).filter(
            BatchDetail.BATCH_ID == batch_id
        ).all()

        total = len(items)
        success = len([i for i in items if i.STATUS in [5,13,14]])
        fail = total - success

        return {
            "total": total,
            "success": success,
            "fail": fail,
            "success_rate": round(success / total * 100, 2) if total else 0
        }

    finally:
        db.close()