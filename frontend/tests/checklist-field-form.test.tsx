import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import ChecklistFormPage from "../src/pages/ChecklistFormPage";
import { inventoryService } from "../src/services/inventoryService";

describe("formulário de checklist de campo", () => {
  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("envia respostas operacionais detalhadas inspiradas na ficha de campo", async () => {
    vi.spyOn(inventoryService, "listPlatforms").mockResolvedValue({ items: [], total: 0 });
    const createChecklist = vi.spyOn(inventoryService, "createChecklist").mockResolvedValue({
      id: "checklist-1",
      title: "Checklist operacional",
      template_name: "Ficha de Campo V2",
      platform_id: null,
      platform_name: null,
      status: "draft",
      current_step: 1,
      total_steps: 7,
      answers: {},
      evidence: [],
      submitted_by_id: 7,
      submitted_by_username: "operacao",
      notes: null,
      created_at: "2026-06-15T12:00:00Z",
      updated_at: "2026-06-15T12:00:00Z",
      submitted_at: null,
    });
    const submitChecklist = vi.spyOn(inventoryService, "submitChecklist").mockResolvedValue({
      id: "checklist-1",
      title: "Checklist operacional",
      template_name: "Ficha de Campo V2",
      platform_id: null,
      platform_name: null,
      status: "submitted",
      current_step: 7,
      total_steps: 7,
      answers: {},
      evidence: [],
      submitted_by_id: 7,
      submitted_by_username: "operacao",
      notes: null,
      created_at: "2026-06-15T12:00:00Z",
      updated_at: "2026-06-15T12:00:00Z",
      submitted_at: "2026-06-15T12:30:00Z",
    });

    render(
      <MemoryRouter>
        <ChecklistFormPage />
      </MemoryRouter>,
    );

    fireEvent.change(await screen.findByLabelText(/código da viagem/i), { target: { value: "MEQ-AX39" } });
    fireEvent.change(screen.getByLabelText(/equipe hm/i), { target: { value: "EMD, CCL" } });
    fireEvent.change(screen.getByLabelText(/^embarcação 1$/i), { target: { value: "Lancha de apoio" } });
    fireEvent.click(screen.getByLabelText(/material embarcado/i));
    fireEvent.click(screen.getByLabelText(/adcp antes/i));
    fireEvent.change(screen.getByLabelText(/falha encontrada/i), { target: { value: "Falha de comunicação" } });
    fireEvent.change(screen.getByLabelText(/como resolveu o problema/i), { target: { value: "Substituição do cabo Y" } });
    fireEvent.click(screen.getByLabelText(/colocar fotos no servidor/i));

    fireEvent.click(screen.getByRole("button", { name: /enviar checklist/i }));

    await waitFor(() => expect(createChecklist).toHaveBeenCalledTimes(1));
    expect(createChecklist).toHaveBeenCalledWith(
      expect.objectContaining({
        template_name: "Ficha de Campo V2",
        total_steps: 7,
        answers: expect.objectContaining({
          "operacao.codigo_viagem": "MEQ-AX39",
          "operacao.equipe_hm": "EMD, CCL",
          "equipe.embarcacao_1": "Lancha de apoio",
          "fotografias.material_embarcado": true,
          "fotografias.adcp_antes_apos_limpeza": true,
          "problema.falha": "Falha de comunicação",
          "problema.solucao": "Substituição do cabo Y",
          "pos_campo.fotos_servidor": true,
        }),
      }),
    );
    expect(submitChecklist).toHaveBeenCalledWith("checklist-1", "Checklist de campo concluído.");
  }, 20000);
});
