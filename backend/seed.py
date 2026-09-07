# seed.py - รันครั้งเดียวตอนติดตั้งระบบใหม่ เพื่อสร้าง admin และคอร์สตัวอย่าง
# วิธีรัน: python seed.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine, SessionLocal
from app import models
from app.security import hash_password
from app.utils import gen_unique_slug
from app.config import settings

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    # ---- CEO account (สิทธิ์สูงสุด ทำได้ทุกอย่างในระบบ) ----
    # หมายเหตุ: รหัสผ่านนี้เป็นตัวเลขล้วน อ่อนแอมาก ใส่ไว้ตามที่ขอเพื่อทดสอบเท่านั้น
    # ต้องเปลี่ยนก่อนใช้งานจริงเด็ดขาด (ระบบยอมให้ผ่านเพราะสร้างตรงในฐานข้อมูล ข้าม validator ของหน้าสมัครสมาชิก)
    CEO_USERNAME = "CEO_BOLO"
    CEO_EMAIL = "ceo.bolo@misterbolo.com"
    CEO_PASSWORD = "Chanathipbolo0303"

    ceo = db.query(models.User).filter(models.User.email == CEO_EMAIL).first()
    if not ceo:
        ceo = models.User(
            username=CEO_USERNAME,
            email=CEO_EMAIL,
            password_hash=hash_password(CEO_PASSWORD),
            full_name="CEO / ผู้บริหารสูงสุด",
            role=models.RoleEnum.ceo
        )
        db.add(ceo)
        db.commit()
        print(f"[seed] สร้างบัญชี CEO แล้ว: {CEO_EMAIL} / {CEO_PASSWORD}")
        print("[seed] *** คำเตือน: รหัสผ่านนี้อ่อนแอมาก (ตัวเลขล้วน) เปลี่ยนทันทีหลัง login ครั้งแรก ***")
    else:
        print("[seed] บัญชี CEO มีอยู่แล้ว ข้ามการสร้าง")

    # ---- Admin account (ตัวอย่างสำหรับทดสอบสิทธิ์ระดับ admin ทั่วไป) ----
    admin = db.query(models.User).filter(models.User.email == settings.seed_admin_email).first()
    if not admin:
        admin = models.User(
            username=settings.seed_admin_username,
            email=settings.seed_admin_email,
            password_hash=hash_password(settings.seed_admin_password),
            full_name="ผู้ดูแลระบบ (Admin)",
            role=models.RoleEnum.admin
        )
        db.add(admin)
        db.commit()
        print(f"[seed] สร้าง admin ตัวอย่างแล้ว: {settings.seed_admin_email} / {settings.seed_admin_password}")
    else:
        print("[seed] admin ตัวอย่างมีอยู่แล้ว ข้ามการสร้าง")

    # ---- Categories ----
    cat_data = [
        ("เขียนโปรแกรม", "สอนเขียนโค้ดตั้งแต่พื้นฐานถึงขั้นสูง"),
        ("ภาษาต่างประเทศ", "คอร์สภาษาเพื่อการสื่อสารและทำงาน"),
        ("ไซเบอร์ซีเคียวริตี้", "ความปลอดภัยไซเบอร์และการทดสอบเจาะระบบ"),
    ]
    categories = {}
    for name, desc in cat_data:
        cat = db.query(models.Category).filter(models.Category.name == name).first()
        if not cat:
            cat = models.Category(name=name, slug=gen_unique_slug(name), description=desc)
            db.add(cat)
            db.commit()
            db.refresh(cat)
            print(f"[seed] สร้างหมวดหมู่: {name}")
        categories[name] = cat

    # ---- Courses ----
    course_data = [
        {
            "title": "Java เขียนโปรแกรมเบื้องต้น",
            "category": "เขียนโปรแกรม",
            "short_desc": "ปูพื้นฐาน Java ตั้งแต่ syntax จนถึง OOP",
            "long_desc": "คอร์สนี้พาไปรู้จัก Java ตั้งแต่การติดตั้ง JDK, ตัวแปร, เงื่อนไข, ลูป, ไปจนถึงแนวคิด Object-Oriented Programming แบบเข้าใจง่าย เหมาะสำหรับผู้เริ่มต้นที่อยากปูพื้นสายเขียนโปรแกรม\n\nแหล่งเรียนรู้เพิ่มเติมฟรี: Oracle Java Tutorials (เอกสารทางการ, ฟรี 100%) และ freeCodeCamp",
            "code_sample": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
            "price": 990,
        },
        {
            "title": "Python เขียนโปรแกรมเบื้องต้น",
            "category": "เขียนโปรแกรม",
            "short_desc": "ปูพื้นฐาน Python ตั้งแต่ตัวแปรจนถึงฟังก์ชัน",
            "long_desc": "เรียนรู้ Python ตั้งแต่พื้นฐาน: ตัวแปร, ชนิดข้อมูล, เงื่อนไข, ลูป, ฟังก์ชัน, list/dict ไปจนถึงการเขียนโปรแกรมเชิงวัตถุเบื้องต้น เหมาะสำหรับผู้เริ่มต้นทุกสายที่อยากเขียนโค้ดเป็น\n\nแหล่งเรียนรู้เพิ่มเติมฟรี: เอกสารทางการที่ python.org และ freeCodeCamp",
            "code_sample": 'def greet(name):\n    print(f"Hello, {name}!")\n\ngreet("World")',
            "price": 890,
        },
        {
            "title": "HTML สร้างเว็บเพจเบื้องต้น",
            "category": "เขียนโปรแกรม",
            "short_desc": "ปูพื้นฐานโครงสร้างเว็บเพจด้วย HTML",
            "long_desc": "เรียนรู้แท็ก HTML พื้นฐานที่ใช้บ่อย การจัดโครงสร้างหน้าเว็บ ฟอร์ม ตาราง และรูปภาพ เพื่อเป็นพื้นฐานก่อนต่อยอดไป CSS และ JavaScript\n\nแหล่งเรียนรู้เพิ่มเติมฟรี: MDN Web Docs (เอกสารมาตรฐานเว็บ ฟรี 100%) และ W3Schools",
            "code_sample": '<!DOCTYPE html>\n<html>\n<head><title>หน้าแรก</title></head>\n<body>\n  <h1>สวัสดี HTML</h1>\n</body>\n</html>',
            "price": 490,
        },
        {
            "title": "CSS ตกแต่งหน้าเว็บให้สวยงาม",
            "category": "เขียนโปรแกรม",
            "short_desc": "จัดสไตล์เว็บเพจ สี ฟอนต์ เลย์เอาต์ responsive",
            "long_desc": "เรียนรู้การจัดสไตล์หน้าเว็บด้วย CSS ตั้งแต่ selector พื้นฐาน, Flexbox, Grid, ไปจนถึงการทำเว็บ responsive รองรับมือถือ\n\nแหล่งเรียนรู้เพิ่มเติมฟรี: MDN Web Docs และ freeCodeCamp",
            "code_sample": 'body {\n  font-family: sans-serif;\n  background: #f5f5f5;\n}\n.card {\n  display: flex;\n  gap: 10px;\n}',
            "price": 490,
        },
        {
            "title": "JavaScript เขียนเว็บให้อินเตอร์แอคทีฟ",
            "category": "เขียนโปรแกรม",
            "short_desc": "เพิ่มความอินเตอร์แอคทีฟให้เว็บเพจด้วย JavaScript",
            "long_desc": "เรียนรู้ JavaScript พื้นฐาน: ตัวแปร, ฟังก์ชัน, DOM manipulation, event listener ไปจนถึงการเรียก API เบื้องต้นด้วย fetch เหมาะสำหรับคนที่มีพื้นฐาน HTML/CSS มาแล้ว\n\nแหล่งเรียนรู้เพิ่มเติมฟรี: MDN Web Docs และ freeCodeCamp",
            "code_sample": 'document.querySelector("button").addEventListener("click", () => {\n  alert("สวัสดี JavaScript!");\n});',
            "price": 690,
        },
        {
            "title": "OOP แนวคิดการเขียนโปรแกรมเชิงวัตถุ",
            "category": "เขียนโปรแกรม",
            "short_desc": "เข้าใจ Class, Object, Inheritance, Polymorphism",
            "long_desc": "ปูพื้นฐานแนวคิด Object-Oriented Programming (OOP) ที่ใช้ได้กับทุกภาษา: Class, Object, Encapsulation, Inheritance, Polymorphism พร้อมตัวอย่างโค้ดจริงเปรียบเทียบ Java และ Python เหมาะสำหรับคนมีพื้นฐานเขียนโปรแกรมมาบ้างแล้วอยากเข้าใจแนวคิดเชิงลึก",
            "code_sample": 'class Animal:\n    def __init__(self, name):\n        self.name = name\n    def speak(self):\n        return f"{self.name} ส่งเสียงร้อง"\n\nclass Dog(Animal):\n    def speak(self):\n        return f"{self.name} เห่า: โฮ่ง!"',
            "price": 790,
        },
        {
            "title": "เลขฐาน: การคำนวณเลขฐาน 2, 8, 10, 16 สำหรับสายคอมพิวเตอร์",
            "category": "เขียนโปรแกรม",
            "short_desc": "แปลงเลขฐานสอง ฐานแปด ฐานสิบ ฐานสิบหก แบบเข้าใจง่าย",
            "long_desc": "ปูพื้นฐานคณิตศาสตร์คอมพิวเตอร์ที่จำเป็นสำหรับสายเขียนโปรแกรมและสายไอที: การแปลงเลขฐาน 2 (Binary), ฐาน 8 (Octal), ฐาน 10 (Decimal), ฐาน 16 (Hexadecimal) ไปมา พร้อมตัวอย่างการใช้งานจริงในการเขียนโปรแกรม เช่น bitwise operation และการอ่านค่าสี HEX",
            "code_sample": "# ตัวอย่างแปลงเลขฐานสิบเป็นฐานสองด้วย Python\nnumber = 42\nprint(bin(number))   # 0b101010\nprint(hex(number))   # 0x2a\nprint(oct(number))   # 0o52",
            "price": 390,
        },
        {
            "title": "Python สำหรับสาย Cyber Security",
            "category": "ไซเบอร์ซีเคียวริตี้",
            "short_desc": "ใช้ Python เขียนสคริปต์ช่วยงานด้าน security",
            "long_desc": "เรียนรู้การใช้ Python เขียนสคริปต์อัตโนมัติ วิเคราะห์ log, สแกนพอร์ตเบื้องต้น, และเข้าใจหลักการเขียนโค้ดให้ปลอดภัยจากช่องโหว่พื้นฐาน (แนวคิดเพื่อการศึกษาเท่านั้น) เหมาะสำหรับผู้ที่มีพื้นฐาน Python มาบ้างแล้ว",
            "code_sample": 'def greet():\n    print("Hello from Python!")\n\nif __name__ == "__main__":\n    greet()',
            "price": 1290,
        },
        {
            "title": "พื้นฐานภาษาอังกฤษเพื่อสายไอที",
            "category": "ภาษาต่างประเทศ",
            "short_desc": "ศัพท์และประโยคที่ใช้บ่อยในวงการไอที",
            "long_desc": "เรียนคำศัพท์เทคนิค การอ่าน documentation ภาษาอังกฤษ และการสื่อสารกับทีมต่างชาติแบบมั่นใจ",
            "code_sample": "",
            "price": 590,
        },
        {
            "title": "Web Security เบื้องต้น: OWASP Top 10",
            "category": "ไซเบอร์ซีเคียวริตี้",
            "short_desc": "รู้จักช่องโหว่เว็บที่พบบ่อยที่สุด และวิธีป้องกัน",
            "long_desc": "ปูพื้นฐาน OWASP Top 10 เช่น SQL Injection, XSS, CSRF พร้อมตัวอย่างวิธีป้องกันในโค้ดจริง (เพื่อการศึกษาและป้องกันระบบของตัวเองเท่านั้น)",
            "code_sample": "# ตัวอย่างการป้องกัน SQL Injection ด้วย parameterized query\ncursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))",
            "price": 1490,
        },
    ]

    for c in course_data:
        exists = db.query(models.Course).filter(models.Course.title == c["title"]).first()
        if exists:
            continue
        cat = categories[c["category"]]
        course = models.Course(
            category_id=cat.id,
            title=c["title"],
            slug=gen_unique_slug(c["title"]),
            short_desc=c["short_desc"],
            long_desc=c["long_desc"],
            code_sample=c["code_sample"],
            price=c["price"],
            is_published=True
        )
        db.add(course)
        print(f"[seed] สร้างคอร์ส: {c['title']}")
    db.commit()

    print("\n[seed] เสร็จสิ้น! บัญชีที่สร้างไว้:")
    print(f"  CEO   -> {CEO_EMAIL} / {CEO_PASSWORD}   (สิทธิ์สูงสุด ทำได้ทุกอย่าง)")
    print(f"  Admin -> {settings.seed_admin_email} / {settings.seed_admin_password}   (จัดการเว็บทั่วไป)")
    print("  *** อย่าลืมเปลี่ยนรหัสผ่านทั้งสองบัญชีนี้ก่อนขึ้น production จริง ***")

finally:
    db.close()
