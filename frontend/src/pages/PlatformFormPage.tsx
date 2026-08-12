import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CircularProgress from "@mui/material/CircularProgress";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import LoadingState from "../components/LoadingState";
import { inventoryService } from "../services/inventoryService";
import { useSnackbar } from "../state/SnackbarContext";

export default function PlatformFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const { showSuccess, showError } = useSnackbar();
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(isEdit);
  const [loadError, setLoadError] = useState(false);
  const [form, setForm] = useState({
    name: "",
    platform_type: "boia_fixa",
    manufacturer: "",
    model: "",
    operational_status: "disponivel",
    description: "",
    reason: "Atualização cadastral.",
  });

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setLoading(true);
    setLoadError(false);
    inventoryService
      .getPlatform(id)
      .then((platform) => {
        if (cancelled) return;
        setForm({
          name: platform.name,
          platform_type: platform.platform_type,
          manufacturer: platform.manufacturer || "",
          model: platform.model || "",
          operational_status: platform.operational_status,
          description: platform.description || "",
          reason: "Atualização cadastral.",
        });
      })
      .catch(() => {
        if (!cancelled) setLoadError(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  function update(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    try {
      if (isEdit && id) {
        const platform = await inventoryService.updatePlatform(id, {
          name: form.name,
          platform_type: form.platform_type,
          manufacturer: form.manufacturer || null,
          model: form.model || null,
          operational_status: form.operational_status,
          description: form.description || null,
          reason: form.reason,
        });
        showSuccess("Plataforma atualizada com sucesso.");
        navigate(`/app/platforms/${platform.id}`);
      } else {
        const platform = await inventoryService.createPlatform({
          name: form.name,
          platform_type: form.platform_type,
          manufacturer: form.manufacturer || undefined,
          model: form.model || undefined,
          operational_status: form.operational_status,
          description: form.description || undefined,
        });
        showSuccess("Plataforma cadastrada com sucesso.");
        navigate(`/app/platforms/${platform.id}`);
      }
    } catch {
      showError(isEdit ? "Não foi possível atualizar a plataforma." : "Não foi possível salvar a plataforma.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <LoadingState message="Carregando plataforma..." />;
  if (loadError) return <Alert severity="error">Erro ao carregar plataforma para edição.</Alert>;

  return (
    <Card>
      <CardContent>
        <Stack component="form" spacing={2.5} onSubmit={handleSubmit}>
          <Typography variant="h5">{isEdit ? "Editar plataforma" : "Nova plataforma"}</Typography>

          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Nome" value={form.name} onChange={(event) => update("name", event.target.value)} required />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField select fullWidth label="Tipo" value={form.platform_type} onChange={(event) => update("platform_type", event.target.value)}>
                <MenuItem value="boia_fixa">Boia fixa</MenuItem>
                <MenuItem value="boia_movel">Boia móvel</MenuItem>
                <MenuItem value="plataforma_fixa">Plataforma fixa</MenuItem>
                <MenuItem value="plataforma_movel">Plataforma móvel</MenuItem>
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Fabricante" value={form.manufacturer} onChange={(event) => update("manufacturer", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Modelo" value={form.model} onChange={(event) => update("model", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField select fullWidth label="Status operacional" value={form.operational_status} onChange={(event) => update("operational_status", event.target.value)}>
                <MenuItem value="disponivel">Disponível</MenuItem>
                <MenuItem value="em_operacao">Em operação</MenuItem>
                <MenuItem value="manutencao">Em manutenção</MenuItem>
                <MenuItem value="inoperante">Inoperante</MenuItem>
              </TextField>
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField fullWidth label="Descrição" value={form.description} onChange={(event) => update("description", event.target.value)} multiline minRows={3} />
            </Grid>
            {isEdit && (
              <Grid size={{ xs: 12 }}>
                <TextField fullWidth label="Justificativa" value={form.reason} onChange={(event) => update("reason", event.target.value)} required multiline minRows={2} />
              </Grid>
            )}
          </Grid>

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
            <Button
              type="submit"
              variant="contained"
              disabled={submitting}
              startIcon={submitting ? <CircularProgress size={18} color="inherit" /> : undefined}
            >
              {submitting ? "Salvando..." : isEdit ? "Salvar alterações" : "Salvar plataforma"}
            </Button>
            <Button variant="outlined" onClick={() => navigate(isEdit && id ? `/app/platforms/${id}` : "/app/platforms")}>
              Cancelar
            </Button>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
