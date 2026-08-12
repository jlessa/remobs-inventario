import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/DeleteOutline";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Fab from "@mui/material/Fab";
import FormControlLabel from "@mui/material/FormControlLabel";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import LoadingState from "../components/LoadingState";
import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import { useAuth } from "../state/AuthContext";
import { useSnackbar } from "../state/SnackbarContext";
import type { Platform } from "../types";

export default function PlatformsPage() {
  const [items, setItems] = useState<Platform[]>([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [activeOnly, setActiveOnly] = useState(true);
  const navigate = useNavigate();
  const { hasAnyPermission } = useAuth();
  const { showSuccess, showError } = useSnackbar();
  const canCreate = hasAnyPermission("platform:create", "platform:update");
  const canDelete = hasAnyPermission("platform:delete", "platform:update");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);
    inventoryService
      .listPlatforms({ activeOnly })
      .then((data) => {
        if (!cancelled) {
          setItems(data.items);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError(true);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [activeOnly]);

  async function handleDelete(item: Platform) {
    const confirmed = window.confirm(`Excluir a plataforma "${item.name}"? Esta ação remove a plataforma da listagem.`);
    if (!confirmed) {
      return;
    }

    setDeletingId(item.id);
    try {
      await inventoryService.deletePlatform(item.id, "Exclusão pela listagem de plataformas.");
      setItems((current) => current.filter((entry) => entry.id !== item.id));
      showSuccess(`Plataforma "${item.name}" excluída com sucesso.`);
    } catch {
      showError(`Não foi possível excluir a plataforma "${item.name}".`);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" useFlexGap flexWrap="wrap" gap={1}>
        <Typography variant="h5">Plataformas</Typography>
        {canCreate && (
          <Button startIcon={<AddIcon />} variant="contained" onClick={() => navigate("/app/platforms/new")} sx={{ display: { xs: "none", sm: "inline-flex" } }}>
            Nova plataforma
          </Button>
        )}
      </Stack>
      <FormControlLabel
        control={
          <Switch
            checked={activeOnly}
            onChange={(event) => setActiveOnly(event.target.checked)}
            inputProps={{ "aria-label": "Somente ativas" }}
          />
        }
        label="Somente ativas"
      />
      {loading && <LoadingState message="Carregando plataformas..." />}
      {error && <Alert severity="error">Erro ao carregar plataformas.</Alert>}
      {!loading && items.length === 0 && !error && (
        <Alert severity="info">
          {activeOnly ? "Nenhuma plataforma ativa encontrada. Desmarque \"Somente ativas\" para ver as inativas." : "Nenhuma plataforma cadastrada."}
        </Alert>
      )}
      {items.map((item) => (
        <Card key={item.id}>
          <Stack direction="row" alignItems="stretch">
            <CardActionArea onClick={() => navigate(`/app/platforms/${item.id}`)} sx={{ flex: 1 }}>
              <CardContent>
                <Stack spacing={1}>
                  <Stack direction="row" justifyContent="space-between" gap={1}>
                    <Typography fontWeight={700}>{item.name}</Typography>
                    <StatusChip status={item.operational_status} />
                  </Stack>
                  <Typography color="text.secondary">{[item.platform_type, item.model].filter(Boolean).join(" • ")}</Typography>
                  {item.description && (
                    <Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>
                      {item.description.split("\n").slice(0, 4).join("\n")}
                    </Typography>
                  )}
                </Stack>
              </CardContent>
            </CardActionArea>
            {canDelete && (
              <Box sx={{ display: "flex", alignItems: "center", pr: 1 }}>
                <IconButton
                  aria-label={`Excluir plataforma ${item.name}`}
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
          aria-label="Cadastrar plataforma"
          color="primary"
          onClick={() => navigate("/app/platforms/new")}
          sx={{ display: { xs: "flex", sm: "none" }, position: "fixed", bottom: 80, right: 16 }}
        >
          <AddIcon />
        </Fab>
      )}
    </Stack>
  );
}
