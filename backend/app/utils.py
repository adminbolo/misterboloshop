# app/utils.py
import re
import secrets
from datetime import datetime


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9ก-๙\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text


def gen_order_no() -> str:
    ymd = datetime.utcnow().strftime("%Y%m%d")
    rand = secrets.token_hex(3).upper()
    return f"MB-{ymd}-{rand}"


def gen_unique_slug(base: str) -> str:
    return f"{slugify(base)}-{secrets.token_hex(3)}"
