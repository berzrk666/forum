import { fetchAPI } from "./client.js";

// Roles
export const getRoles = () => fetchAPI("/auth/roles");
export const createRole = (name) => fetchAPI("/auth/roles", { method: "POST", body: { name } });
export const deleteRole = (id) => fetchAPI(`/auth/roles/${id}`, { method: "DELETE" });

// Modules
export const getModules = () => fetchAPI("/auth/modules");
export const createModule = (name) => fetchAPI("/auth/modules", { method: "POST", body: { name } });
export const deleteModule = (id) => fetchAPI(`/auth/modules/${id}`, { method: "DELETE" });

// Actions
export const getActions = () => fetchAPI("/auth/actions");
export const createAction = (name) => fetchAPI("/auth/actions", { method: "POST", body: { name } });
export const deleteAction = (id) => fetchAPI(`/auth/actions/${id}`, { method: "DELETE" });

// Permissions
export const getRolePermissions = (roleId) => fetchAPI(`/auth/roles/${roleId}/permissions`);
export const addPermission = (roleId, moduleId, actionId) =>
  fetchAPI(`/auth/roles/${roleId}/permissions`, { method: "POST", body: { module_id: moduleId, action_id: actionId } });
export const removePermission = (roleId, moduleId, actionId) =>
  fetchAPI(`/auth/roles/${roleId}/permissions`, { method: "DELETE", body: { module_id: moduleId, action_id: actionId } });

// Users
export const getUsers = () => fetchAPI("/auth/users");
export const assignUserRole = (userId, roleId) =>
  fetchAPI(`/auth/users/${userId}/role`, { method: "PUT", body: { role_id: roleId } });
