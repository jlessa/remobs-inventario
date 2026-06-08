import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import LinearProgress from "@mui/material/LinearProgress";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { inventoryService } from "../services/inventoryService";
import type { Platform } from "../types";

const draftKey = "remobs_checklist_draft";

interface ChecklistDraft {
  title: string;
  template_name: string;
  platform_id: string;
  platform_name: string;
  current_step: number;
  total_steps: number;
  batteries_installed: boolean;
  batteries_quantity: string;
  transmission_ok: boolean;
  notes: string;
}

const defaultDraft: ChecklistDraft = {
  title: "Checklist operacional",
  template_name: "Operacional padrão",
  platform_id: "",
  platform_name: "",
  current_step: 1,
  total_steps: 4,
  batteries_installed: false,
  batteries_quantity: "0",
  transmission_ok: false,
  notes: "",
};

export default function ChecklistFormPage() {
  const navigate = useNavigate();
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [draft, setDraft] = useState<ChecklistDraft>(() => {
    const saved = localStorage.getItem(draftKey);
    return saved ? { ...defaultDraft, ...JSON.parse(saved) } : defaultDraft;
  });
  const [error, setError] = useState(false);
  const [saved, setSaved] = useState(false);
  const progress = useMemo(() => Math.round((draft.current_step / draft.total_steps) * 100), [draft.current_step, draft.total_steps]);

  useEffect(() => {
    inventoryService.listPlatforms().then((data) => setPlatforms(data.items)).catch(() => undefined);
  }, []);

  useEffect(() => {
    localStorage.setItem(draftKey, JSON.stringify(draft));
  }, [draft]);

  function update(field: keyof ChecklistDraft, value: string | boolean | number) {
    setDraft((current) => ({ ...current, [field]: value }));
    setSaved(false);
  }

  async function save(submit: boolean) {
    setError(false);
    const checklist = await inventoryService.createChecklist({
      title: draft.title,
      template_name: draft.template_name,
      platform_id: draft.platform_id || null,
      platform_name: draft.platform_name || null,
      total_steps: draft.total_steps,
      answers: {
        "energia.baterias_instaladas": draft.batteries_installed,
        "energia.quantidade_baterias": Number(draft.batteries_quantity),
        "transmissao.ok": draft.transmission_ok,
      },
      notes: draft.notes,
    });
    if (submit) {
      await inventoryService.submitChecklist(checklist.id, "Checklist concluído em campo.");
    }
    localStorage.removeItem(draftKey);
    navigate(submit ? "/app/checklists" : `/app/checklists/${checklist.id}`);
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      await save(true);
    } catch {
      setError(true);
    }
  }

  return (
    <Card>
      <CardContent>
        <Stack component="form" spacing={2} onSubmit={handleSubmit}>
          <Typography variant="h5">Novo checklist</Typography>
          {error && <Alert severity="error">Não foi possível salvar o checklist.</Alert>}
          {saved && <Alert severity="success">Rascunho salvo neste dispositivo.</Alert>}
          <LinearProgress variant="determinate" value={progress} />
          <Typography variant="body2">
            Etapa {draft.current_step} de {draft.total_steps}
          </Typography>

          <TextField label="Título" value={draft.title} onChange={(event) => update("title", event.target.value)} required />
          <TextField label="Modelo" value={draft.template_name} onChange={(event) => update("template_name", event.target.value)} required />
          <TextField
            select
            label="Plataforma"
            value={draft.platform_id}
            onChange={(event) => {
              const platform = platforms.find((item) => item.id === event.target.value);
              update("platform_id", event.target.value);
              update("platform_name", platform?.name || "");
            }}
          >
            <MenuItem value="">Sem plataforma</MenuItem>
            {platforms.map((platform) => (
              <MenuItem key={platform.id} value={platform.id}>
                {platform.name}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label="Etapa atual"
            type="number"
            value={draft.current_step}
            onChange={(event) => update("current_step", Math.min(draft.total_steps, Math.max(1, Number(event.target.value))))}
          />
          <FormControlLabel
            control={<Checkbox checked={draft.batteries_installed} onChange={(event) => update("batteries_installed", event.target.checked)} />}
            label="Baterias instaladas"
          />
          <TextField
            label="Quantidade de baterias"
            type="number"
            value={draft.batteries_quantity}
            onChange={(event) => update("batteries_quantity", event.target.value)}
          />
          <FormControlLabel
            control={<Checkbox checked={draft.transmission_ok} onChange={(event) => update("transmission_ok", event.target.checked)} />}
            label="Transmissão verificada"
          />
          <TextField label="Observações" value={draft.notes} onChange={(event) => update("notes", event.target.value)} multiline minRows={3} />
          <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
            <Button
              variant="outlined"
              onClick={() => {
                localStorage.setItem(draftKey, JSON.stringify(draft));
                setSaved(true);
              }}
            >
              Salvar rascunho
            </Button>
            <Button type="submit" variant="contained">
              Enviar checklist
            </Button>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
