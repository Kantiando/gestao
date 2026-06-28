import { useMemo, useState } from "react";
import { money } from "../api.js";

const STATUS_REALIZADO = ["realizado", "confirmado", "conciliado", "pago", "recebido", "liquidado"];

function isRealizado(status = "") {
  return STATUS_REALIZADO.includes(String(status || "").toLowerCase());
}

export function emptyMov(contaId = "") {
  const hoje = new Date().toISOString().slice(0, 10);
  return { data_movimento: hoje, competencia: hoje.slice(0, 7), tipo: "saida", descricao: "", valor: "", plano_conta_id: contaId, origem: "manual", status: "realizado" };
}

function somar(lista, tipo) {
  return lista
    .filter((m) => m.tipo === tipo)
    .reduce((soma, m) => soma + Number(m.valor || 0), 0);
}

export function FluxoEditor({ dashboard, movimentos, contas, form, setForm, editId, setEditId, onSubmit, onDelete }) {
  const [contaFiltro, setContaFiltro] = useState("");
  const [visao, setVisao] = useState("todos");
  const update = (key, value) => setForm({ ...form, [key]: value });

  const movimentosPorConta = useMemo(() => {
    if (!contaFiltro) return movimentos;
    return movimentos.filter((m) => m.plano_conta_id === contaFiltro);
  }, [movimentos, contaFiltro]);

  const resumo = useMemo(() => {
    const realizados = movimentosPorConta.filter((m) => isRealizado(m.status));
    const naoRealizados = movimentosPorConta.filter((m) => !isRealizado(m.status));
    const realizadoEntradas = somar(realizados, "entrada");
    const realizadoSaidas = somar(realizados, "saida");
    const aReceber = somar(naoRealizados, "entrada");
    const aPagar = somar(naoRealizados, "saida");
    return {
      realizados,
      naoRealizados,
      realizadoEntradas,
      realizadoSaidas,
      saldoRealizado: realizadoEntradas - realizadoSaidas,
      aReceber,
      aPagar,
      saldoPrevisto: aReceber - aPagar,
      saldoProjetado: realizadoEntradas - realizadoSaidas + aReceber - aPagar,
      quantidade: movimentosPorConta.length,
    };
  }, [movimentosPorConta]);

  const movimentosFiltrados = useMemo(() => {
    if (visao === "realizado") return resumo.realizados;
    if (visao === "nao-realizado") return resumo.naoRealizados;
    if (visao === "a-receber") return resumo.naoRealizados.filter((m) => m.tipo === "entrada");
    if (visao === "a-pagar") return resumo.naoRealizados.filter((m) => m.tipo === "saida");
    return movimentosPorConta;
  }, [movimentosPorConta, resumo, visao]);

  const contaSelecionada = contas.find((c) => c.id === contaFiltro);

  return <section className="grid">
    <article className="card"><span>Entradas realizadas</span><strong>{money(resumo.realizadoEntradas)}</strong></article>
    <article className="card"><span>Saídas realizadas</span><strong>{money(resumo.realizadoSaidas)}</strong></article>
    <article className="card"><span>Saldo realizado</span><strong>{money(resumo.saldoRealizado)}</strong></article>
    <article className="card"><span>A receber</span><strong>{money(resumo.aReceber)}</strong></article>
    <article className="card"><span>A pagar</span><strong>{money(resumo.aPagar)}</strong></article>
    <article className="card"><span>Saldo projetado</span><strong>{money(resumo.saldoProjetado)}</strong></article>

    <div className="panel">
      <h2>Filtro do fluxo de caixa</h2>
      <div className="form-grid">
        <select value={contaFiltro} onChange={(e) => setContaFiltro(e.target.value)}>
          <option value="">Todas as contas</option>
          {contas.map((c) => <option key={c.id} value={c.id}>{c.codigo} · {c.nome} → {c.dre_categoria}</option>)}
        </select>
        <select value={visao} onChange={(e) => setVisao(e.target.value)}>
          <option value="todos">Todos</option>
          <option value="realizado">Realizado</option>
          <option value="nao-realizado">Não realizado</option>
          <option value="a-receber">A receber</option>
          <option value="a-pagar">A pagar</option>
        </select>
        <button type="button" onClick={() => { setContaFiltro(""); setVisao("todos"); }}>Limpar filtros</button>
      </div>
      {contaSelecionada && <p>Conta: <strong>{contaSelecionada.codigo} · {contaSelecionada.nome}</strong></p>}
      <p>Mostrando <strong>{movimentosFiltrados.length}</strong> de <strong>{movimentosPorConta.length}</strong> lançamentos.</p>
    </div>

    <div className="panel">
      <h2>{editId ? "Editar lançamento" : "Novo lançamento"}</h2>
      <form className="form-grid" onSubmit={onSubmit}>
        <input type="date" value={form.data_movimento} onChange={(e) => update("data_movimento", e.target.value)} required />
        <input value={form.competencia} onChange={(e) => update("competencia", e.target.value)} required />
        <select value={form.tipo} onChange={(e) => update("tipo", e.target.value)}><option value="entrada">Entrada</option><option value="saida">Saída</option></select>
        <select value={form.status} onChange={(e) => update("status", e.target.value)}>
          <option value="realizado">Realizado</option>
          <option value="previsto">Não realizado / previsto</option>
        </select>
        <input value={form.descricao} onChange={(e) => update("descricao", e.target.value)} placeholder="Descrição" required />
        <input type="number" step="0.01" value={form.valor} onChange={(e) => update("valor", e.target.value)} placeholder="Valor" required />
        <select value={form.plano_conta_id} onChange={(e) => update("plano_conta_id", e.target.value)} required>{contas.map((c) => <option key={c.id} value={c.id}>{c.codigo} · {c.nome} → {c.dre_categoria}</option>)}</select>
        <button>{editId ? "Salvar" : "Adicionar"}</button>
        {editId && <button type="button" onClick={() => { setEditId(null); setForm(emptyMov(contas[0]?.id || "")); }}>Cancelar</button>}
      </form>
    </div>

    <div className="panel">
      <h2>Lançamentos</h2>
      <table><thead><tr><th>Data</th><th>Descrição</th><th>Conta</th><th>DRE</th><th>Status</th><th>Tipo</th><th>Valor</th><th>Ações</th></tr></thead><tbody>
        {movimentosFiltrados.map((m) => <tr key={m.id}><td>{m.data_movimento}</td><td>{m.descricao}</td><td>{m.conta}</td><td>{m.dre_categoria}</td><td>{isRealizado(m.status) ? "Realizado" : "Não realizado"}</td><td>{m.tipo}</td><td>{money(m.valor)}</td><td><button onClick={() => { setEditId(m.id); setForm({ ...emptyMov(), ...m, valor: String(m.valor), status: isRealizado(m.status) ? "realizado" : "previsto" }); }}>Editar</button><button onClick={() => onDelete(m.id)}>Remover</button></td></tr>)}
      </tbody></table>
    </div>
  </section>;
}
