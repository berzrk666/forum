import { fetchJSON, fetchForm } from "./client.js";

export async function register({ username, email, password }) {
  return fetchJSON("/auth/register", { username, email, password });
}

export async function login({ username, password }) {
  return fetchForm("/auth/login", { username, password });
}
