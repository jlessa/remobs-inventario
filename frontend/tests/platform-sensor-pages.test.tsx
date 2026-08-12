import { screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import PlatformsPage from "../src/pages/PlatformsPage";
import SensorsPage from "../src/pages/SensorsPage";
import { inventoryService } from "../src/services/inventoryService";
import { renderWithProviders } from "./test-utils";

vi.mock("../src/state/AuthContext", () => ({
  useAuth: () => ({
    hasPermission: (permission: string) => ["platform:update", "sensor:update"].includes(permission),
    hasAnyPermission: (...permissions: string[]) =>
      permissions.some((permission) => ["platform:update", "sensor:update", "platform:create", "sensor:create", "platform:delete", "sensor:delete"].includes(permission)),
  }),
}));

describe("ações de cadastro operacional", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("exibe ação para cadastrar plataforma quando usuário pode atualizar plataformas", async () => {
    vi.spyOn(inventoryService, "listPlatforms").mockResolvedValue({ items: [], total: 0 });

    renderWithProviders(
      <MemoryRouter>
        <PlatformsPage />
      </MemoryRouter>,
    );

    expect(await screen.findByRole("button", { name: /nova plataforma/i })).toBeTruthy();
    const onlyActive = await screen.findByRole("switch", { name: /somente ativas/i });
    expect((onlyActive as HTMLInputElement).checked).toBe(true);
  });

  it("exibe ação para excluir plataforma na listagem", async () => {
    vi.spyOn(inventoryService, "listPlatforms").mockResolvedValue({
      items: [
        {
          id: "plat-1",
          name: "Boia 01",
          platform_type: "boia",
          manufacturer: "Axys",
          model: "WatchKeeper",
          operational_status: "em_operacao",
          description: null,
        },
      ],
      total: 1,
    });

    renderWithProviders(
      <MemoryRouter>
        <PlatformsPage />
      </MemoryRouter>,
    );

    expect(await screen.findByRole("button", { name: /excluir plataforma boia 01/i })).toBeTruthy();
  });

  it("exibe ação para cadastrar sensor quando usuário pode atualizar sensores", async () => {
    vi.spyOn(inventoryService, "listSensors").mockResolvedValue({ items: [], total: 0 });

    renderWithProviders(
      <MemoryRouter>
        <SensorsPage />
      </MemoryRouter>,
    );

    expect(await screen.findByRole("button", { name: /novo sensor/i })).toBeTruthy();
  });

  it("exibe ação para excluir sensor na listagem", async () => {
    vi.spyOn(inventoryService, "listSensors").mockResolvedValue({
      items: [
        {
          id: "sensor-1",
          sensor_type: "meteorologico",
          family: "Gill WindSonic",
          brand: "Gill",
          model: "WindSonic",
          serial_number: "SN-1",
          patrimony_number: null,
          operational_status: "operacional",
          calibration_due_at: null,
          notes: null,
        },
      ],
      total: 1,
    });

    renderWithProviders(
      <MemoryRouter>
        <SensorsPage />
      </MemoryRouter>,
    );

    expect(await screen.findByRole("button", { name: /excluir sensor gill windsonic/i })).toBeTruthy();
  });
});
