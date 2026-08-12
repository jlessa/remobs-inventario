import AddIcon from "@mui/icons-material/Add";
import RemoveIcon from "@mui/icons-material/Remove";
import Autocomplete from "@mui/material/Autocomplete";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import IconButton from "@mui/material/IconButton";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import LoadingState from "../components/LoadingState";
import { inventoryService } from "../services/inventoryService";
import { useSnackbar } from "../state/SnackbarContext";
import type { InventoryItem, InventoryLocation, StockBalance } from "../types";

const draftKey = "remobs_movement_request_draft";

interface DraftState {
  itemId: string;
  fromLocationId: string;
  quantity: string;
  destination: string;
  toLocationId: string;
  reason: string;
  evidenceNote: string;
}

const defaultDraft: DraftState = {
  itemId: "",
  fromLocationId: "",
  quantity: "1",
  destination: "Campo",
  toLocationId: "",
  reason: "Uso em operação de campo.",
  evidenceNote: "",
};

function availableQty(balance: StockBalance): number {
  return balance.quantity - balance.reserved_quantity;
}

function availableAtLocation(item: InventoryItem | undefined | null, locationId: string): number {
  const balance = item?.balances.find((entry) => entry.location_id === locationId);
  return balance ? availableQty(balance) : 0;
}

/** Prefere o Local cadastrado no item; senão o primeiro saldo com estoque. */
export function resolveOriginLocationId(item: InventoryItem | undefined | null): string {
  if (item?.current_location_id) return item.current_location_id;

  const withStock = item?.balances.find((balance) => availableQty(balance) > 0);
  if (withStock) return withStock.location_id;

  return item?.balances[0]?.location_id || "";
}

export function originLocationOptions(
  locations: InventoryLocation[],
  item: InventoryItem | undefined | null,
): InventoryLocation[] {
  const options = [...locations];
  if (item?.current_location_id && !options.some((entry) => entry.id === item.current_location_id)) {
    options.unshift({
      id: item.current_location_id,
      name: item.current_location_name || "Local atual",
      location_type: "estoque",
      is_active: true,
      created_at: item.updated_at || item.created_at || "",
    });
  }
  return options;
}

