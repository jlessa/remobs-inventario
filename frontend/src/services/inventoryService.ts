import { inventoryApi } from "../api/client";
import type {
  AlertItem,
  ApiList,
  AuditLog,
  Checklist,
  InventoryItem,
  ItemHistory,
  Movement,
  Platform,
  PlatformDetail,
  Sensor,
  SensorDetail,
  SyncConflict,
  SyncStatus,
} from "../types";

export interface InventoryItemPayload {
  item_type: "consumable" | "permanent_component";
  name: string;
  brand?: string;
  model?: string;
  serial_number?: string;
  patrimony_number?: string;
  invoice_number?: string;
  description?: string;
  condition_status?: string;
  category_name?: string;
  location_name?: string;
  unit?: string;
  initial_quantity?: number;
  minimum_stock_national?: number;
  minimum_stock_import?: number;
  minimum_stock_maintenance?: number;
  ideal_stock?: number;
  reason?: string;
}

export interface MovementRequestPayload {
  item_id: string;
  quantity: number;
  from_location_id: string;
  to_location_name: string;
  reason: string;
}

export interface ChecklistPayload {
  title?: string;
  template_name?: string;
  platform_id?: string | null;
  platform_name?: string | null;
  total_steps?: number;
  current_step?: number;
  answers?: Record<string, unknown>;
  evidence?: Array<Record<string, unknown>>;
  notes?: string | null;
}

export interface SyncConflictDecisionPayload {
  client_action_id: string;
  decision: "adjust" | "discard" | "send_to_admin";
  adjusted_payload?: Record<string, unknown>;
  reason: string;
}

export interface SensorUpdatePayload {
  sensor_type?: string;
  family?: string;
  brand?: string | null;
  model?: string | null;
  serial_number?: string | null;
  patrimony_number?: string | null;
  operational_status?: string;
  calibration_due_at?: string | null;
  notes?: string | null;
  reason?: string | null;
}

export const inventoryService = {
  async listItems(): Promise<ApiList<InventoryItem>> {
    const response = await inventoryApi.get<ApiList<InventoryItem>>("/inventory/items");
    return response.data;
  },

  async getItem(id: string): Promise<InventoryItem> {
    const response = await inventoryApi.get<InventoryItem>(`/inventory/items/${id}`);
    return response.data;
  },

  async getItemHistory(id: string): Promise<ItemHistory> {
    const response = await inventoryApi.get<ItemHistory>(`/inventory/items/${id}/history`);
    return response.data;
  },

  async createItem(payload: InventoryItemPayload): Promise<InventoryItem> {
    const response = await inventoryApi.post<InventoryItem>("/inventory/items", payload);
    return response.data;
  },

  async listMovements(): Promise<ApiList<Movement>> {
    const response = await inventoryApi.get<ApiList<Movement>>("/inventory/movements");
    return response.data;
  },

  async requestMovement(payload: MovementRequestPayload): Promise<Movement> {
    const response = await inventoryApi.post<Movement>("/inventory/movements/request", payload);
    return response.data;
  },

  async approveMovement(id: string, reason: string): Promise<Movement> {
    const response = await inventoryApi.post<Movement>(`/inventory/movements/${id}/approve`, { reason });
    return response.data;
  },

  async rejectMovement(id: string, reason: string): Promise<Movement> {
    const response = await inventoryApi.post<Movement>(`/inventory/movements/${id}/reject`, { reason });
    return response.data;
  },

  async listAlerts(): Promise<ApiList<AlertItem>> {
    const response = await inventoryApi.get<ApiList<AlertItem>>("/alerts");
    return response.data;
  },

  async listAuditLogs(): Promise<ApiList<AuditLog>> {
    const response = await inventoryApi.get<ApiList<AuditLog>>("/audit-logs");
    return response.data;
  },

  async listPlatforms(): Promise<ApiList<Platform>> {
    const response = await inventoryApi.get<ApiList<Platform>>("/platforms");
    return response.data;
  },

  async getPlatform(id: string): Promise<PlatformDetail> {
    const response = await inventoryApi.get<PlatformDetail>(`/platforms/${id}`);
    return response.data;
  },

  async listSensors(): Promise<ApiList<Sensor>> {
    const response = await inventoryApi.get<ApiList<Sensor>>("/sensors");
    return response.data;
  },

  async getSensor(id: string): Promise<SensorDetail> {
    const response = await inventoryApi.get<SensorDetail>(`/sensors/${id}`);
    return response.data;
  },

  async updateSensor(id: string, payload: SensorUpdatePayload): Promise<Sensor> {
    const response = await inventoryApi.patch<Sensor>(`/sensors/${id}`, payload);
    return response.data;
  },

  async listChecklists(): Promise<ApiList<Checklist>> {
    const response = await inventoryApi.get<ApiList<Checklist>>("/checklists");
    return response.data;
  },

  async getChecklist(id: string): Promise<Checklist> {
    const response = await inventoryApi.get<Checklist>(`/checklists/${id}`);
    return response.data;
  },

  async createChecklist(payload: ChecklistPayload): Promise<Checklist> {
    const response = await inventoryApi.post<Checklist>("/checklists", payload);
    return response.data;
  },

  async updateChecklist(id: string, payload: ChecklistPayload): Promise<Checklist> {
    const response = await inventoryApi.patch<Checklist>(`/checklists/${id}`, payload);
    return response.data;
  },

  async submitChecklist(id: string, reason: string): Promise<Checklist> {
    const response = await inventoryApi.post<Checklist>(`/checklists/${id}/submit`, { reason });
    return response.data;
  },

  async getSyncStatus(): Promise<SyncStatus> {
    const response = await inventoryApi.get("/sync/status");
    return response.data;
  },

  async listSyncConflicts(): Promise<ApiList<SyncConflict>> {
    const response = await inventoryApi.get<ApiList<SyncConflict>>("/sync/conflicts");
    return response.data;
  },

  async resolveSyncConflict(payload: SyncConflictDecisionPayload): Promise<{ status: string; client_action_id: string }> {
    const response = await inventoryApi.post<{ status: string; client_action_id: string }>("/sync/resolve-conflict", payload);
    return response.data;
  },
};
