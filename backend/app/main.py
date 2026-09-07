# app/main.py
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .database import Base, engine
from . import models  # noqa: F401  (ต้อง import เพื่อให้ Base.metadata รู้จักทุกตาราง)
from .config import settings
from .limiter import limiter  # instance เดียวใช้ร่วมกับทุก router
from .routers import auth, courses, cart, orders, reports, admin

# สร้างตารางทั้งหมดถ้ายังไม่มี (สำหรับ production จริงควรใช้ Alembic migration แทน)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mister Bolo API",
    description="Backend API สำหรับเว็บขายคอร์สออนไลน์ มิสเตอร์โบโล่ (ระบบชำระเงินเป็นแบบจำลอง/mock)",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS: อนุญาตเฉพาะ origin ของ frontend ที่ตั้งค่าไว้ + ต้องส่ง credentials (cookie) ได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Requested-With"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # แปลง error ของ Pydantic ให้อ่านง่ายขึ้นสำหรับ frontend
    first = exc.errors()[0]
    msg = first.get("msg", "ข้อมูลไม่ถูกต้อง")
    return JSONResponse(status_code=422, content={"detail": msg, "errors": exc.errors()})


app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(reports.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "shop": settings.shop_name}


# ---------------------------------------------------------------------------
# เสิร์ฟ frontend (static HTML/CSS/JS) จาก backend เดียวกัน
# เพื่อให้รันด้วยคำสั่งเดียว (uvicorn) แล้วเข้าใช้งานได้ทั้งเว็บทันที
# ต้อง mount ไว้ "ท้ายสุด" เสมอ ไม่งั้นจะไปทับ route ของ /api/* ที่ประกาศไว้ข้างบน
# ---------------------------------------------------------------------------
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.normpath(os.path.join(BACKEND_DIR, "..", "frontend"))

if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    print(f"[warn] ไม่พบโฟลเดอร์ frontend ที่ {FRONTEND_DIR} — จะรันแค่ API เท่านั้น")
