// js/admin/admin-nav.js
function renderAdminSidebar(activePage) {
  const links = [
    { href: "/admin/dashboard.html", label: "📊 Dashboard", key: "dashboard" },
    { href: "/admin/courses.html", label: "📚 จัดการคอร์ส", key: "courses" },
    { href: "/admin/categories.html", label: "🗂️ หมวดหมู่", key: "categories" },
    { href: "/admin/users.html", label: "👤 ผู้ใช้งาน", key: "users" },
    { href: "/admin/orders.html", label: "🧾 คำสั่งซื้อ", key: "orders" },
    { href: "/admin/reports.html", label: "🛠️ แจ้งปัญหา", key: "reports" },
    { href: "/admin/logs.html", label: "📜 Activity Logs", key: "logs" },
  ];
  const mount = document.getElementById("admin-sidebar-mount");
  if (!mount) return;
  mount.innerHTML = `
    <div class="admin-sidebar">
      ${links.map(l => `<a href="${l.href}" class="${l.key === activePage ? "active" : ""}">${l.label}</a>`).join("")}
    </div>
  `;
}
