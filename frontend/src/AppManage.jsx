import { useEffect, useMemo, useState } from "react";
import { api, competencia, dataInicio, dataFim, money } from "./api.js";
import { FluxoEditor, emptyMov } from "./components/FluxoEditor.jsx";
import { PlanoEditor, emptyConta } from "./components/PlanoEditor.jsx";
import { DreEditor, emptyDre } from "./components/DreEditor.jsx";
import AnalyticsView from "./components/AnalyticsView.jsx";

export default function AppManage() {
  const [view, setView] = useState("fluxo");
  const [empresas, setEmpresas] = useState([]);
  const [empresaId, setEmpresaId] = useState("");
  const [dashboard, setDashboard] = useState(null);
  const [dre, setDre] = useState(null);
  const [categorias, setCategorias] = useState([]);
  const [contas, setContas] = useState([]);
  const [movimentos, setMovimentos] = useState([]);
  const [erro, setErro] = useState("");
  const [msg, setMsg] = useState("");
  const [dreForm, setDreForm] = useState(emptyDre());
  const [dreEditId, setDreEditId] = useState(null);
  const [contaForm, setContaForm] = useState(emptyConta());
  const [contaEditId, setContaEditId] = useState(null);
  const [movForm, setMovForm] = useState(emptyMov());
  const [movEditId, setMovEditId] = useState(null);

  const empresaAtual = useMemo(() => empresas.find((e) => e.id === empresaId), [empresas, empresaId]);

  async function loadBase() {
    const data = await api("/empresas");
    setEmpresas(data);
    if (!empresaId && data[0]) setEmpresaId(data[0].id);
  }

  async function loadEmpresa(id = empresaId) {
    if (!id) return;
    const [dash, cat, pcs, movs, dreData] = await Promise.all([
      api(`/empresas/${id}/dashboard?competencia=${competencia}`),
      api(`/empresas/${id}/dre-categorias`),
      api(`/empresas/${id}/plano-contas`),
      api(`/empresas/${id}/movimentacoes-caixa?data_inicio=${dataInicio}&data_fim=${dataFim}`),
      api(`/empresas/${id}/dre?competencia=${competencia}`),
    ]);
    setDashboard(dash); setCategorias(cat); setContas(pcs); setMovimentos(movs); setDre(dreData);
    if (!movForm.plano_conta_id && pcs[0]) setMovForm((old) => ({ ...old, plano_conta_id: pcs[0].id }));
    if (!contaForm.dre_categoria_id && cat[0]) setContaForm((old) => ({ ...old, dre_categoria_id: cat[0].id }));
  }

  useEffect(() => { loadBase().catch((e) => setErro(e.message)); }, []);
  useEffect(() => { loadEmpresa().catch((e) => setErro(e.message)); }, [empresaId]);

  async function refresh(text = "Atualizado") { await loadEmpresa(); setMsg(text); setErro(""); }

  async function salvarDre(e) {
    e.preventDefault();
    const body = JSON.stringify({ ...dreForm, ordem: Number(dreForm.ordem || 100) });
    if (dreEditId) await api(`/empresas/${empresaId}/dre-categorias/${dreEditId}`, { method: "PUT", body });
    else await api(`/empresas/${empresaId}/dre-categorias`, { method: "POST", body });
    setDreForm(emptyDre()); setDreEditId(null); await refresh("Categoria da DRE salva");
  }

  async function salvarConta(e) {
    e.preventDefault();
    const body = JSON.stringify(contaForm);
    if (contaEditId) await api(`/empresas/${empresaId}/plano-contas/${contaEditId}`, { method: "PUT", body });
    else await api(`/empresas/${empresaId}/plano-contas`, { method: "POST", body });
    setContaForm(emptyConta(categorias[0]?.id || "")); setContaEditId(null); await refresh("Conta salva");
  }

  async function salvarMov(e) {
    e.preventDefault();
    const body = JSON.stringify({ ...movForm, valor: Number(movForm.valor) });
    if (movEditId) await api(`/empresas/${empresaId}/movimentacoes-caixa/${movEditId}`, { method: "PUT", body });
    else await api(`/empresas/${empresaId}/movimentacoes-caixa`, { method: "POST", body });
    setMovForm(emptyMov(contas[0]?.id || "")); setMovEditId(null); await refresh("Lançamento salvo");
  }

  async function remove(path, text) { await api(path, { method: "DELETE" }); await refresh(text); }

  return <div className="app">
    <aside className="sidebar">
      <div className="brand"><div className="logo">G</div><div><strong>Gestão</strong><span>Operação financeira</span></div></div>
      <button className={view === "fluxo" ? "active" : ""} onClick={() => setView("fluxo")}>Fluxo de Caixa</button>
      <button className={view === "analises" ? "active" : ""} onClick={() => setView("analises")}>Análises</button>
      <button className={view === "plano" ? "active" : ""} onClick={() => setView("plano")}>Plano de Contas</button>
      <button className={view === "dre-config" ? "active" : ""} onClick={() => setView("dre-config")}>Categorias DRE</button>
      <button className={view === "dre" ? "active" : ""} onClick={() => setView("dre")}>DRE</button>
      <label>Empresa</label><select value={empresaId} onChange={(e) => setEmpresaId(e.target.value)}>{empresas.map((e) => <option key={e.id} value={e.id}>{e.apelido || e.nome}</option>)}</select>
    </aside>
    <main>
      <header><span>{empresaAtual?.nome || "Empresa"} · {competencia}</span><h1>{title(view)}</h1><p>Entrada/saída → plano de contas → categoria da DRE.</p></header>
      {erro && <div className="erro">{erro}</div>}{msg && <div className="panel"><strong>{msg}</strong></div>}
      {view === "fluxo" && <FluxoEditor dashboard={dashboard} movimentos={movimentos} contas={contas} form={movForm} setForm={setMovForm} editId={movEditId} setEditId={setMovEditId} onSubmit={salvarMov} onDelete={(id) => remove(`/empresas/${empresaId}/movimentacoes-caixa/${id}`, "Lançamento removido")} />}
      {view === "analises" && <AnalyticsView empresaId={empresaId} />}
      {view === "plano" && <PlanoEditor contas={contas} categorias={categorias} form={contaForm} setForm={setContaForm} editId={contaEditId} setEditId={setContaEditId} onSubmit={salvarConta} onDelete={(id) => remove(`/empresas/${empresaId}/plano-contas/${id}`, "Conta removida")} />}
      {view === "dre-config" && <DreEditor categorias={categorias} form={dreForm} setForm={setDreForm} editId={dreEditId} setEditId={setDreEditId} onSubmit={salvarDre} onDelete={(id) => remove(`/empresas/${empresaId}/dre-categorias/${id}`, "Categoria removida")} />}
      {view === "dre" && <DreView dre={dre} />}
    </main>
  </div>;
}

function title(view) { return { fluxo: "Lançamentos do Fluxo de Caixa", analises: "Análises Gerenciais", plano: "Plano de Contas", "dre-config": "Categorias da DRE", dre: "DRE Gerencial" }[view]; }

function DreView({ dre }) {
  return <div className="panel"><h2>DRE livre por categorias</h2><table><thead><tr><th>Ordem</th><th>Categoria</th><th>Chave</th><th>Valor</th></tr></thead><tbody>{(dre?.linhas_customizadas || []).map((l) => <tr key={l.id}><td>{l.ordem}</td><td>{l.nome}</td><td>{l.chave}</td><td>{money(l.valor)}</td></tr>)}</tbody></table><h2>Resumo</h2><table><tbody><tr><td>Receita Bruta</td><td>{money(dre?.receita_bruta)}</td></tr><tr><td>Custos Variáveis</td><td>{money(dre?.custos_variaveis)}</td></tr><tr><td>Lucro Líquido</td><td>{money(dre?.lucro_liquido)}</td></tr></tbody></table></div>;
}
