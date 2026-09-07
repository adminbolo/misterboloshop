# app/routers/courses.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api", tags=["courses"])


@router.get("/categories", response_model=List[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).order_by(models.Category.name).all()


@router.get("/courses", response_model=List[schemas.CourseOut])
def list_courses(category: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.Course).filter(models.Course.is_published == True)  # noqa: E712
    if category:
        cat = db.query(models.Category).filter(models.Category.slug == category).first()
        if not cat:
            return []
        q = q.filter(models.Course.category_id == cat.id)
    return q.order_by(models.Course.created_at.desc()).all()


@router.get("/courses/{slug}", response_model=schemas.CourseOut)
def get_course(slug: str, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.slug == slug).first()
    if not course or not course.is_published:
        raise HTTPException(status_code=404, detail="ไม่พบคอร์สนี้")
    return course
