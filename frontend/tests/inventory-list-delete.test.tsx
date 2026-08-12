import { screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import InventoryListPage from "../src/pages/InventoryListPage";
import { inventoryService } from "../src/services/inventoryService";
import { renderWithProviders } from "./test-utils";

vi.mock("../src/state/AuthContext", () => ({
  useAuth: () => ({
    hasPermission: (permission: string) => ["inventory:item:read", "inventory:item:delete"].includes(permission),
    hasAnyPermission: (...permissions: string[]) =>
      permissions.some((permission) => ["inventory:item:read", "inventory:item:delete"].includes(permission)),
  }),
}));

describe("exclusão na listagem de inventário", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("exibe botão de excluir item quando usuário tem permissão", async () => {
    vi.spyOn(inventoryService, "listItems").mockResolvedValue({
      items: [
        {
          id: "item-1",
          item_type: "consumable",
          name: "Cabo de aço",
          brand: "Acme",
          model: "CA-10",
          serial_number: null,
          patrimony_number: null,
          invoice_number: null,
          description: null,
          condition_status: "operacional",
          unit: "un",
          category_name: "Cabos",
          current_location_id: "loc-1",
          current_location_name: "Paiol",
          stock_total: 4,
          minimum_stock_national: 2,
          ideal_stock: 6,
          row_version: 1,
          balances: [],
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      total: 1,
    });

    renderWithProviders(
      <MemoryRouter>
        <InventoryListPage />
      </MemoryRouter>,
    );

    expect(await screen.findByRole("button", { name: /excluir item cabo de aço/i })).toBeTruthy();
  });
});
