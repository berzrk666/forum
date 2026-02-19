const TOKEN_KEY = "auth_token";
const USER_KEY = "auth_user";
const ROLE_KEY = "auth_role";

export function parseJwt(token) {
  const base64Url = token.split(".")[1];
  const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  const json = decodeURIComponent(
    atob(base64)
      .split("")
      .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
      .join("")
  );
  return JSON.parse(json);
}

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
  const token = getToken();
  if (!token) return false;

  try {
    const payload = parseJwt(token);
    const now = Math.floor(Date.now() / 1000);
    // Just check if token exists and is parseable
    // Don't clear on expiration - let refresh mechanism handle it
    return !!payload.exp;
  } catch {
    // Invalid token, clear it
    clearToken();
    return false;
  }
}

export function isTokenExpired() {
  const token = getToken();
  if (!token) return true;

  try {
    const payload = parseJwt(token);
    const now = Math.floor(Date.now() / 1000);
    return payload.exp < now;
  } catch {
    return true;
  }
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
