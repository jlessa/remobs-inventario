import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Checkbox from "@mui/material/Checkbox";
import Divider from "@mui/material/Divider";
import FormControlLabel from "@mui/material/FormControlLabel";
import LinearProgress from "@mui/material/LinearProgress";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { photographFields, postFieldChecklistFields } from "../checklists/fieldChecklist";
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
  codigo_viagem: string;
  equipe_hm: string;
  data_operacao: string;
  tipo_manobra: string;
  objetivo_manobra: string;
  inicio_manobra: string;
  termino_manobra: string;
  chuva: string;
  vento: string;
  mar: string;
  corrente: string;
  embarcacao_1: string;
  embarcacao_2: string;
  mestre_1: string;
  mestre_2: string;
  marinheiros_1: string;
  marinheiros_2: string;
  empresa_embarcacao: string;
  mergulhadores: string;
  empresa_mergulho: string;
  terceiros: string;
  fotografias: Record<string, boolean>;
  inspecao_adcp: string;
  inspecao_anodos_adcp: string;
  inspecao_suporte_adcp: string;
  inspecao_transdutores_adcp: string;
  inspecao_cabo_adcp: string;
  inspecao_incrustacao: string;
  inspecao_maregrafo: string;
  inspecao_sensor_vento: string;
  inspecao_modem: string;
  inspecao_bateria: string;
  inspecao_painel_solar: string;
  inspecao_observacoes: string;
  problema_falha: string;
  problema_motivo: string;
  problema_item: string;
  problema_solucao: string;
  pos_campo: Record<string, boolean>;
  notes: string;
}

const defaultDraft: ChecklistDraft = {
  title: "Checklist operacional",
  template_name: "Ficha de Campo V2",
  platform_id: "",
  platform_name: "",
  current_step: 1,
  total_steps: 7,
  codigo_viagem: "",
  equipe_hm: "",
  data_operacao: "",
  tipo_manobra: "Preventiva",
  objetivo_manobra: "",
  inicio_manobra: "",
  termino_manobra: "",
  chuva: "Sem chuva",
  vento: "Ventos fracos",
  mar: "Mar calmo",
  corrente: "Correntes fracas",
  embarcacao_1: "",
  embarcacao_2: "",
  mestre_1: "",
  mestre_2: "",
  marinheiros_1: "",
  marinheiros_2: "",
  empresa_embarcacao: "",
  mergulhadores: "",
  empresa_mergulho: "",
  terceiros: "",
  fotografias: Object.fromEntries(photographFields.map((field) => [field.key, false])),
  inspecao_adcp: "OK",
  inspecao_anodos_adcp: "OK",
  inspecao_suporte_adcp: "OK",
  inspecao_transdutores_adcp: "OK",
  inspecao_cabo_adcp: "OK",
  inspecao_incrustacao: "Pouca",
  inspecao_maregrafo: "OK",
  inspecao_sensor_vento: "OK",
  inspecao_modem: "OK",
  inspecao_bateria: "OK",
  inspecao_painel_solar: "OK",
  inspecao_observacoes: "",
  problema_falha: "",
  problema_motivo: "",
  problema_item: "",
  problema_solucao: "",
  pos_campo: Object.fromEntries(postFieldChecklistFields.map((field) => [field.key, false])),
  notes: "",
};

function mergeDraft(saved: string | null): ChecklistDraft {
  if (!saved) return defaultDraft;
  const parsed = JSON.parse(saved) as Partial<ChecklistDraft>;
  return {
    ...defaultDraft,
    ...parsed,
    fotografias: { ...defaultDraft.fotografias, ...(parsed.fotografias ?? {}) },
    pos_campo: { ...defaultDraft.pos_campo, ...(parsed.pos_campo ?? {}) },
  };
}

