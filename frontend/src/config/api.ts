const PRODUCTION_AUTH_API_BASE_URL = "https://api-controle-usuarios.remobs.com.br";
const LOCAL_INVENTORY_API_BASE_URL = "http://127.0.0.1:8000";

export interface ApiEnv {
  VITE_AUTH_API_BASE_URL?: string;
  VITE_INVENTARIO_API_BASE_URL?: string;
}

function normalizeBaseUrl(value: string | undefined): string {
  return (value ?? "").trim().replace(/\/+$/, "");
}

export function getAuthApiBaseUrl(env: ApiEnv = import.meta.env): string {
  return normalizeBaseUrl(env.VITE_AUTH_API_BASE_URL) || PRODUCTION_AUTH_API_BASE_URL;
}

export function getInventoryApiBaseUrl(env: ApiEnv = import.meta.env): string {
  return normalizeBaseUrl(env.VITE_INVENTARIO_API_BASE_URL) || LOCAL_INVENTORY_API_BASE_URL;
}
