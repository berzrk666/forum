import { renderBreadcrumb } from "../components/breadcrumb.js";
import { renderPagination } from "../components/pagination.js";
import { isLoggedIn, getRole } from "../state.js";
import {
  getThread, getPostsByThread, createPost,
  pinThread, unpinThread, lockThread, unlockThread,
} from "../api/admin.js";

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
  let posts = [];
  try {
    const [threadData, postsData] = await Promise.all([
      getThread(threadId),
      getPostsByThread(threadId),
    ]);
    thread = threadData;
    posts = postsData.data || [];
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

  // Moderation buttons
  const modButtons = isMod
    ? `<div style="display:flex; gap: var(--spacing-xs);">
        <button class="btn btn--sm" id="btn-pin">${thread.is_pinned ? "Unpin" : "Pin"}</button>
        <button class="btn btn--sm ${thread.is_locked ? "btn--primary" : "btn--danger"}" id="btn-lock">${thread.is_locked ? "Unlock" : "Lock"}</button>
      </div>`
    : "";

  // Posts
  const postsHtml = posts.length > 0
    ? posts.map((post, idx) => `
        <div class="post">
          <div class="post__sidebar">
            <div class="post__avatar">&#128100;</div>
            <a href="#/profiles/${post.author.id}" class="post__username">${escapeHtml(post.author.username)}</a>
          </div>
          <div class="post__body">
            <div class="post__header">
              <span>${formatDate(post.created_at)}</span>
              <span>#${idx + 1}</span>
            </div>
            <div class="post__content">
              ${formatContent(post.content)}
            </div>
          </div>
        </div>
      `).join("")
    : `<p style="padding: var(--spacing-md); color: var(--color-text-light);">No posts yet. Be the first to reply!</p>`;

  // Reply section
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
          <div id="reply-error" class="form-error" style="display:none;"></div>
          <div class="form-group">
            <textarea id="reply-content" placeholder="Type your reply here..." rows="4"></textarea>
          </div>
        </div>
        <div class="quick-reply__actions">
          <button class="btn btn--primary" id="btn-post-reply">Post Reply</button>
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

  container.innerHTML = `
    <div class="thread-header" style="display:flex; justify-content:space-between; align-items:flex-start;">
      <div>
        <div class="thread-header__title">${escapeHtml(thread.title)}${badgesHtml}</div>
        <div class="thread-header__meta">
          Started by <strong><a href="#/profiles/${thread.author.id}">${escapeHtml(thread.author.username)}</a></strong>
          &middot; ${formatDate(thread.created_at)}
          &middot; ${posts.length} ${posts.length === 1 ? "reply" : "replies"}
        </div>
      </div>
      ${modButtons}
    </div>

    <div id="mod-error" class="form-error" style="display:none; margin-top: var(--spacing-sm);"></div>

    ${postsHtml}

    ${renderPagination(1, 1)}

    ${replySection}
  `;

  // Mount reply handler
  const replyBtn = document.getElementById("btn-post-reply");
  if (replyBtn) {
    replyBtn.addEventListener("click", async () => {
      const textarea = document.getElementById("reply-content");
      const errorEl = document.getElementById("reply-error");
      const content = textarea.value.trim();
      if (!content) return;

      replyBtn.disabled = true;
      replyBtn.textContent = "Posting...";

      try {
        errorEl.style.display = "none";
        await createPost(threadId, content);
        await mountThread();
      } catch (err) {
        replyBtn.disabled = false;
        replyBtn.textContent = "Post Reply";
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
      }
    });
  }

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

function formatContent(text) {
  return text
    .split("\n")
    .map((line) => (line.trim() === "" ? "<br>" : `<p>${escapeHtml(line)}</p>`))
    .join("");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
