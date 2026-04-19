from fastapi import APIRouter
from app.database import SessionLocal
from app.models.test_component_model import TestComponent
from app.models.test_parameter_model import TestParameter

router = APIRouter(tags=["Template Meta"])


# 获取组件列表
@router.get("/components")
def get_components():
    db = SessionLocal()
    try:
        data = db.query(TestComponent).all()

        return [
            {
                "id": c.ID,
                "name": c.NAME
            }
            for c in data
        ]
    finally:
        db.close()


# 获取参数列表
@router.get("/parameters")
def get_parameters():
    db = SessionLocal()
    try:
        data = db.query(TestParameter).all()

        return [
            {
                "id": p.ID,
                "name": p.NAME
            }
            for p in data
        ]
    finally:
        db.close()