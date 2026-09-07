# app/routers/orders.py
# checkout ในระบบนี้เป็นการ "จำลอง" (mock) เท่านั้น ยังไม่เชื่อมต่อ payment gateway จริง
# ทุกคำสั่งซื้อจะยืนยันสถานะ mock_paid ทันที เพื่อ demo flow ทั้งระบบให้ครบ
# ซื้อเสร็จ -> ออกใบเสร็จ + ขอบคุณที่ใช้บริการ เท่านั้น (ไม่มีหน้าเซอร์ไพรส์/easter egg แล้ว)
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user, verify_csrf_header, log_activity
from ..utils import gen_order_no
from ..config import settings

router = APIRouter(prefix="/api/orders", tags=["orders"])

ADMIN_ROLES = (models.RoleEnum.admin, models.RoleEnum.ceo)


@router.post("/checkout", response_model=schemas.CheckoutResponse, dependencies=[Depends(verify_csrf_header)])
def checkout(request: Request, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    items = db.query(models.CartItem).options(joinedload(models.CartItem.course)).filter(
        models.CartItem.user_id == user.id
    ).all()
    if not items:
        raise HTTPException(status_code=400, detail="ตะกร้าว่าง ไม่สามารถชำระเงินได้")

    subtotal = sum(i.course.price * i.quantity for i in items)
    vat = round(subtotal * 0.07, 2)
    total = round(subtotal + vat, 2)

    order = models.Order(
        order_no=gen_order_no(),
        user_id=user.id,
        subtotal=subtotal,
        vat=vat,
        total=total,
        status="mock_paid",
        payment_mode="mock"
    )
    db.add(order)
    db.flush()  # ได้ order.id ก่อน commit

    for i in items:
        db.add(models.OrderItem(
            order_id=order.id,
            course_id=i.course_id,
            course_title=i.course.title,
            unit_price=i.course.price,
            quantity=i.quantity
        ))
        db.delete(i)  # เคลียร์ตะกร้าหลังสั่งซื้อ

    db.commit()
    db.refresh(order)

    log_activity(db, request, "checkout_mock", user_id=user.id, details={
        "order_no": order.order_no, "total": total, "item_count": len(items)
    })

    return schemas.CheckoutResponse(order=order, redirect=f"/receipt.html?order_no={order.order_no}")


@router.get("/mine", response_model=List[schemas.OrderOut])
def my_orders(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Order).filter(models.Order.user_id == user.id).order_by(models.Order.created_at.desc()).all()


@router.get("/{order_no}", response_model=schemas.OrderOut)
def get_order(order_no: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.order_no == order_no).first()
    if not order or (order.user_id != user.id and user.role not in ADMIN_ROLES):
        raise HTTPException(status_code=404, detail="ไม่พบคำสั่งซื้อนี้")
    return order


@router.get("/{order_no}/receipt-info")
def receipt_info(order_no: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """ข้อมูลเสริมสำหรับพิมพ์ใบเสร็จ (ข้อมูลร้าน + ผู้ซื้อ) แยกจาก order object ปกติ"""
    order = db.query(models.Order).filter(models.Order.order_no == order_no).first()
    if not order or (order.user_id != user.id and user.role not in ADMIN_ROLES):
        raise HTTPException(status_code=404, detail="ไม่พบคำสั่งซื้อนี้")
    buyer = db.query(models.User).filter(models.User.id == order.user_id).first()
    return {
        "shop": {"name": settings.shop_name, "tax_id": settings.shop_tax_id, "address": settings.shop_address},
        "buyer": {"username": buyer.username, "full_name": buyer.full_name, "email": buyer.email}
    }
