# 🥟 Mister Bolo — เว็บขายคอร์สออนไลน์ (Demo)

โปรเจกต์เว็บขายคอร์สออนไลน์แบบเต็มระบบ แยก **Backend** (Python/FastAPI) และ
**Frontend** (HTML/CSS/JS) ออกจากกันชัดเจน สื่อสารกันผ่าน REST API

> ⚠️ **ระบบชำระเงินเป็นการจำลอง (Mock) ทั้งหมด** ไม่มีการเชื่อมต่อ payment
> gateway จริง ทุกคำสั่งซื้อจะถูกยืนยัน "ชำระเงินแล้ว" ทันทีเพื่อ demo flow
> ทั้งระบบ ซื้อเสร็จจะได้ใบเสร็จพร้อมข้อความขอบคุณที่ใช้บริการทันที

## โครงสร้างโปรเจกต์

```
misterbolo/
├── backend/            # FastAPI REST API
│   ├── app/
│   │   ├── main.py         จุดเริ่มแอป, CORS, error handler
│   │   ├── config.py        อ่านค่าจาก .env
│   │   ├── database.py      ตั้งค่า SQLAlchemy + SQLite
│   │   ├── models.py        ORM models (User, Course, Order, ...)
│   │   ├── schemas.py       Pydantic validation
│   │   ├── security.py      bcrypt hash + JWT
│   │   ├── deps.py          auth/admin dependency, CSRF, activity log
│   │   ├── limiter.py       rate limiter (instance เดียวใช้ร่วมกัน)
│   │   └── routers/         auth, courses, cart, orders, reports, admin
│   ├── seed.py           สร้าง admin + คอร์สตัวอย่าง
│   ├── requirements.txt
│   └── .env.example
└── frontend/           # Static site — เรียก backend ผ่าน fetch API
    ├── *.html              หน้าเว็บทั้งหมด (public + user)
    ├── admin/*.html         หน้า admin panel
    ├── css/style.css
    └── js/                  api.js, nav.js, auth-guard.js, ...
```

## วิธีรัน (รันคำสั่งเดียวจบ — backend เสิร์ฟ frontend ให้ในตัว)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# เปิด .env แก้ JWT_SECRET เป็นสตริงสุ่มยาวๆ (ห้ามใช้ค่า default)

python seed.py                    # สร้างบัญชี CEO/Admin + คอร์สตัวอย่าง (รันครั้งเดียว)
uvicorn app.main:app --reload --port 8000
```

เปิดเบราว์เซอร์ไปที่ **`http://localhost:8000`** ได้เลย — ทั้งหน้าเว็บและ API
วิ่งอยู่บนพอร์ตเดียวกัน (backend เสิร์ฟไฟล์ frontend ให้อัตโนมัติ) ไม่ต้องเปิด
สอง terminal แล้ว

ดู API docs อัตโนมัติได้ที่ `http://localhost:8000/docs`

> หมายเหตุ: ถ้าอยากแยกรัน frontend คนละ process ระหว่าง dev (เช่นใช้ live
> server อื่น) ยังทำได้ — ใส่ `<script>window.MB_API_BASE = "http://localhost:8000";</script>`
> ก่อนโหลด `js/api.js` ในแต่ละหน้า แล้วรัน `python3 -m http.server 5500` ในโฟลเดอร์ frontend

### ระบบสิทธิ์ 3 ระดับ

| Role | ทำอะไรได้ |
|---|---|
| **User** (สมัครเองผ่านหน้าเว็บ) | ดูคอร์ส, ใส่ตะกร้า, ซื้อ(จำลอง), แจ้งปัญหา |
| **Admin** | ทำทุกอย่างของ User + จัดการคอร์ส/หมวดหมู่/ดูออเดอร์/ตอบเรื่องแจ้งปัญหา |
| **CEO** (สิทธิ์สูงสุด) | ทำทุกอย่างของ Admin + เลื่อนขั้น/ถอดสิทธิ์ admin, ระงับบัญชี, ดู log ทั้งหมด |

**บัญชีที่ `seed.py` สร้างให้อัตโนมัติ:**

| Role | Email | Password |
|---|---|---|
| CEO | `ceo.bolo@misterbolo.com` (username: `CEO_BOLO`) | `123456789` |
| Admin (ตัวอย่าง) | `admin@misterbolo.com` | `ChangeMe123!` |

⚠️ **รหัสผ่าน CEO เป็นตัวเลขล้วน อ่อนแอมาก ใส่ให้ตามที่ขอเพื่อทดสอบเท่านั้น
เปลี่ยนทันทีหลัง login ครั้งแรกก่อนใช้งานจริงเด็ดขาด** (ระบบยังไม่มีหน้า
"เปลี่ยนรหัสผ่านตัวเอง" ในเวอร์ชันนี้ — ต้องรันคำสั่งอัปเดตฐานข้อมูล/API
โดยตรง ถ้าต้องการฟีเจอร์นี้แจ้งมาได้ ทำเพิ่มให้)

