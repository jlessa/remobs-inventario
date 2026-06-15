import { render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import HomePage from "../src/pages/HomePage";
import { inventoryService } from "../src/services/inventoryService";

vi.mock("../src/services/inventoryService", () => ({
  inventoryService: {
    listItems: vi.fn(),
    listMovements: vi.fn(),
    listAlerts: vi.fn(),
    listPlatforms: vi.fn(),
    listSensors: vi.fn(),
    listChecklists: vi.fn(),
    getSyncStatus: vi.fn(),
  },
}));

function expectMetric(label: string, value: string) {
  const labelElement = screen.getByText(label);
  const cardContent = labelElement.closest(".MuiCardContent-root");
  expect(cardContent).toBeTruthy();
  expect(within(cardContent as HTMLElement).getByText(value)).toBeTruthy();
}

describe("dashboard operacional", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("consulta checklists e exibe indicadores de registros e envios", async () => {
    vi.mocked(inventoryService.listItems).mockResolvedValue({ items: [], total: 0 });
    vi.mocked(inventoryService.listMovements).mockResolvedValue({ items: [], total: 0 });
    vi.mocked(inventoryService.listAlerts).mockResolvedValue({ items: [], total: 0 });
    vi.mocked(inventoryService.listPlatforms).mockResolvedValue({ items: [], total: 0 });
    vi.mocked(inventoryService.listSensors).mockResolvedValue({ items: [], total: 0 });
    vi.mocked(inventoryService.listChecklists).mockResolvedValue({
      items: [
        { id: "checklist-1", status: "submitted" },
        { id: "checklist-2", status: "draft" },
      ],
      total: 2,
    } as never);
    vi.mocked(inventoryService.getSyncStatus).mockResolvedValue({
      pending_actions: 0,
      conflict_actions: 0,
      server_time: "2026-06-15T18:00:00Z",
    });

    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );

    await waitFor(() => expect(inventoryService.listChecklists).toHaveBeenCalledTimes(1));
    expectMetric("Checklists registrados", "2");
    expectMetric("Checklists enviados", "1");
  });
});
