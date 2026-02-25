import { renderBreadcrumb } from "../components/breadcrumb.js";
import { renderPagination } from "../components/pagination.js";
import { isLoggedIn, getRole } from "../state.js";
import {
  getThread, getPostsByThread, createPost,
  pinThread, unpinThread, lockThread, unlockThread,
} from "../api/admin.js";

const MOD_ROLES = ["Admin", "Moderator"];
const POSTS_PER_PAGE = 5;
let currentPostPage = 1;

function getForumContext() {
  try {
    return JSON.parse(sessionStorage.getItem("current_forum"));
  } catch {
    return null;
  }
}

export function renderThread(threadId) {
  const forum = getForumContext();
  const crumbs = [{ label: "Forum Home", href: "#/" }];
  if (forum) {
    crumbs.push({ label: forum.name, href: `#/forum/${forum.id}` });
  }
  crumbs.push({ label: "Thread" });
  const breadcrumb = renderBreadcrumb(crumbs);

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
  currentPostPage = 1;
  await loadThreadPage();
}

async function loadThreadPage() {
  const container = document.getElementById("thread-content");
  if (!container) return;

  const threadId = Number(container.dataset.threadId);

  try {
    await _mountThreadInner(container, threadId);
  } catch (err) {
    container.innerHTML = `
      <div class="form-box">
        <div class="form-box__header">Error</div>
        <div class="form-box__body">
          <p style="color: var(--color-error);">Something went wrong: ${escapeHtml(String(err))}</p>
          <a href="#/" class="btn btn--primary" style="margin-top: var(--spacing-md);">Return Home</a>
        </div>
      </div>
    `;
  }
}

async function _mountThreadInner(container, threadId) {
  let thread = null;
  let posts = [];
  let totalPages = 1;
  let totalItems = 0;
  try {
    const [threadData, postsData] = await Promise.all([
      getThread(threadId),
      getPostsByThread(threadId, currentPostPage, POSTS_PER_PAGE),
    ]);
    thread = threadData;
    posts = postsData.data || [];
    totalPages = postsData.total_pages || 1;
    totalItems = postsData.total_items || 0;
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

  if (!thread) {
    container.innerHTML = `
      <div class="form-box">
        <div class="form-box__header">Thread Not Found</div>
        <div class="form-box__body">
          <p>This thread does not exist.</p>
          <a href="#/" class="btn btn--primary" style="margin-top: var(--spacing-md);">Return Home</a>
        </div>
      </div>
    `;
    return;
  }

  // Update breadcrumb with thread title
  const forum = getForumContext();
  const breadcrumb = document.querySelector(".breadcrumb");
  if (breadcrumb) {
    const forumCrumb = forum
      ? `<a href="#/forum/${forum.id}" class="breadcrumb__item">${escapeHtml(forum.name)}</a>
         <span class="breadcrumb__sep">&raquo;</span>`
      : "";
    breadcrumb.innerHTML = `
      <a href="#/" class="breadcrumb__item">Forum Home</a>
      <span class="breadcrumb__sep">&raquo;</span>
      ${forumCrumb}
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

  // Opening post (thread content)
  const opHtml = `
    <div class="post post--op">
      <div class="post__sidebar">
        <div class="post__avatar">&#128100;</div>
        <a href="#/profiles/${thread.author.id}" class="post__username">${escapeHtml(thread.author.username)}</a>
        <div class="post__label">Thread Starter</div>
      </div>
      <div class="post__body">
        <div class="post__header">
          <span>${formatDate(thread.created_at)}</span>
          <span>#1</span>
        </div>
        <div class="post__content">
          ${formatContent(thread.content || "")}
        </div>
      </div>
    </div>
  `;

  // Reply posts
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
              <span>#${(currentPostPage - 1) * POSTS_PER_PAGE + idx + 2}</span>
            </div>
            <div class="post__content">
              ${formatContent(post.content)}
            </div>
          </div>
        </div>
      `).join("")
    : "";

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
    <div class="thread-header thread-header--attached" style="display:flex; justify-content:space-between; align-items:flex-start; border-color: var(--color-primary); border-width: 2px 2px 0 2px; border-style: solid;">
      <div>
        <div class="thread-header__title">${escapeHtml(thread.title)}${badgesHtml}</div>
        <div class="thread-header__meta">
          Started by <strong><a href="#/profiles/${thread.author.id}">${escapeHtml(thread.author.username)}</a></strong>
          &middot; ${formatDate(thread.created_at)}
          &middot; ${totalItems} ${totalItems === 1 ? "reply" : "replies"}
        </div>
      </div>
      ${modButtons}
    </div>
    <div id="mod-error" class="form-error" style="display:none; margin-top: var(--spacing-sm);"></div>
    ${opHtml}

    ${postsHtml}

    ${renderPagination(currentPostPage, totalPages)}

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
        await loadThreadPage();
      } catch (err) {
        replyBtn.disabled = false;
        replyBtn.textContent = "Post Reply";
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
      }
    });
  }

  // Pagination click handler
  const pagination = container.querySelector(".pagination");
  if (pagination) {
    pagination.addEventListener("click", async (e) => {
      const item = e.target.closest(".pagination__item[data-page]");
      if (!item || item.classList.contains("pagination__item--disabled") || item.classList.contains("pagination__item--active")) return;
      currentPostPage = Number(item.dataset.page);
      await loadThreadPage();
      container.scrollIntoView({ behavior: "smooth" });
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
        await loadThreadPage();
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
        await loadThreadPage();
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
