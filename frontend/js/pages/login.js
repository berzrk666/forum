import { renderBreadcrumb } from "../components/breadcrumb.js";
import { login } from "../api/auth.js";
import { setToken, setUser, setRole, parseJwt } from "../state.js";

export function renderLogin() {
  const breadcrumb = renderBreadcrumb([
    { label: "Forum Home", href: "#/" },
    { label: "Log In" },
  ]);

  return `
    ${breadcrumb}
    <div class="main-content">
      <div class="form-box">
        <div class="form-box__header">Log In</div>
        <div class="form-box__body">
          <div id="login-error" class="form-error" style="display:none;"></div>
          <form id="login-form">
            <div class="form-group">
              <label for="login-username">Username</label>
              <input type="text" id="login-username" placeholder="Enter your username" required>
            </div>
            <div class="form-group">
              <label for="login-password">Password</label>
              <input type="password" id="login-password" placeholder="Enter your password" required>
            </div>
            <button type="submit" class="btn btn--primary" style="width: 100%;">Log In</button>
          </form>
        </div>
        <div class="form-box__footer">
          Don't have an account? <a href="#/register">Register here</a>
        </div>
      </div>
    </div>
  `;
}

export function mountLogin() {
  const form = document.getElementById("login-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById("login-error");
    errorEl.style.display = "none";

    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;

    try {
      const data = await login({ username, password });
      const payload = parseJwt(data.access_token);
      setToken(data.access_token);
      setUser(username);
      setRole(payload.role || "");
      window.location.hash = "#/";
    } catch (err) {
      errorEl.textContent = err.message;
      errorEl.style.display = "block";
    }
  });
}
