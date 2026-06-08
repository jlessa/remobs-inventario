import Chip from "@mui/material/Chip";

const colorByStatus: Record<string, "success" | "warning" | "error" | "default" | "info"> = {
  operacional: "success",
  aprovado: "success",
  approved: "success",
  submitted: "success",
  em_operacao: "success",
  pendente: "warning",
  pending: "warning",
  draft: "warning",
  inconsistencia: "warning",
  adjusted: "warning",
  sent_to_admin: "warning",
  manutencao: "error",
  avariado: "error",
  rejected: "error",
  discarded: "error",
  disponivel: "default",
  nao_instalado: "default",
};

export default function StatusChip({ status }: { status: string }) {
  const normalized = status.toLowerCase();
  return (
    <Chip
      size="small"
      color={colorByStatus[normalized] || "info"}
      label={status.replaceAll("_", " ")}
      variant={colorByStatus[normalized] === "default" ? "outlined" : "filled"}
    />
  );
}
