import CircularProgress from "@mui/material/CircularProgress";
import Box from "@mui/material/Box";
import { Navigate, Route, Routes } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import AppLayout from "./layouts/AppLayout";
import AlertsPage from "./pages/AlertsPage";
import ChecklistDetailPage from "./pages/ChecklistDetailPage";
import ChecklistFormPage from "./pages/ChecklistFormPage";
import ChecklistListPage from "./pages/ChecklistListPage";
import HomePage from "./pages/HomePage";
import InventoryDetailPage from "./pages/InventoryDetailPage";
import InventoryFormPage from "./pages/InventoryFormPage";
import InventoryListPage from "./pages/InventoryListPage";
import LoginPage from "./pages/LoginPage";
import MenuPage from "./pages/MenuPage";
import MovementRequestPage from "./pages/MovementRequestPage";
import MovementsPage from "./pages/MovementsPage";
import PlatformDetailPage from "./pages/PlatformDetailPage";
import PlatformsPage from "./pages/PlatformsPage";
import SensorDetailPage from "./pages/SensorDetailPage";
import SensorsPage from "./pages/SensorsPage";
import SyncPage from "./pages/SyncPage";
import { useAuth } from "./state/AuthContext";

export default function App() {
  const { loading } = useAuth();

  if (loading) {
    return (
      <Box sx={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/app" element={<AppLayout />}>
          <Route index element={<Navigate to="/app/home" replace />} />
          <Route path="home" element={<HomePage />} />
          <Route path="inventory" element={<InventoryListPage />} />
          <Route path="inventory/new" element={<InventoryFormPage />} />
          <Route path="inventory/:id" element={<InventoryDetailPage />} />
          <Route path="movements" element={<MovementsPage />} />
          <Route path="movements/new" element={<MovementRequestPage />} />
          <Route path="alerts" element={<AlertsPage />} />
          <Route path="platforms" element={<PlatformsPage />} />
          <Route path="platforms/:id" element={<PlatformDetailPage />} />
          <Route path="sensors" element={<SensorsPage />} />
          <Route path="sensors/:id" element={<SensorDetailPage />} />
          <Route path="checklists" element={<ChecklistListPage />} />
          <Route path="checklists/new" element={<ChecklistFormPage />} />
          <Route path="checklists/:id" element={<ChecklistDetailPage />} />
          <Route path="sync" element={<SyncPage />} />
          <Route path="menu" element={<MenuPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/app/home" replace />} />
    </Routes>
  );
}
