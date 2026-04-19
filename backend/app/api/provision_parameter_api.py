from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models.test_provision_parameter_model import TestProvisionParameter
from app.schemas.provision_parameter_schema import (
    ProvisionParameterCreateRequest,
    ProvisionParameterListResponse,
    ProvisionParameterDetailResponse
)
router = APIRouter(prefix="/provision-params", tags=["Provision Parameters"])

@router.post("")
def create_provision_param(req: ProvisionParameterCreateRequest):

    db = SessionLocal()

    try:
        new_item = TestProvisionParameter(
            action_id=req.action_id,
            platform_code=req.platform_code,
            provision_type=req.provision_type,
            provision_Mandatory_aram=req.provision_mandatory_param,
            provision_optional_aram=req.provision_optional_param,
            state=req.state,
            ext1=req.ext1,
            ext2=req.ext2,
            ext3=req.ext3,
            product_line=req.product_line,
            veris_code_status=req.veris_code_status,
            platform=req.platform
        )

        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        return {
            "message": "success",
            "id": new_item.provision_seq_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

@router.get("", response_model=ProvisionParameterListResponse)
def get_list(product_line: str = None, platform_code: str = None):

    db = SessionLocal()

    try:
        query = db.query(TestProvisionParameter)

        if product_line:
            query = query.filter(TestProvisionParameter.product_line == product_line)

        if platform_code:
            query = query.filter(TestProvisionParameter.platform_code == platform_code)

        items = query.all()

        result = []

        for i in items:
            result.append({
                "id": i.provision_seq_id,
                "action_id": i.action_id,
                "platform_code": i.platform_code,
                "provision_type": i.provision_type,
                "mandatory": i.provision_Mandatory_aram,
                "optional": i.provision_optional_aram,
                "state": i.state,
                "active": i.state == "U",
                "product_line": i.product_line
            })

        return {
            "total": len(result),
            "data": result
        }

    finally:
        db.close()

@router.get("/{id}", response_model=ProvisionParameterDetailResponse)
def get_one(id: int):

    db = SessionLocal()

    try:
        item = db.query(TestProvisionParameter).filter(
            TestProvisionParameter.provision_seq_id == id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Not found")

        return {
            "id": item.provision_seq_id,
            "action_id": item.action_id,
            "platform_code": item.platform_code,
            "provision_type": item.provision_type,
            "mandatory": item.provision_Mandatory_aram,
            "optional": item.provision_optional_aram,
            "state": item.state,
            "ext1": item.ext1,
            "ext2": item.ext2,
            "ext3": item.ext3,
            "product_line": item.product_line,
            "veris_code_status": item.veris_code_status,
            "platform": item.platform
        }

    finally:
        db.close()