import { fireEvent, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import InventoryFormPage from "../src/pages/InventoryFormPage";
import { inventoryService } from "../src/services/inventoryService";
import { renderWithProviders } from "./test-utils";

vi.mock("../src/state/AuthContext", () => ({
  useAuth: () => ({
    hasPermission: () => true,
    hasAnyPermission: () => true,
  }),
}));

describe("autocomplete no cadastro de itens", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("busca sugestões a partir de 1 letra no campo Nome", async () => {
    const suggest = vi.spyOn(inventoryService, "suggestItemField").mockResolvedValue(["Silicone bisnaga 200 ml"]);

    renderWithProviders(
      <MemoryRouter>
        <InventoryFormPage />
      </MemoryRouter>,
    );

    const nameInput = screen.getByRole("combobox", { name: /^nome/i });
    fireEvent.change(nameInput, { target: { value: "s" } });

    await waitFor(
      () => {
        expect(suggest).toHaveBeenCalledWith("name", "s", expect.objectContaining({ signal: expect.any(AbortSignal) }));
      },
      { timeout: 2000 },
    );

    expect(await screen.findByText("Silicone bisnaga 200 ml")).toBeTruthy();
  });
});
