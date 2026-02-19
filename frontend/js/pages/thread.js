import { renderBreadcrumb } from "../components/breadcrumb.js";
import { renderPagination } from "../components/pagination.js";
import { isLoggedIn, getRole } from "../state.js";
import { getThread, pinThread, unpinThread, lockThread, unlockThread } from "../api/admin.js";

const MOD_ROLES = ["Admin", "Moderator"];

export function renderThread(threadId) {
  const breadcrumb = renderBreadcrumb([
    { label: "Forum Home", href: "#/" },
    { label: "Loading..." },
  ]);

  return `
    ${breadcrumb}
    <div class="main-content" id="thread-content" data-thread-id="${threadId}">
      <div style="text-align:center; color: var(--color-text-muted); padding: var(--spacing-lg);">
        Loading...
      </div>
    </div>
  `;
}

export async function mountThread() {
  const container = document.getElementById("thread-content");
  if (!container) return;

  const threadId = Number(container.dataset.threadId);

  let thread = null;
  try {
    thread = await getThread(threadId);
  } catch (err) {
    container.innerHTML = `
      <div class="form-box">
        <div class="form-box__header">Error</div>
        <div class="form-box__body">
          <p style="color: var(--color-error);">${escapeHtml(err.message)}</p>
          <a href="#/" class="btn btn--primary" style="margin-top: var(--spacing-md);">Return Home</a>
        </div>
      </div>
    `;
    return;
  }

  // Update breadcrumb
  const breadcrumb = document.querySelector(".breadcrumb");
  if (breadcrumb) {
    breadcrumb.innerHTML = `
      <a href="#/" class="breadcrumb__item">Forum Home</a>
      <span class="breadcrumb__sep">&raquo;</span>
      <span class="breadcrumb__item breadcrumb__item--active">${escapeHtml(thread.title)}</span>
    `;
  }

  const isMod = isLoggedIn() && MOD_ROLES.includes(getRole());

  // Status badges
  const badges = [];
  if (thread.is_pinned) badges.push('<span class="admin-badge" style="background: var(--color-primary);">Pinned</span>');
  if (thread.is_locked) badges.push('<span class="admin-badge" style="background: var(--color-error);">Locked</span>');
  const badgesHtml = badges.length > 0 ? " " + badges.join(" ") : "";

  // Moderation buttons (placed in thread header)
  const modButtons = isMod
    ? `<div style="display:flex; gap: var(--spacing-xs);">
        <button class="btn btn--sm" id="btn-pin">${thread.is_pinned ? "Unpin" : "Pin"}</button>
        <button class="btn btn--sm ${thread.is_locked ? "btn--primary" : "btn--danger"}" id="btn-lock">${thread.is_locked ? "Unlock" : "Lock"}</button>
      </div>`
    : "";

  // Quick reply (hidden if locked or not logged in)
  let replySection = "";
  if (thread.is_locked) {
    replySection = `
      <div style="margin-top: var(--spacing-lg); padding: var(--spacing-md); background: var(--color-bg-alt); border: 1px solid var(--color-border); text-align:center; color: var(--color-text-muted);">
        &#128274; This thread is locked. No new replies can be posted.
      </div>
    `;
  } else if (isLoggedIn()) {
    replySection = `
      <div class="quick-reply">
        <div class="quick-reply__header">Quick Reply</div>
        <div class="quick-reply__body">
          <div class="form-group">
            <textarea placeholder="Type your reply here..." disabled></textarea>
          </div>
        </div>
        <div class="quick-reply__actions">
          <button class="btn btn--secondary" disabled>Preview</button>
          <button class="btn btn--primary" disabled>Post Reply</button>
        </div>
      </div>
    `;
  } else {
    replySection = `
      <div style="margin-top: var(--spacing-lg); padding: var(--spacing-md); background: var(--color-bg-alt); border: 1px solid var(--color-border); text-align:center; color: var(--color-text-muted);">
        <a href="#/login">Log in</a> to post a reply.
      </div>
    `;
  }

  // Thread opening post (the thread itself, shown as the first post)
  const openingPost = `
    <div class="post">
      <div class="post__sidebar">
        <div class="post__avatar">&#128100;</div>
        <a href="#/profiles/${thread.author.id}" class="post__username">${escapeHtml(thread.author.username)}</a>
      </div>
      <div class="post__body">
        <div class="post__header">
          <span>${formatDate(thread.created_at)}</span>
          <span>#1</span>
        </div>
        <div class="post__content">
          <p style="color: var(--color-text-muted); font-style: italic;">Posts not yet implemented.</p>
        </div>
      </div>
    </div>
  `;

  container.innerHTML = `
    <div class="thread-header" style="display:flex; justify-content:space-between; align-items:flex-start;">
      <div>
        <div class="thread-header__title">${escapeHtml(thread.title)}${badgesHtml}</div>
        <div class="thread-header__meta">
          Started by <strong><a href="#/profiles/${thread.author.id}">${escapeHtml(thread.author.username)}</a></strong>
          &middot; ${formatDate(thread.created_at)}
        </div>
      </div>
      ${modButtons}
    </div>

    <div id="mod-error" class="form-error" style="display:none; margin-top: var(--spacing-sm);"></div>

    ${openingPost}

    ${renderPagination(1, 1)}

    ${replySection}
  `;

  // Mount moderation button handlers
  if (isMod) {
    const pinBtn = document.getElementById("btn-pin");
    const lockBtn = document.getElementById("btn-lock");
    const modError = document.getElementById("mod-error");

    pinBtn.addEventListener("click", async () => {
      pinBtn.disabled = true;
      try {
        modError.style.display = "none";
        if (thread.is_pinned) {
          await unpinThread(threadId);
        } else {
          await pinThread(threadId);
        }
        await mountThread();
      } catch (err) {
        pinBtn.disabled = false;
        modError.textContent = err.message;
        modError.style.display = "block";
      }
    });

    lockBtn.addEventListener("click", async () => {
      lockBtn.disabled = true;
      try {
        modError.style.display = "none";
        if (thread.is_locked) {
          await unlockThread(threadId);
        } else {
          await lockThread(threadId);
        }
        await mountThread();
      } catch (err) {
        lockBtn.disabled = false;
        modError.textContent = err.message;
        modError.style.display = "block";
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
    hour: "2-digit",
    minute: "2-digit",
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
