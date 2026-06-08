import AssignmentTurnedInIcon from "@mui/icons-material/AssignmentTurnedIn";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ChecklistIcon from "@mui/icons-material/FactCheck";
import HubIcon from "@mui/icons-material/Hub";
import InventoryIcon from "@mui/icons-material/Inventory2";
import SensorsIcon from "@mui/icons-material/Sensors";
import SyncIcon from "@mui/icons-material/Sync";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import type { SvgIconComponent } from "@mui/icons-material";

export interface NavigationItem {
  label: string;
  path: string;
  icon: SvgIconComponent;
  permissions: string[];
  bottom: boolean;
}

export const navigationItems: NavigationItem[] = [
  { label: "Início", path: "/app/home", icon: DashboardIcon, permissions: [], bottom: true },
  { label: "Inventário", path: "/app/inventory", icon: InventoryIcon, permissions: ["inventory:item:read"], bottom: true },
  { label: "Operação", path: "/app/movements", icon: AssignmentTurnedInIcon, permissions: ["inventory:movement:request"], bottom: true },
  { label: "Alertas", path: "/app/alerts", icon: WarningAmberIcon, permissions: ["inventory:item:read"], bottom: true },
  { label: "Plataformas", path: "/app/platforms", icon: HubIcon, permissions: ["platform:read"], bottom: false },
  { label: "Sensores", path: "/app/sensors", icon: SensorsIcon, permissions: ["sensor:read"], bottom: false },
  { label: "Checklists", path: "/app/checklists", icon: ChecklistIcon, permissions: ["checklist:submit"], bottom: false },
  { label: "Sincronização", path: "/app/sync", icon: SyncIcon, permissions: ["inventory:item:read"], bottom: false },
];

export function hasPermission(userPermissions: string[], required: string[]): boolean {
  if (userPermissions.includes("*")) {
    return true;
  }
  return required.every((permission) => userPermissions.includes(permission));
}

export function getVisibleNavigation(userPermissions: string[]): NavigationItem[] {
  return navigationItems.filter((item) => hasPermission(userPermissions, item.permissions));
}
