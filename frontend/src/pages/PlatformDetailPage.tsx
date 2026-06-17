import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import SensorsIcon from "@mui/icons-material/Sensors";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import LoadingState from "../components/LoadingState";
import StatusChip from "../components/StatusChip";
import { inventoryService } from "../services/inventoryService";
import type { PlatformDetail } from "../types";

export default function PlatformDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [platform, setPlatform] = useState<PlatformDetail | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!id) return;
    inventoryService
      .getPlatform(id)
      .then(setPlatform)
      .catch(() => setError(true));
  }, [id]);

  if (error) return <Alert severity="error">Erro ao carregar plataforma.</Alert>;
  if (!platform) return <LoadingState message="Carregando plataforma..." />;

  return (
    <Stack spacing={2}>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/app/platforms")} sx={{ alignSelf: "flex-start" }}>
        Plataformas
      </Button>

      <Card>
        <CardContent>
          <Stack spacing={1}>
            <Stack direction="row" justifyContent="space-between" gap={1}>
              <Typography variant="h5">{platform.name}</Typography>
              <StatusChip status={platform.operational_status} />
            </Stack>
            <Typography color="text.secondary">
              {[platform.platform_type, platform.manufacturer, platform.model].filter(Boolean).join(" • ")}
            </Typography>
            {platform.description && <Typography>{platform.description}</Typography>}
          </Stack>
        </CardContent>
      </Card>

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6">Casco</Typography>
              {platform.hull ? (
                <Stack spacing={1} sx={{ mt: 1 }}>
                  <Typography fontWeight={700}>{platform.hull.code}</Typography>
                  <Typography color="text.secondary">{platform.hull.model || "Modelo não informado"}</Typography>
                  <StatusChip status={platform.hull.status} />
                </Stack>
              ) : (
                <Alert severity="info" sx={{ mt: 1 }}>
                  Casco não vinculado.
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h6">Sistemas</Typography>
              {platform.systems.length === 0 && <Alert severity="info">Nenhum sistema cadastrado.</Alert>}
              <List dense>
                {platform.systems.map((system) => (
                  <ListItem key={system.id} disableGutters secondaryAction={<StatusChip status={system.status} />}>
                    <ListItemText primary={system.name} secondary={system.notes || "Sem observação"} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Stack spacing={1.5}>
            <Typography variant="h6">Sensores vinculados</Typography>
            {platform.sensors.length === 0 && <Alert severity="info">Nenhum sensor ativo vinculado.</Alert>}
            {platform.sensors.map((sensor) => (
              <Card key={sensor.id} variant="outlined">
                <CardActionArea onClick={() => navigate(`/app/sensors/${sensor.id}`)}>
                  <CardContent>
                    <Stack direction="row" spacing={1.5} alignItems="center" justifyContent="space-between">
                      <Stack direction="row" spacing={1.5} alignItems="center">
                        <SensorsIcon color="primary" />
                        <Stack>
                          <Typography fontWeight={700}>{sensor.family}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {[sensor.sensor_type, sensor.model, sensor.serial_number].filter(Boolean).join(" • ")}
                          </Typography>
                        </Stack>
                      </Stack>
                      <StatusChip status={sensor.operational_status} />
                    </Stack>
                  </CardContent>
                </CardActionArea>
              </Card>
            ))}
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  );
}
