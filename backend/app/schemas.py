# app/schemas.py
# Pydantic schemas - ทุก request/response ผ่านการ validate ที่นี่ทั้งหมด
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
import re


# ---------- Auth / User ----------
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]{3,30}$", v):
            raise ValueError("ชื่อผู้ใช้ต้องมี 3-30 ตัวอักษร ใช้ได้เฉพาะ a-z, 0-9, _")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร")
        if not re.search(r"\d", v) or not re.search(r"[a-zA-Z]", v):
            raise ValueError("รหัสผ่านต้องมีทั้งตัวอักษรและตัวเลข")
        return v

    @field_validator("phone")
    @classmethod
    def phone_valid(cls, v):
        if v and not re.match(r"^[0-9\-+() ]{6,20}$", v):
            raise ValueError("เบอร์โทรไม่ถูกต้อง")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    status: str
    created_at: datetime


class UserAdminOut(UserOut):
    failed_login_count: int


class RoleUpdate(BaseModel):
    role: str  # "user" หรือ "admin" เท่านั้น (จำกัดที่ router อีกชั้น)


# ---------- Category ----------
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    description: Optional[str] = None


# ---------- Course ----------
class CourseCreate(BaseModel):
    title: str
    category_id: Optional[int] = None
    short_desc: Optional[str] = ""
    long_desc: Optional[str] = ""
    code_sample: Optional[str] = ""
    price: float = 0
    image_url: Optional[str] = None
    is_published: bool = True

    @field_validator("price")
    @classmethod
    def price_non_negative(cls, v):
        if v < 0:
            raise ValueError("ราคาต้องไม่ติดลบ")
        return v


class CourseUpdate(CourseCreate):
    pass


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    short_desc: Optional[str] = None
    long_desc: Optional[str] = None
    code_sample: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    is_published: bool
    category_id: Optional[int] = None
    created_at: datetime


# ---------- Cart ----------
class CartAddRequest(BaseModel):
    course_id: int
    quantity: int = 1

    @field_validator("quantity")
    @classmethod
    def qty_range(cls, v):
        if v < 1 or v > 20:
            raise ValueError("จำนวนต้องอยู่ระหว่าง 1-20")
        return v


class CartUpdateRequest(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def qty_range(cls, v):
        if v < 0 or v > 20:
            raise ValueError("จำนวนต้องอยู่ระหว่าง 0-20")
        return v


class CartItemOut(BaseModel):
    cart_item_id: int
    course_id: int
    title: str
    price: float
    image_url: Optional[str] = None
    quantity: int


# ---------- Order ----------
class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    course_id: int
    course_title: str
    unit_price: float
    quantity: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_no: str
    subtotal: float
    vat: float
    total: float
    status: str
    payment_mode: str
    created_at: datetime
    items: List[OrderItemOut] = []


class CheckoutResponse(BaseModel):
    order: OrderOut
    redirect: str


# ---------- Report ----------
class ReportCreate(BaseModel):
    subject: str
    message: str

    @field_validator("subject")
    @classmethod
    def subject_len(cls, v):
        if not (3 <= len(v.strip()) <= 150):
            raise ValueError("หัวข้อต้องมี 3-150 ตัวอักษร")
        return v.strip()

    @field_validator("message")
    @classmethod
    def message_len(cls, v):
        if not (5 <= len(v.strip()) <= 2000):
            raise ValueError("รายละเอียดต้องมี 5-2000 ตัวอักษร")
        return v.strip()


class ReportUpdate(BaseModel):
    status: str
    admin_note: Optional[str] = None


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject: str
    message: str
    status: str
    admin_note: Optional[str] = None
    created_at: datetime
    user_id: Optional[int] = None


# ---------- Activity Log ----------
class ActivityLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: Optional[int] = None
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
