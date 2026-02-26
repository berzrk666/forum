import { renderBreadcrumb } from "../components/breadcrumb.js";
import { isLoggedIn, getRole } from "../state.js";
import { getUsers, getCategories, createCategory, deleteCategory, getForums, createForum, updateForum } from "../api/admin.js";

const ADMIN_ROLES = ["admin", "moderator"];

function canAccessAdmin() {
  return isLoggedIn() && ADMIN_ROLES.includes(getRole());
}

export function renderAdmin() {
  if (!canAccessAdmin()) {
    return `
      <div class="main-content">
        <div class="form-box">
          <div class="form-box__header">Access Denied</div>
          <div class="form-box__body">
            <p>You do not have permission to access the admin dashboard.</p>
            <br>
            <a href="#/" class="btn btn--primary">Return to Forum</a>
          </div>
        </div>
      </div>
    `;
  }

  const breadcrumb = renderBreadcrumb([
    { label: "Forum Home", href: "#/" },
    { label: "Admin Dashboard" },
  ]);

  return `
    ${breadcrumb}
    <div class="main-content">
      <div class="admin-layout">
        <nav class="admin-sidebar">
          <div class="admin-sidebar__section">
            <div class="admin-sidebar__header">General</div>
            <div class="admin-sidebar__links">
              <a class="admin-sidebar__link admin-sidebar__link--active" data-section="dashboard">Dashboard</a>
              <a class="admin-sidebar__link" data-section="settings">Forum Settings</a>
              <a class="admin-sidebar__link" data-section="announcements">Announcements</a>
            </div>
          </div>
          <div class="admin-sidebar__section">
            <div class="admin-sidebar__header">Forums</div>
            <div class="admin-sidebar__links">
              <a class="admin-sidebar__link" data-section="categories">Categories</a>
              <a class="admin-sidebar__link" data-section="forums">Forums</a>
              <a class="admin-sidebar__link" data-section="forum-order">Forum Ordering</a>
            </div>
          </div>
          <div class="admin-sidebar__section">
            <div class="admin-sidebar__header">Users</div>
            <div class="admin-sidebar__links">
              <a class="admin-sidebar__link" data-section="users">Manage Users</a>
              <a class="admin-sidebar__link" data-section="roles">Roles</a>
              <a class="admin-sidebar__link" data-section="permissions">Permissions</a>
              <a class="admin-sidebar__link" data-section="ranks">User Ranks</a>
              <a class="admin-sidebar__link" data-section="bans">Bans & Warnings</a>
            </div>
          </div>
          <div class="admin-sidebar__section">
            <div class="admin-sidebar__header">Moderation</div>
            <div class="admin-sidebar__links">
              <a class="admin-sidebar__link" data-section="reports">Reported Content</a>
              <a class="admin-sidebar__link" data-section="approval">Approval Queue</a>
              <a class="admin-sidebar__link" data-section="word-filters">Word Filters</a>
              <a class="admin-sidebar__link" data-section="mod-logs">Moderation Logs</a>
            </div>
          </div>
          <div class="admin-sidebar__section">
            <div class="admin-sidebar__header">Appearance</div>
            <div class="admin-sidebar__links">
              <a class="admin-sidebar__link" data-section="themes">Themes</a>
              <a class="admin-sidebar__link" data-section="smilies">Smilies</a>
              <a class="admin-sidebar__link" data-section="bbcode">BBCode</a>
            </div>
          </div>
          <div class="admin-sidebar__section">
            <div class="admin-sidebar__header">Maintenance</div>
            <div class="admin-sidebar__links">
              <a class="admin-sidebar__link" data-section="cache">Cache</a>
              <a class="admin-sidebar__link" data-section="backups">Backups</a>
              <a class="admin-sidebar__link" data-section="logs">System Logs</a>
            </div>
          </div>
        </nav>
        <div class="admin-content" id="admin-content">
          <div class="admin-content__header">Dashboard</div>
          <div class="admin-content__body">
            <div style="text-align:center; color: var(--color-text-muted);">Loading...</div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function mountAdmin() {
  if (!canAccessAdmin()) return;

  let activeSection = "dashboard";

  document.querySelectorAll(".admin-sidebar__link").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const section = link.dataset.section;
      if (section === activeSection) return;

      document.querySelectorAll(".admin-sidebar__link").forEach((l) =>
        l.classList.remove("admin-sidebar__link--active")
      );
      link.classList.add("admin-sidebar__link--active");

      activeSection = section;
      renderSection(section);
    });
  });

  renderSection(activeSection);
}

async function renderSection(section) {
  const container = document.getElementById("admin-content");
  if (!container) return;

  const sections = {
    // General
    dashboard: { title: "Dashboard", render: renderDashboard },
    settings: { title: "Forum Settings", render: renderSettings },
    announcements: { title: "Announcements", render: renderAnnouncements },
    // Forums
    categories: { title: "Categories", render: renderCategories },
    forums: { title: "Forums", render: renderForums },
    "forum-order": { title: "Forum Ordering", render: renderPlaceholder },
    // Users
    users: { title: "Manage Users", render: renderUsers },
    roles: { title: "Roles", render: renderRoles },
    permissions: { title: "Permissions", render: renderPermissions },
    ranks: { title: "User Ranks", render: renderRanks },
    bans: { title: "Bans & Warnings", render: renderBans },
    // Moderation
    reports: { title: "Reported Content", render: renderReports },
    approval: { title: "Approval Queue", render: renderApproval },
    "word-filters": { title: "Word Filters", render: renderWordFilters },
    "mod-logs": { title: "Moderation Logs", render: renderModLogs },
    // Appearance
    themes: { title: "Themes", render: renderThemes },
    smilies: { title: "Smilies", render: renderPlaceholder },
    bbcode: { title: "BBCode", render: renderPlaceholder },
    // Maintenance
    cache: { title: "Cache Management", render: renderCache },
    backups: { title: "Backups", render: renderBackups },
    logs: { title: "System Logs", render: renderPlaceholder },
  };

  const config = sections[section] || sections.dashboard;

  container.innerHTML = `
    <div class="admin-content__header">${config.title}</div>
    <div class="admin-content__body">
      <div style="text-align:center; color: var(--color-text-muted);">Loading...</div>
    </div>
  `;

  const body = container.querySelector(".admin-content__body");
  await config.render(body);
}

// ═══════════════════════════════════════════════════════════════════════════
// GENERAL
// ═══════════════════════════════════════════════════════════════════════════

async function renderDashboard(container) {
  try {
    const data = await getUsers(1, 5);
    const users = data.data || [];

    container.innerHTML = `
      <div class="stats-grid">
        <div class="stat-box">
          <div class="stat-box__value">${data.total_items || 0}</div>
          <div class="stat-box__label">Users</div>
        </div>
        <div class="stat-box">
          <div class="stat-box__value">0</div>
          <div class="stat-box__label">Categories</div>
        </div>
        <div class="stat-box">
          <div class="stat-box__value">0</div>
          <div class="stat-box__label">Forums</div>
        </div>
        <div class="stat-box">
          <div class="stat-box__value">0</div>
          <div class="stat-box__label">Threads</div>
        </div>
        <div class="stat-box">
          <div class="stat-box__value">0</div>
          <div class="stat-box__label">Posts</div>
        </div>
        <div class="stat-box">
          <div class="stat-box__value">0</div>
          <div class="stat-box__label">Reports</div>
        </div>
      </div>

      <div style="display: flex; gap: var(--spacing-md);">
        <div style="flex: 1;">
          <div class="category-group">
            <div class="category-group__header">Recent Users</div>
            <div class="forum-table">
              <table>
                <thead>
                  <tr>
                    <th>Username</th>
                    <th style="width:120px;">Registered</th>
                  </tr>
                </thead>
                <tbody>
                  ${renderUserRowsCompact(users.slice(0, 5))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div style="flex: 1;">
          <div class="category-group">
            <div class="category-group__header">Recent Activity</div>
            <div class="forum-table">
              <table>
                <thead>
                  <tr>
                    <th>Action</th>
                    <th style="width:120px;">Time</th>
                  </tr>
                </thead>
                <tbody>
                  <tr><td colspan="2" style="text-align:center; color: var(--color-text-muted);">No recent activity</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<p style="color: var(--color-error);">${escapeHtml(err.message)}</p>`;
  }
}

function renderSettings(container) {
  container.innerHTML = `
    <form class="admin-form">
      <div class="admin-form__section">
        <h3 class="admin-form__title">Basic Settings</h3>
        <div class="form-group">
          <label>Forum Name</label>
          <input type="text" value="RetroForum" placeholder="Enter forum name">
        </div>
        <div class="form-group">
          <label>Forum Description</label>
          <textarea rows="3" placeholder="A brief description of your forum">A classic forum for discussions</textarea>
        </div>
        <div class="form-group">
          <label>Site URL</label>
          <input type="url" value="http://localhost:8080" placeholder="https://example.com">
        </div>
      </div>

      <div class="admin-form__section">
        <h3 class="admin-form__title">User Settings</h3>
        <div class="form-group">
          <label><input type="checkbox" checked> Allow new registrations</label>
        </div>
        <div class="form-group">
          <label><input type="checkbox"> Require email verification</label>
        </div>
        <div class="form-group">
          <label><input type="checkbox"> Enable CAPTCHA on registration</label>
        </div>
        <div class="form-group">
          <label>Default user role</label>
          <select class="admin-select">
            <option>Member</option>
            <option>Junior Member</option>
          </select>
        </div>
      </div>

      <div class="admin-form__section">
        <h3 class="admin-form__title">Posting Settings</h3>
        <div class="form-group">
          <label>Minimum posts before links allowed</label>
          <input type="number" value="5" min="0">
        </div>
        <div class="form-group">
          <label>Flood control (seconds between posts)</label>
          <input type="number" value="30" min="0">
        </div>
        <div class="form-group">
          <label><input type="checkbox" checked> Allow signatures</label>
        </div>
        <div class="form-group">
          <label><input type="checkbox" checked> Allow avatars</label>
        </div>
      </div>

      <div class="admin-form__actions">
        <button type="button" class="btn btn--primary" disabled>Save Settings</button>
      </div>
    </form>
  `;
}

function renderAnnouncements(container) {
  container.innerHTML = `
    <div class="category-group">
      <div class="category-group__header">Active Announcements</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th style="width:100px;">Type</th>
              <th style="width:120px;">Created</th>
              <th style="width:100px; text-align:center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr><td colspan="4" style="text-align:center; color: var(--color-text-muted);">No announcements</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="form-box" style="max-width:100%; margin-top: var(--spacing-md);">
      <div class="form-box__header">Create Announcement</div>
      <div class="form-box__body">
        <div class="form-group">
          <label>Title</label>
          <input type="text" placeholder="Announcement title">
        </div>
        <div class="form-group">
          <label>Content</label>
          <textarea rows="4" placeholder="Announcement content..."></textarea>
        </div>
        <div class="form-group">
          <label>Type</label>
          <select class="admin-select" style="width:200px;">
            <option>Info</option>
            <option>Warning</option>
            <option>Important</option>
          </select>
        </div>
        <div class="form-group">
          <label><input type="checkbox"> Show on all pages</label>
        </div>
        <button type="button" class="btn btn--primary" disabled>Create Announcement</button>
      </div>
    </div>
  `;
}

// ═══════════════════════════════════════════════════════════════════════════
// FORUMS
// ═══════════════════════════════════════════════════════════════════════════

async function renderCategories(container) {
  let categories = [];
  try {
    const data = await getCategories();
    categories = data.data || [];
  } catch (err) {
    container.innerHTML = `<p style="color: var(--color-error);">${escapeHtml(err.message)}</p>`;
    return;
  }

  const realCategoryRows = categories.length > 0
    ? categories.map((cat) => `
        <tr>
          <td>${cat.order}</td>
          <td>${escapeHtml(cat.name)}</td>
          <td>0</td>
          <td style="text-align:center;">
            <button class="btn btn--sm" disabled>Edit</button>
            <button class="btn btn--sm btn--danger" data-delete-category="${cat.id}">Delete</button>
          </td>
        </tr>
      `).join("")
    : '<tr><td colspan="4" style="text-align:center; color: var(--color-text-muted);">No categories configured</td></tr>';

  const sampleCategories = [
    { order: 1, name: "General", forums: 2 },
    { order: 2, name: "Technology", forums: 3 },
    { order: 3, name: "Off-Topic", forums: 2 },
  ];

  const sampleCategoryRows = sampleCategories.map((cat) => `
    <tr style="opacity: 0.6;">
      <td>${cat.order}</td>
      <td>${escapeHtml(cat.name)}</td>
      <td>${cat.forums}</td>
      <td style="text-align:center;">
        <button class="btn btn--sm" disabled>Edit</button>
        <button class="btn btn--sm btn--danger" disabled>Delete</button>
      </td>
    </tr>
  `).join("");

  container.innerHTML = `
    <div class="category-group">
      <div class="category-group__header">Forum Categories</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th style="width:50px;">Order</th>
              <th>Name</th>
              <th style="width:80px;">Forums</th>
              <th style="width:120px; text-align:center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            ${realCategoryRows}
          </tbody>
        </table>
      </div>
    </div>

    <div class="form-box" style="max-width:100%; margin-top: var(--spacing-md);">
      <div class="form-box__header">Add Category</div>
      <div class="form-box__body">
        <div id="category-error" class="form-error" style="display:none;"></div>
        <form id="add-category-form" style="display:flex; gap: var(--spacing-sm); align-items:flex-end;">
          <div class="form-group" style="flex:1; margin-bottom:0;">
            <label>Category Name</label>
            <input type="text" id="category-name" placeholder="e.g. General Discussion" required>
          </div>
          <div class="form-group" style="width:80px; margin-bottom:0;">
            <label>Order</label>
            <input type="number" id="category-order" min="1" placeholder="${categories.length + 1}">
          </div>
          <button type="submit" class="btn btn--primary">Add Category</button>
        </form>
      </div>
    </div>

    <div class="category-group" style="margin-top: var(--spacing-lg);">
      <div class="category-group__header" style="background: var(--color-text-muted);">Sample Categories (for reference)</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th style="width:50px;">Order</th>
              <th>Name</th>
              <th style="width:80px;">Forums</th>
              <th style="width:120px; text-align:center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            ${sampleCategoryRows}
          </tbody>
        </table>
      </div>
    </div>
  `;

  // Mount form handler
  const form = document.getElementById("add-category-form");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const errorEl = document.getElementById("category-error");
      const nameInput = document.getElementById("category-name");
      const orderInput = document.getElementById("category-order");

      const name = nameInput.value.trim();
      const order = orderInput.value ? parseInt(orderInput.value, 10) : null;

      if (!name) return;

      try {
        errorEl.style.display = "none";
        await createCategory(name, order);
        await renderCategories(container);
      } catch (err) {
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
      }
    });
  }

  // Mount delete handlers
  document.querySelectorAll("[data-delete-category]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.deleteCategory;
      if (!confirm("Are you sure you want to delete this category?")) return;
      try {
        await deleteCategory(id);
        await renderCategories(container);
      } catch (err) {
        alert(err.message);
      }
    });
  });
}

async function renderForums(container) {
  let forums = [];
  let categories = [];
  try {
    const [forumsData, categoriesData] = await Promise.all([getForums(), getCategories()]);
    forums = forumsData.data || [];
    categories = categoriesData.data || [];
  } catch (err) {
    container.innerHTML = `<p style="color: var(--color-error);">${escapeHtml(err.message)}</p>`;
    return;
  }

  const forumRows = forums.length > 0
    ? forums.map((forum) => `
        <tr data-forum-row="${forum.id}">
          <td>${forum.order}</td>
          <td><strong>${escapeHtml(forum.name)}</strong>
            <div style="font-size:11px; color: var(--color-text-muted);">${escapeHtml(forum.description)}</div>
          </td>
          <td>${escapeHtml(forum.category.name)}</td>
          <td style="text-align:center;">
            <button class="btn btn--sm" data-edit-forum="${forum.id}">Edit</button>
          </td>
        </tr>
      `).join("")
    : '<tr><td colspan="4" style="text-align:center; color: var(--color-text-muted);">No forums configured</td></tr>';

  const categoryOptions = categories.map((cat) =>
    `<option value="${cat.id}">${escapeHtml(cat.name)}</option>`
  ).join("");

  container.innerHTML = `
    <div class="category-group">
      <div class="category-group__header">Forums</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th style="width:50px;">Order</th>
              <th>Name</th>
              <th style="width:120px;">Category</th>
              <th style="width:120px; text-align:center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            ${forumRows}
          </tbody>
        </table>
      </div>
    </div>

    <div id="edit-forum-box" class="form-box" style="max-width:100%; margin-top: var(--spacing-md); display:none;">
      <div class="form-box__header">Edit Forum</div>
      <div class="form-box__body">
        <div id="edit-forum-error" class="form-error" style="display:none;"></div>
        <form id="edit-forum-form">
          <input type="hidden" id="edit-forum-id">
          <div style="display:flex; gap: var(--spacing-sm); align-items:flex-end; flex-wrap:wrap;">
            <div class="form-group" style="flex:1; min-width:150px; margin-bottom:0;">
              <label>Forum Name</label>
              <input type="text" id="edit-forum-name" required>
            </div>
            <div class="form-group" style="flex:1; min-width:150px; margin-bottom:0;">
              <label>Description</label>
              <input type="text" id="edit-forum-description" required>
            </div>
            <div class="form-group" style="width:150px; margin-bottom:0;">
              <label>Category</label>
              <select class="admin-select" id="edit-forum-category" required>
                ${categoryOptions}
              </select>
            </div>
            <div class="form-group" style="width:80px; margin-bottom:0;">
              <label>Order</label>
              <input type="number" id="edit-forum-order" min="1" required>
            </div>
            <button type="submit" class="btn btn--primary">Save</button>
            <button type="button" class="btn" id="cancel-edit-forum">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <div class="form-box" style="max-width:100%; margin-top: var(--spacing-md);">
      <div class="form-box__header">Add Forum</div>
      <div class="form-box__body">
        <div id="forum-error" class="form-error" style="display:none;"></div>
        <form id="add-forum-form">
          <div style="display:flex; gap: var(--spacing-sm); align-items:flex-end; flex-wrap:wrap;">
            <div class="form-group" style="flex:1; min-width:150px; margin-bottom:0;">
              <label>Forum Name</label>
              <input type="text" id="forum-name" placeholder="e.g. Introductions" required>
            </div>
            <div class="form-group" style="flex:1; min-width:150px; margin-bottom:0;">
              <label>Description</label>
              <input type="text" id="forum-description" placeholder="Brief description" required>
            </div>
            <div class="form-group" style="width:150px; margin-bottom:0;">
              <label>Category</label>
              <select class="admin-select" id="forum-category" required>
                <option value="">-- Select --</option>
                ${categoryOptions}
              </select>
            </div>
            <div class="form-group" style="width:80px; margin-bottom:0;">
              <label>Order</label>
              <input type="number" id="forum-order" min="1" placeholder="${forums.length + 1}">
            </div>
            <button type="submit" class="btn btn--primary">Add Forum</button>
          </div>
        </form>
      </div>
    </div>
  `;

  // Mount add form handler
  const addForm = document.getElementById("add-forum-form");
  if (addForm) {
    addForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const errorEl = document.getElementById("forum-error");
      const name = document.getElementById("forum-name").value.trim();
      const description = document.getElementById("forum-description").value.trim();
      const category_id = parseInt(document.getElementById("forum-category").value, 10);
      const orderVal = document.getElementById("forum-order").value;
      const order = orderVal ? parseInt(orderVal, 10) : forums.length + 1;

      if (!name || !description || !category_id) return;

      try {
        errorEl.style.display = "none";
        await createForum(name, description, order, category_id);
        await renderForums(container);
      } catch (err) {
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
      }
    });
  }

  // Mount edit button handlers
  document.querySelectorAll("[data-edit-forum]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const forumId = parseInt(btn.dataset.editForum, 10);
      const forum = forums.find((f) => f.id === forumId);
      if (!forum) return;

      document.getElementById("edit-forum-id").value = forum.id;
      document.getElementById("edit-forum-name").value = forum.name;
      document.getElementById("edit-forum-description").value = forum.description;
      document.getElementById("edit-forum-category").value = forum.category.id;
      document.getElementById("edit-forum-order").value = forum.order;
      document.getElementById("edit-forum-box").style.display = "block";
      document.getElementById("edit-forum-error").style.display = "none";
    });
  });

  // Mount cancel edit handler
  const cancelBtn = document.getElementById("cancel-edit-forum");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      document.getElementById("edit-forum-box").style.display = "none";
    });
  }

  // Mount edit form handler
  const editForm = document.getElementById("edit-forum-form");
  if (editForm) {
    editForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const errorEl = document.getElementById("edit-forum-error");
      const id = parseInt(document.getElementById("edit-forum-id").value, 10);
      const name = document.getElementById("edit-forum-name").value.trim();
      const description = document.getElementById("edit-forum-description").value.trim();
      const category_id = parseInt(document.getElementById("edit-forum-category").value, 10);
      const order = parseInt(document.getElementById("edit-forum-order").value, 10);

      if (!name || !description || !category_id || !order) return;

      try {
        errorEl.style.display = "none";
        await updateForum(id, { name, description, category_id, order });
        await renderForums(container);
      } catch (err) {
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
      }
    });
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// USERS
// ═══════════════════════════════════════════════════════════════════════════

async function renderUsers(container) {
  try {
    const data = await getUsers();
    const users = data.data || [];

    container.innerHTML = `
      <div class="admin-toolbar">
        <div class="admin-toolbar__search">
          <input type="text" placeholder="Search users..." class="admin-search">
        </div>
        <div class="admin-toolbar__actions">
          <button class="btn btn--primary btn--sm" disabled>Add User</button>
        </div>
      </div>

      <div class="category-group">
        <div class="category-group__header">All Users (${data.total_items || 0})</div>
        <div class="forum-table">
          <table>
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th style="width:100px;">Role</th>
                <th style="width:80px;">Posts</th>
                <th style="width:120px;">Registered</th>
                <th style="width:140px; text-align:center;">Actions</th>
              </tr>
            </thead>
            <tbody>
              ${users.map((user) => `
                <tr>
                  <td><strong>${escapeHtml(user.username)}</strong></td>
                  <td>${escapeHtml(user.email)}</td>
                  <td><span class="admin-badge">Member</span></td>
                  <td>0</td>
                  <td>${formatDate(user.created_at)}</td>
                  <td style="text-align:center;">
                    <button class="btn btn--sm" disabled>Edit</button>
                    <button class="btn btn--sm btn--danger" disabled>Ban</button>
                  </td>
                </tr>
              `).join("") || '<tr><td colspan="6" style="text-align:center;">No users found.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<p style="color: var(--color-error);">${escapeHtml(err.message)}</p>`;
  }
}

function renderRoles(container) {
  container.innerHTML = `
    <div class="category-group">
      <div class="category-group__header">Roles</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th>Role Name</th>
              <th style="width:80px;">Users</th>
              <th style="width:100px;">Priority</th>
              <th style="width:120px; text-align:center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><span class="admin-badge admin-badge--admin">Admin</span> Administrator</td>
              <td>1</td>
              <td>100</td>
              <td style="text-align:center;">
                <button class="btn btn--sm" disabled>Edit</button>
              </td>
            </tr>
            <tr>
              <td><span class="admin-badge admin-badge--mod">Mod</span> Moderator</td>
              <td>0</td>
              <td>50</td>
              <td style="text-align:center;">
                <button class="btn btn--sm" disabled>Edit</button>
                <button class="btn btn--sm btn--danger" disabled>Delete</button>
              </td>
            </tr>
            <tr>
              <td><span class="admin-badge">Member</span> Member</td>
              <td>0</td>
              <td>10</td>
              <td style="text-align:center;">
                <button class="btn btn--sm" disabled>Edit</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="form-box" style="max-width:100%; margin-top: var(--spacing-md);">
      <div class="form-box__header">Add Role</div>
      <div class="form-box__body">
        <div style="display:flex; gap: var(--spacing-sm); align-items:flex-end;">
          <div class="form-group" style="flex:1; margin-bottom:0;">
            <label>Role Name</label>
            <input type="text" placeholder="e.g. VIP Member">
          </div>
          <div class="form-group" style="width:100px; margin-bottom:0;">
            <label>Priority</label>
            <input type="number" value="20" min="1" max="99">
          </div>
          <button type="button" class="btn btn--primary" disabled>Add Role</button>
        </div>
      </div>
    </div>
  `;
}

function renderPermissions(container) {
  container.innerHTML = `
    <div class="form-group" style="margin-bottom: var(--spacing-md);">
      <label>Select Role</label>
      <select class="admin-select" style="width:200px;">
        <option>-- Select Role --</option>
        <option>Administrator</option>
        <option>Moderator</option>
        <option>Member</option>
      </select>
    </div>

    <div class="category-group">
      <div class="category-group__header">Forum Permissions</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th>Permission</th>
              <th style="width:80px; text-align:center;">View</th>
              <th style="width:80px; text-align:center;">Create</th>
              <th style="width:80px; text-align:center;">Edit</th>
              <th style="width:80px; text-align:center;">Delete</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Threads</td>
              <td style="text-align:center;"><input type="checkbox" checked disabled></td>
              <td style="text-align:center;"><input type="checkbox" checked disabled></td>
              <td style="text-align:center;"><input type="checkbox" disabled></td>
              <td style="text-align:center;"><input type="checkbox" disabled></td>
            </tr>
            <tr>
              <td>Posts</td>
              <td style="text-align:center;"><input type="checkbox" checked disabled></td>
              <td style="text-align:center;"><input type="checkbox" checked disabled></td>
              <td style="text-align:center;"><input type="checkbox" checked disabled></td>
              <td style="text-align:center;"><input type="checkbox" disabled></td>
            </tr>
            <tr>
              <td>Attachments</td>
              <td style="text-align:center;"><input type="checkbox" checked disabled></td>
              <td style="text-align:center;"><input type="checkbox" disabled></td>
              <td style="text-align:center;"><input type="checkbox" disabled></td>
              <td style="text-align:center;"><input type="checkbox" disabled></td>
            </tr>
            <tr>
              <td>Private Messages</td>
              <td style="text-align:center;"><input type="checkbox" checked disabled></td>
              <td style="text-align:center;"><input type="checkbox" checked disabled></td>
              <td style="text-align:center;"><input type="checkbox" disabled></td>
              <td style="text-align:center;"><input type="checkbox" disabled></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="category-group" style="margin-top: var(--spacing-md);">
      <div class="category-group__header">Moderation Permissions</div>
      <div class="forum-table">
        <table>
          <tbody>
            <tr>
              <td><input type="checkbox" disabled> Can lock threads</td>
            </tr>
            <tr>
              <td><input type="checkbox" disabled> Can pin threads</td>
            </tr>
            <tr>
              <td><input type="checkbox" disabled> Can move threads</td>
            </tr>
            <tr>
              <td><input type="checkbox" disabled> Can edit any post</td>
            </tr>
            <tr>
              <td><input type="checkbox" disabled> Can delete any post</td>
            </tr>
            <tr>
              <td><input type="checkbox" disabled> Can ban users</td>
            </tr>
            <tr>
              <td><input type="checkbox" disabled> Can view reports</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="admin-form__actions" style="margin-top: var(--spacing-md);">
      <button type="button" class="btn btn--primary" disabled>Save Permissions</button>
    </div>
  `;
}

function renderRanks(container) {
  container.innerHTML = `
    <p style="margin-bottom: var(--spacing-md); color: var(--color-text-light);">
      User ranks are titles automatically assigned based on post count.
    </p>

    <div class="category-group">
      <div class="category-group__header">User Ranks</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th>Rank Title</th>
              <th style="width:120px;">Min Posts</th>
              <th style="width:120px; text-align:center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Newbie</td>
              <td>0</td>
              <td style="text-align:center;">
                <button class="btn btn--sm" disabled>Edit</button>
              </td>
            </tr>
            <tr>
              <td>Junior Member</td>
              <td>10</td>
              <td style="text-align:center;">
                <button class="btn btn--sm" disabled>Edit</button>
                <button class="btn btn--sm btn--danger" disabled>Delete</button>
              </td>
            </tr>
            <tr>
              <td>Member</td>
              <td>50</td>
              <td style="text-align:center;">
                <button class="btn btn--sm" disabled>Edit</button>
                <button class="btn btn--sm btn--danger" disabled>Delete</button>
              </td>
            </tr>
            <tr>
              <td>Senior Member</td>
              <td>200</td>
              <td style="text-align:center;">
                <button class="btn btn--sm" disabled>Edit</button>
                <button class="btn btn--sm btn--danger" disabled>Delete</button>
              </td>
            </tr>
            <tr>
              <td>Veteran</td>
              <td>500</td>
              <td style="text-align:center;">
                <button class="btn btn--sm" disabled>Edit</button>
                <button class="btn btn--sm btn--danger" disabled>Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="form-box" style="max-width:100%; margin-top: var(--spacing-md);">
      <div class="form-box__header">Add Rank</div>
      <div class="form-box__body">
        <div style="display:flex; gap: var(--spacing-sm); align-items:flex-end;">
          <div class="form-group" style="flex:1; margin-bottom:0;">
            <label>Rank Title</label>
            <input type="text" placeholder="e.g. Elite Member">
          </div>
          <div class="form-group" style="width:120px; margin-bottom:0;">
            <label>Min Posts</label>
            <input type="number" value="100" min="0">
          </div>
          <button type="button" class="btn btn--primary" disabled>Add Rank</button>
        </div>
      </div>
    </div>
  `;
}

function renderBans(container) {
  container.innerHTML = `
    <div class="category-group">
      <div class="category-group__header">Active Bans</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th>User</th>
              <th>Reason</th>
              <th style="width:100px;">Type</th>
              <th style="width:120px;">Expires</th>
              <th style="width:100px; text-align:center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr><td colspan="5" style="text-align:center; color: var(--color-text-muted);">No active bans</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="category-group" style="margin-top: var(--spacing-md);">
      <div class="category-group__header">IP Bans</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th>IP Address</th>
              <th>Reason</th>
              <th style="width:120px;">Created</th>
              <th style="width:100px; text-align:center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr><td colspan="4" style="text-align:center; color: var(--color-text-muted);">No IP bans</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="form-box" style="max-width:100%; margin-top: var(--spacing-md);">
      <div class="form-box__header">Ban User</div>
      <div class="form-box__body">
        <div class="form-group">
          <label>Username or IP</label>
          <input type="text" placeholder="Enter username or IP address">
        </div>
        <div class="form-group">
          <label>Reason</label>
          <input type="text" placeholder="Reason for ban">
        </div>
        <div class="form-group">
          <label>Duration</label>
          <select class="admin-select" style="width:200px;">
            <option>Permanent</option>
            <option>1 Day</option>
            <option>3 Days</option>
            <option>1 Week</option>
            <option>2 Weeks</option>
            <option>1 Month</option>
            <option>3 Months</option>
          </select>
        </div>
        <button type="button" class="btn btn--danger" disabled>Ban User</button>
      </div>
    </div>
  `;
}

// ═══════════════════════════════════════════════════════════════════════════
// MODERATION
// ═══════════════════════════════════════════════════════════════════════════

function renderReports(container) {
  container.innerHTML = `
    <div class="admin-toolbar">
      <div class="admin-toolbar__filter">
        <select class="admin-select" style="width:150px;">
          <option>All Reports</option>
          <option>Open</option>
          <option>Resolved</option>
        </select>
      </div>
    </div>

    <div class="category-group">
      <div class="category-group__header">Reported Content</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th>Content</th>
              <th style="width:100px;">Reported By</th>
              <th>Reason</th>
              <th style="width:100px;">Status</th>
              <th style="width:120px;">Date</th>
              <th style="width:140px; text-align:center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr><td colspan="6" style="text-align:center; color: var(--color-text-muted);">No reports</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function renderApproval(container) {
  container.innerHTML = `
    <div class="category-group">
      <div class="category-group__header">Posts Awaiting Approval</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th>Author</th>
              <th>Content Preview</th>
              <th style="width:100px;">Type</th>
              <th style="width:120px;">Submitted</th>
              <th style="width:140px; text-align:center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr><td colspan="5" style="text-align:center; color: var(--color-text-muted);">No posts awaiting approval</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function renderWordFilters(container) {
  container.innerHTML = `
    <p style="margin-bottom: var(--spacing-md); color: var(--color-text-light);">
      Word filters automatically censor or block posts containing specified words.
    </p>

    <div class="category-group">
      <div class="category-group__header">Word Filters</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th>Word/Pattern</th>
              <th>Replacement</th>
              <th style="width:100px;">Action</th>
              <th style="width:100px; text-align:center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr><td colspan="4" style="text-align:center; color: var(--color-text-muted);">No word filters configured</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="form-box" style="max-width:100%; margin-top: var(--spacing-md);">
      <div class="form-box__header">Add Word Filter</div>
      <div class="form-box__body">
        <div style="display:flex; gap: var(--spacing-sm); align-items:flex-end;">
          <div class="form-group" style="flex:1; margin-bottom:0;">
            <label>Word/Pattern</label>
            <input type="text" placeholder="Word to filter">
          </div>
          <div class="form-group" style="flex:1; margin-bottom:0;">
            <label>Replacement</label>
            <input type="text" placeholder="****">
          </div>
          <div class="form-group" style="width:150px; margin-bottom:0;">
            <label>Action</label>
            <select class="admin-select">
              <option>Replace</option>
              <option>Block Post</option>
            </select>
          </div>
          <button type="button" class="btn btn--primary" disabled>Add Filter</button>
        </div>
      </div>
    </div>
  `;
}

function renderModLogs(container) {
  container.innerHTML = `
    <div class="admin-toolbar">
      <div class="admin-toolbar__filter">
        <select class="admin-select" style="width:150px;">
          <option>All Actions</option>
          <option>Bans</option>
          <option>Deletions</option>
          <option>Edits</option>
          <option>Moves</option>
        </select>
        <select class="admin-select" style="width:150px;">
          <option>All Moderators</option>
        </select>
      </div>
    </div>

    <div class="category-group">
      <div class="category-group__header">Moderation Logs</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th style="width:120px;">Moderator</th>
              <th>Action</th>
              <th>Target</th>
              <th style="width:150px;">Date</th>
            </tr>
          </thead>
          <tbody>
            <tr><td colspan="4" style="text-align:center; color: var(--color-text-muted);">No moderation actions logged</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// ═══════════════════════════════════════════════════════════════════════════
// APPEARANCE
// ═══════════════════════════════════════════════════════════════════════════

function renderThemes(container) {
  container.innerHTML = `
    <div class="category-group">
      <div class="category-group__header">Available Themes</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th>Theme</th>
              <th style="width:100px;">Status</th>
              <th style="width:140px; text-align:center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>RetroForum Classic</strong> <span class="admin-badge">Default</span></td>
              <td><span style="color: var(--color-success);">Active</span></td>
              <td style="text-align:center;">
                <button class="btn btn--sm" disabled>Preview</button>
              </td>
            </tr>
            <tr>
              <td>RetroForum Dark</td>
              <td><span style="color: var(--color-text-muted);">Inactive</span></td>
              <td style="text-align:center;">
                <button class="btn btn--sm" disabled>Preview</button>
                <button class="btn btn--sm btn--primary" disabled>Activate</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="form-box" style="max-width:100%; margin-top: var(--spacing-md);">
      <div class="form-box__header">Custom CSS</div>
      <div class="form-box__body">
        <div class="form-group">
          <label>Additional CSS (appended to active theme)</label>
          <textarea rows="8" placeholder="/* Custom CSS here */" style="font-family: monospace;"></textarea>
        </div>
        <button type="button" class="btn btn--primary" disabled>Save CSS</button>
      </div>
    </div>
  `;
}

// ═══════════════════════════════════════════════════════════════════════════
// MAINTENANCE
// ═══════════════════════════════════════════════════════════════════════════

function renderCache(container) {
  container.innerHTML = `
    <div class="stats-grid" style="margin-bottom: var(--spacing-lg);">
      <div class="stat-box">
        <div class="stat-box__value">--</div>
        <div class="stat-box__label">Cache Size</div>
      </div>
      <div class="stat-box">
        <div class="stat-box__value">--</div>
        <div class="stat-box__label">Cache Entries</div>
      </div>
      <div class="stat-box">
        <div class="stat-box__value">--</div>
        <div class="stat-box__label">Hit Rate</div>
      </div>
    </div>

    <div class="category-group">
      <div class="category-group__header">Cache Operations</div>
      <div class="admin-content__body" style="border: 1px solid var(--color-border); border-top: none;">
        <p>Clear cached data to resolve stale content issues.</p>
        <div style="display: flex; gap: var(--spacing-sm); margin-top: var(--spacing-md);">
          <button class="btn btn--primary" disabled>Clear Template Cache</button>
          <button class="btn btn--primary" disabled>Clear Permission Cache</button>
          <button class="btn btn--danger" disabled>Clear All Cache</button>
        </div>
      </div>
    </div>
  `;
}

function renderBackups(container) {
  container.innerHTML = `
    <div class="category-group">
      <div class="category-group__header">Database Backups</div>
      <div class="forum-table">
        <table>
          <thead>
            <tr>
              <th>Filename</th>
              <th style="width:100px;">Size</th>
              <th style="width:150px;">Created</th>
              <th style="width:140px; text-align:center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr><td colspan="4" style="text-align:center; color: var(--color-text-muted);">No backups available</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="form-box" style="max-width:100%; margin-top: var(--spacing-md);">
      <div class="form-box__header">Create Backup</div>
      <div class="form-box__body">
        <p style="margin-bottom: var(--spacing-md);">Create a backup of the forum database. This may take a few minutes for large forums.</p>
        <div class="form-group">
          <label><input type="checkbox" checked> Include user data</label>
        </div>
        <div class="form-group">
          <label><input type="checkbox" checked> Include posts and threads</label>
        </div>
        <div class="form-group">
          <label><input type="checkbox"> Include attachments</label>
        </div>
        <button type="button" class="btn btn--primary" disabled>Create Backup</button>
      </div>
    </div>
  `;
}

// ═══════════════════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════════════════

function renderPlaceholder(container) {
  container.innerHTML = `
    <div class="admin-placeholder">
      <div class="admin-placeholder__icon">&#128736;</div>
      <div class="admin-placeholder__text">
        This feature is not yet implemented.<br>
        Backend API endpoints needed.
      </div>
    </div>
  `;
}

function renderUserRowsCompact(users) {
  if (!users.length) {
    return '<tr><td colspan="2" style="text-align:center; color: var(--color-text-muted);">No users found.</td></tr>';
  }
  return users.map((user) => `
    <tr>
      <td>${escapeHtml(user.username)}</td>
      <td>${formatDate(user.created_at)}</td>
    </tr>
  `).join("");
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
