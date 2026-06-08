import { describe, expect, it } from "vitest";

import { authApi } from "../src/api/client";

describe("cliente de autenticação", () => {
  it("resolve o endpoint de login para o autenticador de produção", () => {
    expect(authApi.getUri({ url: "/auth/login" })).toBe("https://api-controle-usuarios.remobs.com.br/auth/login");
  });
});
