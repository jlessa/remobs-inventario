import { describe, expect, it } from "vitest";

import { getAuthApiBaseUrl, getInventoryApiBaseUrl } from "../src/config/api";

describe("configuração das APIs", () => {
  it("usa o autenticador de produção quando a variável de ambiente não está definida", () => {
    expect(getAuthApiBaseUrl({})).toBe("https://api-controle-usuarios.remobs.com.br");
  });

  it("remove barra final da URL do autenticador", () => {
    expect(getAuthApiBaseUrl({ VITE_AUTH_API_BASE_URL: "https://api-controle-usuarios.remobs.com.br/" })).toBe(
      "https://api-controle-usuarios.remobs.com.br",
    );
  });

  it("permite sobrescrever o autenticador por variável de ambiente explícita", () => {
    expect(getAuthApiBaseUrl({ VITE_AUTH_API_BASE_URL: "http://localhost:8015" })).toBe("http://localhost:8015");
  });

  it("usa a API local do inventário quando a variável de ambiente não está definida", () => {
    expect(getInventoryApiBaseUrl({})).toBe("http://127.0.0.1:8000");
  });

  it("remove barra final da URL da API de inventário", () => {
    expect(getInventoryApiBaseUrl({ VITE_INVENTARIO_API_BASE_URL: "http://127.0.0.1:8000/" })).toBe(
      "http://127.0.0.1:8000",
    );
  });
});
