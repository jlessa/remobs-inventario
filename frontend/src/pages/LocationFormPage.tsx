import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CircularProgress from "@mui/material/CircularProgress";
import FormControlLabel from "@mui/material/FormControlLabel";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Switch from "@mui/material/Switch";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import LoadingState from "../components/LoadingState";
import { inventoryService } from "../services/inventoryService";
import { useSnackbar } from "../state/SnackbarContext";

export default function LocationFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const { showSuccess, showError } = useSnackbar();
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(isEdit);
  const [loadError, setLoadError] = useState(false);
  const [form, setForm] = useState({
    name: "",
    location_type: "estoque",
    is_active: true,
    reason: "Atualização cadastral.",
  });

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setLoading(true);
    setLoadError(false);
    inventoryService
      .getLocation(id)
      .then((location) => {
        if (cancelled) return;
        setForm({
          name: location.name,
          location_type: location.location_type,
          is_active: location.is_active,
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

  function update<K extends keyof typeof form>(field: K, value: (typeof form)[K]) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    try {
      if (isEdit && id) {
        await inventoryService.updateLocation(id, {
          name: form.name,
          location_type: form.location_type,
          is_active: form.is_active,
          reason: form.reason,
        });
        showSuccess("Local atualizado com sucesso.");
        navigate("/app/locations");
      } else {
        await inventoryService.createLocation({
          name: form.name,
          location_type: form.location_type,
        });
        showSuccess("Local cadastrado com sucesso.");
        navigate("/app/locations");
      }
    } catch {
      showError(isEdit ? "Não foi possível atualizar o local." : "Não foi possível salvar o local.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <LoadingState message="Carregando local..." />;
  if (loadError) return <Alert severity="error">Erro ao carregar local para edição.</Alert>;

  return (
    <Card>
      <CardContent>
        <Stack component="form" spacing={2.5} onSubmit={handleSubmit}>
          <Typography variant="h5">{isEdit ? "Editar local" : "Novo local"}</Typography>

          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Nome" value={form.name} onChange={(event) => update("name", event.target.value)} required />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField select fullWidth label="Tipo" value={form.location_type} onChange={(event) => update("location_type", event.target.value)}>
                <MenuItem value="estoque">Estoque</MenuItem>
                <MenuItem value="campo">Campo</MenuItem>
                <MenuItem value="manutencao">Manutenção</MenuItem>
                <MenuItem value="outro">Outro</MenuItem>
              </TextField>
            </Grid>
            {isEdit && (
              <>
                <Grid size={{ xs: 12, md: 6 }}>
                  <FormControlLabel
                    control={<Switch checked={form.is_active} onChange={(event) => update("is_active", event.target.checked)} />}
                    label="Ativo"
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="Motivo da alteração"
                    value={form.reason}
                    onChange={(event) => update("reason", event.target.value)}
                    multiline
                    minRows={2}
                    required
                  />
                </Grid>
              </>
            )}
          </Grid>

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
            <Button variant="outlined" onClick={() => navigate("/app/locations")} disabled={submitting}>
              Cancelar
            </Button>
            <Button type="submit" variant="contained" disabled={submitting || form.name.trim().length < 1}>
              {submitting ? <CircularProgress size={18} /> : isEdit ? "Salvar" : "Cadastrar"}
            </Button>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
