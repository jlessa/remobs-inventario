import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#0f766e", dark: "#115e59", light: "#ccfbf1", contrastText: "#ffffff" },
    secondary: { main: "#2563eb" },
    success: { main: "#15803d" },
    warning: { main: "#d97706" },
    error: { main: "#dc2626" },
    background: { default: "#f8fafc", paper: "#ffffff" },
    text: { primary: "#111827", secondary: "#4b5563" },
    divider: "#dbe3ea",
  },
  shape: { borderRadius: 8 },
  typography: {
    fontFamily: '"Segoe UI", Roboto, Arial, sans-serif',
    h4: { fontWeight: 700, letterSpacing: 0 },
    h5: { fontWeight: 700, letterSpacing: 0 },
    h6: { fontWeight: 700, letterSpacing: 0 },
    button: { textTransform: "none", fontWeight: 700, letterSpacing: 0 },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { minHeight: 44 },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: { minWidth: 44, minHeight: 44 },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: { border: "1px solid #dbe3ea", boxShadow: "none" },
      },
    },
    MuiTextField: {
      defaultProps: { size: "small" },
    },
  },
});

export default theme;
