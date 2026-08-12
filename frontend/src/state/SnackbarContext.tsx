import Alert from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";
import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

export type SnackbarSeverity = "success" | "error" | "info" | "warning";

interface SnackbarState {
  open: boolean;
  message: string;
  severity: SnackbarSeverity;
}

export interface SnackbarContextValue {
  showSnackbar: (message: string, severity?: SnackbarSeverity) => void;
  showSuccess: (message: string) => void;
  showError: (message: string) => void;
  showInfo: (message: string) => void;
  showWarning: (message: string) => void;
}

const SnackbarContext = createContext<SnackbarContextValue | null>(null);

export function SnackbarProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<SnackbarState>({
    open: false,
    message: "",
    severity: "info",
  });

  const close = useCallback(() => {
    setState((current) => ({ ...current, open: false }));
  }, []);

  const showSnackbar = useCallback((message: string, severity: SnackbarSeverity = "info") => {
    setState({ open: true, message, severity });
  }, []);

  const value = useMemo<SnackbarContextValue>(
    () => ({
      showSnackbar,
      showSuccess: (message: string) => showSnackbar(message, "success"),
      showError: (message: string) => showSnackbar(message, "error"),
      showInfo: (message: string) => showSnackbar(message, "info"),
      showWarning: (message: string) => showSnackbar(message, "warning"),
    }),
    [showSnackbar],
  );

  return (
    <SnackbarContext.Provider value={value}>
      {children}
      <Snackbar
        open={state.open}
        autoHideDuration={5000}
        onClose={(_event, reason) => {
          if (reason === "clickaway") {
            return;
          }
          close();
        }}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        sx={{ bottom: { xs: 80, md: 24 } }}
      >
        <Alert severity={state.severity} variant="filled" onClose={close} sx={{ width: "100%" }}>
          {state.message}
        </Alert>
      </Snackbar>
    </SnackbarContext.Provider>
  );
}

export function useSnackbar(): SnackbarContextValue {
  const context = useContext(SnackbarContext);
  if (!context) {
    throw new Error("useSnackbar deve ser usado dentro de SnackbarProvider.");
  }
  return context;
}
