import { addRoute, resolve } from "./router.js";
import { renderHeader, mountHeader } from "./components/header.js";
import { renderFooter } from "./components/footer.js";
import { renderHome, mountHome } from "./pages/home.js";
import { renderCategory } from "./pages/category.js";
import { renderForum, mountForum } from "./pages/forum.js";
import { renderThread } from "./pages/thread.js";
import { renderLogin, mountLogin } from "./pages/login.js";
import { renderRegister, mountRegister } from "./pages/register.js";
import { renderAdmin, mountAdmin } from "./pages/admin.js";

// Register routes — each returns { html, mount? }
addRoute("/", () => ({ html: renderHome(), mount: mountHome }));
addRoute("/category/:id", ({ id }) => ({ html: renderCategory(Number(id)) }));
addRoute("/forum/:id", ({ id }) => ({ html: renderForum(Number(id)), mount: mountForum }));
addRoute("/thread/:id", ({ id }) => ({ html: renderThread(Number(id)) }));
addRoute("/login", () => ({ html: renderLogin(), mount: mountLogin }));
addRoute("/register", () => ({ html: renderRegister(), mount: mountRegister }));
addRoute("/admin", () => ({ html: renderAdmin(), mount: mountAdmin }));

function render() {
  const app = document.getElementById("app");
  const page = resolve() || {};
  const pageContent = page.html || notFound();

  app.innerHTML = `
    ${renderHeader()}
    ${pageContent}
    ${renderFooter()}
  `;

  // Attach event listeners after innerHTML is set
  mountHeader();
  if (page.mount) page.mount();

  window.scrollTo(0, 0);
}

function notFound() {
  return `
    <div class="main-content">
      <div class="form-box">
        <div class="form-box__header">404 - Page Not Found</div>
        <div class="form-box__body">
          <p>The page you're looking for doesn't exist.</p>
          <br>
          <a href="#/" class="btn btn--primary">Return to Forum Home</a>
        </div>
      </div>
    </div>
  `;
}

// Listen for hash changes
window.addEventListener("hashchange", render);

// Initial render
if (!window.location.hash) {
  window.location.hash = "#/";
} else {
  render();
}
