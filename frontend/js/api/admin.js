import { fetchAPI } from "./client.js";

export const getUsers = () => fetchAPI("/users/");
