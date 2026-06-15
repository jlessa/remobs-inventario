import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { inventoryService } from "../services/inventoryService";

export default function PlatformFormPage() {
  const navigate = useNavigate();
  const [error, setError] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    name: "",
    platform_type: "boia_fixa",
    manufacturer: "",
    model: "",
    operational_status: "disponivel",
    description: "",
  });

  function update(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(false);
    try {
      const platform = await inventoryService.createPlatform({
        name: form.name,
        platform_type: form.platform_type,
        manufacturer: form.manufacturer || undefined,
        model: form.model || undefined,
        operational_status: form.operational_status,
        description: form.description || undefined,
      });
      navigate(`/app/platforms/${platform.id}`);
    } catch {
      setError(true);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card>
      <CardContent>
        <Stack component="form" spacing={2.5} onSubmit={handleSubmit}>
          <Typography variant="h5">Nova plataforma</Typography>
          {error && <Alert severity="error">Não foi possível salvar a plataforma.</Alert>}

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
          </Grid>

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
            <Button type="submit" variant="contained" disabled={submitting}>
              Salvar plataforma
            </Button>
            <Button variant="outlined" onClick={() => navigate("/app/platforms")}>
              Cancelar
            </Button>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
