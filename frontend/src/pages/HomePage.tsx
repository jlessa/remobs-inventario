import AssignmentTurnedInIcon from "@mui/icons-material/AssignmentTurnedIn";
import FactCheckIcon from "@mui/icons-material/FactCheck";
import InventoryIcon from "@mui/icons-material/Inventory2";
import SyncIcon from "@mui/icons-material/Sync";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import type { AlertItem, InventoryItem, Movement, Platform, Sensor, SyncStatus } from "../types";

interface DashboardState {
  items: InventoryItem[];
  movements: Movement[];
  alerts: AlertItem[];
  platforms: Platform[];
  sensors: Sensor[];
  sync: SyncStatus | null;
}

const initialState: DashboardState = {
  items: [],
  movements: [],
  alerts: [],
  platforms: [],
  sensors: [],
  sync: null,
};

export default function HomePage() {
  const [data, setData] = useState<DashboardState>(initialState);
  const [error, setError] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      inventoryService.listItems(),
      inventoryService.listMovements(),
      inventoryService.listAlerts(),
      inventoryService.listPlatforms(),
      inventoryService.listSensors(),
      inventoryService.getSyncStatus(),
    ])
      .then(([items, movements, alerts, platforms, sensors, sync]) =>
        setData({
          items: items.items,
          movements: movements.items,
          alerts: alerts.items,
          platforms: platforms.items,
          sensors: sensors.items,
          sync,
        }),
      )
      .catch(() => setError(true));
  }, []);

  const summary = useMemo(() => {
    const criticalStock = data.items.filter(
      (item) => item.minimum_stock_national > 0 && item.stock_total < item.minimum_stock_national,
    );
    const pendingMovements = data.movements.filter((movement) => movement.status === "pending");
    const platformsInOperation = data.platforms.filter((platform) => platform.operational_status === "em_operacao");
    const platformsInMaintenance = data.platforms.filter((platform) =>
      ["manutencao", "em_manutencao", "offline"].includes(platform.operational_status),
    );
    const brokenSensors = data.sensors.filter((sensor) => ["avariado", "inconsistencia"].includes(sensor.operational_status));

    return {
      criticalStock,
      pendingMovements,
      platformsInOperation,
      platformsInMaintenance,
      brokenSensors,
    };
  }, [data]);

  const cards = [
    ["Itens cadastrados", data.items.length, "inventory"],
    ["Estoque crítico", summary.criticalStock.length, "warning"],
    ["Solicitações pendentes", summary.pendingMovements.length, "movement"],
    ["Plataformas em operação", summary.platformsInOperation.length, "platform"],
    ["Plataformas em manutenção", summary.platformsInMaintenance.length, "platform"],
    ["Sensores com alerta", summary.brokenSensors.length, "sensor"],
    ["Pendências offline", data.sync?.pending_actions ?? 0, "sync"],
    ["Conflitos offline", data.sync?.conflict_actions ?? 0, "sync"],
  ];

  return (
    <Stack spacing={2.5}>
      {error && <Alert severity="warning">Não foi possível carregar todos os indicadores.</Alert>}

      <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
        <Button startIcon={<AssignmentTurnedInIcon />} variant="contained" onClick={() => navigate("/app/movements/new")}>
          Solicitar saída
        </Button>
        <Button startIcon={<FactCheckIcon />} variant="outlined" onClick={() => navigate("/app/checklists/new")}>
          Novo checklist
        </Button>
        <Button startIcon={<SyncIcon />} variant="outlined" onClick={() => navigate("/app/sync")}>
          Sincronização
        </Button>
      </Stack>

      <Grid container spacing={2}>
        {cards.map(([label, value]) => (
          <Grid key={label} size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">{label}</Typography>
                <Typography variant="h4">{value}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Stack spacing={1.5}>
                <Typography variant="h6">Alertas críticos</Typography>
                {data.alerts.length === 0 && <Alert severity="success">Nenhum alerta ativo.</Alert>}
                {data.alerts.slice(0, 4).map((alert) => (
                  <Stack key={alert.id} direction="row" justifyContent="space-between" gap={1}>
                    <Typography>{alert.title}</Typography>
                    <StatusChip status={alert.severity} />
                  </Stack>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Stack spacing={1.5}>
                <Typography variant="h6">Estoque crítico</Typography>
                {summary.criticalStock.length === 0 && <Alert severity="success">Sem item abaixo do mínimo nacional.</Alert>}
                {summary.criticalStock.slice(0, 4).map((item) => (
                  <Stack key={item.id} direction="row" justifyContent="space-between" gap={1}>
                    <Stack>
                      <Typography>{item.name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {item.stock_total} {item.unit} de mínimo {item.minimum_stock_national}
                      </Typography>
                    </Stack>
                    <InventoryIcon color="warning" />
                  </Stack>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  );
}
