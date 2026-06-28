import { useEffect, useState } from "react";
import { api, dataInicio, dataFim, money } from "../api.js";

export default function AnalyticsView({ empresaId }) {
  const [inicio, setInicio] = useState(dataInicio);
  const [fim, setFim] = useState(dataFim);
  const [drePeriodo, setDrePeriodo] = useState(null);
  const [participacao, setParticipacao] = useState(null);
  const [erro, setErro] = useState("");

  async function carregar(e) {
    if (e) e.preventDefault();
    if (!empresaId) return;
    try {
      const [dreData, partData] = await Promise.all([
        api(`/empresas/${empresaId}/dre-periodo?data_inicio=${inicio}&data_fim=${fim}`),
        api(`/empresas/${empresaId}/plano-contas/participacao?data_inicio=${inicio}&data_fim=${fim}`),
      ]);
      setDrePeriodo(dreData);
      setParticipacao(partData);
      setErro("");
    } catch (error) {
      setErro(error.message);
    }
  }

  useEffect(() => { carregar(); }, [empresaId]);

  return <section className="grid">
    <div className="panel">
      <h2>Análise por período</h2>
      <form className="form-grid" onSubmit={carregar}>
        <input type="date" value={inicio} onChange={(e) => setInicio(e.target.value)} />
        <input type="date" value={fim} onChange={(e) => setFim(e.target.value)} />
        <button>Atualizar análise</button>
      </form>
      {erro && <p className="erro">{erro}</p>}
    </div>

    <article className="card"><span>Receita</span><strong>{money(drePeriodo?.receita_bruta)}</strong></article>
    <article className="card"><span>Custos variáveis</span><strong>{money(drePeriodo?.custos_variaveis)}</strong></article>
    <article className="card"><span>Despesas operacionais</span><strong>{money(drePeriodo?.despesas_operacionais)}</strong></article>
    <article className="card"><span>Lucro líquido</span><strong>{money(drePeriodo?.lucro_liquido)}</strong></article>
    <article className="card"><span>Margem líquida</span><strong>{Number(drePeriodo?.margem_liquida_percentual || 0).toFixed(2)}%</strong></article>
    <article className="card"><span>Total de saídas</span><strong>{money(participacao?.total_saidas)}</strong></article>

    <div className="panel">
      <h2>DRE por data-data</h2>
      <table>
        <thead><tr><th>Ordem</th><th>Categoria</th><th>Entradas</th><th>Saídas</th><th>Valor bruto</th></tr></thead>
        <tbody>{(drePeriodo?.linhas_customizadas || []).map((linha) => <tr key={linha.id}>
          <td>{linha.ordem}</td><td>{linha.nome}</td><td>{money(linha.entradas)}</td><td>{money(linha.saidas)}</td><td>{money(linha.valor)}</td>
        </tr>)}</tbody>
      </table>
    </div>

    <div className="panel">
      <h2>Participação dos gastos por plano de contas</h2>
      <table>
        <thead><tr><th>Conta</th><th>DRE</th><th>Qtde.</th><th>Saídas</th><th>% dos gastos</th><th>Entradas</th></tr></thead>
        <tbody>{(participacao?.contas || []).map((conta) => <tr key={conta.plano_conta_id}>
          <td>{conta.codigo} · {conta.nome}</td>
          <td>{conta.dre_categoria}</td>
          <td>{conta.quantidade}</td>
          <td>{money(conta.saidas)}</td>
          <td>{Number(conta.participacao_saidas_percentual || 0).toFixed(2)}%</td>
          <td>{money(conta.entradas)}</td>
        </tr>)}</tbody>
      </table>
    </div>
  </section>;
}
