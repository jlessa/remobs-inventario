import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useNavigate } from "react-router-dom";

import { getVisibleNavigation } from "../navigation";
import { useAuth } from "../state/AuthContext";

export default function MenuPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const items = getVisibleNavigation(user?.permission_codes ?? []);

  return (
    <Stack spacing={2}>
      <Typography variant="h5">Menu</Typography>
      {items.map((item) => (
        <Card key={item.path}>
          <CardActionArea onClick={() => navigate(item.path)}>
            <CardContent>
              <Typography fontWeight={700}>{item.label}</Typography>
            </CardContent>
          </CardActionArea>
        </Card>
      ))}
    </Stack>
  );
}
