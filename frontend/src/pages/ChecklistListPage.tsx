import AddIcon from "@mui/icons-material/Add";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import LinearProgress from "@mui/material/LinearProgress";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import type { Checklist } from "../types";

export default function ChecklistListPage() {
  const [items, setItems] = useState<Checklist[]>([]);
  const [error, setError] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    inventoryService
      .listChecklists()
      .then((data) => setItems(data.items))
      .catch(() => setError(true));
  }, []);

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h5">Checklists</Typography>
        <Button startIcon={<AddIcon />} variant="contained" onClick={() => navigate("/app/checklists/new")}>
          Novo checklist
        </Button>
      </Stack>
      {error && <Alert severity="error">Erro ao carregar checklists.</Alert>}
      {items.length === 0 && !error && <Alert severity="info">Nenhum checklist encontrado.</Alert>}
      {items.map((item) => {
        const progress = Math.round((item.current_step / item.total_steps) * 100);
        return (
          <Card key={item.id}>
            <CardActionArea onClick={() => navigate(`/app/checklists/${item.id}`)}>
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
          </Card>
        );
      })}
    </Stack>
  );
}
