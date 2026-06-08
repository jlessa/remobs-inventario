import axios from "axios";

import { getAuthApiBaseUrl, getInventoryApiBaseUrl } from "../config/api";

const authBaseURL = getAuthApiBaseUrl();
const inventoryBaseURL = getInventoryApiBaseUrl();

export const authApi = axios.create({ baseURL: authBaseURL });
export const inventoryApi = axios.create({ baseURL: inventoryBaseURL });

function attachToken(config: import("axios").InternalAxiosRequestConfig) {
  const token = localStorage.getItem("remobs_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}

function handleAuthError(error: unknown) {
  if (axios.isAxiosError(error) && error.response?.status === 401) {
    localStorage.removeItem("remobs_token");
    if (window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
  }
  return Promise.reject(error);
}

authApi.interceptors.request.use(attachToken);
inventoryApi.interceptors.request.use(attachToken);
authApi.interceptors.response.use((response) => response, handleAuthError);
inventoryApi.interceptors.response.use((response) => response, handleAuthError);
