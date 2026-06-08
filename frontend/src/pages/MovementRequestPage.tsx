import AddIcon from "@mui/icons-material/Add";
import RemoveIcon from "@mui/icons-material/Remove";
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

import { inventoryService } from "../services/inventoryService";
import type { InventoryItem, StockBalance } from "../types";

const draftKey = "remobs_movement_request_draft";

interface DraftState {
  itemId: string;
  fromLocationId: string;
  quantity: string;
  destination: string;
  reason: string;
  evidenceNote: string;
}

const defaultDraft: DraftState = {
  itemId: "",
  fromLocationId: "",
  quantity: "1",
  destination: "Campo",
  reason: "Uso em operação de campo.",
  evidenceNote: "",
};

export default function MovementRequestPage() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [draft, setDraft] = useState<DraftState>(() => {
    const saved = localStorage.getItem(draftKey);
    return saved ? { ...defaultDraft, ...JSON.parse(saved) } : defaultDraft;
  });
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const stateItemId = (location.state as { itemId?: string } | null)?.itemId;

  useEffect(() => {
    inventoryService.listItems().then((data) => {
      setItems(data.items);
      const preferredItemId = stateItemId || draft.itemId || data.items[0]?.id || "";
      const preferredItem = data.items.find((item) => item.id === preferredItemId) || data.items[0];
      setDraft((current) => ({
        ...current,
        itemId: preferredItem?.id || "",
        fromLocationId: current.fromLocationId || preferredItem?.balances[0]?.location_id || "",
      }));
    });
  }, [draft.itemId, stateItemId]);

  useEffect(() => {
    localStorage.setItem(draftKey, JSON.stringify(draft));
  }, [draft]);

  const selected = useMemo(() => items.find((item) => item.id === draft.itemId), [draft.itemId, items]);
  const selectedBalance = useMemo<StockBalance | undefined>(
    () => selected?.balances.find((balance) => balance.location_id === draft.fromLocationId),
    [draft.fromLocationId, selected],
  );
  const quantity = Number(draft.quantity);
  const available = selectedBalance ? selectedBalance.quantity - selectedBalance.reserved_quantity : 0;
  const validationError =
    !selected ? "Selecione um item." :
    !selectedBalance ? "Selecione uma origem." :
    quantity <= 0 ? "Informe quantidade maior que zero." :
    quantity > available ? "Quantidade maior que o estoque disponível." :
    draft.reason.trim().length < 3 ? "Informe o motivo da saída." :
    null;

  function update(field: keyof DraftState, value: string) {
    setDraft((current) => ({ ...current, [field]: value }));
    setSaved(false);
  }

  async function sendRequest() {
    if (!selected || !selectedBalance || validationError) return;
    setError(false);
    try {
      await inventoryService.requestMovement({
        item_id: selected.id,
        quantity,
        from_location_id: selectedBalance.location_id,
        to_location_name: draft.destination,
        reason: [draft.reason, draft.evidenceNote && `Evidência: ${draft.evidenceNote}`].filter(Boolean).join("\n"),
      });
      localStorage.removeItem(draftKey);
      navigate("/app/movements");
    } catch {
      setError(true);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!validationError) setConfirmOpen(true);
  }

  return (
    <>
      <Card>
        <CardContent>
          <Stack component="form" spacing={2} onSubmit={handleSubmit}>
            <Typography variant="h5">Solicitar saída</Typography>
            {error && <Alert severity="error">Não foi possível solicitar a saída.</Alert>}
            {saved && <Alert severity="success">Rascunho salvo neste dispositivo.</Alert>}
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
                  fromLocationId: item?.balances[0]?.location_id || "",
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
            <TextField select label="Origem" value={draft.fromLocationId} onChange={(event) => update("fromLocationId", event.target.value)} required>
              {selected?.balances.map((balance) => (
                <MenuItem key={balance.id} value={balance.location_id}>
                  {balance.location_name} ({balance.quantity - balance.reserved_quantity} disponível)
                </MenuItem>
              ))}
            </TextField>
            <Stack direction="row" spacing={1} alignItems="center">
              <IconButton onClick={() => update("quantity", String(Math.max(1, quantity - 1)))}>
                <RemoveIcon />
              </IconButton>
              <TextField label="Quantidade" type="number" value={draft.quantity} onChange={(event) => update("quantity", event.target.value)} required />
              <IconButton onClick={() => update("quantity", String(quantity + 1))}>
                <AddIcon />
              </IconButton>
            </Stack>
            <TextField label="Destino" value={draft.destination} onChange={(event) => update("destination", event.target.value)} required />
            <TextField label="Justificativa" value={draft.reason} onChange={(event) => update("reason", event.target.value)} multiline minRows={2} required />
            <TextField label="Evidência ou foto registrada" value={draft.evidenceNote} onChange={(event) => update("evidenceNote", event.target.value)} multiline minRows={2} />
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
              <Button
                variant="outlined"
                onClick={() => {
                  localStorage.setItem(draftKey, JSON.stringify(draft));
                  setSaved(true);
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
