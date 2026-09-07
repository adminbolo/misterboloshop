# app/deps.py
# FastAPI dependencies ที่ใช้ซ้ำในทุก router: get_db, current user, require admin, logger, csrf
import json
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .database import get_db
from .security import decode_access_token
from . import models

COOKIE_NAME = "mb_token"


def get_client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_optional_user(request: Request, db: Session = Depends(get_db)) -> Optional[models.User]:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    user = db.query(models.User).filter(models.User.id == int(payload["sub"])).first()
    if not user or user.status != models.StatusEnum.active:
        return None
    return user


def get_current_user(user: Optional[models.User] = Depends(get_optional_user)) -> models.User:
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="กรุณาเข้าสู่ระบบก่อน")
    return user


def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    # ceo มีสิทธิ์ทุกอย่างที่ admin ทำได้ด้วย (สิทธิ์สูงกว่า ไม่ใช่แยกกันคนละสาย)
    if user.role not in (models.RoleEnum.admin, models.RoleEnum.ceo):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ต้องเป็นผู้ดูแลระบบเท่านั้น")
    return user


def require_ceo(user: models.User = Depends(get_current_user)) -> models.User:
    # เฉพาะ CEO เท่านั้น: จัดการสิทธิ์ผู้ใช้, แต่งตั้ง/ถอด admin
    if user.role != models.RoleEnum.ceo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="เฉพาะ CEO เท่านั้นที่ทำรายการนี้ได้")
    return user


# ป้องกัน CSRF แบบเบา: บังคับ custom header นี้ในทุก state-changing request
# เบราว์เซอร์ทั่วไปจะไม่แนบ custom header ให้เองข้ามโดเมน (ต่างจาก cookie ที่แนบอัตโนมัติ)
# ทำให้ฟอร์ม/สคริปต์จากเว็บอื่นไม่สามารถยิง request ปลอมมาได้ แม้จะมี cookie ติดตัว user อยู่
def verify_csrf_header(request: Request):
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        marker = request.headers.get("x-requested-with")
        if marker != "XMLHttpRequest":
            raise HTTPException(status_code=403, detail="คำขอไม่ผ่านการตรวจสอบความปลอดภัย (CSRF)")


def log_activity(db: Session, request: Request, action: str, user_id: Optional[int] = None, details: Optional[dict] = None):
    entry = models.ActivityLog(
        user_id=user_id,
        action=action,
        details=json.dumps(details, ensure_ascii=False) if details else None,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent", "")[:300]
    )
    db.add(entry)
    db.commit()
