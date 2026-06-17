import AddIcon from "@mui/icons-material/Add";
import SearchIcon from "@mui/icons-material/Search";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Fab from "@mui/material/Fab";
import InputAdornment from "@mui/material/InputAdornment";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import LoadingState from "../components/LoadingState";
import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import { useAuth } from "../state/AuthContext";
import type { InventoryItem } from "../types";

type Filter = "todos" | "critico" | "consumable" | "permanent_component" | "avariado";

export default function InventoryListPage() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("todos");
  const navigate = useNavigate();
  const { hasPermission } = useAuth();

  useEffect(() => {
    inventoryService
      .listItems()
      .then((data) => setItems(data.items))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return items.filter((item) => {
      const matchesQuery =
        !normalized ||
        [item.name, item.brand, item.model, item.serial_number, item.patrimony_number, item.current_location_name]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(normalized));
      const isCritical = item.minimum_stock_national > 0 && item.stock_total < item.minimum_stock_national;
      const matchesFilter =
        filter === "todos" ||
        (filter === "critico" && isCritical) ||
        (filter === "avariado" && ["avariado", "inoperante", "manutencao"].includes(item.condition_status)) ||
        item.item_type === filter;
      return matchesQuery && matchesFilter;
    });
  }, [filter, items, query]);

  const filters: Array<[Filter, string]> = [
    ["todos", "Todos"],
    ["critico", "Crítico"],
    ["consumable", "Consumíveis"],
    ["permanent_component", "Permanentes"],
    ["avariado", "Avariados"],
  ];

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h5">Inventário</Typography>
        {hasPermission("inventory:item:create") && (
          <Button startIcon={<AddIcon />} variant="contained" onClick={() => navigate("/app/inventory/new")} sx={{ display: { xs: "none", sm: "inline-flex" } }}>
            Novo item
          </Button>
        )}
      </Stack>
      <TextField
        label="Buscar item, série, patrimônio ou local"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment> }}
      />
      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
        {filters.map(([value, label]) => (
          <Chip key={value} label={label} color={filter === value ? "primary" : "default"} onClick={() => setFilter(value)} />
        ))}
      </Stack>
      {loading && <LoadingState message="Carregando inventário..." />}
      {error && <Alert severity="error">Erro ao carregar inventário.</Alert>}
      {!loading && filtered.length === 0 && !error && <Alert severity="info">Nenhum item encontrado.</Alert>}
      <Stack spacing={1.5}>
        {filtered.map((item) => {
          const isCritical = item.minimum_stock_national > 0 && item.stock_total < item.minimum_stock_national;
          return (
            <Card key={item.id}>
              <CardActionArea onClick={() => navigate(`/app/inventory/${item.id}`)}>
                <CardContent>
                  <Stack spacing={1}>
                    <Stack direction="row" justifyContent="space-between" gap={1}>
                      <Box>
                        <Typography fontWeight={700}>{item.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {[item.brand, item.model, item.current_location_name].filter(Boolean).join(" • ")}
                        </Typography>
                      </Box>
                      <StatusChip status={item.condition_status} />
                    </Stack>
                    <Stack direction="row" spacing={1} alignItems="center" useFlexGap flexWrap="wrap">
                      <Typography variant="body2">
                        Saldo total: {item.stock_total} {item.unit}
                      </Typography>
                      {isCritical && <Chip size="small" color="warning" label={`Mínimo ${item.minimum_stock_national}`} />}
                      {item.serial_number && <Chip size="small" variant="outlined" label={`Série ${item.serial_number}`} />}
                    </Stack>
                  </Stack>
                </CardContent>
              </CardActionArea>
            </Card>
          );
        })}
      </Stack>
      {hasPermission("inventory:item:create") && (
        <Fab
          color="primary"
          onClick={() => navigate("/app/inventory/new")}
          sx={{ display: { xs: "flex", sm: "none" }, position: "fixed", bottom: 80, right: 16 }}
        >
          <AddIcon />
        </Fab>
      )}
    </Stack>
  );
}
