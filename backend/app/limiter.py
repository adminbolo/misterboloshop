# app/limiter.py
# ต้องมี Limiter instance เดียวใช้ร่วมกันทั้งแอป (main.py + ทุก router ที่ใช้ @limiter.limit)
# ถ้าสร้างหลาย instance แยกกัน การนับ rate limit จะไม่ sync กัน
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
