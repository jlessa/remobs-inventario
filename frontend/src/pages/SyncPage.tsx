import RefreshIcon from "@mui/icons-material/Refresh";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";

import LoadingState from "../components/LoadingState";
import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import type { SyncConflict, SyncStatus } from "../types";

export default function SyncPage() {
  const [status, setStatus] = useState<SyncStatus | null>(null);
  const [conflicts, setConflicts] = useState<SyncConflict[]>([]);
  const [error, setError] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    setError(false);
    Promise.all([
      inventoryService.getSyncStatus(),
      inventoryService.listSyncConflicts().catch(() => ({ items: [], total: 0 })),
    ])
      .then(([syncStatus, conflictList]) => {
        setStatus(syncStatus);
        setConflicts(conflictList.items);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function resolve(conflict: SyncConflict, decision: "adjust" | "discard" | "send_to_admin") {
    setError(false);
    try {
      await inventoryService.resolveSyncConflict({
        client_action_id: conflict.client_action_id,
        decision,
        reason: "Decisão registrada na tela de sincronização.",
      });
      setMessage("Conflito atualizado.");
      load();
    } catch {
      setError(true);
    }
  }

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h5">Sincronização</Typography>
        <Button startIcon={<RefreshIcon />} variant="contained" onClick={load}>
          Atualizar
        </Button>
      </Stack>
      {error && <Alert severity="warning">Não foi possível consultar o estado de sincronização.</Alert>}
      {message && <Alert severity="success">{message}</Alert>}
      {loading && <LoadingState message="Carregando sincronização..." />}
      {!loading && (
        <>
      <Card>
        <CardContent>
          <Stack spacing={1.5}>
            <Stack direction="row" justifyContent="space-between" gap={1}>
              <Typography>Pendências offline</Typography>
              <Typography fontWeight={700}>{status?.pending_actions ?? 0}</Typography>
            </Stack>
            <Stack direction="row" justifyContent="space-between" gap={1}>
              <Typography>Conflitos offline</Typography>
              <Typography fontWeight={700}>{status?.conflict_actions ?? conflicts.length}</Typography>
            </Stack>
            <Typography color="text.secondary">
              Servidor: {status?.server_time ? new Date(status.server_time).toLocaleString("pt-BR") : "não consultado"}
            </Typography>
          </Stack>
        </CardContent>
      </Card>

      <Stack spacing={1.5}>
        <Typography variant="h6">Conflitos para revisão</Typography>
        {conflicts.length === 0 && <Alert severity="success">Nenhum conflito offline pendente.</Alert>}
        {conflicts.map((conflict) => (
          <Card key={conflict.id}>
            <CardContent>
              <Stack spacing={1.5}>
                <Stack direction="row" justifyContent="space-between" gap={1}>
                  <Typography fontWeight={700}>{conflict.action_type}</Typography>
                  <StatusChip status={conflict.status} />
                </Stack>
                <Typography color="text.secondary">{conflict.error_message || "Conflito detectado durante sincronização."}</Typography>
                <Typography variant="body2">{JSON.stringify(conflict.payload)}</Typography>
                <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                  <Button variant="outlined" onClick={() => resolve(conflict, "adjust")}>
                    Ajustar solicitação
                  </Button>
                  <Button variant="outlined" color="error" onClick={() => resolve(conflict, "discard")}>
                    Descartar
                  </Button>
                  <Button variant="contained" onClick={() => resolve(conflict, "send_to_admin")}>
                    Enviar para revisão
                  </Button>
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        ))}
      </Stack>
        </>
      )}
    </Stack>
  );
}
