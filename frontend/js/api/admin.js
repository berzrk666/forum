import { fetchAPI } from "./client.js";

export const getUsers = () => fetchAPI("/users/");

// Categories
export const getCategories = () => fetchAPI("/categories/");
export const createCategory = (name, order) =>
  fetchAPI("/categories/", { method: "POST", body: { name, order } });
export const deleteCategory = (id) =>
  fetchAPI(`/categories/${id}`, { method: "DELETE" });
