import { renderBreadcrumb } from "../components/breadcrumb.js";
import { renderPagination } from "../components/pagination.js";
import { isLoggedIn } from "../state.js";
import { getForums, getThreadsByForum, createThread } from "../api/admin.js";

export function renderForum(forumId) {
  const breadcrumb = renderBreadcrumb([
    { label: "Forum Home", href: "#/" },
    { label: "Loading..." },
  ]);

  return `
    ${breadcrumb}
    <div class="main-content" id="forum-content" data-forum-id="${forumId}">
      <div style="text-align:center; color: var(--color-text-muted); padding: var(--spacing-lg);">
        Loading...
      </div>
    </div>
  `;
}

export async function mountForum() {
  const container = document.getElementById("forum-content");
  if (!container) return;

  const forumId = Number(container.dataset.forumId);

  // Fetch forum info and threads in parallel
  let forum = null;
  let threads = [];
  try {
    const [forumsData, threadsData] = await Promise.all([
      getForums(),
      getThreadsByForum(forumId),
    ]);
    forum = (forumsData.data || []).find((f) => f.id === forumId) || null;
    threads = threadsData.data || [];
  } catch (err) {
    container.innerHTML = `
      <div class="form-box">
        <div class="form-box__body">
          <p style="color: var(--color-error);">Failed to load forum: ${escapeHtml(err.message)}</p>
          <a href="#/" class="btn btn--primary" style="margin-top: var(--spacing-md);">Return Home</a>
        </div>
      </div>
    `;
    return;
  }

  if (!forum) {
    container.innerHTML = `
      <div class="form-box">
        <div class="form-box__header">Forum Not Found</div>
        <div class="form-box__body">
          <p>This forum does not exist.</p>
          <a href="#/" class="btn btn--primary" style="margin-top: var(--spacing-md);">Return Home</a>
        </div>
      </div>
    `;
    return;
  }

  // Update breadcrumb now that we have the forum name
  const breadcrumb = document.querySelector(".breadcrumb");
  if (breadcrumb) {
    breadcrumb.innerHTML = `
      <a href="#/" class="breadcrumb__item">Forum Home</a>
      <span class="breadcrumb__sep">&raquo;</span>
      <span class="breadcrumb__item breadcrumb__item--active">${escapeHtml(forum.name)}</span>
    `;
  }

  // Sort: pinned threads first, then by date
  const pinnedThreads = threads.filter((t) => t.is_pinned);
  const normalThreads = threads.filter((t) => !t.is_pinned);

  const threadRows = threads.length > 0
    ? [...pinnedThreads, ...normalThreads].map((thread) => {
        const pinned = thread.is_pinned;
        const locked = thread.is_locked;
        const rowStyle = pinned ? ` style="background-color: var(--color-sticky) !important;"` : "";
        const prefix = pinned ? `<strong>[Sticky]</strong> ` : "";
        const lockIcon = locked ? ` &#128274;` : "";
        const icon = locked ? "&#128274;" : "&#128196;";

        return `
          <tr>
            <td class="forum-table__icon"${rowStyle}>${icon}</td>
            <td class="forum-table__title"${rowStyle}>
              ${prefix}<a href="#/thread/${thread.id}">${escapeHtml(thread.title)}</a>${lockIcon}
              <div class="forum-table__description">
                Started by <a href="#/profiles/${thread.author.id}">${escapeHtml(thread.author.username)}</a>
                ${locked ? ' &mdash; <span style="color: var(--color-error);">Locked</span>' : ""}
              </div>
            </td>
            <td class="forum-table__stat"${rowStyle}>0</td>
            <td class="forum-table__stat"${rowStyle}>0</td>
            <td class="forum-table__lastpost"${rowStyle}>
              by <strong><a href="#/profiles/${thread.author.id}">${escapeHtml(thread.author.username)}</a></strong><br>
              ${formatDate(thread.created_at)}
            </td>
          </tr>
        `;
      }).join("")
    : `<tr>
        <td colspan="5" style="text-align:center; color: var(--color-text-muted); padding: var(--spacing-md);">
          No threads yet. Be the first to post!
        </td>
      </tr>`;

  const newThreadSection = isLoggedIn()
    ? `
      <div class="form-box" style="margin-top: var(--spacing-lg);">
        <div class="form-box__header">Post New Thread</div>
        <div class="form-box__body">
          <div id="new-thread-error" class="form-error" style="display:none;"></div>
          <form id="new-thread-form" style="display:flex; gap: var(--spacing-sm); align-items:flex-end;">
            <div class="form-group" style="flex:1; margin-bottom:0;">
              <label>Thread Title</label>
              <input type="text" id="thread-title" placeholder="Enter thread title" required maxlength="200">
            </div>
            <button type="submit" class="btn btn--primary">Post Thread</button>
          </form>
        </div>
      </div>
    `
    : `
      <div style="margin-top: var(--spacing-lg); padding: var(--spacing-md); background: var(--color-bg-alt); border: 1px solid var(--color-border); text-align:center; color: var(--color-text-muted);">
        <a href="#/login">Log in</a> to post a new thread.
      </div>
    `;

  container.innerHTML = `
    <div class="action-bar">
      <div>
        <h2 style="font-size: 1rem; margin:0;">${escapeHtml(forum.name)}</h2>
        <div style="font-size:11px; color: var(--color-text-muted);">${escapeHtml(forum.description)}</div>
      </div>
      ${isLoggedIn() ? `<button class="btn btn--primary" id="scroll-to-new-thread">+ New Thread</button>` : ""}
    </div>

    <div class="forum-table">
      <table>
        <thead>
          <tr>
            <th style="width:30px"></th>
            <th>Thread</th>
            <th style="width:70px">Replies</th>
            <th style="width:70px">Views</th>
            <th style="width:180px">Last Post</th>
          </tr>
        </thead>
        <tbody>
          ${threadRows}
        </tbody>
      </table>
    </div>

    ${renderPagination(1, 1)}

    ${newThreadSection}
  `;

  // Scroll-to-form button
  const scrollBtn = document.getElementById("scroll-to-new-thread");
  if (scrollBtn) {
    scrollBtn.addEventListener("click", () => {
      document.getElementById("new-thread-form")?.scrollIntoView({ behavior: "smooth" });
      document.getElementById("thread-title")?.focus();
    });
  }

  // New thread form submission
  const form = document.getElementById("new-thread-form");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const errorEl = document.getElementById("new-thread-error");
      const title = document.getElementById("thread-title").value.trim();
      if (!title) return;

      const submitBtn = form.querySelector("button[type=submit]");
      submitBtn.disabled = true;
      submitBtn.textContent = "Posting...";

      try {
        errorEl.style.display = "none";
        await createThread(title, forumId);
        // Re-mount to refresh thread list
        await mountForum();
      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.textContent = "Post Thread";
        errorEl.textContent = err.message.includes("401") || err.message.toLowerCase().includes("unauthorized")
          ? "You must be logged in to post a thread."
          : err.message;
        errorEl.style.display = "block";
      }
    });
  }
}

function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
