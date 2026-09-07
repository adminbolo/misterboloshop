// js/home.js
async function loadFeaturedCourses() {
  const grid = document.getElementById("course-grid");
  try {
    const courses = await api.courses();
    if (courses.length === 0) {
      grid.innerHTML = `<p>ยังไม่มีคอร์สในระบบ</p>`;
      return;
    }
    grid.innerHTML = courses.slice(0, 6).map(courseCardHtml).join("");
  } catch (e) {
    grid.innerHTML = `<p>โหลดข้อมูลคอร์สไม่สำเร็จ: ${escapeHtml(e.message)}</p>`;
  }
}

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

document.addEventListener("DOMContentLoaded", loadFeaturedCourses);
