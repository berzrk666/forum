import { getForumById, getThreadsByForumId, getUserById } from "../data/dummy.js";
import { renderBreadcrumb } from "../components/breadcrumb.js";
import { renderPagination } from "../components/pagination.js";

export function renderCategory(forumId) {
  const forum = getForumById(forumId);
  if (!forum) {
    return `<div class="main-content"><p>Forum not found.</p></div>`;
  }

  const allThreads = getThreadsByForumId(forumId);

  const breadcrumb = renderBreadcrumb([
    { label: "Forum Home", href: "#/" },
    { label: forum.groupName, href: "#/" },
    { label: forum.name },
  ]);

  const stickyRows = allThreads
    .filter((t) => t.sticky)
    .map((t) => threadRow(t, true))
    .join("");

  const normalRows = allThreads
    .filter((t) => !t.sticky)
    .map((t) => threadRow(t, false))
    .join("");

  return `
    ${breadcrumb}
    <div class="main-content">
      <div class="action-bar">
        <h2 style="font-size: 1rem;">${forum.name}</h2>
        <button class="btn btn--primary">+ New Thread</button>
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
            ${stickyRows}${normalRows}
          </tbody>
        </table>
      </div>

      ${renderPagination(1, 1)}
    </div>
  `;
}

function threadRow(thread, isSticky) {
  const author = getUserById(thread.authorId);
  const prefix = isSticky ? `<strong>[Sticky]</strong> ` : "";
  const rowStyle = isSticky ? ` style="background-color: var(--color-sticky) !important;"` : "";

  return `
    <tr>
      <td class="forum-table__icon"${rowStyle}>&#128196;</td>
      <td class="forum-table__title"${rowStyle}>
        ${prefix}<a href="#/thread/${thread.id}">${thread.title}</a>
        <div class="forum-table__description">Started by ${author?.username || "Unknown"}</div>
      </td>
      <td class="forum-table__stat"${rowStyle}>${thread.replies}</td>
      <td class="forum-table__stat"${rowStyle}>${thread.views}</td>
      <td class="forum-table__lastpost"${rowStyle}>
        by <strong>${thread.lastPost.author}</strong><br>
        ${thread.lastPost.date}
      </td>
    </tr>
  `;
}
