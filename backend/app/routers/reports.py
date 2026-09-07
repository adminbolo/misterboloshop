# app/routers/reports.py
from typing import Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_optional_user, log_activity, verify_csrf_header

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("", response_model=schemas.ReportOut, status_code=201, dependencies=[Depends(verify_csrf_header)])
def submit_report(request: Request, payload: schemas.ReportCreate, db: Session = Depends(get_db), user: Optional[models.User] = Depends(get_optional_user)):
    report = models.Report(
        user_id=user.id if user else None,
        subject=payload.subject,
        message=payload.message
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    log_activity(db, request, "report_submitted", user_id=user.id if user else None, details={"report_id": report.id, "subject": payload.subject})
    return report
