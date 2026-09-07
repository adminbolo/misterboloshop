# app/security.py
# ศูนย์รวมทุกอย่างเกี่ยวกับความปลอดภัย: hash password, สร้าง/ตรวจ JWT
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
from .config import settings

# bcrypt cost 12 - สมดุลระหว่างความปลอดภัยกับ performance ของ server
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.algorithm)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
