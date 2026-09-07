# app/routers/admin.py
# รวม endpoint ทั้งหมดที่ต้องเป็น admin เท่านั้น: courses, categories, users, orders, reports, logs
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import require_admin, require_ceo, log_activity, verify_csrf_header
from ..utils import gen_unique_slug

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


# ---------- Dashboard ----------
@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    return {
        "users": db.query(models.User).count(),
        "courses": db.query(models.Course).count(),
        "orders": db.query(models.Order).count(),
        "revenue": sum(o.total for o in db.query(models.Order).filter(models.Order.status == "mock_paid").all()),
        "open_reports": db.query(models.Report).filter(models.Report.status == "open").count()
    }


# ---------- Categories ----------
@router.post("/categories", response_model=schemas.CategoryOut, status_code=201, dependencies=[Depends(verify_csrf_header)])
def create_category(request: Request, payload: schemas.CategoryCreate, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    existing = db.query(models.Category).filter(models.Category.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="หมวดหมู่นี้มีอยู่แล้ว")
    cat = models.Category(name=payload.name, slug=gen_unique_slug(payload.name), description=payload.description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    log_activity(db, request, "admin_category_create", user_id=admin.id, details={"name": payload.name})
    return cat


# ---------- Courses ----------
@router.get("/courses", response_model=List[schemas.CourseOut])
def admin_list_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).order_by(models.Course.created_at.desc()).all()


@router.post("/courses", response_model=schemas.CourseOut, status_code=201, dependencies=[Depends(verify_csrf_header)])
def create_course(request: Request, payload: schemas.CourseCreate, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    course = models.Course(
        category_id=payload.category_id,
        title=payload.title,
        slug=gen_unique_slug(payload.title),
        short_desc=payload.short_desc,
        long_desc=payload.long_desc,
        code_sample=payload.code_sample,
        price=payload.price,
        image_url=payload.image_url,
        is_published=payload.is_published
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    log_activity(db, request, "admin_course_create", user_id=admin.id, details={"course_id": course.id, "title": course.title})
    return course


@router.put("/courses/{course_id}", response_model=schemas.CourseOut, dependencies=[Depends(verify_csrf_header)])
def update_course(course_id: int, request: Request, payload: schemas.CourseUpdate, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="ไม่พบคอร์สนี้")
    for field in ("category_id", "title", "short_desc", "long_desc", "code_sample", "price", "image_url", "is_published"):
        setattr(course, field, getattr(payload, field))
    db.commit()
    db.refresh(course)
    log_activity(db, request, "admin_course_update", user_id=admin.id, details={"course_id": course.id})
    return course


@router.delete("/courses/{course_id}", status_code=204, dependencies=[Depends(verify_csrf_header)])
def delete_course(course_id: int, request: Request, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="ไม่พบคอร์สนี้")
    db.delete(course)
    db.commit()
    log_activity(db, request, "admin_course_delete", user_id=admin.id, details={"course_id": course_id})
    return None


# ---------- Users ----------
@router.get("/users", response_model=List[schemas.UserAdminOut])
def admin_list_users(db: Session = Depends(get_db)):
    return db.query(models.User).order_by(models.User.id.desc()).all()


@router.post("/users/{user_id}/toggle-ban", response_model=schemas.UserAdminOut, dependencies=[Depends(verify_csrf_header)])
def toggle_ban(user_id: int, request: Request, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้นี้")
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="ไม่สามารถระงับบัญชีตัวเองได้")
    if target.role == models.RoleEnum.ceo:
        raise HTTPException(status_code=403, detail="ไม่สามารถระงับบัญชี CEO ได้")
    target.status = models.StatusEnum.banned if target.status == models.StatusEnum.active else models.StatusEnum.active
    db.commit()
    db.refresh(target)
    log_activity(db, request, "admin_user_status_change", user_id=admin.id, details={"target_user": target.id, "new_status": target.status.value})
    return target


# ---------- Role management (CEO เท่านั้น) ----------
@router.post("/users/{user_id}/set-role", response_model=schemas.UserAdminOut, dependencies=[Depends(verify_csrf_header)])
def set_role(user_id: int, request: Request, payload: schemas.RoleUpdate, db: Session = Depends(get_db), ceo: models.User = Depends(require_ceo)):
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้นี้")
    if target.id == ceo.id:
        raise HTTPException(status_code=400, detail="ไม่สามารถเปลี่ยนสิทธิ์ตัวเองได้")
    if target.role == models.RoleEnum.ceo:
        raise HTTPException(status_code=403, detail="ไม่สามารถเปลี่ยนสิทธิ์ของ CEO คนอื่นได้")
    if payload.role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="กำหนดสิทธิ์ได้เฉพาะ user หรือ admin เท่านั้นผ่านช่องทางนี้")

    old_role = target.role.value
    target.role = models.RoleEnum(payload.role)
    db.commit()
    db.refresh(target)
    log_activity(db, request, "ceo_role_change", user_id=ceo.id, details={"target_user": target.id, "old_role": old_role, "new_role": payload.role})
    return target


# ---------- Orders ----------
@router.get("/orders", response_model=List[schemas.OrderOut])
def admin_list_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).all()


# ---------- Reports ----------
@router.get("/reports", response_model=List[schemas.ReportOut])
def admin_list_reports(db: Session = Depends(get_db)):
    return db.query(models.Report).order_by(models.Report.created_at.desc()).all()


@router.put("/reports/{report_id}", response_model=schemas.ReportOut, dependencies=[Depends(verify_csrf_header)])
def admin_update_report(report_id: int, request: Request, payload: schemas.ReportUpdate, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="ไม่พบรายการนี้")
    report.status = payload.status
    report.admin_note = payload.admin_note
    db.commit()
    db.refresh(report)
    log_activity(db, request, "admin_report_update", user_id=admin.id, details={"report_id": report_id, "status": payload.status})
    return report


# ---------- Activity Logs ----------
@router.get("/logs", response_model=List[schemas.ActivityLogOut])
def admin_list_logs(limit: int = 300, db: Session = Depends(get_db)):
    return db.query(models.ActivityLog).order_by(models.ActivityLog.created_at.desc()).limit(limit).all()
