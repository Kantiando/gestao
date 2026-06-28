export function emptyDre() {
  return { nome: "", chave: "", grupo: "operacional", ordem: 100, sinal: "positivo", ativa: true };
}

export function DreEditor({ categorias, form, setForm, editId, setEditId, onSubmit, onDelete }) {
  const update = (key, value) => setForm({ ...form, [key]: value });
  return <section className="grid">
    <div className="panel">
      <h2>{editId ? "Editar categoria da DRE" : "Nova categoria da DRE"}</h2>
      <form className="form-grid" onSubmit={onSubmit}>
        <input value={form.nome} onChange={(e) => update("nome", e.target.value)} placeholder="Nome" required />
        <input value={form.chave} onChange={(e) => update("chave", e.target.value)} placeholder="chave_sem_espaco" required />
        <input value={form.grupo} onChange={(e) => update("grupo", e.target.value)} placeholder="Grupo" />
        <input type="number" value={form.ordem} onChange={(e) => update("ordem", e.target.value)} placeholder="Ordem" />
        <select value={form.sinal} onChange={(e) => update("sinal", e.target.value)}>
          <option value="positivo">Positivo</option><option value="negativo">Negativo</option><option value="neutro">Neutro</option>
        </select>
        <button>{editId ? "Salvar edição" : "Adicionar categoria"}</button>
        {editId && <button type="button" onClick={() => { setEditId(null); setForm(emptyDre()); }}>Cancelar</button>}
      </form>
    </div>
    <div className="panel">
      <h2>Categorias cadastradas</h2>
      <table><thead><tr><th>Ordem</th><th>Nome</th><th>Chave</th><th>Sinal</th><th>Ações</th></tr></thead><tbody>
        {categorias.map((c) => <tr key={c.id}><td>{c.ordem}</td><td>{c.nome}</td><td>{c.chave}</td><td>{c.sinal}</td><td><button onClick={() => { setEditId(c.id); setForm({ nome: c.nome, chave: c.chave, grupo: c.grupo, ordem: c.ordem, sinal: c.sinal, ativa: c.ativa }); }}>Editar</button><button onClick={() => onDelete(c.id)}>Apagar</button></td></tr>)}
      </tbody></table>
    </div>
  </section>;
}
