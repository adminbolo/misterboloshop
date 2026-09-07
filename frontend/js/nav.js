// js/nav.js
// วาด navbar เดียวกันทุกหน้า และเช็คสถานะ login แบบ dynamic
async function renderNav() {
  const mount = document.getElementById("navbar-mount");
  if (!mount) return;

  const user = await api.me();
  let cartCount = 0;
  if (user) {
    try {
      const items = await api.cart();
      cartCount = items.reduce((s, i) => s + i.quantity, 0);
    } catch (e) { /* ignore */ }
  }

  mount.innerHTML = `
    <nav class="navbar">
      <div class="container">
        <a href="/index.html" class="brand">🥟 มิสเตอร์โบโล่</a>
        <div class="nav-links">
          <a href="/courses.html">คอร์สเรียน</a>
          <a href="/about.html">เกี่ยวกับเรา</a>
          <a href="/howto.html">วิธีใช้งาน</a>
          <a href="/report.html">แจ้งปัญหา</a>
          ${user ? `
            <a href="/cart.html">ตะกร้า ${cartCount > 0 ? `<span class="nav-cart-badge">${cartCount}</span>` : ""}</a>
            <a href="/my-orders.html">คำสั่งซื้อของฉัน</a>
            ${(user.role === "admin" || user.role === "ceo") ? `<a href="/admin/dashboard.html">${user.role === "ceo" ? "👑 CEO Panel" : "Admin"}</a>` : ""}
            <a href="#" id="nav-logout">ออกจากระบบ (${user.username})</a>
          ` : `
            <a href="/login.html">เข้าสู่ระบบ</a>
            <a href="/register.html" class="btn-nav">สมัครสมาชิก</a>
          `}
        </div>
      </div>
    </nav>
  `;

  const logoutLink = document.getElementById("nav-logout");
  if (logoutLink) {
    logoutLink.addEventListener("click", async (e) => {
      e.preventDefault();
      await api.logout().catch(() => {});
      window.location.href = "/index.html";
    });
  }
}

document.addEventListener("DOMContentLoaded", renderNav);
