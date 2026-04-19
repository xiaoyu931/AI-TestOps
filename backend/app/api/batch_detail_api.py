from fastapi import APIRouter
from sqlalchemy import asc, desc
from datetime import datetime

from app.database import SessionLocal
from app.models.batch_detail_model import BatchDetail
from app.schemas.batch_detail_schema import BatchDetailListResponse

router = APIRouter(prefix="/batch-details", tags=["Batch Details"])


@router.get("", response_model=BatchDetailListResponse)
def get_batch_detail_list(
    batch_detail_id: int = None,
    batch_id: int = None,
    cfg_id: int = None,
    status: int = None,
    task_status: int = None,
    create_date_from: str = None,
    create_date_to: str = None,
    page: int = 1,
    page_size: int = 10,
    sort_field: str = "batch_detail_id",
    sort_order: str = "desc"
):
    db = SessionLocal()
    try:
        query = db.query(BatchDetail)

        # ===== Filters =====
        if batch_detail_id:
            query = query.filter(BatchDetail.BATCH_DETAIL_ID == batch_detail_id)

        if batch_id:
            query = query.filter(BatchDetail.BATCH_ID == batch_id)

        if cfg_id:
            query = query.filter(BatchDetail.CFG_ID == cfg_id)

        if status is not None:
            query = query.filter(BatchDetail.STATUS == status)

        if task_status is not None:
            query = query.filter(BatchDetail.TASK_STATUS == task_status)

        if create_date_from:
            try:
                dt_from = datetime.fromisoformat(create_date_from)
                query = query.filter(BatchDetail.CREATE_DATE >= dt_from)
            except ValueError:
                pass

        if create_date_to:
            try:
                dt_to = datetime.fromisoformat(create_date_to)
                query = query.filter(BatchDetail.CREATE_DATE <= dt_to)
            except ValueError:
                pass

        # ===== Sort =====
        sort_column = {
            "batch_detail_id": BatchDetail.BATCH_DETAIL_ID,
            "batch_id": BatchDetail.BATCH_ID,
            "cfg_id": BatchDetail.CFG_ID,
            "status": BatchDetail.STATUS,
            "task_status": BatchDetail.TASK_STATUS,
            "create_date": BatchDetail.CREATE_DATE,
            "finish_date": BatchDetail.FINISH_DATE,
        }.get(sort_field.lower(), BatchDetail.BATCH_DETAIL_ID)

        if sort_order == "asc":
            query = query.order_by(asc(sort_column), asc(BatchDetail.BATCH_DETAIL_ID))
        else:
            query = query.order_by(desc(sort_column), desc(BatchDetail.BATCH_DETAIL_ID))

        total = query.count()
        rows = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "total": total,
            "data": [
                {
                    "batch_detail_id": x.BATCH_DETAIL_ID,
                    "batch_id": x.BATCH_ID,
                    "cfg_id": x.CFG_ID,
                    "uipath_case_exe_id": x.UIPATH_CASE_EXE_ID,
                    "order_case_exe_id": x.ORDER_CASE_EXE_ID,
                    "verify_case_exe_id": x.VERIFY_CASE_EXE_ID,
                    "status": x.STATUS if x.STATUS is not None else 0,
                    "task_status": x.TASK_STATUS if x.TASK_STATUS is not None else 0,
                    "create_date": x.CREATE_DATE,
                    "finish_date": x.FINISH_DATE,
                }
                for x in rows
            ]
        }

    finally:
        db.close()