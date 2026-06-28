import { money } from "../api.js";

export function emptyMov(contaId = "") {
  const hoje = new Date().toISOString().slice(0, 10);
  return { data_movimento: hoje, competencia: hoje.slice(0, 7), tipo: "saida", descricao: "", valor: "", plano_conta_id: contaId, origem: "manual", status: "confirmado" };
}

export function FluxoEditor({ dashboard, movimentos, contas, form, setForm, editId, setEditId, onSubmit, onDelete }) {
  const fluxo = dashboard?.fluxo_caixa || {};
  const update = (key, value) => setForm({ ...form, [key]: value });
  return <section className="grid">
    <article className="card"><span>Entradas</span><strong>{money(fluxo.entradas)}</strong></article>
    <article className="card"><span>Saídas</span><strong>{money(fluxo.saidas)}</strong></article>
    <article className="card"><span>Saldo</span><strong>{money(fluxo.saldo_periodo)}</strong></article>
    <div className="panel">
      <h2>{editId ? "Editar lançamento" : "Novo lançamento"}</h2>
      <form className="form-grid" onSubmit={onSubmit}>
        <input type="date" value={form.data_movimento} onChange={(e) => update("data_movimento", e.target.value)} required />
        <input value={form.competencia} onChange={(e) => update("competencia", e.target.value)} required />
        <select value={form.tipo} onChange={(e) => update("tipo", e.target.value)}><option value="entrada">Entrada</option><option value="saida">Saída</option></select>
        <input value={form.descricao} onChange={(e) => update("descricao", e.target.value)} placeholder="Descrição" required />
        <input type="number" step="0.01" value={form.valor} onChange={(e) => update("valor", e.target.value)} placeholder="Valor" required />
        <select value={form.plano_conta_id} onChange={(e) => update("plano_conta_id", e.target.value)} required>{contas.map((c) => <option key={c.id} value={c.id}>{c.codigo} · {c.nome} → {c.dre_categoria}</option>)}</select>
        <button>{editId ? "Salvar" : "Adicionar"}</button>
        {editId && <button type="button" onClick={() => { setEditId(null); setForm(emptyMov(contas[0]?.id || "")); }}>Cancelar</button>}
      </form>
    </div>
    <div className="panel">
      <h2>Lançamentos</h2>
      <table><thead><tr><th>Data</th><th>Descrição</th><th>Conta</th><th>DRE</th><th>Tipo</th><th>Valor</th><th>Ações</th></tr></thead><tbody>
        {movimentos.map((m) => <tr key={m.id}><td>{m.data_movimento}</td><td>{m.descricao}</td><td>{m.conta}</td><td>{m.dre_categoria}</td><td>{m.tipo}</td><td>{money(m.valor)}</td><td><button onClick={() => { setEditId(m.id); setForm({ ...emptyMov(), ...m, valor: String(m.valor) }); }}>Editar</button><button onClick={() => onDelete(m.id)}>Remover</button></td></tr>)}
      </tbody></table>
    </div>
  </section>;
}
