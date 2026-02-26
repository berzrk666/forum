import { fetchAPI } from "./client.js";

export const getUsers = () => fetchAPI("/users/");

// Categories
export const getCategories = () => fetchAPI("/categories/");
export const createCategory = (name, order) =>
  fetchAPI("/categories/", { method: "POST", body: { name, order } });
export const deleteCategory = (id) =>
  fetchAPI(`/categories/${id}`, { method: "DELETE" });

// Forums
export const getForums = () => fetchAPI("/forums/");
export const createForum = (name, description, order, category_id) =>
  fetchAPI("/forums/", { method: "POST", body: { name, description, order, category_id } });
export const updateForum = (id, data) =>
  fetchAPI(`/forums/${id}`, { method: "PUT", body: data });

// Threads
export const getThreadsByForum = (forum_id, page = 1, limit = 20) =>
  fetchAPI(`/forums/${forum_id}/threads?page=${page}&limit=${limit}`);
export const getThread = (id) => fetchAPI(`/thread/${id}`);
export const createThread = (title, content, forum_id) =>
  fetchAPI("/thread/", { method: "POST", body: { title, content, forum_id } });
export const editThread = (id, title, content) =>
  fetchAPI(`/thread/${id}/edit`, { method: "PATCH", body: { title, content } });
// Posts
export const getPostsByThread = (thread_id, page = 1, limit = 20) =>
  fetchAPI(`/thread/${thread_id}/posts?page=${page}&limit=${limit}`);
export const createPost = (thread_id, content) =>
  fetchAPI("/posts/", { method: "POST", body: { thread_id, content } });

export const pinThread = (id) => fetchAPI(`/thread/${id}/pin`, { method: "PATCH" });
export const unpinThread = (id) => fetchAPI(`/thread/${id}/unpin`, { method: "PATCH" });
export const lockThread = (id) => fetchAPI(`/thread/${id}/lock`, { method: "PATCH" });
export const unlockThread = (id) => fetchAPI(`/thread/${id}/unlock`, { method: "PATCH" });
