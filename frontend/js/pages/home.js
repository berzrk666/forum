import { getCategoryForums } from "../data/dummy.js";
import { renderBreadcrumb } from "../components/breadcrumb.js";

export function renderHome() {
  const categories = getCategoryForums();

  const breadcrumb = renderBreadcrumb([
    { label: "Forum Home", href: "#/" },
  ]);

  const groups = categories.map((cat) => {
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

  return `
    ${breadcrumb}
    <div class="main-content">
      ${groups}
    </div>
  `;
}
