import { getCategoryForums } from "../data/dummy.js";
import { renderBreadcrumb } from "../components/breadcrumb.js";
import { fetchAPI } from "../api/client.js";

export function renderHome() {
  const breadcrumb = renderBreadcrumb([
    { label: "Forum Home", href: "#/" },
  ]);

  return `
    ${breadcrumb}
    <div class="main-content" id="home-content">
      <div style="text-align:center; color: var(--color-text-muted); padding: var(--spacing-lg);">
        Loading...
      </div>
    </div>
  `;
}

export async function mountHome() {
  const container = document.getElementById("home-content");
  if (!container) return;

  // Fetch real categories
  let realCategories = [];
  try {
    const data = await fetchAPI("/categories/");
    realCategories = data.data || [];
  } catch (err) {
    console.error("Failed to load categories:", err);
  }

  // Get sample categories
  const sampleCategories = getCategoryForums();

  // Render real categories (no forums yet)
  const realGroups = realCategories.map((cat) => `
    <div class="category-group">
      <div class="category-group__header">${escapeHtml(cat.name)}</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th style="width:30px"></th>
              <th>Forum</th>
              <th style="width:70px">Threads</th>
              <th style="width:70px">Posts</th>
              <th style="width:180px">Last Post</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colspan="5" style="text-align:center; color: var(--color-text-muted); padding: var(--spacing-md);">
                No forums in this category yet
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `).join("");

  // Render sample categories
  const sampleGroups = sampleCategories.map((cat) => {
    const rows = cat.forums
      .map(
        (forum) => `
        <tr>
          <td class="forum-table__icon">&#128172;</td>
          <td class="forum-table__title">
            <a href="#/category/${forum.id}">${forum.name}</a>
            <div class="forum-table__description">${forum.description}</div>
          </td>
          <td class="forum-table__stat">${forum.threads}</td>
          <td class="forum-table__stat">${forum.posts}</td>
          <td class="forum-table__lastpost">
            <a href="#">${forum.lastPost.thread}</a><br>
            by <strong>${forum.lastPost.author}</strong><br>
            ${forum.lastPost.date}
          </td>
        </tr>
      `
      )
      .join("");

    return `
      <div class="category-group">
        <div class="category-group__header">${cat.groupName}</div>
        <div class="forum-table">
          <table>
            <thead>
              <tr>
                <th style="width:30px"></th>
                <th>Forum</th>
                <th style="width:70px">Threads</th>
                <th style="width:70px">Posts</th>
                <th style="width:180px">Last Post</th>
              </tr>
            </thead>
            <tbody>
              ${rows}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }).join("");

  // Build final HTML
  let html = "";

  if (realCategories.length > 0) {
    html += realGroups;
    html += `
      <div style="margin: var(--spacing-lg) 0; padding: var(--spacing-md); background: var(--color-bg-alt); border: 1px dashed var(--color-border); text-align: center; color: var(--color-text-muted);">
        &#9660; Sample Data Below (for reference) &#9660;
      </div>
    `;
  }

  html += sampleGroups;

  container.innerHTML = html;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