function buildAnswers(draft: ChecklistDraft): Record<string, unknown> {
  return {
    "operacao.codigo_viagem": draft.codigo_viagem,
    "operacao.equipe_hm": draft.equipe_hm,
    "operacao.data": draft.data_operacao,
    "operacao.tipo_manobra": draft.tipo_manobra,
    "operacao.objetivo": draft.objetivo_manobra,
    "operacao.horario_inicio": draft.inicio_manobra,
    "operacao.horario_termino": draft.termino_manobra,
    "ambiente.chuva": draft.chuva,
    "ambiente.vento": draft.vento,
    "ambiente.mar": draft.mar,
    "ambiente.corrente": draft.corrente,
    "equipe.embarcacao_1": draft.embarcacao_1,
    "equipe.embarcacao_2": draft.embarcacao_2,
    "equipe.mestre_1": draft.mestre_1,
    "equipe.mestre_2": draft.mestre_2,
    "equipe.marinheiros_1": draft.marinheiros_1,
    "equipe.marinheiros_2": draft.marinheiros_2,
    "equipe.empresa_embarcacao": draft.empresa_embarcacao,
    "equipe.mergulhadores": draft.mergulhadores,
    "equipe.empresa_mergulho": draft.empresa_mergulho,
    "equipe.terceiros": draft.terceiros,
    ...draft.fotografias,
    "inspecao.adcp": draft.inspecao_adcp,
    "inspecao.anodos_adcp": draft.inspecao_anodos_adcp,
    "inspecao.suporte_adcp": draft.inspecao_suporte_adcp,
    "inspecao.transdutores_adcp": draft.inspecao_transdutores_adcp,
    "inspecao.cabo_adcp": draft.inspecao_cabo_adcp,
    "inspecao.incrustacao": draft.inspecao_incrustacao,
    "inspecao.maregrafo": draft.inspecao_maregrafo,
    "inspecao.sensor_vento": draft.inspecao_sensor_vento,
    "inspecao.modem": draft.inspecao_modem,
    "inspecao.bateria": draft.inspecao_bateria,
    "inspecao.painel_solar": draft.inspecao_painel_solar,
    "inspecao.observacoes": draft.inspecao_observacoes,
    "problema.falha": draft.problema_falha,
    "problema.motivo": draft.problema_motivo,
    "problema.item": draft.problema_item,
    "problema.solucao": draft.problema_solucao,
    ...draft.pos_campo,
  };
}

function buildEvidence(draft: ChecklistDraft): Array<Record<string, unknown>> {
  return photographFields
    .filter((field) => draft.fotografias[field.key])
    .map((field) => ({
      type: "foto_obrigatoria",
      key: field.key,
      label: field.label,
      status: "registrada",
    }));
}

const maneuverTypes = ["Emergencial", "Preventiva", "Instalação", "Desinstalação", "Aferição", "Vistoria", "Visita técnica", "Nivelamento de régua", "Outro"];
const rainOptions = ["Sem chuva", "Chuva fraca", "Chuva forte"];
const windOptions = ["Ventos fracos", "Vento moderado", "Ventos fortes"];
const seaOptions = ["Mar calmo", "Ondas moderadas", "Ondas altas"];
const currentOptions = ["Correntes fracas", "Correntes moderadas", "Correntes fortes"];
const inspectionOptions = ["OK", "Observação", "Foi substituído", "Não se aplica"];
const foulingOptions = ["Pouca", "Média", "Muita", "Não se aplica"];

