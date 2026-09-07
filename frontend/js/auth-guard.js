// js/auth-guard.js
// ใช้ป้องกันหน้าฝั่ง client (UX เท่านั้น) — การป้องกันจริงอยู่ที่ backend เสมอ
// เรียก requireLogin() หรือ requireAdmin() ที่บนสุดของหน้าที่ต้องการจำกัดสิทธิ์
async function requireLogin() {
  const user = await api.me();
  if (!user) {
    window.location.href = "/login.html?next=" + encodeURIComponent(window.location.pathname);
    return null;
  }
  return user;
}

async function requireAdmin() {
  const user = await requireLogin();
  if (!user) return null;
  if (user.role !== "admin" && user.role !== "ceo") {
    document.body.innerHTML = `<div class="empty-state"><h2>403 - ไม่มีสิทธิ์เข้าถึง</h2><p>หน้านี้สำหรับผู้ดูแลระบบเท่านั้น</p><a href="/index.html" class="btn btn-primary">กลับหน้าหลัก</a></div>`;
    return null;
  }
  return user;
}

async function requireCeo() {
  const user = await requireLogin();
  if (!user) return null;
  if (user.role !== "ceo") {
    document.body.innerHTML = `<div class="empty-state"><h2>403 - ไม่มีสิทธิ์เข้าถึง</h2><p>หน้านี้สำหรับ CEO เท่านั้น</p><a href="/admin/dashboard.html" class="btn btn-primary">กลับ Admin Dashboard</a></div>`;
    return null;
  }
  return user;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function formatMoney(n) {
  return Number(n).toLocaleString("th-TH", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatDate(iso) {
  return new Date(iso).toLocaleString("th-TH", { dateStyle: "medium", timeStyle: "short" });
}

// แสดงรูปคอร์สจริงถ้ามี image_url ตั้งไว้ (จาก admin panel) ถ้าไม่มีหรือโหลดรูปไม่สำเร็จ
// จะ fallback กลับไปเป็นกล่องสีพร้อมตัวอักษรแรกของชื่อคอร์สเหมือนเดิมอัตโนมัติ
function courseImgHtml(course, extraStyle = "") {
  if (course.image_url) {
    const letter = escapeHtml(course.title.slice(0, 1));
    return `<img src="${escapeHtml(course.image_url)}" alt="${escapeHtml(course.title)}" class="card-img-photo" style="${extraStyle}" onerror="this.outerHTML='<div class=&quot;card-img&quot; style=&quot;${extraStyle}&quot;>${letter}</div>'">`;
  }
  return `<div class="card-img" style="${extraStyle}">${escapeHtml(course.title.slice(0, 1))}</div>`;
}
