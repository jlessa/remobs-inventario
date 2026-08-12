import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/DeleteOutline";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Fab from "@mui/material/Fab";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import LoadingState from "../components/LoadingState";
import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import { useAuth } from "../state/AuthContext";
import { useSnackbar } from "../state/SnackbarContext";
import type { Sensor } from "../types";

export default function SensorsPage() {
  const [items, setItems] = useState<Sensor[]>([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const navigate = useNavigate();
  const { hasAnyPermission } = useAuth();
  const { showSuccess, showError } = useSnackbar();
  const canCreate = hasAnyPermission("sensor:create", "sensor:update");
  const canDelete = hasAnyPermission("sensor:delete", "sensor:update");

  useEffect(() => {
    inventoryService
      .listSensors()
      .then((data) => setItems(data.items))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  async function handleDelete(item: Sensor) {
    const confirmed = window.confirm(`Excluir o sensor "${item.family}"? Esta ação remove o sensor da listagem.`);
    if (!confirmed) {
      return;
    }

    setDeletingId(item.id);
    try {
      await inventoryService.deleteSensor(item.id, "Exclusão pela listagem de sensores.");
      setItems((current) => current.filter((entry) => entry.id !== item.id));
      showSuccess(`Sensor "${item.family}" excluído com sucesso.`);
    } catch {
      showError(`Não foi possível excluir o sensor "${item.family}".`);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h5">Sensores</Typography>
        {canCreate && (
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
          <Stack direction="row" alignItems="stretch">
            <CardActionArea onClick={() => navigate(`/app/sensors/${item.id}`)} sx={{ flex: 1 }}>
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
            {canDelete && (
              <Box sx={{ display: "flex", alignItems: "center", pr: 1 }}>
                <IconButton
                  aria-label={`Excluir sensor ${item.family}`}
                  color="error"
                  disabled={deletingId === item.id}
                  onClick={() => handleDelete(item)}
                >
                  <DeleteIcon />
                </IconButton>
              </Box>
            )}
          </Stack>
        </Card>
      ))}
      {canCreate && (
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
