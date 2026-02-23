import { renderBreadcrumb } from "../components/breadcrumb.js";
import { register } from "../api/auth.js";
import { setToken, setUser, setUserId, setRole, parseJwt } from "../state.js";

export function renderRegister() {
  const breadcrumb = renderBreadcrumb([
    { label: "Forum Home", href: "#/" },
    { label: "Register" },
  ]);

  return `
    ${breadcrumb}
    <div class="main-content">
      <div class="form-box">
        <div class="form-box__header">Create an Account</div>
        <div class="form-box__body">
          <div id="register-error" class="form-error" style="display:none;"></div>
          <form id="register-form">
            <div class="form-group">
              <label for="reg-username">Username</label>
              <input type="text" id="reg-username" placeholder="Choose a username" required>
            </div>
            <div class="form-group">
              <label for="reg-email">Email Address</label>
              <input type="email" id="reg-email" placeholder="Enter your email" required>
            </div>
            <div class="form-group">
              <label for="reg-password">Password</label>
              <input type="password" id="reg-password" placeholder="Choose a password" required>
            </div>
            <div class="form-group">
              <label for="reg-password-confirm">Confirm Password</label>
              <input type="password" id="reg-password-confirm" placeholder="Confirm your password" required>
            </div>
            <button type="submit" class="btn btn--primary" style="width: 100%;">Register</button>
          </form>
        </div>
        <div class="form-box__footer">
          Already have an account? <a href="#/login">Log in here</a>
        </div>
      </div>
    </div>
  `;
}

export function mountRegister() {
  const form = document.getElementById("register-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById("register-error");
    errorEl.style.display = "none";

    const username = document.getElementById("reg-username").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    const confirm = document.getElementById("reg-password-confirm").value;

    if (password !== confirm) {
      errorEl.textContent = "Passwords do not match.";
      errorEl.style.display = "block";
      return;
    }

    try {
      const data = await register({ username, email, password });
      const payload = parseJwt(data.access_token);
      setToken(data.access_token);
      setUser(username);
      setUserId(payload.sub);
      setRole(payload.role || "");
      window.location.hash = "#/";
    } catch (err) {
      errorEl.textContent = err.message;
      errorEl.style.display = "block";
    }
  });
}
