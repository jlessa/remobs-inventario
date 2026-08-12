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
import type { InventoryLocation } from "../types";

export default function LocationsPage() {
  const [items, setItems] = useState<InventoryLocation[]>([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [activeOnly, setActiveOnly] = useState(true);
  const navigate = useNavigate();
  const { hasAnyPermission } = useAuth();
  const { showSuccess, showError } = useSnackbar();
  const canCreate = hasAnyPermission("location:create", "location:update");
  const canDelete = hasAnyPermission("location:delete", "location:update");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);
    inventoryService
      .listLocations({ activeOnly })
      .then((data) => {
        if (!cancelled) setItems(data.items);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [activeOnly]);

  async function handleDelete(item: InventoryLocation) {
    const confirmed = window.confirm(`Inativar o local "${item.name}"? Ele deixa de aparecer nas listas ativas.`);
    if (!confirmed) return;

    setDeletingId(item.id);
    try {
      await inventoryService.deleteLocation(item.id, "Exclusão pela listagem de locais.");
      setItems((current) => current.filter((entry) => entry.id !== item.id));
      showSuccess(`Local "${item.name}" inativado com sucesso.`);
    } catch {
      showError(`Não foi possível inativar o local "${item.name}".`);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" useFlexGap flexWrap="wrap" gap={1}>
        <Typography variant="h5">Locais</Typography>
        {canCreate && (
          <Button startIcon={<AddIcon />} variant="contained" onClick={() => navigate("/app/locations/new")} sx={{ display: { xs: "none", sm: "inline-flex" } }}>
            Novo local
          </Button>
        )}
      </Stack>
      <FormControlLabel
        control={
          <Switch
            checked={activeOnly}
            onChange={(event) => setActiveOnly(event.target.checked)}
            inputProps={{ "aria-label": "Somente ativos" }}
          />
        }
        label="Somente ativos"
      />
      {loading && <LoadingState message="Carregando locais..." />}
      {error && <Alert severity="error">Erro ao carregar locais.</Alert>}
      {!loading && items.length === 0 && !error && (
        <Alert severity="info">
          {activeOnly ? "Nenhum local ativo encontrado. Desmarque \"Somente ativos\" para ver os inativos." : "Nenhum local cadastrado."}
        </Alert>
      )}
      {items.map((item) => (
        <Card key={item.id}>
          <Stack direction="row" alignItems="stretch">
            <CardActionArea onClick={() => navigate(`/app/locations/${item.id}/edit`)} sx={{ flex: 1 }}>
              <CardContent>
                <Stack spacing={1}>
                  <Stack direction="row" justifyContent="space-between" gap={1}>
                    <Typography fontWeight={700}>{item.name}</Typography>
                    <StatusChip status={item.is_active ? "ativo" : "inativo"} />
                  </Stack>
                  <Typography color="text.secondary">{item.location_type}</Typography>
                </Stack>
              </CardContent>
            </CardActionArea>
            {canDelete && item.is_active && (
              <Box sx={{ display: "flex", alignItems: "center", pr: 1 }}>
                <IconButton
                  aria-label={`Excluir local ${item.name}`}
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
          aria-label="Cadastrar local"
          color="primary"
          onClick={() => navigate("/app/locations/new")}
          sx={{ display: { xs: "flex", sm: "none" }, position: "fixed", bottom: 80, right: 16 }}
        >
          <AddIcon />
        </Fab>
      )}
    </Stack>
  );
}
