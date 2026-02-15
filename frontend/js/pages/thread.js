import {
  getThreadById,
  getPostsByThreadId,
  getForumIdByThreadId,
  getForumById,
  getUserById,
} from "../data/dummy.js";
import { renderBreadcrumb } from "../components/breadcrumb.js";
import { renderPagination } from "../components/pagination.js";

export function renderThread(threadId) {
  const thread = getThreadById(threadId);
  if (!thread) {
    return `<div class="main-content"><p>Thread not found.</p></div>`;
  }

  const forumId = getForumIdByThreadId(threadId);
  const forum = getForumById(forumId);
  const threadPosts = getPostsByThreadId(threadId);
  const author = getUserById(thread.authorId);

  const breadcrumb = renderBreadcrumb([
    { label: "Forum Home", href: "#/" },
    { label: forum?.groupName || "", href: "#/" },
    { label: forum?.name || "", href: `#/category/${forumId}` },
    { label: thread.title },
  ]);

  const postsHtml = threadPosts
    .map((post) => {
      const postAuthor = getUserById(post.authorId);
      return `
        <div class="post">
          <div class="post__sidebar">
            <div class="post__avatar">&#128100;</div>
            <div class="post__username">${postAuthor?.username || "Unknown"}</div>
            <div class="post__user-info">
              ${postAuthor?.role || ""}<br>
              Posts: ${postAuthor?.posts || 0}<br>
              Joined: ${postAuthor?.joinDate || ""}
            </div>
          </div>
          <div class="post__body">
            <div class="post__header">
              <span>${post.date}</span>
              <span>#${post.id}</span>
            </div>
            <div class="post__content">
              ${formatContent(post.content)}
            </div>
            <div class="post__footer">
              <button class="btn btn--secondary">Quote</button>
              <button class="btn btn--secondary">Reply</button>
            </div>
          </div>
        </div>
      `;
    })
    .join("");

  const noPostsMsg =
    threadPosts.length === 0
      ? `<p style="padding: var(--spacing-md); color: var(--color-text-light);">No posts yet. Be the first to reply!</p>`
      : "";

  return `
    ${breadcrumb}
    <div class="main-content">
      <div class="thread-header">
        <div class="thread-header__title">${thread.title}</div>
        <div class="thread-header__meta">
          Started by <strong>${author?.username || "Unknown"}</strong>
          &middot; ${thread.replies} replies &middot; ${thread.views} views
        </div>
      </div>

      ${postsHtml}
      ${noPostsMsg}

      ${renderPagination(1, 1)}

      <div class="quick-reply">
        <div class="quick-reply__header">Quick Reply</div>
        <div class="quick-reply__body">
          <div class="form-group">
            <textarea placeholder="Type your reply here..."></textarea>
          </div>
        </div>
        <div class="quick-reply__actions">
          <button class="btn btn--secondary">Preview</button>
          <button class="btn btn--primary">Post Reply</button>
        </div>
      </div>
    </div>
  `;
}

function formatContent(text) {
  return text
    .split("\n")
    .map((line) => (line.trim() === "" ? "<br>" : `<p>${line}</p>`))
    .join("");
}
