import { isLoggedIn, getUser, clearToken } from "../state.js";

export function renderHeader() {
  const loggedIn = isLoggedIn();
  const username = getUser();

  const nav = loggedIn
    ? `<a href="#/" class="site-header__link">Forum Home</a>
       <a href="#/admin" class="site-header__link">Admin</a>
       <span class="site-header__link">Welcome, ${username}</span>
       <a href="#" class="site-header__link" id="logout-btn">Log Out</a>`
    : `<a href="#/" class="site-header__link">Forum Home</a>
       <a href="#/login" class="site-header__link">Log In</a>
       <a href="#/register" class="site-header__link">Register</a>`;

  return `
    <header class="site-header">
      <div class="site-header__inner">
        <div class="site-header__title">
          <a href="#/">RetroForum</a>
        </div>
        <nav class="site-header__nav">
          ${nav}
        </nav>
      </div>
    </header>
  `;
}

export function mountHeader() {
  const btn = document.getElementById("logout-btn");
  if (!btn) return;

  btn.addEventListener("click", (e) => {
    e.preventDefault();
    clearToken();
    window.location.hash = "#/";
    window.dispatchEvent(new HashChangeEvent("hashchange"));
  });
}
