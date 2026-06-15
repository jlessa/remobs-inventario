import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import PlatformsPage from "../src/pages/PlatformsPage";
import SensorsPage from "../src/pages/SensorsPage";
import { inventoryService } from "../src/services/inventoryService";

vi.mock("../src/state/AuthContext", () => ({
  useAuth: () => ({
    hasPermission: (permission: string) => ["platform:update", "sensor:update"].includes(permission),
  }),
}));

describe("ações de cadastro operacional", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("exibe ação para cadastrar plataforma quando usuário pode atualizar plataformas", async () => {
    vi.spyOn(inventoryService, "listPlatforms").mockResolvedValue({ items: [], total: 0 });

    render(
      <MemoryRouter>
        <PlatformsPage />
      </MemoryRouter>,
    );

    expect(await screen.findByRole("button", { name: /nova plataforma/i })).toBeTruthy();
  });

  it("exibe ação para cadastrar sensor quando usuário pode atualizar sensores", async () => {
    vi.spyOn(inventoryService, "listSensors").mockResolvedValue({ items: [], total: 0 });

    render(
      <MemoryRouter>
        <SensorsPage />
      </MemoryRouter>,
    );

    expect(await screen.findByRole("button", { name: /novo sensor/i })).toBeTruthy();
  });
});
