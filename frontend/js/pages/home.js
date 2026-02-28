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

  let realCategories = [];
  let realForums = [];
  try {
    const [catData, forumData] = await Promise.all([
      fetchAPI("/categories/"),
      fetchAPI("/forums/"),
    ]);
    realCategories = catData.data || [];
    realForums = forumData.data || [];
  } catch (err) {
    console.error("Failed to load data:", err);
  }

  // Group forums by category name
  const forumsByCategory = {};
  for (const forum of realForums) {
    const catName = forum.category.name;
    if (!forumsByCategory[catName]) {
      forumsByCategory[catName] = [];
    }
    forumsByCategory[catName].push(forum);
  }

  // Render real categories with their forums
  const realGroups = realCategories.map((cat) => {
    const forums = forumsByCategory[cat.name] || [];
    const forumRows = forums.length > 0
      ? forums.map((forum) => `
          <tr>
            <td class="forum-table__icon">&#128172;</td>
            <td class="forum-table__title">
              <a href="#/forum/${forum.id}" data-forum-name="${escapeAttr(forum.name)}">${escapeHtml(forum.name)}</a>
              <div class="forum-table__description">${escapeHtml(forum.description)}</div>
            </td>
            <td class="forum-table__stat">${forum.n_threads}</td>
            <td class="forum-table__stat">${forum.n_posts}</td>
            <td class="forum-table__lastpost" style="color: var(--color-text-muted);">No posts yet</td>
          </tr>
        `).join("")
      : `<tr>
          <td colspan="5" style="text-align:center; color: var(--color-text-muted); padding: var(--spacing-md);">
            No forums in this category yet
          </td>
        </tr>`;

    return `
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
              ${forumRows}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }).join("");

  // Sample categories as fallback
  const sampleCategories = getCategoryForums();
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
          <td class="forum-table__stat">${forum.n_threads}</td>
          <td class="forum-table__stat">${forum.n_posts}</td>
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

  // Store forum context on click for breadcrumbs
  container.addEventListener("click", (e) => {
    const link = e.target.closest("a[data-forum-name]");
    if (!link) return;
    const href = link.getAttribute("href");
    const match = href.match(/#\/forum\/(\d+)/);
    if (match) {
      sessionStorage.setItem("current_forum", JSON.stringify({
        id: Number(match[1]),
        name: link.dataset.forumName,
      }));
    }
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function escapeAttr(str) {
  return str.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
