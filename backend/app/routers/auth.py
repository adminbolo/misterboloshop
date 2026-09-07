# app/routers/auth.py
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .. import models, schemas
from ..database import get_db
from ..security import hash_password, verify_password, create_access_token
from ..deps import get_current_user, log_activity, COOKIE_NAME, verify_csrf_header
from ..config import settings
from ..limiter import limiter  # instance เดียวกับ main.py

router = APIRouter(prefix="/api/auth", tags=["auth"])

COOKIE_KWARGS = dict(
    httponly=True,          # กัน JS อ่าน token -> กัน XSS ขโมย session
    samesite="strict",      # กัน CSRF ระดับ browser
    secure=settings.env == "production",  # production ต้องวิ่งบน HTTPS เท่านั้น
    max_age=60 * 60 * 24 * 7,
    path="/"
)

MAX_FAILED_ATTEMPTS = 5
LOCK_MINUTES = 15


@router.post("/register", response_model=schemas.UserOut, status_code=201)
@limiter.limit("8/hour")
def register(request: Request, response: Response, payload: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        or_(models.User.email == payload.email.lower(), models.User.username == payload.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="อีเมลหรือชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว")

    user = models.User(
        username=payload.username,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        phone=payload.phone,
        role=models.RoleEnum.user
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_activity(db, request, "register", user_id=user.id, details={"username": user.username})

    token = create_access_token(user.id, user.role.value)
    response.set_cookie(COOKIE_NAME, token, **COOKIE_KWARGS)
    return user


@router.post("/login", response_model=schemas.UserOut)
@limiter.limit("10/15minute")
def login(request: Request, response: Response, payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email.lower()).first()

    # ข้อความ error ต้อง generic เหมือนกันหมด กัน user enumeration attack
    generic_error = "อีเมลหรือรหัสผ่านไม่ถูกต้อง"

    if not user:
        log_activity(db, request, "login_failed", details={"email": payload.email, "reason": "no_such_user"})
        raise HTTPException(status_code=401, detail=generic_error)

    if user.locked_until and user.locked_until > datetime.utcnow():
        log_activity(db, request, "login_blocked_locked", user_id=user.id)
        raise HTTPException(status_code=423, detail="บัญชีถูกล็อคชั่วคราวจากการล็อคอินผิดหลายครั้ง กรุณาลองใหม่ภายหลัง")

    if user.status != models.StatusEnum.active:
        log_activity(db, request, "login_blocked_banned", user_id=user.id)
        raise HTTPException(status_code=403, detail="บัญชีนี้ถูกระงับการใช้งาน")

    if not verify_password(payload.password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCK_MINUTES)
        db.commit()
        log_activity(db, request, "login_failed", user_id=user.id, details={"reason": "bad_password"})
        raise HTTPException(status_code=401, detail=generic_error)

    user.failed_login_count = 0
    user.locked_until = None
    db.commit()

    log_activity(db, request, "login_success", user_id=user.id)

    token = create_access_token(user.id, user.role.value)
    response.set_cookie(COOKIE_NAME, token, **COOKIE_KWARGS)
    return user


@router.post("/logout", dependencies=[Depends(verify_csrf_header)])
def logout(request: Request, response: Response, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    log_activity(db, request, "logout", user_id=user.id)
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"message": "ออกจากระบบแล้ว"}


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user