export default function MovementRequestPage() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [locations, setLocations] = useState<InventoryLocation[]>([]);
  const [draft, setDraft] = useState<DraftState>(() => {
    const saved = localStorage.getItem(draftKey);
    return saved ? { ...defaultDraft, ...JSON.parse(saved) } : defaultDraft;
  });
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [loadingItems, setLoadingItems] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  const { showSuccess, showError, showInfo } = useSnackbar();
  const stateItemId = (location.state as { itemId?: string } | null)?.itemId;

  useEffect(() => {
    Promise.all([
      inventoryService.listItems(),
      inventoryService.listLocations({ activeOnly: true }),
      stateItemId ? inventoryService.getItem(stateItemId).catch(() => null) : Promise.resolve(null),
    ])
      .then(([itemsData, locationsData, detailedItem]) => {
        const mergedItems =
          detailedItem && !itemsData.items.some((item) => item.id === detailedItem.id)
            ? [detailedItem, ...itemsData.items]
            : itemsData.items;
        setItems(mergedItems);
        setLocations(locationsData.items);
        const preferredItemId = detailedItem?.id || stateItemId || draft.itemId || mergedItems[0]?.id || "";
        const preferredItem =
          detailedItem || mergedItems.find((item) => item.id === preferredItemId) || mergedItems[0];
        setDraft((current) => {
          const itemChanged = Boolean(stateItemId) || current.itemId !== (preferredItem?.id || "");
          const nextItemId = preferredItem?.id || "";
          const nextOrigin =
            itemChanged || !current.fromLocationId
              ? resolveOriginLocationId(preferredItem)
              : current.fromLocationId;
          const matchedDestination =
            locationsData.items.find(
              (entry) => entry.name.toLowerCase() === (current.destination || "").trim().toLowerCase(),
            ) || null;
          return {
            ...current,
            itemId: nextItemId,
            fromLocationId: nextOrigin,
            toLocationId: matchedDestination?.id || current.toLocationId || "",
            destination: matchedDestination?.name || current.destination,
          };
        });
      })
      .catch(() => undefined)
      .finally(() => setLoadingItems(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stateItemId]);

  useEffect(() => {
    localStorage.setItem(draftKey, JSON.stringify(draft));
  }, [draft]);

  const selected = useMemo(() => items.find((item) => item.id === draft.itemId), [draft.itemId, items]);
  const originOptions = useMemo(() => originLocationOptions(locations, selected), [locations, selected]);
  const selectedOrigin = useMemo(
    () => originOptions.find((entry) => entry.id === draft.fromLocationId) || null,
    [draft.fromLocationId, originOptions],
  );
  const available = availableAtLocation(selected, draft.fromLocationId);
  const selectedDestination = useMemo(() => {
    if (draft.toLocationId) {
      return locations.find((entry) => entry.id === draft.toLocationId) || null;
    }
    return locations.find((entry) => entry.name.toLowerCase() === draft.destination.trim().toLowerCase()) || null;
  }, [draft.destination, draft.toLocationId, locations]);

  const quantity = Number(draft.quantity);
  const validationError =
    !selected ? "Selecione um item." :
    !draft.fromLocationId ? "Selecione uma origem." :
    quantity <= 0 ? "Informe quantidade maior que zero." :
    quantity > available ? "Quantidade maior que o estoque disponível." :
    draft.destination.trim().length < 1 ? "Informe o destino." :
    draft.reason.trim().length < 3 ? "Informe o motivo da saída." :
    null;

  function update(field: keyof DraftState, value: string) {
    setDraft((current) => ({ ...current, [field]: value }));
  }

  async function sendRequest() {
    if (!selected || !draft.fromLocationId || validationError) return;
    try {
      await inventoryService.requestMovement({
        item_id: selected.id,
        quantity,
        from_location_id: draft.fromLocationId,
        ...(draft.toLocationId
          ? { to_location_id: draft.toLocationId }
          : { to_location_name: draft.destination.trim() }),
        reason: [draft.reason, draft.evidenceNote && `Evidência: ${draft.evidenceNote}`].filter(Boolean).join("\n"),
      });
      localStorage.removeItem(draftKey);
      showSuccess("Solicitação de saída registrada.");
      navigate("/app/movements");
    } catch {
      showError("Não foi possível solicitar a saída.");
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!validationError) setConfirmOpen(true);
  }

  if (loadingItems) return <LoadingState message="Carregando itens..." />;

  return (
    <>
      <Card>
        <CardContent>
          <Stack component="form" spacing={2} onSubmit={handleSubmit}>
            <Typography variant="h5">Solicitar saída</Typography>
            {validationError && <Alert severity="warning">{validationError}</Alert>}
            <TextField
              select
              label="Item"
              value={draft.itemId}
              onChange={(event) => {
                const item = items.find((candidate) => candidate.id === event.target.value);
                setDraft((current) => ({
                  ...current,
                  itemId: event.target.value,
                  fromLocationId: resolveOriginLocationId(item),
                }));
              }}
              required
            >
              {items.map((item) => (
                <MenuItem key={item.id} value={item.id}>
                  {item.name} ({item.stock_total} {item.unit})
                </MenuItem>
              ))}
            </TextField>
            <Autocomplete
              options={originOptions}
              value={selectedOrigin}
              getOptionLabel={(option) => `${option.name} (${availableAtLocation(selected, option.id)} disponível)`}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              onChange={(_event, value) => update("fromLocationId", value?.id || "")}
              renderInput={(params) => <TextField {...params} label="Origem" required />}
            />
            <Stack direction="row" spacing={1} alignItems="center">
              <IconButton onClick={() => update("quantity", String(Math.max(1, quantity - 1)))}>
                <RemoveIcon />
              </IconButton>
              <TextField label="Quantidade" type="number" value={draft.quantity} onChange={(event) => update("quantity", event.target.value)} required />
              <IconButton onClick={() => update("quantity", String(quantity + 1))}>
                <AddIcon />
              </IconButton>
            </Stack>
            <Autocomplete
              freeSolo
              options={locations}
              value={selectedDestination}
              inputValue={draft.destination}
              getOptionLabel={(option) => (typeof option === "string" ? option : option.name)}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              onChange={(_event, value) => {
                if (typeof value === "string") {
                  setDraft((current) => ({ ...current, destination: value, toLocationId: "" }));
                  return;
                }
                if (value) {
                  setDraft((current) => ({
                    ...current,
                    destination: value.name,
                    toLocationId: value.id,
                  }));
                  return;
                }
                setDraft((current) => ({ ...current, destination: "", toLocationId: "" }));
              }}
              onInputChange={(_event, value, reason) => {
                if (reason === "input" || reason === "clear") {
                  const match = locations.find((entry) => entry.name.toLowerCase() === value.trim().toLowerCase());
                  setDraft((current) => ({
                    ...current,
                    destination: value,
                    toLocationId: match?.id || "",
                  }));
                }
              }}
              renderInput={(params) => <TextField {...params} label="Destino" required />}
            />
            <TextField label="Justificativa" value={draft.reason} onChange={(event) => update("reason", event.target.value)} multiline minRows={2} required />
            <TextField label="Evidência ou foto registrada" value={draft.evidenceNote} onChange={(event) => update("evidenceNote", event.target.value)} multiline minRows={2} />
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
              <Button
                variant="outlined"
                onClick={() => {
                  localStorage.setItem(draftKey, JSON.stringify(draft));
                  showInfo("Rascunho salvo neste dispositivo.");
                }}
              >
                Salvar rascunho
              </Button>
              <Button type="submit" variant="contained" disabled={Boolean(validationError)}>
                Enviar solicitação
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      <Dialog open={confirmOpen} onClose={() => setConfirmOpen(false)} fullWidth>
        <DialogTitle>Confirmar saída</DialogTitle>
        <DialogContent>
          <Typography>
            Solicitar {quantity} {selected?.unit} de {selected?.name} para {draft.destination}?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmOpen(false)}>Cancelar</Button>
          <Button variant="contained" onClick={sendRequest}>
            Confirmar
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
