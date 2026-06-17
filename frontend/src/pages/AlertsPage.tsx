import Alert from "@mui/material/Alert";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";

import LoadingState from "../components/LoadingState";
import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import type { AlertItem } from "../types";

export default function AlertsPage() {
  const [items, setItems] = useState<AlertItem[]>([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    inventoryService
      .listAlerts()
      .then((data) => setItems(data.items))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Stack spacing={2}>
      <Typography variant="h5">Alertas</Typography>
      {loading && <LoadingState message="Carregando alertas..." />}
      {error && <Alert severity="error">Erro ao carregar alertas.</Alert>}
      {!loading && items.length === 0 && !error && <Alert severity="success">Nenhum alerta ativo.</Alert>}
      {items.map((item) => (
        <Card key={item.id}>
          <CardContent>
            <Stack spacing={1}>
              <Stack direction="row" justifyContent="space-between" gap={1}>
                <Typography fontWeight={700}>{item.title}</Typography>
                <StatusChip status={item.severity} />
              </Stack>
              <Typography color="text.secondary">{item.message}</Typography>
            </Stack>
          </CardContent>
        </Card>
      ))}
    </Stack>
  );
}
