from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models.billing_data_pool_model import BillingTestDataPool
from app.schemas.billing_data_pool_schema import (
    BillingDataCreateRequest,
    BillingDataListResponse
)
from datetime import datetime
router = APIRouter(prefix="/billing-pool", tags=["Billing Data Pool"])

@router.post("")
def create_data(req: BillingDataCreateRequest):

    db = SessionLocal()

    try:
        existing = db.query(BillingTestDataPool).filter(
            BillingTestDataPool.cust_id == req.cust_id
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="cust_id already exists")

        new_data = BillingTestDataPool(
            cfg_id=req.cfg_id,
            testCaseName_str=req.test_case_name,
            cust_id=req.cust_id,
            account_id=req.account_id,
            order_id=req.order_id,
            status=0,
            create_time=datetime.now()
        )

        db.add(new_data)
        db.commit()

        return {"message": "created"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

@router.get("", response_model=BillingDataListResponse)
def get_list(cfg_id: str = None, status: int = None):

    db = SessionLocal()

    try:
        query = db.query(BillingTestDataPool)

        if cfg_id:
            query = query.filter(BillingTestDataPool.cfg_id == cfg_id)

        if status is not None:
            query = query.filter(BillingTestDataPool.status == status)

        items = query.all()

        result = []

        for i in items:
            result.append({
                "id": i.id,
                "cfg_id": i.cfg_id,
                "test_case_name": i.testCaseName_str,
                "cust_id": i.cust_id,
                "account_id": i.account_id,
                "order_id": i.order_id,
                "status": i.status,
                "used": i.status == 1,
                "create_time": i.create_time,
                "used_time": i.used_time
            })

        return {
            "total": len(result),
            "data": result
        }

    finally:
        db.close()

@router.get("/next")
def get_next_data(cfg_id: str):

    db = SessionLocal()

    try:
        data = db.query(BillingTestDataPool).filter(
            BillingTestDataPool.cfg_id == cfg_id,
            BillingTestDataPool.status == 0
        ).first()

        if not data:
            raise HTTPException(status_code=404, detail="No available data")

        # 标记为已使用
        data.status = 1
        data.used_time = datetime.now()

        db.commit()

        return {
            "cust_id": data.cust_id,
            "account_id": data.account_id,
            "order_id": data.order_id
        }

    finally:
        db.close()