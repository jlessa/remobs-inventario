import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/DeleteOutline";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import IconButton from "@mui/material/IconButton";
import LinearProgress from "@mui/material/LinearProgress";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import LoadingState from "../components/LoadingState";
import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import { useAuth } from "../state/AuthContext";
import { useSnackbar } from "../state/SnackbarContext";
import type { Checklist } from "../types";

export default function ChecklistListPage() {
  const [items, setItems] = useState<Checklist[]>([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const navigate = useNavigate();
  const { hasAnyPermission } = useAuth();
  const { showSuccess, showError } = useSnackbar();
  const canCreate = hasAnyPermission("checklist:create", "checklist:submit");
  const canDelete = hasAnyPermission("checklist:delete", "checklist:submit");

  useEffect(() => {
    inventoryService
      .listChecklists()
      .then((data) => setItems(data.items))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  async function handleDelete(item: Checklist) {
    const confirmed = window.confirm(`Excluir o checklist "${item.title}"? Esta ação remove o registro permanentemente.`);
    if (!confirmed) {
      return;
    }

    setDeletingId(item.id);
    try {
      await inventoryService.deleteChecklist(item.id, "Exclusão pela listagem de checklists.");
      setItems((current) => current.filter((entry) => entry.id !== item.id));
      showSuccess(`Checklist "${item.title}" excluído com sucesso.`);
    } catch {
      showError(`Não foi possível excluir o checklist "${item.title}".`);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h5">Checklists</Typography>
        {canCreate && (
          <Button startIcon={<AddIcon />} variant="contained" onClick={() => navigate("/app/checklists/new")}>
            Novo checklist
          </Button>
        )}
      </Stack>
      {loading && <LoadingState message="Carregando checklists..." />}
      {error && <Alert severity="error">Erro ao carregar checklists.</Alert>}
      {!loading && items.length === 0 && !error && <Alert severity="info">Nenhum checklist encontrado.</Alert>}
      {items.map((item) => {
        const progress = Math.round((item.current_step / item.total_steps) * 100);
        return (
          <Card key={item.id}>
            <Stack direction="row" alignItems="stretch">
              <CardActionArea onClick={() => navigate(`/app/checklists/${item.id}`)} sx={{ flex: 1 }}>
                <CardContent>
                  <Stack spacing={1}>
                    <Stack direction="row" justifyContent="space-between" gap={1}>
                      <Typography fontWeight={700}>{item.title}</Typography>
                      <StatusChip status={item.status} />
                    </Stack>
                    <Typography color="text.secondary">{[item.template_name, item.platform_name].filter(Boolean).join(" • ")}</Typography>
                    <LinearProgress variant="determinate" value={progress} />
                    <Typography variant="body2">
                      Etapa {item.current_step} de {item.total_steps}
                    </Typography>
                  </Stack>
                </CardContent>
              </CardActionArea>
              {canDelete && (
                <Box sx={{ display: "flex", alignItems: "center", pr: 1 }}>
                  <IconButton
                    aria-label={`Excluir checklist ${item.title}`}
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
        );
      })}
    </Stack>
  );
}
