import Alert from "@mui/material/Alert";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import type { Platform } from "../types";

export default function PlatformsPage() {
  const [items, setItems] = useState<Platform[]>([]);
  const [error, setError] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    inventoryService
      .listPlatforms()
      .then((data) => setItems(data.items))
      .catch(() => setError(true));
  }, []);

  return (
    <Stack spacing={2}>
      <Typography variant="h5">Plataformas</Typography>
      {error && <Alert severity="error">Erro ao carregar plataformas.</Alert>}
      {items.length === 0 && !error && <Alert severity="info">Nenhuma plataforma cadastrada.</Alert>}
      {items.map((item) => (
        <Card key={item.id}>
          <CardActionArea onClick={() => navigate(`/app/platforms/${item.id}`)}>
            <CardContent>
              <Stack spacing={1}>
                <Stack direction="row" justifyContent="space-between" gap={1}>
                  <Typography fontWeight={700}>{item.name}</Typography>
                  <StatusChip status={item.operational_status} />
                </Stack>
                <Typography color="text.secondary">{[item.platform_type, item.model].filter(Boolean).join(" • ")}</Typography>
                {item.description && <Typography variant="body2">{item.description}</Typography>}
              </Stack>
            </CardContent>
          </CardActionArea>
        </Card>
      ))}
    </Stack>
  );
}
