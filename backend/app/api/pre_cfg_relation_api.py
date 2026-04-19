from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models.pre_cfg_relation_model import PreCfgRelation
from app.schemas.pre_cfg_relation_schema import (
    PreCfgRelationCreateRequest,
    PreCfgRelationListResponse
)
router = APIRouter(prefix="/pre-relations", tags=["Pre CFG Relation"])

@router.post("")
def create_relation(req: PreCfgRelationCreateRequest):

    db = SessionLocal()

    try:
        existing = db.query(PreCfgRelation).filter(
            PreCfgRelation.preCfgId == req.pre_cfg_id,
            PreCfgRelation.cfgId == req.cfg_id
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Relation already exists")

        relation = PreCfgRelation(
            preCfgId=req.pre_cfg_id,
            cfgId=req.cfg_id
        )

        db.add(relation)
        db.commit()

        return {"message": "success"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

@router.get("", response_model=PreCfgRelationListResponse)
def get_relations(cfg_id: str = None):

    db = SessionLocal()

    try:
        query = db.query(PreCfgRelation)

        if cfg_id:
            query = query.filter(PreCfgRelation.cfgId == cfg_id)

        items = query.all()

        result = []

        for i in items:
            result.append({
                "pre_cfg_id": i.preCfgId,
                "cfg_id": i.cfgId
            })

        return {
            "total": len(result),
            "data": result
        }

    finally:
        db.close()

@router.delete("")
def delete_relation(pre_cfg_id: str, cfg_id: str):

    db = SessionLocal()

    try:
        relation = db.query(PreCfgRelation).filter(
            PreCfgRelation.preCfgId == pre_cfg_id,
            PreCfgRelation.cfgId == cfg_id
        ).first()

        if not relation:
            raise HTTPException(status_code=404, detail="Not found")

        db.delete(relation)
        db.commit()

        return {"message": "deleted"}

    finally:
        db.close()