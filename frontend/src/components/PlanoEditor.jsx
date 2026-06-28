export function emptyConta(categoriaId = "") {
  return { codigo: "", nome: "", tipo: "despesa_variavel", grupo: "Geral", dre_categoria_id: categoriaId, ativo: true };
}

export function PlanoEditor({ contas, categorias, form, setForm, editId, setEditId, onSubmit, onDelete }) {
  const update = (key, value) => setForm({ ...form, [key]: value });
  return <section className="grid">
    <div className="panel">
      <h2>{editId ? "Editar conta" : "Nova conta do plano"}</h2>
      <form className="form-grid" onSubmit={onSubmit}>
        <input value={form.codigo} onChange={(e) => update("codigo", e.target.value)} placeholder="Código" required />
        <input value={form.nome} onChange={(e) => update("nome", e.target.value)} placeholder="Nome da conta" required />
        <select value={form.tipo} onChange={(e) => update("tipo", e.target.value)}>
          <option value="receita">Receita</option><option value="custo_variavel">Custo variável</option><option value="despesa_fixa">Despesa fixa</option><option value="despesa_variavel">Despesa variável</option><option value="despesa_financeira">Despesa financeira</option><option value="investimento">Investimento</option>
        </select>
        <input value={form.grupo} onChange={(e) => update("grupo", e.target.value)} placeholder="Grupo" />
        <select value={form.dre_categoria_id} onChange={(e) => update("dre_categoria_id", e.target.value)}>
          {categorias.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
        </select>
        <button>{editId ? "Salvar edição" : "Adicionar conta"}</button>
        {editId && <button type="button" onClick={() => { setEditId(null); setForm(emptyConta(categorias[0]?.id || "")); }}>Cancelar</button>}
      </form>
    </div>
    <div className="panel">
      <h2>Plano de contas</h2>
      <table><thead><tr><th>Código</th><th>Nome</th><th>Tipo</th><th>Grupo</th><th>DRE</th><th>Ações</th></tr></thead><tbody>
        {contas.map((c) => <tr key={c.id}><td>{c.codigo}</td><td>{c.nome}</td><td>{c.tipo}</td><td>{c.grupo}</td><td>{c.dre_categoria}</td><td><button onClick={() => { setEditId(c.id); setForm({ codigo: c.codigo, nome: c.nome, tipo: c.tipo, grupo: c.grupo, dre_categoria_id: c.dre_categoria_id, ativo: c.ativo }); }}>Editar</button><button onClick={() => onDelete(c.id)}>Apagar</button></td></tr>)}
      </tbody></table>
    </div>
  </section>;
}
