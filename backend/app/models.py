# app/models.py
# นิยาม schema ฐานข้อมูลทั้งหมดของระบบ แยกเป็นตารางชัดเจนตามหน้าที่
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship
from .database import Base


class RoleEnum(str, enum.Enum):
    user = "user"     # ดูคอร์ส/ซื้อคอร์สได้ปกติ
    admin = "admin"   # จัดการคอร์ส/หมวดหมู่/ออเดอร์/แจ้งปัญหา (ทำงานเว็บทั่วไป)
    ceo = "ceo"        # สิทธิ์สูงสุด: ทำได้ทุกอย่างที่ admin ทำได้ + จัดการสิทธิ์ผู้ใช้/แต่งตั้ง-ถอด admin


class StatusEnum(str, enum.Enum):
    active = "active"
    banned = "banned"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.user, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.active, nullable=False)
    failed_login_count = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    courses = relationship("Course", back_populates="category")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(150), nullable=False)
    slug = Column(String(180), unique=True, nullable=False, index=True)
    short_desc = Column(String(300), nullable=True)
    long_desc = Column(Text, nullable=True)
    code_sample = Column(Text, nullable=True)
    price = Column(Float, nullable=False, default=0)
    image_url = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="courses")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="cart_items")
    course = relationship("Course")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(40), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subtotal = Column(Float, nullable=False)
    vat = Column(Float, nullable=False, default=0)
    total = Column(Float, nullable=False)
    status = Column(String(20), default="mock_paid", nullable=False)
    payment_mode = Column(String(20), default="mock", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    course_title = Column(String(150), nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    subject = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="open", nullable=False)  # open, in_progress, closed
    admin_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(50), nullable=False, index=True)
    details = Column(Text, nullable=True)  # JSON string
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User")
