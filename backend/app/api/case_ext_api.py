from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models.cfg_test_case_task_model import TestCaseTask
from app.models.cfg_test_case_data_model import TestCaseData
from app.models.test_case_execution_model import TestCaseExecution
from app.models.test_component_execution_model import TestComponentExecution

router = APIRouter(prefix="/cases-ext", tags=["Case EXT"])

# =============================
# 更新 Case
# =============================
@router.put("/{cfg_id}")
def update_case(cfg_id: int, data: dict):
    db = SessionLocal()

    try:
        case = db.query(TestCaseTask).filter(
            TestCaseTask.CFG_ID == cfg_id
        ).first()

        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        for k, v in data.items():
            if hasattr(case, k):
                setattr(case, k, v)

        db.commit()

        return {"message": "updated"}

    finally:
        db.close()


# =============================
# 删除 Case
# =============================
@router.delete("/{cfg_id}")
def delete_case(cfg_id: int):
    db = SessionLocal()

    try:
        db.query(TestCaseData).filter(TestCaseData.CFG_ID == cfg_id).delete()
        db.query(TestCaseTask).filter(TestCaseTask.CFG_ID == cfg_id).delete()

        db.commit()

        return {"message": "deleted"}

    finally:
        db.close()


# =============================
# Case 全链路（🔥核心）
# =============================
@router.get("/{cfg_id}/full")
def get_case_full(cfg_id: int):

    db = SessionLocal()

    try:
        case = db.query(TestCaseTask).filter(
            TestCaseTask.CFG_ID == cfg_id
        ).first()

        executions = db.query(TestCaseExecution).filter(
            TestCaseExecution.CFG_ID == cfg_id
        ).all()

        exe_list = []

        for exe in executions:
            components = db.query(TestComponentExecution).filter(
                TestComponentExecution.TEST_CASE_EXE_ID == exe.TEST_CASE_EXE_ID
            ).all()

            exe_list.append({
                "execution": exe.TEST_CASE_EXE_ID,
                "state": exe.STATE,
                "components": [
                    {
                        "name": c.TEST_COMPONENT_NAME,
                        "state": c.STATE,
                        "error": c.PYTHON_ERROR_MESSAGE
                    } for c in components
                ]
            })

        return {
            "case": case.TEST_CASE_NAME,
            "executions": exe_list
        }

    finally:
        db.close()