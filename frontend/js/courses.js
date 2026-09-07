// js/courses.js
function courseCardHtml(course) {
  return `
    <a href="/course-detail.html?slug=${encodeURIComponent(course.slug)}" class="card">
      ${courseImgHtml(course)}
      <div class="card-body">
        <div class="card-title">${escapeHtml(course.title)}</div>
        <div class="card-desc">${escapeHtml(course.short_desc || "")}</div>
        <div class="card-price">฿${formatMoney(course.price)}</div>
      </div>
    </a>
  `;
}

async function loadCategories(activeSlug) {
  const mount = document.getElementById("category-filter");
  try {
    const cats = await api.categories();
    const chip = (label, slug, active) => `
      <a href="${slug ? `/courses.html?category=${encodeURIComponent(slug)}` : "/courses.html"}"
         class="btn btn-sm ${active ? "btn-primary" : "btn-secondary"}">${escapeHtml(label)}</a>
    `;
    mount.innerHTML = chip("ทั้งหมด", null, !activeSlug) + cats.map(c => chip(c.name, c.slug, c.slug === activeSlug)).join("");
  } catch (e) { /* ignore filter load error */ }
}

async function loadCourses() {
  const params = new URLSearchParams(window.location.search);
  const category = params.get("category");
  const grid = document.getElementById("course-grid");

  await loadCategories(category);

  try {
    const courses = await api.courses(category);
    grid.innerHTML = courses.length
      ? courses.map(courseCardHtml).join("")
      : `<div class="empty-state">ยังไม่มีคอร์สในหมวดนี้</div>`;
  } catch (e) {
    grid.innerHTML = `<p>โหลดข้อมูลไม่สำเร็จ: ${escapeHtml(e.message)}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", loadCourses);
