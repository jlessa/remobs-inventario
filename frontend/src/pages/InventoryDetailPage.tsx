import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import AssignmentTurnedInIcon from "@mui/icons-material/AssignmentTurnedIn";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import LoadingState from "../components/LoadingState";
import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import type { InventoryItem, ItemHistory } from "../types";

export default function InventoryDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [item, setItem] = useState<InventoryItem | null>(null);
  const [history, setHistory] = useState<ItemHistory | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!id) return;
    Promise.all([inventoryService.getItem(id), inventoryService.getItemHistory(id)])
      .then(([itemData, historyData]) => {
        setItem(itemData);
        setHistory(historyData);
      })
      .catch(() => setError(true));
  }, [id]);

  if (error) return <Alert severity="error">Erro ao carregar item.</Alert>;
  if (!item) return <LoadingState message="Carregando item..." />;

  return (
    <Stack spacing={2}>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/app/inventory")} sx={{ alignSelf: "flex-start" }}>
        Inventário
      </Button>

      <Card>
        <CardContent>
          <Stack spacing={1}>
            <Stack direction="row" justifyContent="space-between" gap={1}>
              <Typography variant="h5">{item.name}</Typography>
              <StatusChip status={item.condition_status} />
            </Stack>
            <Typography color="text.secondary">{[item.brand, item.model, item.category_name].filter(Boolean).join(" • ")}</Typography>
            <Typography>
              Saldo total: {item.stock_total} {item.unit}
            </Typography>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
              <Button startIcon={<AssignmentTurnedInIcon />} variant="contained" onClick={() => navigate("/app/movements/new", { state: { itemId: item.id } })}>
                Solicitar saída
              </Button>
              <Button variant="outlined">Anexar foto</Button>
              <Button variant="outlined">Anexar documento</Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6">Identificação</Typography>
              <List dense>
                <ListItem disableGutters>
                  <ListItemText primary="Número de série" secondary={item.serial_number || "Não informado"} />
                </ListItem>
                <ListItem disableGutters>
                  <ListItemText primary="Patrimônio" secondary={item.patrimony_number || "Não informado"} />
                </ListItem>
                <ListItem disableGutters>
                  <ListItemText primary="Nota fiscal" secondary={item.invoice_number || "Não informado"} />
                </ListItem>
                <ListItem disableGutters>
                  <ListItemText primary="Descrição" secondary={item.description || "Sem descrição"} />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6">Saldos por local</Typography>
              <List dense>
                {item.balances.map((balance) => (
                  <ListItem key={balance.id} disableGutters>
                    <ListItemText primary={balance.location_name} secondary={`${balance.quantity} ${item.unit} (${balance.reserved_quantity} reservado)`} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Stack spacing={1}>
            <Typography variant="h6">Histórico</Typography>
            {!history && <Alert severity="info">Histórico não carregado.</Alert>}
            {history?.movements.length === 0 && history.audit_logs.length === 0 && <Alert severity="info">Sem histórico para este item.</Alert>}
            {history?.movements.slice(0, 5).map((movement) => (
              <Stack key={movement.id} direction="row" justifyContent="space-between" gap={1}>
                <Typography>
                  {movement.quantity} {item.unit} de {movement.from_location_name || "origem"} para {movement.to_location_name || "destino"}
                </Typography>
                <StatusChip status={movement.status} />
              </Stack>
            ))}
            {history?.audit_logs.slice(0, 5).map((log) => (
              <Typography key={log.id} variant="body2" color="text.secondary">
                {new Date(log.occurred_at).toLocaleString("pt-BR")} • {log.action} • {log.actor_username || "Sistema"}
              </Typography>
            ))}
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  );
}
