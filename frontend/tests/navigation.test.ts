import { describe, expect, it } from "vitest";

import { getVisibleNavigation } from "../src/navigation";

describe("navegação por permissão", () => {
  it("oculta módulos sem permissão operacional", () => {
    const items = getVisibleNavigation(["inventory:item:read"]);

    expect(items.map((item) => item.label)).toContain("Inventário");
    expect(items.map((item) => item.label)).not.toContain("Checklists");
    expect(items.map((item) => item.label)).not.toContain("Logs");
  });

  it("exibe apenas módulos operacionais para permissão coringa", () => {
    const items = getVisibleNavigation(["*"]);

    expect(items.map((item) => item.label)).toEqual([
      "Início",
      "Inventário",
      "Operação",
      "Alertas",
      "Plataformas",
      "Sensores",
      "Checklists",
      "Sincronização",
    ]);
  });
});
