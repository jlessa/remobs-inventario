import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CircularProgress from "@mui/material/CircularProgress";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { inventoryService } from "../services/inventoryService";

export default function InventoryFormPage() {
  const navigate = useNavigate();
  const [error, setError] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    item_type: "consumable",
    name: "",
    brand: "",
    model: "",
    serial_number: "",
    patrimony_number: "",
    invoice_number: "",
    description: "",
    condition_status: "operacional",
    category_name: "Consumíveis",
    location_name: "Estoque",
    unit: "un",
    initial_quantity: "0",
    minimum_stock_national: "0",
    minimum_stock_import: "0",
    minimum_stock_maintenance: "0",
    ideal_stock: "0",
    reason: "Cadastro inicial.",
  });

  function update(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(false);
    try {
      const item = await inventoryService.createItem({
        item_type: form.item_type as "consumable" | "permanent_component",
        name: form.name,
        brand: form.brand || undefined,
        model: form.model || undefined,
        serial_number: form.serial_number || undefined,
        patrimony_number: form.patrimony_number || undefined,
        invoice_number: form.invoice_number || undefined,
        description: form.description || undefined,
        condition_status: form.condition_status,
        category_name: form.category_name,
        location_name: form.location_name,
        unit: form.unit,
        initial_quantity: Number(form.initial_quantity),
        minimum_stock_national: Number(form.minimum_stock_national),
        minimum_stock_import: Number(form.minimum_stock_import),
        minimum_stock_maintenance: Number(form.minimum_stock_maintenance),
        ideal_stock: Number(form.ideal_stock),
        reason: form.reason,
      });
      navigate(`/app/inventory/${item.id}`);
    } catch {
      setError(true);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card>
      <CardContent>
        <Stack component="form" spacing={2.5} onSubmit={handleSubmit}>
          <Typography variant="h5">Novo item</Typography>
          {error && <Alert severity="error">Não foi possível salvar o item.</Alert>}

          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField select fullWidth label="Tipo" value={form.item_type} onChange={(event) => update("item_type", event.target.value)}>
                <MenuItem value="consumable">Consumível</MenuItem>
                <MenuItem value="permanent_component">Componente permanente</MenuItem>
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Categoria" value={form.category_name} onChange={(event) => update("category_name", event.target.value)} required />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField fullWidth label="Nome" value={form.name} onChange={(event) => update("name", event.target.value)} required />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Marca" value={form.brand} onChange={(event) => update("brand", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Modelo" value={form.model} onChange={(event) => update("model", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Número de série" value={form.serial_number} onChange={(event) => update("serial_number", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Patrimônio" value={form.patrimony_number} onChange={(event) => update("patrimony_number", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Nota fiscal" value={form.invoice_number} onChange={(event) => update("invoice_number", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField select fullWidth label="Condição" value={form.condition_status} onChange={(event) => update("condition_status", event.target.value)}>
                <MenuItem value="operacional">Operacional</MenuItem>
                <MenuItem value="manutencao">Em manutenção</MenuItem>
                <MenuItem value="avariado">Avariado</MenuItem>
                <MenuItem value="reservado">Reservado</MenuItem>
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Local" value={form.location_name} onChange={(event) => update("location_name", event.target.value)} required />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField fullWidth label="Unidade" value={form.unit} onChange={(event) => update("unit", event.target.value)} required />
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <TextField fullWidth label="Quantidade inicial" type="number" value={form.initial_quantity} onChange={(event) => update("initial_quantity", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <TextField fullWidth label="Mínimo nacional" type="number" value={form.minimum_stock_national} onChange={(event) => update("minimum_stock_national", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <TextField fullWidth label="Mínimo importação" type="number" value={form.minimum_stock_import} onChange={(event) => update("minimum_stock_import", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <TextField fullWidth label="Estoque ideal" type="number" value={form.ideal_stock} onChange={(event) => update("ideal_stock", event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField fullWidth label="Descrição" value={form.description} onChange={(event) => update("description", event.target.value)} multiline minRows={2} />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField fullWidth label="Justificativa" value={form.reason} onChange={(event) => update("reason", event.target.value)} required multiline minRows={2} />
            </Grid>
          </Grid>

          <Button
            type="submit"
            variant="contained"
            disabled={submitting}
            startIcon={submitting ? <CircularProgress size={18} color="inherit" /> : undefined}
          >
            {submitting ? "Salvando..." : "Salvar item"}
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}
