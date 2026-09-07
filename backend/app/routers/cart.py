# app/routers/cart.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from fastapi import Request

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user, verify_csrf_header, log_activity

router = APIRouter(prefix="/api/cart", tags=["cart"], dependencies=[Depends(verify_csrf_header)])


def _serialize(item: models.CartItem) -> schemas.CartItemOut:
    return schemas.CartItemOut(
        cart_item_id=item.id,
        course_id=item.course_id,
        title=item.course.title,
        price=item.course.price,
        image_url=item.course.image_url,
        quantity=item.quantity
    )


@router.get("", response_model=List[schemas.CartItemOut])
def view_cart(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    items = db.query(models.CartItem).options(joinedload(models.CartItem.course)).filter(
        models.CartItem.user_id == user.id
    ).all()
    return [_serialize(i) for i in items]


@router.post("/add", response_model=schemas.CartItemOut, status_code=201)
def add_to_cart(request: Request, payload: schemas.CartAddRequest, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    course = db.query(models.Course).filter(models.Course.id == payload.course_id, models.Course.is_published == True).first()  # noqa: E712
    if not course:
        raise HTTPException(status_code=404, detail="ไม่พบคอร์สนี้")

    existing = db.query(models.CartItem).filter(
        models.CartItem.user_id == user.id, models.CartItem.course_id == course.id
    ).first()
    if existing:
        existing.quantity = min(existing.quantity + payload.quantity, 20)
        item = existing
    else:
        item = models.CartItem(user_id=user.id, course_id=course.id, quantity=payload.quantity)
        db.add(item)
    db.commit()
    db.refresh(item)

    log_activity(db, request, "add_to_cart", user_id=user.id, details={"course_id": course.id, "title": course.title})
    return _serialize(item)


@router.put("/{item_id}")
def update_cart_item(item_id: int, request: Request, payload: schemas.CartUpdateRequest, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    item = db.query(models.CartItem).filter(models.CartItem.id == item_id, models.CartItem.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="ไม่พบรายการนี้ในตะกร้า")

    if payload.quantity == 0:
        db.delete(item)
        db.commit()
        log_activity(db, request, "remove_from_cart", user_id=user.id, details={"cart_item_id": item_id})
        return {"removed": True}

    item.quantity = payload.quantity
    db.commit()
    db.refresh(item)
    log_activity(db, request, "update_cart", user_id=user.id, details={"cart_item_id": item_id, "quantity": payload.quantity})
    return _serialize(item)


@router.delete("/{item_id}", status_code=204)
def remove_cart_item(item_id: int, request: Request, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    item = db.query(models.CartItem).filter(models.CartItem.id == item_id, models.CartItem.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="ไม่พบรายการนี้ในตะกร้า")
    db.delete(item)
    db.commit()
    log_activity(db, request, "remove_from_cart", user_id=user.id, details={"cart_item_id": item_id})
    return None
