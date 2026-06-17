import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import LoadingState from "../components/LoadingState";
import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import { useAuth } from "../state/AuthContext";
import type { Movement } from "../types";

export default function MovementsPage() {
  const [items, setItems] = useState<Movement[]>([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { hasPermission } = useAuth();

  function load() {
    inventoryService
      .listMovements()
      .then((data) => setItems(data.items))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function decide(id: string, action: "approve" | "reject") {
    const reason = action === "approve" ? "Decisão autorizada pelo painel." : "Decisão reprovada pelo painel.";
    if (action === "approve") await inventoryService.approveMovement(id, reason);
    if (action === "reject") await inventoryService.rejectMovement(id, reason);
    load();
  }

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h5">Operação</Typography>
        {hasPermission("inventory:movement:request") && (
          <Button variant="contained" onClick={() => navigate("/app/movements/new")}>
            Solicitar saída
          </Button>
        )}
      </Stack>
      {loading && <LoadingState message="Carregando movimentações..." />}
      {error && <Alert severity="error">Erro ao carregar movimentações.</Alert>}
      {!loading && items.length === 0 && !error && <Alert severity="info">Nenhuma movimentação registrada.</Alert>}
      {items.map((movement) => (
        <Card key={movement.id}>
          <CardContent>
            <Stack spacing={1}>
              <Stack direction="row" justifyContent="space-between" gap={1}>
                <Typography fontWeight={700}>{movement.quantity} item(ns)</Typography>
                <StatusChip status={movement.status} />
              </Stack>
              <Typography variant="body2" color="text.secondary">
                {movement.from_location_name} → {movement.to_location_name}
              </Typography>
              <Typography variant="body2">Solicitado por {movement.requested_by_username}</Typography>
              {movement.status === "pending" && hasPermission("inventory:movement:approve") && (
                <Stack direction="row" spacing={1}>
                  <Button variant="contained" onClick={() => decide(movement.id, "approve")}>Aprovar</Button>
                  <Button variant="outlined" color="error" onClick={() => decide(movement.id, "reject")}>Reprovar</Button>
                </Stack>
              )}
            </Stack>
          </CardContent>
        </Card>
      ))}
    </Stack>
  );
}