> ⚠️ **ห้ามใช้โดเมนอีเมลที่เป็น "reserved/special-use" เวลาสร้างบัญชีทดสอบเพิ่มเอง**
> เช่น `.local`, `.test`, `.example`, `.invalid` หรือ `example.com/.net/.org`
> เพราะ library ตรวจสอบอีเมล (`email-validator`) จะปฏิเสธอีเมลกลุ่มนี้ทันที
> ต่อให้สร้างบัญชีในฐานข้อมูลสำเร็จ (เช่นผ่าน seed script ที่ข้ามการเช็ค)
> ก็จะ **login ผ่านหน้าเว็บไม่ได้** เพราะขั้นตอน login เช็คอีเมลก่อนเช็ครหัสผ่าน
> ใช้โดเมนทั่วไปแทน เช่น `.com`, `.co`, หรือโดเมนจริงที่มึงมีอยู่

**สำคัญ**: หน้าสมัครสมาชิกสาธารณะ (`/register.html`) **จะได้ role "user"
เสมอ** ไม่มีตัวเลือกเลือกเป็น admin/CEO ให้กด — เป็นการป้องกันไม่ให้ใครก็ตาม
สมัครเข้ามาแล้วได้สิทธิ์สูงสุดในระบบ (privilege escalation) การเลื่อนขั้นเป็น
admin ทำได้ทาง CEO เท่านั้น ผ่านหน้า Admin → จัดการผู้ใช้งาน

## Deploy ขึ้น Ubuntu Server จริง (สรุปคร่าวๆ — พาทำละเอียดได้ทีหลัง)

1. ติดตั้ง Python 3.11+, nginx
2. Clone โปรเจกต์ขึ้นเซิร์ฟเวอร์ ตั้งค่า `.env` ให้ `ENV=production` และ
   `JWT_SECRET` เป็นค่าสุ่มจริง, `FRONTEND_ORIGIN` เป็น domain จริง
3. รัน backend ด้วย `gunicorn` + `uvicorn worker` เบื้องหลัง (systemd service)
4. ตั้ง nginx เป็น reverse proxy: `/api/*` → backend (port 8000),
   ไฟล์ frontend เสิร์ฟเป็น static files ตรงๆ
5. ติดตั้ง SSL (Let's Encrypt / certbot) — **จำเป็น** เพราะ cookie ตั้งค่า
   `secure=True` ตอน production จะทำงานเฉพาะ HTTPS เท่านั้น
6. ตั้ง firewall (ufw) เปิดเฉพาะ 80/443

## ความปลอดภัยที่ทำไว้แล้ว

- **Password**: bcrypt hash (cost 12) ไม่เก็บ plaintext
- **Session**: JWT ใน httpOnly cookie (กัน JS อ่าน token), SameSite=Strict
- **Brute-force**: rate limit login/register + ล็อคบัญชีอัตโนมัติ 15 นาที
  หลัง login ผิด 5 ครั้งติด
- **User enumeration**: ข้อความ error login ผิดใช้คำเดียวกันหมด
- **CSRF**: บังคับ custom header `X-Requested-With` ในทุก request ที่แก้ข้อมูล
- **RBAC 3 ระดับ**: user/admin/ceo บังคับที่ backend ผ่าน dependency
  (`require_admin`, `require_ceo`) ไม่ใช่แค่ซ่อนปุ่มฝั่ง frontend —
  ต่อให้แก้ HTML/JS เองก็เรียก API สำเร็จไม่ได้ถ้าไม่มีสิทธิ์จริง
- **ป้องกัน privilege escalation**: หน้าสมัครสมาชิกสาธารณะไม่มีทางเลือก role
  ได้เป็น user เท่านั้นเสมอ ต้องให้ CEO เลื่อนขั้นให้ทีหลัง, ห้าม CEO/admin
  แก้สิทธิ์หรือระงับบัญชี CEO คนอื่น, ห้ามแก้สิทธิ์ตัวเอง
- **Input validation**: Pydantic validate ทุก field ทั้งฝั่ง register,
  course, report

## สิ่งที่ควรทำเพิ่มก่อนใช้งานเก็บเงินจริง

- [ ] เปลี่ยนจาก mock checkout เป็น payment gateway จริง (Omise, 2C2P, Stripe)
- [ ] ย้ายจาก SQLite เป็น PostgreSQL สำหรับ production ที่มี concurrent users เยอะ
- [ ] ใช้ Alembic migration แทน `Base.metadata.create_all()`
- [ ] ตั้ง automated backup ของฐานข้อมูล
- [ ] เพิ่ม email verification ตอนสมัครสมาชิก
- [ ] ทำใบเสร็จให้ตรงตามข้อกำหนดใบกำกับภาษีจริงของกรมสรรพากร (ถ้าจะขายจริง)
- [ ] Load test + security audit ก่อนเปิดใช้งานจริง
