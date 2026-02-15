import { renderBreadcrumb } from "../components/breadcrumb.js";
import { isLoggedIn } from "../state.js";
import * as api from "../api/admin.js";

export function renderAdmin() {
  if (!isLoggedIn()) {
    return `
      <div class="main-content">
        <div class="form-box">
          <div class="form-box__header">Access Denied</div>
          <div class="form-box__body">
            <p>You must be logged in to access the admin dashboard.</p>
            <br>
            <a href="#/login" class="btn btn--primary">Log In</a>
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
      <div class="admin-tabs">
        <button class="admin-tabs__tab admin-tabs__tab--active" data-tab="roles">Roles</button>
        <button class="admin-tabs__tab" data-tab="permissions">Permissions</button>
        <button class="admin-tabs__tab" data-tab="users">Users</button>
      </div>
      <div id="admin-content">
        <div class="form-box" style="max-width:100%;">
          <div class="form-box__body" style="text-align:center; color: var(--color-text-muted);">
            Loading...
          </div>
        </div>
      </div>
    </div>
  `;
}

export function mountAdmin() {
  if (!isLoggedIn()) return;

  let roles = [];
  let modules = [];
  let actions = [];
  let users = [];
  let activeTab = "roles";
  let selectedRoleId = null;
  let rolePermissions = [];

  loadData();

  // Tab switching
  document.querySelectorAll(".admin-tabs__tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      activeTab = tab.dataset.tab;
      document.querySelectorAll(".admin-tabs__tab").forEach((t) =>
        t.classList.remove("admin-tabs__tab--active")
      );
      tab.classList.add("admin-tabs__tab--active");
      selectedRoleId = null;
      rolePermissions = [];
      renderActiveTab();
    });
  });

  async function loadData() {
    try {
      const [rolesData, modulesData, actionsData, usersData] = await Promise.all([
        api.getRoles().catch(() => []),
        api.getModules().catch(() => []),
        api.getActions().catch(() => []),
        api.getUsers().catch(() => []),
      ]);
      roles = Array.isArray(rolesData) ? rolesData : rolesData?.res || [];
      modules = Array.isArray(modulesData) ? modulesData : modulesData?.res || [];
      actions = Array.isArray(actionsData) ? actionsData : actionsData?.res || [];
      users = Array.isArray(usersData) ? usersData : usersData?.res || [];
    } catch {
      roles = [];
      modules = [];
      actions = [];
      users = [];
    }
    renderActiveTab();
  }

  function renderActiveTab() {
    const container = document.getElementById("admin-content");
    if (!container) return;

    if (activeTab === "roles") {
      container.innerHTML = renderRolesTab();
      mountRolesTab();
    } else if (activeTab === "permissions") {
      container.innerHTML = renderPermissionsTab();
      mountPermissionsTab();
    } else if (activeTab === "users") {
      container.innerHTML = renderUsersTab();
      mountUsersTab();
    }
  }

  // ── Roles Tab ──

  function renderRolesTab() {
    const rows = roles.map(
      (r) => `
      <tr>
        <td>${r.id}</td>
        <td>${escapeHtml(r.name)}</td>
        <td style="text-align:center;">
          <button class="btn btn--danger btn--sm" data-delete-role="${r.id}">Delete</button>
        </td>
      </tr>`
    ).join("");

    return `
      <div class="category-group">
        <div class="category-group__header">Roles</div>
        <div class="forum-table">
          <table>
            <thead>
              <tr>
                <th style="width:60px;">ID</th>
                <th>Name</th>
                <th style="width:80px; text-align:center;">Actions</th>
              </tr>
            </thead>
            <tbody>
              ${rows || '<tr><td colspan="3" style="text-align:center;">No roles found.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
      <div class="form-box" style="max-width:100%; margin-top: var(--spacing-md);">
        <div class="form-box__header">Add New Role</div>
        <div class="form-box__body">
          <div id="role-error" class="form-error" style="display:none;"></div>
          <form id="add-role-form" style="display:flex; gap: var(--spacing-sm); align-items:flex-end;">
            <div class="form-group" style="flex:1; margin-bottom:0;">
              <label for="role-name">Role Name</label>
              <input type="text" id="role-name" placeholder="e.g. moderator" required>
            </div>
            <button type="submit" class="btn btn--primary">Add Role</button>
          </form>
        </div>
      </div>
    `;
  }

  function mountRolesTab() {
    const form = document.getElementById("add-role-form");
    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const errorEl = document.getElementById("role-error");
        const name = document.getElementById("role-name").value.trim();
        if (!name) return;
        try {
          errorEl.style.display = "none";
          await api.createRole(name);
          await loadData();
        } catch (err) {
          errorEl.textContent = err.message;
          errorEl.style.display = "block";
        }
      });
    }

    document.querySelectorAll("[data-delete-role]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.deleteRole;
        try {
          await api.deleteRole(id);
          await loadData();
        } catch (err) {
          alert(err.message);
        }
      });
    });
  }

  // ── Permissions Tab ──

  function renderPermissionsTab() {
    const roleOptions = roles.map(
      (r) => `<option value="${r.id}" ${r.id === selectedRoleId ? "selected" : ""}>${escapeHtml(r.name)}</option>`
    ).join("");

    let matrixHtml = "";
    if (selectedRoleId) {
      const actionHeaders = actions.map(
        (a) => `<th style="width:80px; text-align:center;">${escapeHtml(a.name)}</th>`
      ).join("");

      const moduleRows = modules.map((m) => {
        const cells = actions.map((a) => {
          const checked = rolePermissions.some(
            (p) => p.module_id === m.id && p.action_id === a.id
          );
          return `
            <td style="text-align:center;">
              <input type="checkbox" class="perm-checkbox" data-module="${m.id}" data-action="${a.id}" ${checked ? "checked" : ""}>
            </td>`;
        }).join("");

        return `<tr><td>${escapeHtml(m.name)}</td>${cells}</tr>`;
      }).join("");

      matrixHtml = `
        <div class="category-group" style="margin-top: var(--spacing-md);">
          <div class="category-group__header">Permissions for: ${escapeHtml(roles.find((r) => r.id === selectedRoleId)?.name || "")}</div>
          <div class="forum-table">
            <table>
              <thead>
                <tr>
                  <th>Module</th>
                  ${actionHeaders}
                </tr>
              </thead>
              <tbody>
                ${moduleRows || '<tr><td colspan="' + (actions.length + 1) + '" style="text-align:center;">No modules defined.</td></tr>'}
              </tbody>
            </table>
          </div>
        </div>
      `;
    }

    // Module rows with delete buttons
    const moduleRows = modules.map(
      (m) => `
      <tr>
        <td>${escapeHtml(m.name)}</td>
        <td style="text-align:center;">
          <button class="btn btn--danger btn--sm" data-delete-module="${m.id}">Delete</button>
        </td>
      </tr>`
    ).join("");

    // Action rows with delete buttons
    const actionRows = actions.map(
      (a) => `
      <tr>
        <td>${escapeHtml(a.name)}</td>
        <td style="text-align:center;">
          <button class="btn btn--danger btn--sm" data-delete-action="${a.id}">Delete</button>
        </td>
      </tr>`
    ).join("");

    return `
      <div class="action-bar">
        <h3 style="margin:0;">Manage Permissions</h3>
        <div class="form-group" style="margin-bottom:0; width:200px;">
          <select id="perm-role-select" class="admin-select">
            <option value="">-- Select a Role --</option>
            ${roleOptions}
          </select>
        </div>
      </div>
      ${matrixHtml}
      <div style="display:flex; gap: var(--spacing-md); margin-top: var(--spacing-md);">
        <div class="form-box" style="max-width:100%; flex:1;">
          <div class="form-box__header">Modules</div>
          <div class="form-box__body" style="padding-bottom:0;">
            <table style="width:100%; margin-bottom: var(--spacing-sm);">
              <tbody>
                ${moduleRows || '<tr><td style="text-align:center; color: var(--color-text-muted);">No modules.</td></tr>'}
              </tbody>
            </table>
            <div id="module-error" class="form-error" style="display:none;"></div>
            <form id="add-module-form" style="display:flex; gap:var(--spacing-sm); align-items:flex-end; padding-bottom: var(--spacing-sm);">
              <div class="form-group" style="flex:1; margin-bottom:0;">
                <input type="text" id="module-name" placeholder="e.g. posts" required>
              </div>
              <button type="submit" class="btn btn--primary btn--sm">Add</button>
            </form>
          </div>
        </div>
        <div class="form-box" style="max-width:100%; flex:1;">
          <div class="form-box__header">Actions</div>
          <div class="form-box__body" style="padding-bottom:0;">
            <table style="width:100%; margin-bottom: var(--spacing-sm);">
              <tbody>
                ${actionRows || '<tr><td style="text-align:center; color: var(--color-text-muted);">No actions.</td></tr>'}
              </tbody>
            </table>
            <div id="action-error" class="form-error" style="display:none;"></div>
            <form id="add-action-form" style="display:flex; gap:var(--spacing-sm); align-items:flex-end; padding-bottom: var(--spacing-sm);">
              <div class="form-group" style="flex:1; margin-bottom:0;">
                <input type="text" id="action-name" placeholder="e.g. read" required>
              </div>
              <button type="submit" class="btn btn--primary btn--sm">Add</button>
            </form>
          </div>
        </div>
      </div>
    `;
  }

  function mountPermissionsTab() {
    const roleSelect = document.getElementById("perm-role-select");
    if (roleSelect) {
      roleSelect.addEventListener("change", async () => {
        const val = roleSelect.value;
        if (!val) {
          selectedRoleId = null;
          rolePermissions = [];
          renderActiveTab();
          return;
        }
        selectedRoleId = Number(val);
        try {
          const data = await api.getRolePermissions(selectedRoleId);
          rolePermissions = Array.isArray(data) ? data : data?.res || [];
        } catch {
          rolePermissions = [];
        }
        renderActiveTab();
      });
    }

    // Permission checkboxes
    document.querySelectorAll(".perm-checkbox").forEach((cb) => {
      cb.addEventListener("change", async () => {
        const moduleId = Number(cb.dataset.module);
        const actionId = Number(cb.dataset.action);
        try {
          if (cb.checked) {
            await api.addPermission(selectedRoleId, moduleId, actionId);
          } else {
            await api.removePermission(selectedRoleId, moduleId, actionId);
          }
          // Reload permissions to stay in sync
          const data = await api.getRolePermissions(selectedRoleId);
          rolePermissions = Array.isArray(data) ? data : data?.res || [];
        } catch (err) {
          cb.checked = !cb.checked; // revert on error
          alert(err.message);
        }
      });
    });

    // Add module
    const moduleForm = document.getElementById("add-module-form");
    if (moduleForm) {
      moduleForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const errorEl = document.getElementById("module-error");
        const name = document.getElementById("module-name").value.trim();
        if (!name) return;
        try {
          errorEl.style.display = "none";
          await api.createModule(name);
          await loadData();
        } catch (err) {
          errorEl.textContent = err.message;
          errorEl.style.display = "block";
        }
      });
    }

    // Add action
    const actionForm = document.getElementById("add-action-form");
    if (actionForm) {
      actionForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const errorEl = document.getElementById("action-error");
        const name = document.getElementById("action-name").value.trim();
        if (!name) return;
        try {
          errorEl.style.display = "none";
          await api.createAction(name);
          await loadData();
        } catch (err) {
          errorEl.textContent = err.message;
          errorEl.style.display = "block";
        }
      });
    }

    // Delete module
    document.querySelectorAll("[data-delete-module]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          await api.deleteModule(btn.dataset.deleteModule);
          await loadData();
        } catch (err) {
          alert(err.message);
        }
      });
    });

    // Delete action
    document.querySelectorAll("[data-delete-action]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          await api.deleteAction(btn.dataset.deleteAction);
          await loadData();
        } catch (err) {
          alert(err.message);
        }
      });
    });
  }

  // ── Users Tab ──

  function renderUsersTab() {
    const rows = users.map((u) => {
      const roleOptions = roles.map(
        (r) => `<option value="${r.id}" ${u.role_id === r.id ? "selected" : ""}>${escapeHtml(r.name)}</option>`
      ).join("");

      return `
        <tr>
          <td>${u.id}</td>
          <td>${escapeHtml(u.username)}</td>
          <td>${escapeHtml(u.email || "")}</td>
          <td>
            <select class="admin-select" data-user-id="${u.id}">
              <option value="" ${!u.role_id ? "selected" : ""}>-- No Role --</option>
              ${roleOptions}
            </select>
          </td>
        </tr>`;
    }).join("");

    return `
      <div class="category-group">
        <div class="category-group__header">User Role Assignments</div>
        <div class="forum-table">
          <table>
            <thead>
              <tr>
                <th style="width:60px;">ID</th>
                <th>Username</th>
                <th>Email</th>
                <th style="width:180px;">Role</th>
              </tr>
            </thead>
            <tbody>
              ${rows || '<tr><td colspan="4" style="text-align:center;">No users found.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  function mountUsersTab() {
    document.querySelectorAll("select[data-user-id]").forEach((sel) => {
      sel.addEventListener("change", async () => {
        const userId = sel.dataset.userId;
        const roleId = sel.value ? Number(sel.value) : null;
        try {
          await api.assignUserRole(userId, roleId);
        } catch (err) {
          alert(err.message);
          // Revert — reload data
          await loadData();
        }
      });
    });
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