export default function ChecklistFormPage() {
  const navigate = useNavigate();
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [draft, setDraft] = useState<ChecklistDraft>(() => mergeDraft(localStorage.getItem(draftKey)));
  const [error, setError] = useState(false);
  const [saved, setSaved] = useState(false);
  const progress = useMemo(() => Math.round((draft.current_step / draft.total_steps) * 100), [draft.current_step, draft.total_steps]);

  useEffect(() => {
    inventoryService.listPlatforms().then((data) => setPlatforms(data.items)).catch(() => undefined);
  }, []);

  useEffect(() => {
    localStorage.setItem(draftKey, JSON.stringify(draft));
  }, [draft]);

  function update(field: keyof ChecklistDraft, value: string | number | Record<string, boolean>) {
    setDraft((current) => ({ ...current, [field]: value }));
    setSaved(false);
  }

  function updatePhoto(key: string, checked: boolean) {
    setDraft((current) => ({ ...current, fotografias: { ...current.fotografias, [key]: checked } }));
    setSaved(false);
  }

  function updatePostField(key: string, checked: boolean) {
    setDraft((current) => ({ ...current, pos_campo: { ...current.pos_campo, [key]: checked } }));
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
      answers: buildAnswers(draft),
      evidence: buildEvidence(draft),
      notes: draft.notes,
    });
    if (submit) {
      await inventoryService.submitChecklist(checklist.id, "Checklist de campo concluído.");
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
        <Stack component="form" spacing={2.5} onSubmit={handleSubmit}>
          <Typography variant="h5">Novo checklist de campo</Typography>
          {error && <Alert severity="error">Não foi possível salvar o checklist.</Alert>}
          {saved && <Alert severity="success">Rascunho salvo neste dispositivo.</Alert>}
          <LinearProgress variant="determinate" value={progress} />
          <Typography variant="body2">
            Etapa {draft.current_step} de {draft.total_steps}
          </Typography>

          <Stack spacing={2}>
            <Typography variant="h6">Operação</Typography>
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
            <TextField label="Código da viagem" value={draft.codigo_viagem} onChange={(event) => update("codigo_viagem", event.target.value)} />
            <TextField label="Equipe HM" value={draft.equipe_hm} onChange={(event) => update("equipe_hm", event.target.value)} />
            <TextField
              label="Data"
              type="date"
              value={draft.data_operacao}
              onChange={(event) => update("data_operacao", event.target.value)}
              InputLabelProps={{ shrink: true }}
            />
            <TextField select label="Tipo de manobra" value={draft.tipo_manobra} onChange={(event) => update("tipo_manobra", event.target.value)}>
              {maneuverTypes.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Motivo e objetivos da manobra"
              value={draft.objetivo_manobra}
              onChange={(event) => update("objetivo_manobra", event.target.value)}
              multiline
              minRows={2}
            />
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField
                fullWidth
                label="Horário de início da manobra"
                type="time"
                value={draft.inicio_manobra}
                onChange={(event) => update("inicio_manobra", event.target.value)}
                InputLabelProps={{ shrink: true }}
              />
              <TextField
                fullWidth
                label="Horário de término da manobra"
                type="time"
                value={draft.termino_manobra}
                onChange={(event) => update("termino_manobra", event.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Stack>
          </Stack>

          <Divider />

          <Stack spacing={2}>
            <Typography variant="h6">Condições ambientais</Typography>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth select label="Chuva" value={draft.chuva} onChange={(event) => update("chuva", event.target.value)}>
                {rainOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
              <TextField fullWidth select label="Vento" value={draft.vento} onChange={(event) => update("vento", event.target.value)}>
                {windOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth select label="Mar" value={draft.mar} onChange={(event) => update("mar", event.target.value)}>
                {seaOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
              <TextField fullWidth select label="Corrente" value={draft.corrente} onChange={(event) => update("corrente", event.target.value)}>
                {currentOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
            </Stack>
          </Stack>

          <Divider />

          <Stack spacing={2}>
            <Typography variant="h6">Equipe e embarcação</Typography>
            <TextField label="Embarcação 1" value={draft.embarcacao_1} onChange={(event) => update("embarcacao_1", event.target.value)} />
            <TextField label="Embarcação 2" value={draft.embarcacao_2} onChange={(event) => update("embarcacao_2", event.target.value)} />
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth label="Mestre da embarcação 1" value={draft.mestre_1} onChange={(event) => update("mestre_1", event.target.value)} />
              <TextField fullWidth label="Mestre da embarcação 2" value={draft.mestre_2} onChange={(event) => update("mestre_2", event.target.value)} />
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth label="Marinheiros da embarcação 1" value={draft.marinheiros_1} onChange={(event) => update("marinheiros_1", event.target.value)} />
              <TextField fullWidth label="Marinheiros da embarcação 2" value={draft.marinheiros_2} onChange={(event) => update("marinheiros_2", event.target.value)} />
            </Stack>
            <TextField label="Empresa da embarcação" value={draft.empresa_embarcacao} onChange={(event) => update("empresa_embarcacao", event.target.value)} />
            <TextField label="Mergulhadores" value={draft.mergulhadores} onChange={(event) => update("mergulhadores", event.target.value)} />
            <TextField label="Empresa de mergulho" value={draft.empresa_mergulho} onChange={(event) => update("empresa_mergulho", event.target.value)} />
            <TextField label="Terceiros" value={draft.terceiros} onChange={(event) => update("terceiros", event.target.value)} multiline minRows={2} />
          </Stack>

          <Divider />

          <Stack spacing={1}>
            <Typography variant="h6">Fotografias obrigatórias</Typography>
            <Stack direction={{ xs: "column", sm: "row" }} flexWrap="wrap" gap={1}>
              {photographFields.map((field) => (
                <FormControlLabel
                  key={field.key}
                  control={<Checkbox checked={draft.fotografias[field.key]} onChange={(event) => updatePhoto(field.key, event.target.checked)} />}
                  label={field.label}
                />
              ))}
            </Stack>
          </Stack>

          <Divider />

          <Stack spacing={2}>
            <Typography variant="h6">Inspeção técnica</Typography>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth select label="ADCP" value={draft.inspecao_adcp} onChange={(event) => update("inspecao_adcp", event.target.value)}>
                {inspectionOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
              <TextField fullWidth select label="Anodos ADCP" value={draft.inspecao_anodos_adcp} onChange={(event) => update("inspecao_anodos_adcp", event.target.value)}>
                {inspectionOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth select label="Suporte ADCP" value={draft.inspecao_suporte_adcp} onChange={(event) => update("inspecao_suporte_adcp", event.target.value)}>
                {inspectionOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                fullWidth
                select
                label="Transdutores ADCP"
                value={draft.inspecao_transdutores_adcp}
                onChange={(event) => update("inspecao_transdutores_adcp", event.target.value)}
              >
                {inspectionOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth select label="Cabo ADCP" value={draft.inspecao_cabo_adcp} onChange={(event) => update("inspecao_cabo_adcp", event.target.value)}>
                {inspectionOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
              <TextField fullWidth select label="Incrustação" value={draft.inspecao_incrustacao} onChange={(event) => update("inspecao_incrustacao", event.target.value)}>
                {foulingOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth select label="Marégrafo" value={draft.inspecao_maregrafo} onChange={(event) => update("inspecao_maregrafo", event.target.value)}>
                {inspectionOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
              <TextField fullWidth select label="Sensor de vento" value={draft.inspecao_sensor_vento} onChange={(event) => update("inspecao_sensor_vento", event.target.value)}>
                {inspectionOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth select label="Modem" value={draft.inspecao_modem} onChange={(event) => update("inspecao_modem", event.target.value)}>
                {inspectionOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
              <TextField fullWidth select label="Bateria" value={draft.inspecao_bateria} onChange={(event) => update("inspecao_bateria", event.target.value)}>
                {inspectionOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
              <TextField fullWidth select label="Painel solar" value={draft.inspecao_painel_solar} onChange={(event) => update("inspecao_painel_solar", event.target.value)}>
                {inspectionOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
            </Stack>
            <TextField label="Observações técnicas" value={draft.inspecao_observacoes} onChange={(event) => update("inspecao_observacoes", event.target.value)} multiline minRows={2} />
          </Stack>

          <Divider />

          <Stack spacing={2}>
            <Typography variant="h6">Problemas e diagnóstico</Typography>
            <TextField label="Falha encontrada" value={draft.problema_falha} onChange={(event) => update("problema_falha", event.target.value)} />
            <TextField label="Motivo provável" value={draft.problema_motivo} onChange={(event) => update("problema_motivo", event.target.value)} />
            <TextField label="Item que falhou" value={draft.problema_item} onChange={(event) => update("problema_item", event.target.value)} />
            <TextField
              label="Como resolveu o problema?"
              value={draft.problema_solucao}
              onChange={(event) => update("problema_solucao", event.target.value)}
              multiline
              minRows={3}
            />
          </Stack>

          <Divider />

          <Stack spacing={1}>
            <Typography variant="h6">Pós-campo</Typography>
            {postFieldChecklistFields.map((field) => (
              <FormControlLabel
                key={field.key}
                control={<Checkbox checked={draft.pos_campo[field.key]} onChange={(event) => updatePostField(field.key, event.target.checked)} />}
                label={field.label}
              />
            ))}
            <TextField label="Observações" value={draft.notes} onChange={(event) => update("notes", event.target.value)} multiline minRows={3} />
          </Stack>

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
