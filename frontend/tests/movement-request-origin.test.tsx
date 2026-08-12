import { screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import MovementRequestPage, { resolveOriginLocationId } from "../src/pages/MovementRequestPage";
import { inventoryService } from "../src/services/inventoryService";
import type { InventoryItem } from "../src/types";
import { renderWithProviders } from "./test-utils";

const itemEstoque: InventoryItem = {
  id: "item-1",
  item_type: "consumable",
  name: "Bateria 28Ah",
  brand: "Moura",
  model: "28Ah",
  serial_number: null,
  patrimony_number: null,
  invoice_number: null,
  description: null,
  condition_status: "operacional",
  category_name: "Energia",
  current_location_id: "loc-campo",
  current_location_name: "Campo",
  unit: "un",
  minimum_stock_national: 1,
  ideal_stock: 5,
  row_version: 1,
  stock_total: 5,
  balances: [
    {
      id: "bal-estoque",
      location_id: "loc-estoque",
      location_name: "Estoque",
      quantity: 2,
      reserved_quantity: 0,
    },
    {
      id: "bal-campo",
      location_id: "loc-campo",
      location_name: "Campo",
      quantity: 3,
      reserved_quantity: 0,
    },
  ],
};

describe("resolveOriginLocationId", () => {
  it("prefere o local atual do item quando há saldo disponível", () => {
    expect(resolveOriginLocationId(itemEstoque)).toBe("loc-campo");
  });

  it("mantém o local atual do item mesmo sem saldo disponível nesse local", () => {
    const item: InventoryItem = {
      ...itemEstoque,
      current_location_id: "loc-campo",
      balances: [
        {
          id: "bal-estoque",
          location_id: "loc-estoque",
          location_name: "Estoque",
          quantity: 2,
          reserved_quantity: 0,
        },
        {
          id: "bal-campo",
          location_id: "loc-campo",
          location_name: "Campo",
          quantity: 1,
          reserved_quantity: 1,
        },
      ],
    };
    expect(resolveOriginLocationId(item)).toBe("loc-campo");
  });

  it("usa o local atual mesmo sem linhas de saldo", () => {
    expect(resolveOriginLocationId({ ...itemEstoque, balances: [] })).toBe("loc-campo");
  });
});

describe("MovementRequestPage origem", () => {
  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("preenche origem com o local atual ao abrir com itemId do detalhe", async () => {
    localStorage.setItem(
      "remobs_movement_request_draft",
      JSON.stringify({
        itemId: "outro",
        fromLocationId: "loc-estoque",
        quantity: "1",
        destination: "Campo",
        reason: "Uso em operação de campo.",
        evidenceNote: "",
      }),
    );
    vi.spyOn(inventoryService, "listItems").mockResolvedValue({ items: [itemEstoque], total: 1 });
    vi.spyOn(inventoryService, "getItem").mockResolvedValue(itemEstoque);
    vi.spyOn(inventoryService, "listLocations").mockResolvedValue({
      items: [
        {
          id: "loc-campo",
          name: "Campo",
          location_type: "campo",
          is_active: true,
          created_at: "2026-01-01T00:00:00Z",
        },
        {
          id: "loc-estoque",
          name: "Estoque",
          location_type: "estoque",
          is_active: true,
          created_at: "2026-01-01T00:00:00Z",
        },
      ],
      total: 2,
    });

    renderWithProviders(
      <MemoryRouter initialEntries={[{ pathname: "/app/movements/new", state: { itemId: "item-1" } }]}>
        <Routes>
          <Route path="/app/movements/new" element={<MovementRequestPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      const origin = screen.getByRole("combobox", { name: /^Origem/i }) as HTMLInputElement;
      expect(origin.value).toMatch(/Campo/);
    });
    const origin = screen.getByRole("combobox", { name: /^Origem/i }) as HTMLInputElement;
    expect(origin.value).not.toMatch(/Estoque/);
  });

  it("preenche origem com o local do item mesmo sem saldos", async () => {
    const itemSemSaldo: InventoryItem = { ...itemEstoque, stock_total: 0, balances: [] };
    vi.spyOn(inventoryService, "listItems").mockResolvedValue({ items: [itemSemSaldo], total: 1 });
    vi.spyOn(inventoryService, "getItem").mockResolvedValue(itemSemSaldo);
    vi.spyOn(inventoryService, "listLocations").mockResolvedValue({
      items: [
        {
          id: "loc-campo",
          name: "Campo",
          location_type: "campo",
          is_active: true,
          created_at: "2026-01-01T00:00:00Z",
        },
        {
          id: "loc-estoque",
          name: "Estoque",
          location_type: "estoque",
          is_active: true,
          created_at: "2026-01-01T00:00:00Z",
        },
      ],
      total: 2,
    });

    renderWithProviders(
      <MemoryRouter initialEntries={[{ pathname: "/app/movements/new", state: { itemId: "item-1" } }]}>
        <Routes>
          <Route path="/app/movements/new" element={<MovementRequestPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      const origin = screen.getByRole("combobox", { name: /^Origem/i }) as HTMLInputElement;
      expect(origin.value).toMatch(/Campo/);
    });
  });
});
