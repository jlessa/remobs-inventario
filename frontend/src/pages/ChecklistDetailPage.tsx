import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CircularProgress from "@mui/material/CircularProgress";
import LinearProgress from "@mui/material/LinearProgress";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { checklistAnswerGroups, formatChecklistValue, getKnownChecklistAnswerKeys } from "../checklists/fieldChecklist";
import LoadingState from "../components/LoadingState";
import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import type { Checklist } from "../types";

export default function ChecklistDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [checklist, setChecklist] = useState<Checklist | null>(null);
  const [error, setError] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!id) return;
    inventoryService
      .getChecklist(id)
      .then(setChecklist)
      .catch(() => setError(true));
  }, [id]);

  async function submit() {
    if (!checklist) return;
    setSubmitting(true);
    setError(false);
    try {
      const updated = await inventoryService.submitChecklist(checklist.id, "Checklist enviado pelo painel operacional.");
      setChecklist(updated);
    } catch {
      setError(true);
    } finally {
      setSubmitting(false);
    }
  }

  if (error && !checklist) return <Alert severity="error">Erro ao carregar checklist.</Alert>;
  if (!checklist) return <LoadingState message="Carregando checklist..." />;

  const progress = Math.round((checklist.current_step / checklist.total_steps) * 100);
  const knownAnswerKeys = getKnownChecklistAnswerKeys();
  const groupedAnswers = checklistAnswerGroups
    .map((group) => ({
      ...group,
      fields: group.fields.filter((field) => Object.prototype.hasOwnProperty.call(checklist.answers, field.key)),
    }))
    .filter((group) => group.fields.length > 0);
  const extraAnswers = Object.entries(checklist.answers).filter(([key]) => !knownAnswerKeys.has(key));

  return (
    <Stack spacing={2}>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/app/checklists")} sx={{ alignSelf: "flex-start" }}>
        Checklists
      </Button>
      {error && <Alert severity="error">Não foi possível enviar o checklist.</Alert>}
      <Card>
        <CardContent>
          <Stack spacing={1.5}>
            <Stack direction="row" justifyContent="space-between" gap={1}>
              <Typography variant="h5">{checklist.title}</Typography>
              <StatusChip status={checklist.status} />
            </Stack>
            <Typography color="text.secondary">{[checklist.template_name, checklist.platform_name].filter(Boolean).join(" • ")}</Typography>
            <LinearProgress variant="determinate" value={progress} />
            <Typography>
              Etapa {checklist.current_step} de {checklist.total_steps}
            </Typography>
            {checklist.submitted_at && <Typography>Enviado em {new Date(checklist.submitted_at).toLocaleString("pt-BR")}</Typography>}
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Stack spacing={2}>
            <Typography variant="h6">Respostas</Typography>
            {groupedAnswers.map((group) => (
              <Stack key={group.title} spacing={1}>
                <Typography variant="subtitle1" fontWeight={700}>
                  {group.title}
                </Typography>
                {group.fields.map((field) => (
                  <Stack key={field.key} direction={{ xs: "column", sm: "row" }} justifyContent="space-between" gap={1}>
                    <Typography color="text.secondary">{field.label}</Typography>
                    <Typography fontWeight={700}>{formatChecklistValue(checklist.answers[field.key])}</Typography>
                  </Stack>
                ))}
              </Stack>
            ))}
            {extraAnswers.length > 0 && (
              <Stack spacing={1}>
                <Typography variant="subtitle1" fontWeight={700}>
                  Outras respostas
                </Typography>
                {extraAnswers.map(([key, value]) => (
                  <Stack key={key} direction={{ xs: "column", sm: "row" }} justifyContent="space-between" gap={1}>
                    <Typography color="text.secondary">{key.replaceAll(".", " / ")}</Typography>
                    <Typography fontWeight={700}>{formatChecklistValue(value)}</Typography>
                  </Stack>
                ))}
              </Stack>
            )}
            {Object.keys(checklist.answers).length === 0 && <Alert severity="info">Nenhuma resposta registrada.</Alert>}
          </Stack>
        </CardContent>
      </Card>

      {checklist.status !== "submitted" && (
        <Button
          variant="contained"
          onClick={submit}
          disabled={submitting}
          startIcon={submitting ? <CircularProgress size={18} color="inherit" /> : undefined}
        >
          {submitting ? "Enviando..." : "Enviar checklist"}
        </Button>
      )}
    </Stack>
  );
}
