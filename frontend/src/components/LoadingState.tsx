import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";

interface LoadingStateProps {
  message?: string;
  minHeight?: number | string;
}

/**
 * Feedback visual de carregamento, centralizado e responsivo.
 * Ocupa a largura total e se adapta a telas pequenas, evitando que
 * estados vazios apareçam enquanto os dados ainda estão sendo buscados.
 */
export default function LoadingState({ message = "Carregando...", minHeight }: LoadingStateProps) {
  return (
    <Box
      role="status"
      aria-live="polite"
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 1.5,
        width: "100%",
        py: { xs: 5, sm: 6 },
        px: 2,
        minHeight: minHeight ?? { xs: 180, sm: 220 },
      }}
    >
      <CircularProgress aria-hidden />
      {message && (
        <Typography variant="body2" color="text.secondary" textAlign="center">
          {message}
        </Typography>
      )}
    </Box>
  );
}
