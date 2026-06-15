export interface ChecklistAnswerField {
  key: string;
  label: string;
}

export interface ChecklistAnswerGroup {
  title: string;
  fields: ChecklistAnswerField[];
}

export const photographFields: ChecklistAnswerField[] = [
  { key: "fotografias.embarcacao", label: "Embarcação" },
  { key: "fotografias.material_embarcado", label: "Material embarcado" },
  { key: "fotografias.chegando_saindo_estacao", label: "Chegando / saindo da estação" },
  { key: "fotografias.caixa_dentro_fora", label: "Caixa dentro / fora" },
  { key: "fotografias.mergulhador", label: "Mergulhador" },
  { key: "fotografias.adcp_antes_apos_limpeza", label: "ADCP antes / após limpeza" },
  { key: "fotografias.conector_adcp", label: "Conector ADCP" },
  { key: "fotografias.maregrafo", label: "Marégrafo" },
  { key: "fotografias.boia", label: "Boia" },
  { key: "fotografias.estacao_meteorologica", label: "Estação meteorológica" },
  { key: "fotografias.painel_solar", label: "Painel solar" },
  { key: "fotografias.marketing", label: "Fotos para marketing" },
];

export const postFieldChecklistFields: ChecklistAnswerField[] = [
  { key: "pos_campo.atualizar_pendencias", label: "Atualizar aba de pendências" },
  { key: "pos_campo.fotos_servidor", label: "Colocar fotos no servidor" },
  { key: "pos_campo.adicionar_pendencias", label: "Adicionar pendências na tabela" },
  { key: "pos_campo.entrega_ficha", label: "Entrega da ficha de campo" },
];

export const checklistAnswerGroups: ChecklistAnswerGroup[] = [
  {
    title: "Operação",
    fields: [
      { key: "operacao.codigo_viagem", label: "Código da viagem" },
      { key: "operacao.equipe_hm", label: "Equipe HM" },
      { key: "operacao.data", label: "Data" },
      { key: "operacao.tipo_manobra", label: "Tipo de manobra" },
      { key: "operacao.objetivo", label: "Motivo e objetivos da manobra" },
      { key: "operacao.horario_inicio", label: "Horário de início da manobra" },
      { key: "operacao.horario_termino", label: "Horário de término da manobra" },
    ],
  },
  {
    title: "Condições ambientais",
    fields: [
      { key: "ambiente.chuva", label: "Chuva" },
      { key: "ambiente.vento", label: "Vento" },
      { key: "ambiente.mar", label: "Mar" },
      { key: "ambiente.corrente", label: "Corrente" },
    ],
  },
  {
    title: "Equipe e embarcação",
    fields: [
      { key: "equipe.embarcacao_1", label: "Embarcação 1" },
      { key: "equipe.embarcacao_2", label: "Embarcação 2" },
      { key: "equipe.mestre_1", label: "Mestre da embarcação 1" },
      { key: "equipe.mestre_2", label: "Mestre da embarcação 2" },
      { key: "equipe.marinheiros_1", label: "Marinheiros da embarcação 1" },
      { key: "equipe.marinheiros_2", label: "Marinheiros da embarcação 2" },
      { key: "equipe.empresa_embarcacao", label: "Empresa da embarcação" },
      { key: "equipe.mergulhadores", label: "Mergulhadores" },
      { key: "equipe.empresa_mergulho", label: "Empresa de mergulho" },
      { key: "equipe.terceiros", label: "Terceiros" },
    ],
  },
  {
    title: "Fotografias obrigatórias",
    fields: photographFields,
  },
  {
    title: "Inspeção técnica",
    fields: [
      { key: "inspecao.adcp", label: "ADCP" },
      { key: "inspecao.anodos_adcp", label: "Anodos ADCP" },
      { key: "inspecao.suporte_adcp", label: "Suporte ADCP" },
      { key: "inspecao.transdutores_adcp", label: "Transdutores ADCP" },
      { key: "inspecao.cabo_adcp", label: "Cabo ADCP" },
      { key: "inspecao.incrustacao", label: "Incrustação" },
      { key: "inspecao.maregrafo", label: "Marégrafo" },
      { key: "inspecao.sensor_vento", label: "Sensor de vento" },
      { key: "inspecao.modem", label: "Modem" },
      { key: "inspecao.bateria", label: "Bateria" },
      { key: "inspecao.painel_solar", label: "Painel solar" },
      { key: "inspecao.observacoes", label: "Observações técnicas" },
    ],
  },
  {
    title: "Problemas e diagnóstico",
    fields: [
      { key: "problema.falha", label: "Falha encontrada" },
      { key: "problema.motivo", label: "Motivo provável" },
      { key: "problema.item", label: "Item que falhou" },
      { key: "problema.solucao", label: "Como resolveu o problema" },
    ],
  },
  {
    title: "Pós-campo",
    fields: postFieldChecklistFields,
  },
];

export function formatChecklistValue(value: unknown): string {
  if (typeof value === "boolean") return value ? "Sim" : "Não";
  if (Array.isArray(value)) return value.length ? value.join(", ") : "Não informado";
  if (value === null || value === undefined || value === "") return "Não informado";
  return String(value);
}

export function getKnownChecklistAnswerKeys(): Set<string> {
  return new Set(checklistAnswerGroups.flatMap((group) => group.fields.map((field) => field.key)));
}
