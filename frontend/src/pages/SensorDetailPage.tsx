import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import type { SensorDetail } from "../types";

export default function SensorDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [sensor, setSensor] = useState<SensorDetail | null>(null);
  const [error, setError] = useState(false);
  const [actionError, setActionError] = useState(false);

  useEffect(() => {
    if (!id) return;
    inventoryService
      .getSensor(id)
      .then(setSensor)
      .catch(() => setError(true));
  }, [id]);

  if (error) return <Alert severity="error">Erro ao carregar sensor.</Alert>;
  if (!sensor) return <Alert severity="info">Carregando sensor.</Alert>;

  const calibrationText = sensor.calibration_due_at
    ? new Date(sensor.calibration_due_at).toLocaleDateString("pt-BR")
    : "Sem vencimento informado";

  return (
    <Stack spacing={2}>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/app/sensors")} sx={{ alignSelf: "flex-start" }}>
        Sensores
      </Button>

      <Card>
        <CardContent>
          <Stack spacing={1}>
            <Stack direction="row" justifyContent="space-between" gap={1}>
              <Typography variant="h5">{sensor.family}</Typography>
              <StatusChip status={sensor.operational_status} />
            </Stack>
            <Typography color="text.secondary">
              {[sensor.sensor_type, sensor.brand, sensor.model].filter(Boolean).join(" • ")}
            </Typography>
            <Typography>Número de série: {sensor.serial_number || "Não informado"}</Typography>
            <Typography>Patrimônio: {sensor.patrimony_number || "Não informado"}</Typography>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Stack spacing={1}>
            <Typography variant="h6">Plataforma vinculada</Typography>
            {sensor.current_platform ? (
              <Stack direction="row" justifyContent="space-between" gap={1}>
                <Button onClick={() => navigate(`/app/platforms/${sensor.current_platform?.id}`)}>
                  {sensor.current_platform.name}
                </Button>
                <StatusChip status={sensor.current_platform.operational_status} />
              </Stack>
            ) : (
              <Alert severity="info">Sensor sem plataforma ativa.</Alert>
            )}
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Stack spacing={1}>
            <Typography variant="h6">Calibração e operação</Typography>
            {actionError && <Alert severity="error">Não foi possível registrar a inconsistência.</Alert>}
            <Typography>Vencimento: {calibrationText}</Typography>
            {sensor.notes && <Typography color="text.secondary">{sensor.notes}</Typography>}
            <Button
              startIcon={<ErrorOutlineIcon />}
              variant="outlined"
              color="warning"
              onClick={async () => {
                setActionError(false);
                try {
                  await inventoryService.updateSensor(sensor.id, {
                    operational_status: "inconsistencia",
                    reason: "Inconsistência registrada pelo painel operacional.",
                  });
                  const updated = await inventoryService.getSensor(sensor.id);
                  setSensor(updated);
                } catch {
                  setActionError(true);
                }
              }}
            >
              Registrar inconsistência
            </Button>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6">Histórico de instalações</Typography>
          {sensor.installations.length === 0 && <Alert severity="info">Nenhuma instalação registrada.</Alert>}
          <List dense>
            {sensor.installations.map((installation) => (
              <ListItem key={installation.id} disableGutters secondaryAction={<StatusChip status={installation.status} />}>
                <ListItemText primary={installation.platform_name} secondary={installation.notes || "Sem observação"} />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </Stack>
  );
}
