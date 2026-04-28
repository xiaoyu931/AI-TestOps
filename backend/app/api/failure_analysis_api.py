from fastapi import APIRouter

from app.database import SessionLocal
from app.schemas.failure_analysis_schema import FailureAnalysisResponse
from app.services.failure_analysis_service import FailureAnalysisService

router = APIRouter(prefix="/failure-analysis", tags=["Failure Analysis"])


@router.get("", response_model=FailureAnalysisResponse)
def get_failure_analysis(
    batch_id: int = None,
    cfg_id: int = None,
    uipath_case_name: str = None,
    create_date_from: str = None,
    create_date_to: str = None,
):
    db = SessionLocal()

    try:
        service = FailureAnalysisService(db)
        return service.get_failure_analysis(
            batch_id=batch_id,
            cfg_id=cfg_id,
            uipath_case_name=uipath_case_name,
            create_date_from=create_date_from,
            create_date_to=create_date_to,
        )
    finally:
        db.close()
