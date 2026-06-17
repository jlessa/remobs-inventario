import AddIcon from "@mui/icons-material/Add";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Fab from "@mui/material/Fab";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import LoadingState from "../components/LoadingState";
import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import { useAuth } from "../state/AuthContext";
import type { Sensor } from "../types";

export default function SensorsPage() {
  const [items, setItems] = useState<Sensor[]>([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { hasPermission } = useAuth();

  useEffect(() => {
    inventoryService
      .listSensors()
      .then((data) => setItems(data.items))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h5">Sensores</Typography>
        {hasPermission("sensor:update") && (
          <Button startIcon={<AddIcon />} variant="contained" onClick={() => navigate("/app/sensors/new")} sx={{ display: { xs: "none", sm: "inline-flex" } }}>
            Novo sensor
          </Button>
        )}
      </Stack>
      {loading && <LoadingState message="Carregando sensores..." />}
      {error && <Alert severity="error">Erro ao carregar sensores.</Alert>}
      {!loading && items.length === 0 && !error && <Alert severity="info">Nenhum sensor cadastrado.</Alert>}
      {items.map((item) => (
        <Card key={item.id}>
          <CardActionArea onClick={() => navigate(`/app/sensors/${item.id}`)}>
            <CardContent>
              <Stack spacing={1}>
                <Stack direction="row" justifyContent="space-between" gap={1}>
                  <Typography fontWeight={700}>{item.family}</Typography>
                  <StatusChip status={item.operational_status} />
                </Stack>
                <Typography color="text.secondary">{[item.sensor_type, item.model, item.serial_number].filter(Boolean).join(" • ")}</Typography>
                {item.calibration_due_at && (
                  <Typography variant="body2">Calibração: {new Date(item.calibration_due_at).toLocaleDateString("pt-BR")}</Typography>
                )}
              </Stack>
            </CardContent>
          </CardActionArea>
        </Card>
      ))}
      {hasPermission("sensor:update") && (
        <Fab
          aria-label="Cadastrar sensor"
          color="primary"
          onClick={() => navigate("/app/sensors/new")}
          sx={{ display: { xs: "flex", sm: "none" }, position: "fixed", bottom: 80, right: 16 }}
        >
          <AddIcon />
        </Fab>
      )}
    </Stack>
  );
}
