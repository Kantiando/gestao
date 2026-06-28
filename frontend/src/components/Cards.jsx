import { money } from "../api.js";

export function Card({ label, value }) {
  return <article className="card"><span>{label}</span><strong>{value}</strong></article>;
}

export function ResumoCards({ dashboard, movimentos }) {
  const dre = dashboard?.dre || {};
  const fluxo = dashboard?.fluxo_caixa || {};
  return <>
    <Card label="Receita DRE" value={money(dre.receita_bruta)} />
    <Card label="Lucro líquido" value={money(dre.lucro_liquido)} />
    <Card label="Entradas caixa" value={money(fluxo.entradas)} />
    <Card label="Saídas caixa" value={money(fluxo.saidas)} />
    <Card label="Saldo caixa" value={money(fluxo.saldo_periodo)} />
    <Card label="Movimentos" value={movimentos.length} />
  </>;
}
