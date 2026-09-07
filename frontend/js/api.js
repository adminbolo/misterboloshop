// js/api.js
// ตัวกลางเรียก backend API ทั้งหมด
// ค่า default คือ "" (same-origin) เพราะตอนนี้ backend เสิร์ฟ frontend ให้ในตัว
// (รันด้วย uvicorn คำสั่งเดียว เข้าเว็บที่พอร์ตเดียวกันได้เลย)
// ถ้าจะแยก frontend ไปรันคนละที่ (เช่น dev แยก process) ให้ตั้งค่า window.MB_API_BASE
// ก่อนโหลดไฟล์นี้ เช่น <script>window.MB_API_BASE = "http://localhost:8000";</script>
const API_BASE = window.MB_API_BASE || "";

async function apiRequest(path, { method = "GET", body = null } = {}) {
  const headers = { "Content-Type": "application/json" };
  // custom header นี้คือกลไก CSRF ฝั่งเรา (ดู deps.py: verify_csrf_header)
  if (method !== "GET") headers["X-Requested-With"] = "XMLHttpRequest";

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    credentials: "include", // ต้องมี เพื่อให้ cookie mb_token แนบไปด้วย
    body: body ? JSON.stringify(body) : null
  });

  let data = null;
  try { data = await res.json(); } catch (e) { /* no body */ }

  if (!res.ok) {
    const message = (data && (data.detail || data.errors?.[0]?.msg)) || `เกิดข้อผิดพลาด (${res.status})`;
    const err = new Error(message);
    err.status = res.status;
    throw err;
  }
  return data;
}

const api = {
  get: (path) => apiRequest(path),
  post: (path, body) => apiRequest(path, { method: "POST", body }),
  put: (path, body) => apiRequest(path, { method: "PUT", body }),
  del: (path) => apiRequest(path, { method: "DELETE" }),

  me: () => apiRequest("/api/auth/me").catch(() => null),
  register: (data) => apiRequest("/api/auth/register", { method: "POST", body: data }),
  login: (data) => apiRequest("/api/auth/login", { method: "POST", body: data }),
  logout: () => apiRequest("/api/auth/logout", { method: "POST" }),

  categories: () => apiRequest("/api/categories"),
  courses: (category) => apiRequest("/api/courses" + (category ? `?category=${encodeURIComponent(category)}` : "")),
  course: (slug) => apiRequest(`/api/courses/${encodeURIComponent(slug)}`),

  cart: () => apiRequest("/api/cart"),
  addToCart: (course_id, quantity = 1) => apiRequest("/api/cart/add", { method: "POST", body: { course_id, quantity } }),
  updateCartItem: (id, quantity) => apiRequest(`/api/cart/${id}`, { method: "PUT", body: { quantity } }),
  removeCartItem: (id) => apiRequest(`/api/cart/${id}`, { method: "DELETE" }),

  checkout: () => apiRequest("/api/orders/checkout", { method: "POST" }),
  myOrders: () => apiRequest("/api/orders/mine"),
  order: (orderNo) => apiRequest(`/api/orders/${encodeURIComponent(orderNo)}`),
  receiptInfo: (orderNo) => apiRequest(`/api/orders/${encodeURIComponent(orderNo)}/receipt-info`),

  submitReport: (data) => apiRequest("/api/reports", { method: "POST", body: data }),

  admin: {
    stats: () => apiRequest("/api/admin/stats"),
    courses: () => apiRequest("/api/admin/courses"),
    createCourse: (data) => apiRequest("/api/admin/courses", { method: "POST", body: data }),
    updateCourse: (id, data) => apiRequest(`/api/admin/courses/${id}`, { method: "PUT", body: data }),
    deleteCourse: (id) => apiRequest(`/api/admin/courses/${id}`, { method: "DELETE" }),
    createCategory: (data) => apiRequest("/api/admin/categories", { method: "POST", body: data }),
    users: () => apiRequest("/api/admin/users"),
    toggleBan: (id) => apiRequest(`/api/admin/users/${id}/toggle-ban`, { method: "POST" }),
    setRole: (id, role) => apiRequest(`/api/admin/users/${id}/set-role`, { method: "POST", body: { role } }),
    orders: () => apiRequest("/api/admin/orders"),
    reports: () => apiRequest("/api/admin/reports"),
    updateReport: (id, data) => apiRequest(`/api/admin/reports/${id}`, { method: "PUT", body: data }),
    logs: () => apiRequest("/api/admin/logs")
  }
};
