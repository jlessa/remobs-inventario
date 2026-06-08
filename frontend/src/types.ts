export type PermissionCode = string;

export interface RemobsUser {
  id: number;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  permission_codes: PermissionCode[];
}

export interface StockBalance {
  id: string;
  location_id: string;
  location_name: string;
  quantity: number;
  reserved_quantity: number;
}

export interface InventoryItem {
  id: string;
  item_type: "consumable" | "permanent_component";
  name: string;
  brand: string | null;
  model: string | null;
  serial_number: string | null;
  patrimony_number: string | null;
  invoice_number: string | null;
  description: string | null;
  condition_status: string;
  category_name: string | null;
  current_location_name: string | null;
  unit: string;
  minimum_stock_national: number;
  ideal_stock: number;
  row_version: number;
  stock_total: number;
  balances: StockBalance[];
  created_at?: string;
  updated_at?: string;
}

export interface Movement {
  id: string;
  item_id: string;
  from_location_name: string | null;
  to_location_name: string | null;
  quantity: number;
  requested_by_username: string;
  approved_by_username: string | null;
  status: string;
  reason: string;
  created_at: string;
}

export interface AlertItem {
  id: string;
  alert_type: string;
  severity: string;
  title: string;
  message: string;
  status: string;
  created_at: string;
}

export interface AuditLog {
  id: string;
  occurred_at: string;
  actor_username: string | null;
  action: string;
  entity_type: string;
  entity_label_snapshot: string | null;
  reason: string | null;
  status: string;
}

export interface Platform {
  id: string;
  name: string;
  platform_type: string;
  manufacturer?: string | null;
  operational_status: string;
  model: string | null;
  description?: string | null;
}

export interface Sensor {
  id: string;
  sensor_type: string;
  family: string;
  brand?: string | null;
  model: string | null;
  serial_number?: string | null;
  patrimony_number?: string | null;
  operational_status: string;
  calibration_due_at: string | null;
  notes?: string | null;
}

export interface PlatformSystem {
  id: string;
  name: string;
  status: string;
  notes: string | null;
}

export interface PlatformHull {
  id: string;
  code: string;
  model: string | null;
  status: string;
  notes: string | null;
}

export interface PlatformLinkedSensor extends Sensor {
  installation_status: string;
  installation_notes: string | null;
}

export interface PlatformDetail extends Platform {
  hull: PlatformHull | null;
  systems: PlatformSystem[];
  sensors: PlatformLinkedSensor[];
}

export interface SensorPlatform {
  id: string;
  name: string;
  platform_type: string;
  operational_status: string;
}

export interface SensorInstallation {
  id: string;
  platform_id: string;
  platform_name: string;
  status: string;
  installed_at: string | null;
  removed_at: string | null;
  notes: string | null;
}

export interface SensorDetail extends Sensor {
  current_platform: SensorPlatform | null;
  installations: SensorInstallation[];
}

export interface Checklist {
  id: string;
  title: string;
  template_name: string;
  platform_id: string | null;
  platform_name: string | null;
  status: "draft" | "submitted" | string;
  current_step: number;
  total_steps: number;
  answers: Record<string, unknown>;
  evidence: Array<Record<string, unknown>>;
  submitted_by_id: number;
  submitted_by_username: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  submitted_at: string | null;
}

export interface ItemHistory {
  movements: Movement[];
  audit_logs: Array<{
    id: string;
    occurred_at: string;
    actor_username: string | null;
    action: string;
    reason: string | null;
  }>;
}

export interface SyncStatus {
  pending_actions: number;
  conflict_actions: number;
  server_time: string;
}

export interface SyncConflict {
  id: string;
  client_action_id: string;
  action_type: string;
  entity_type: string;
  entity_id: string | null;
  payload: Record<string, unknown>;
  status: string;
  error_message: string | null;
  created_at: string;
}

export interface ApiList<T> {
  items: T[];
  total: number;
}
