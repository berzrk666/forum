const TOKEN_KEY = "auth_token";
const USER_KEY = "auth_user";
const ROLE_KEY = "auth_role";

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(ROLE_KEY);
}

export function isLoggedIn() {
  return !!getToken();
}

export function setUser(username) {
  localStorage.setItem(USER_KEY, username);
}

export function getUser() {
  return localStorage.getItem(USER_KEY);
}

export function setRole(role) {
  localStorage.setItem(ROLE_KEY, role || "");
}

export function getRole() {
  return localStorage.getItem(ROLE_KEY);
}
