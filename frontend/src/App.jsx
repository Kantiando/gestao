import { useEffect, useMemo, useState } from "react";

const competencia = "2025-06";

function apiBaseUrl() {
  if (typeof window !== "undefined" && window.location.hostname.includes("onrender.com")) {
    return "https://gestao-api.onrender.com";
  }
  return "http://localhost:8000";
}

async function request(path) {
  const response = await fetch(`${apiBaseUrl()}${path}`);
  if (!response.ok) throw new Error("Erro ao conectar com a API");
  return response.json();
}

function money(value) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value || 0);
}

function percent(value) {
  return `${Number(value || 0).toFixed(2)}%`;
}

export default function App() {
  const [view, setView] = useState("geral");
  const [empresas, setEmpresas] = useState([]);
  const [empresaId, setEmpresaId] = useState("");
  const [consolidado, setConsolidado] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [planoContas, setPlanoContas] = useState([]);
  const [lancamentos, setLancamentos] = useState([]);
  const [erro, setErro] = useState("");

  const empresaAtual = useMemo(() => empresas.find((empresa) => empresa.id === empresaId), [empresas, empresaId]);

  useEffect(() => {
    async function load() {
      try {
        const [empresasData, dreData] = await Promise.all([
          request("/empresas"),
          request(`/dre/consolidado?competencia=${competencia}`),
        ]);
        setEmpresas(empresasData);
        setConsolidado(dreData);
        if (empresasData[0]) setEmpresaId(empresasData[0].id);
      } catch (error) {
        setErro("Backend não conectado. Rode o FastAPI em http://localhost:8000.");
      }
    }
    load();
  }, []);

  useEffect(() => {
    async function loadEmpresa() {
      if (!empresaId) return;
      try {
        const [dashData, contasData, lancamentosData] = await Promise.all([
          request(`/empresas/${empresaId}/dashboard?competencia=${competencia}`),
          request(`/empresas/${empresaId}/plano-contas`),
          request(`/empresas/${empresaId}/lancamentos?competencia=${competencia}`),
        ]);
        setDashboard(dashData);
        setPlanoContas(contasData);
        setLancamentos(lancamentosData);
      } catch (error) {
        setErro("Não foi possível carregar os dados da empresa.");
      }
    }
    loadEmpresa();
  }, [empresaId]);

  const dreEmpresa = dashboard?.dre;

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="logo">G</div>
          <div>
            <strong>Gestão</strong>
            <span>Holding privada</span>
          </div>
        </div>

        <button className={view === "geral" ? "active" : ""} onClick={() => setView("geral")}>Visão Geral</button>
        <button className={view === "empresa" ? "active" : ""} onClick={() => setView("empresa")}>Empresa</button>
        <button className={view === "dre" ? "active" : ""} onClick={() => setView("dre")}>DRE</button>
        <button className={view === "plano" ? "active" : ""} onClick={() => setView("plano")}>Plano de Contas</button>
        <button className={view === "metas" ? "active" : ""} onClick={() => setView("metas")}>Metas</button>

        <label>Empresa ativa</label>
        <select value={empresaId} onChange={(event) => setEmpresaId(event.target.value)}>
          {empresas.map((empresa) => <option key={empresa.id} value={empresa.id}>{empresa.apelido || empresa.nome}</option>)}
        </select>
      </aside>

      <main>
        <header>
          <span>Competência {competencia}</span>
          <h1>{titulo(view, empresaAtual)}</h1>
          <p>Core inicial sem login, sem Supabase e sem variáveis de ambiente.</p>
        </header>

        {erro ? <div className="erro">{erro}</div> : null}

        {view === "geral" && <Resumo dre={consolidado} empresas={empresas} />}
        {view === "empresa" && <Empresa dre={dreEmpresa} lancamentos={lancamentos} />}
        {view === "dre" && <Dre dre={dreEmpresa} />}
        {view === "plano" && <Plano contas={planoContas} />}
        {view === "metas" && <Metas metas={dashboard?.metas || []} />}
      </main>
    </div>
  );
}

function titulo(view, empresa) {
  const nome = empresa?.apelido || empresa?.nome || "Empresa";
  return {
    geral: "Visão geral da holding",
    empresa: `${nome} - Dashboard`,
    dre: `${nome} - DRE gerencial`,
    plano: `${nome} - Plano de contas`,
    metas: `${nome} - Metas`,
  }[view];
}

function Card({ label, value, hint }) {
  return <article className="card"><span>{label}</span><strong>{value}</strong>{hint && <small>{hint}</small>}</article>;
}

function Resumo({ dre, empresas }) {
  return <section className="grid"><Card label="Receita total" value={money(dre?.receita_bruta)} hint="consolidado" /><Card label="Custos variáveis" value={money(dre?.custos_variaveis)} /><Card label="Lucro líquido" value={money(dre?.lucro_liquido)} /><Card label="Margem líquida" value={percent(dre?.margem_liquida_percentual)} /><div className="panel"><h2>Empresas</h2>{empresas.map((empresa) => <p key={empresa.id}>{empresa.nome}</p>)}</div></section>;
}

function Empresa({ dre, lancamentos }) {
  return <section className="grid"><Card label="Receita" value={money(dre?.receita_bruta)} /><Card label="Despesas + custos" value={money((dre?.custos_variaveis || 0) + (dre?.despesas_operacionais || 0))} /><Card label="Lucro líquido" value={money(dre?.lucro_liquido)} /><Card label="Margem líquida" value={percent(dre?.margem_liquida_percentual)} /><TabelaLancamentos lancamentos={lancamentos} /></section>;
}

function Dre({ dre }) {
  const linhas = [["Receita Bruta", dre?.receita_bruta], ["(-) Custos Variáveis", dre?.custos_variaveis], ["= Lucro Bruto", dre?.lucro_bruto], ["(-) Despesas Operacionais", dre?.despesas_operacionais], ["= Resultado Operacional", dre?.resultado_operacional], ["= Lucro Líquido", dre?.lucro_liquido], ["Investimentos", dre?.investimentos]];
  return <div className="panel"><h2>DRE simplificada</h2><table><tbody>{linhas.map(([label, value]) => <tr key={label}><td>{label}</td><td>{money(value)}</td></tr>)}</tbody></table></div>;
}

function Plano({ contas }) {
  return <div className="panel"><h2>Plano de contas</h2><table><thead><tr><th>Código</th><th>Nome</th><th>Tipo</th><th>Grupo</th><th>DRE</th></tr></thead><tbody>{contas.map((conta) => <tr key={conta.id}><td>{conta.codigo}</td><td>{conta.nome}</td><td>{conta.tipo}</td><td>{conta.grupo}</td><td>{conta.dre_linha}</td></tr>)}</tbody></table></div>;
}

function Metas({ metas }) {
  return <section className="metas">{metas.map((meta) => <article key={meta.id} className="meta"><strong>{meta.nome}</strong><span>Meta: {money(meta.valor_meta)}</span><span>Realizado: {money(meta.realizado)}</span><div className="bar"><div style={{ width: `${Math.min(meta.progresso, 100)}%` }} /></div><small>{percent(meta.progresso)} concluído</small></article>)}</section>;
}

function TabelaLancamentos({ lancamentos }) {
  return <div className="panel"><h2>Lançamentos</h2><table><thead><tr><th>Data</th><th>Descrição</th><th>Tipo</th><th>Valor</th></tr></thead><tbody>{lancamentos.map((item) => <tr key={item.id}><td>{item.data_lancamento}</td><td>{item.descricao}</td><td>{item.tipo}</td><td>{money(item.valor)}</td></tr>)}</tbody></table></div>;
}
