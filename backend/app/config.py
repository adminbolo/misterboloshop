# app/config.py
# จุดเดียวที่อ่านค่า config ทั้งหมดของระบบ (12-factor style)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "development"
    jwt_secret: str = "insecure_default_change_me"
    jwt_expire_minutes: int = 10080
    algorithm: str = "HS256"
    frontend_origin: str = "http://localhost:5500"

    shop_name: str = "Mister Bolo"
    shop_tax_id: str = "0000000000000"
    shop_address: str = "-"

    seed_admin_email: str = "admin@misterbolo.com"
    seed_admin_password: str = "ChangeMe123!"
    seed_admin_username: str = "admin"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

if settings.env == "production" and settings.jwt_secret == "insecure_default_change_me":
    raise RuntimeError(
        "ห้ามใช้ JWT_SECRET default ตอนรัน production! ตั้งค่า JWT_SECRET ใน .env ก่อน"
    )
