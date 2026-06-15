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

export default function SensorFormPage() {
  const navigate = useNavigate();
  const [error, setError] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    sensor_type: "meteorologico",
    family: "",
    brand: "",
    model: "",
    serial_number: "",
    patrimony_number: "",
    operational_status: "nao_instalado",
    calibration_due_at: "",
    notes: "",
  });

  function update(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(false);
    try {
      const sensor = await inventoryService.createSensor({
        sensor_type: form.sensor_type,
        family: form.family,
        brand: form.brand || undefined,
        model: form.model || undefined,
        serial_number: form.serial_number || undefined,
        patrimony_number: form.patrimony_number || undefined,
        operational_status: form.operational_status,
        calibration_due_at: form.calibration_due_at ? new Date(`${form.calibration_due_at}T00:00:00`).toISOString() : undefined,
        notes: form.notes || undefined,
      });
      navigate(`/app/sensors/${sensor.id}`);
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
          <Typography variant="h5">Novo sensor</Typography>
          {error && <Alert severity="error">Não foi possível salvar o sensor.</Alert>}

          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField select fullWidth label="Tipo" value={form.sensor_type} onChange={(event) => update("sensor_type", event.target.value)}>
                <MenuItem value="meteorologico">Meteorológico</MenuItem>
                <MenuItem value="oceanografico">Oceanográfico</MenuItem>
                <MenuItem value="ondas">Ondas</MenuItem>
                <MenuItem value="posicionamento">Posicionamento</MenuItem>
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Família" value={form.family} onChange={(event) => update("family", event.target.value)} required />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Marca" value={form.brand} onChange={(event) => update("brand", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Modelo" value={form.model} onChange={(event) => update("model", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Número de série" value={form.serial_number} onChange={(event) => update("serial_number", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Patrimônio" value={form.patrimony_number} onChange={(event) => update("patrimony_number", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField select fullWidth label="Status operacional" value={form.operational_status} onChange={(event) => update("operational_status", event.target.value)}>
                <MenuItem value="nao_instalado">Não instalado</MenuItem>
                <MenuItem value="operacional">Operacional</MenuItem>
                <MenuItem value="manutencao">Em manutenção</MenuItem>
                <MenuItem value="inconsistencia">Inconsistência</MenuItem>
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Vencimento da calibração"
                type="date"
                value={form.calibration_due_at}
                onChange={(event) => update("calibration_due_at", event.target.value)}
                slotProps={{ inputLabel: { shrink: true } }}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField fullWidth label="Observações" value={form.notes} onChange={(event) => update("notes", event.target.value)} multiline minRows={3} />
            </Grid>
          </Grid>

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
            <Button type="submit" variant="contained" disabled={submitting}>
              Salvar sensor
            </Button>
            <Button variant="outlined" onClick={() => navigate("/app/sensors")}>
              Cancelar
            </Button>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
