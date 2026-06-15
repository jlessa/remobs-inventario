import { afterEach, describe, expect, it, vi } from "vitest";

import { inventoryApi } from "../src/api/client";
import { inventoryService } from "../src/services/inventoryService";

describe("cliente de inventário", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("resolve endpoints operacionais para a API local do inventário por padrão", () => {
    expect(inventoryApi.getUri({ url: "/inventory/items" })).toBe("http://127.0.0.1:8000/inventory/items");
  });

  it("consulta detalhes operacionais de plataforma e sensor", async () => {
    const get = vi.spyOn(inventoryApi, "get").mockResolvedValue({ data: { id: "id-teste" } });
    const patch = vi.spyOn(inventoryApi, "patch").mockResolvedValue({ data: { id: "sensor-1" } });

    await inventoryService.getPlatform("plataforma-1");
    await inventoryService.getSensor("sensor-1");
    await inventoryService.updateSensor("sensor-1", { operational_status: "inconsistencia", reason: "Falha em campo." });

    expect(get).toHaveBeenNthCalledWith(1, "/platforms/plataforma-1");
    expect(get).toHaveBeenNthCalledWith(2, "/sensors/sensor-1");
    expect(patch).toHaveBeenCalledWith("/sensors/sensor-1", { operational_status: "inconsistencia", reason: "Falha em campo." });
  });

  it("cadastra plataformas e sensores nos endpoints operacionais", async () => {
    const post = vi.spyOn(inventoryApi, "post").mockResolvedValue({ data: { id: "id-teste" } });

    await inventoryService.createPlatform({
      name: "Boia 01",
      platform_type: "boia",
      operational_status: "disponivel",
    });
    await inventoryService.createSensor({
      sensor_type: "ondas",
      family: "Ondógrafo",
      operational_status: "nao_instalado",
    });

    expect(post).toHaveBeenNthCalledWith(1, "/platforms", {
      name: "Boia 01",
      platform_type: "boia",
      operational_status: "disponivel",
    });
    expect(post).toHaveBeenNthCalledWith(2, "/sensors", {
      sensor_type: "ondas",
      family: "Ondógrafo",
      operational_status: "nao_instalado",
    });
  });

  it("envia checklists e resolve conflitos offline", async () => {
    const post = vi.spyOn(inventoryApi, "post").mockResolvedValue({ data: { id: "id-teste", status: "ok" } });
    const patch = vi.spyOn(inventoryApi, "patch").mockResolvedValue({ data: { id: "id-teste" } });
    const get = vi.spyOn(inventoryApi, "get").mockResolvedValue({ data: { items: [], total: 0 } });

    await inventoryService.listChecklists();
    await inventoryService.createChecklist({ title: "Checklist", template_name: "Campo", total_steps: 4 });
    await inventoryService.updateChecklist("checklist-1", { current_step: 2 });
    await inventoryService.submitChecklist("checklist-1", "Checklist concluído.");
    await inventoryService.listSyncConflicts();
    await inventoryService.resolveSyncConflict({
      client_action_id: "offline-1",
      decision: "discard",
      reason: "Conferido em campo.",
    });

    expect(get).toHaveBeenNthCalledWith(1, "/checklists");
    expect(post).toHaveBeenNthCalledWith(1, "/checklists", { title: "Checklist", template_name: "Campo", total_steps: 4 });
    expect(patch).toHaveBeenCalledWith("/checklists/checklist-1", { current_step: 2 });
    expect(post).toHaveBeenNthCalledWith(2, "/checklists/checklist-1/submit", { reason: "Checklist concluído." });
    expect(get).toHaveBeenNthCalledWith(2, "/sync/conflicts");
    expect(post).toHaveBeenNthCalledWith(3, "/sync/resolve-conflict", {
      client_action_id: "offline-1",
      decision: "discard",
      reason: "Conferido em campo.",
    });
  });
});
