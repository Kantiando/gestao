from collections import defaultdict
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Gestão Empresarial API",
    description="Fallback principal para Render quando o serviço roda pela raiz do repositório.",
    version="0.2.2",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmpresaCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    apelido: str | None = None
    cnpj: str | None = None


EMPRESA_ID = str(uuid4())

empresas = [
    {
        "id": EMPRESA_ID,
        "nome": "ColorGlass",
        "apelido": "ColorGlass",
        "cnpj": None,
        "ativa": True,
    }
]

plano_contas = [
    {"id": "pc-1", "empresa_id": EMPRESA_ID, "codigo": "1.1", "nome": "Vendas ColorGlass", "tipo": "receita", "grupo": "Receitas", "dre_linha": "receita_bruta", "ativo": True},
    {"id": "pc-2", "empresa_id": EMPRESA_ID, "codigo": "2.1", "nome": "Alumínio / Perfis", "tipo": "custo_variavel", "grupo": "Custos Variáveis", "dre_linha": "custos_variaveis", "ativo": True},
    {"id": "pc-3", "empresa_id": EMPRESA_ID, "codigo": "2.2", "nome": "Vidro", "tipo": "custo_variavel", "grupo": "Custos Variáveis", "dre_linha": "custos_variaveis", "ativo": True},
    {"id": "pc-4", "empresa_id": EMPRESA_ID, "codigo": "2.3", "nome": "Pintura", "tipo": "custo_variavel", "grupo": "Custos Variáveis", "dre_linha": "custos_variaveis", "ativo": True},
    {"id": "pc-5", "empresa_id": EMPRESA_ID, "codigo": "2.4", "nome": "Insumos e acessórios", "tipo": "custo_variavel", "grupo": "Custos Variáveis", "dre_linha": "custos_variaveis", "ativo": True},
    {"id": "pc-6", "empresa_id": EMPRESA_ID, "codigo": "2.5", "nome": "Frete", "tipo": "despesa_variavel", "grupo": "Despesas Variáveis", "dre_linha": "despesas_operacionais", "ativo": True},
    {"id": "pc-7", "empresa_id": EMPRESA_ID, "codigo": "3.1", "nome": "Folha", "tipo": "despesa_fixa", "grupo": "Despesas Fixas", "dre_linha": "despesas_operacionais", "ativo": True},
    {"id": "pc-8", "empresa_id": EMPRESA_ID, "codigo": "3.2", "nome": "Pró-labore", "tipo": "despesa_fixa", "grupo": "Despesas Fixas", "dre_linha": "despesas_operacionais", "ativo": True},
    {"id": "pc-9", "empresa_id": EMPRESA_ID, "codigo": "3.3", "nome": "Sistemas", "tipo": "despesa_fixa", "grupo": "Despesas Fixas", "dre_linha": "despesas_operacionais", "ativo": True},
    {"id": "pc-10", "empresa_id": EMPRESA_ID, "codigo": "3.4", "nome": "Comissão", "tipo": "despesa_variavel", "grupo": "Despesas Variáveis", "dre_linha": "despesas_operacionais", "ativo": True},
    {"id": "pc-11", "empresa_id": EMPRESA_ID, "codigo": "3.5", "nome": "Outros gastos", "tipo": "despesa_variavel", "grupo": "Despesas Variáveis", "dre_linha": "despesas_operacionais", "ativo": True},
]

lancamentos = [
    {"id": "l-1", "empresa_id": EMPRESA_ID, "plano_conta_id": "pc-1", "data_lancamento": "2025-06-30", "competencia": "2025-06", "tipo": "receita", "descricao": "Receita junho/2025", "valor": 82379.72, "status": "pago"},
    {"id": "l-2", "empresa_id": EMPRESA_ID, "plano_conta_id": "pc-5", "data_lancamento": "2025-06-30", "competencia": "2025-06", "tipo": "despesa", "descricao": "Insumos junho/2025", "valor": 13189.20, "status": "pago"},
    {"id": "l-3", "empresa_id": EMPRESA_ID, "plano_conta_id": "pc-4", "data_lancamento": "2025-06-30", "competencia": "2025-06", "tipo": "despesa", "descricao": "Pintura junho/2025", "valor": 10905.00, "status": "pago"},
    {"id": "l-4", "empresa_id": EMPRESA_ID, "plano_conta_id": "pc-3", "data_lancamento": "2025-06-30", "competencia": "2025-06", "tipo": "despesa", "descricao": "Vidro junho/2025", "valor": 9036.17, "status": "pago"},
    {"id": "l-5", "empresa_id": EMPRESA_ID, "plano_conta_id": "pc-7", "data_lancamento": "2025-06-30", "competencia": "2025-06", "tipo": "despesa", "descricao": "Folha junho/2025", "valor": 9034.73, "status": "pago"},
    {"id": "l-6", "empresa_id": EMPRESA_ID, "plano_conta_id": "pc-11", "data_lancamento": "2025-06-30", "competencia": "2025-06", "tipo": "despesa", "descricao": "Outros gastos junho/2025", "valor": 4439.75, "status": "pago"},
    {"id": "l-7", "empresa_id": EMPRESA_ID, "plano_conta_id": "pc-10", "data_lancamento": "2025-06-30", "competencia": "2025-06", "tipo": "despesa", "descricao": "Comissão junho/2025", "valor": 2357.32, "status": "pago"},
    {"id": "l-8", "empresa_id": EMPRESA_ID, "plano_conta_id": "pc-6", "data_lancamento": "2025-06-30", "competencia": "2025-06", "tipo": "despesa", "descricao": "Frete junho/2025", "valor": 2189.98, "status": "pago"},
    {"id": "l-9", "empresa_id": EMPRESA_ID, "plano_conta_id": "pc-8", "data_lancamento": "2025-06-30", "competencia": "2025-06", "tipo": "despesa", "descricao": "Pró-labore junho/2025", "valor": 2000.00, "status": "pago"},
    {"id": "l-10", "empresa_id": EMPRESA_ID, "plano_conta_id": "pc-2", "data_lancamento": "2025-06-30", "competencia": "2025-06", "tipo": "despesa", "descricao": "Perfis junho/2025", "valor": 1272.77, "status": "pago"},
    {"id": "l-11", "empresa_id": EMPRESA_ID, "plano_conta_id": "pc-9", "data_lancamento": "2025-06-30", "competencia": "2025-06", "tipo": "despesa", "descricao": "Sistemas junho/2025", "valor": 414.00, "status": "pago"},
]

movimentos = [
    {"id": "m-1", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-03", "tipo": "entrada", "descricao": "Recebimentos de clientes", "valor": 28000.00, "categoria": "Vendas ColorGlass"},
    {"id": "m-2", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-10", "tipo": "entrada", "descricao": "Recebimentos de clientes", "valor": 21000.00, "categoria": "Vendas ColorGlass"},
    {"id": "m-3", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-20", "tipo": "entrada", "descricao": "Recebimentos de clientes", "valor": 33379.72, "categoria": "Vendas ColorGlass"},
    {"id": "m-4", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-05", "tipo": "saida", "descricao": "Pagamento insumos", "valor": 13189.20, "categoria": "Insumos e acessórios"},
    {"id": "m-5", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-07", "tipo": "saida", "descricao": "Pagamento pintura", "valor": 10905.00, "categoria": "Pintura"},
    {"id": "m-6", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-11", "tipo": "saida", "descricao": "Pagamento vidro", "valor": 9036.17, "categoria": "Vidro"},
    {"id": "m-7", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-14", "tipo": "saida", "descricao": "Pagamento folha", "valor": 9034.73, "categoria": "Folha"},
    {"id": "m-8", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-16", "tipo": "saida", "descricao": "Pagamento outros gastos", "valor": 4439.75, "categoria": "Outros gastos"},
    {"id": "m-9", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-17", "tipo": "saida", "descricao": "Pagamento comissão", "valor": 2357.32, "categoria": "Comissão"},
    {"id": "m-10", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-21", "tipo": "saida", "descricao": "Pagamento frete", "valor": 2189.98, "categoria": "Frete"},
    {"id": "m-11", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-25", "tipo": "saida", "descricao": "Pagamento pró-labore", "valor": 2000.00, "categoria": "Pró-labore"},
    {"id": "m-12", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-26", "tipo": "saida", "descricao": "Pagamento perfis", "valor": 1272.77, "categoria": "Alumínio / Perfis"},
    {"id": "m-13", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-28", "tipo": "saida", "descricao": "Pagamento sistemas", "valor": 414.00, "categoria": "Sistemas"},
]

metas = [
    {"id": "meta-1", "empresa_id": EMPRESA_ID, "nome": "Faturamento mensal", "tipo_meta": "receita", "valor_meta": 100000, "periodo": "2025-06", "ativa": True},
    {"id": "meta-2", "empresa_id": EMPRESA_ID, "nome": "Lucro líquido mínimo", "tipo_meta": "lucro", "valor_meta": 15000, "periodo": "2025-06", "ativa": True},
    {"id": "meta-3", "empresa_id": EMPRESA_ID, "nome": "Saldo de caixa mínimo", "tipo_meta": "caixa", "valor_meta": 10000, "periodo": "2025-06", "ativa": True},
]


def empresa_ou_404(empresa_id: str) -> dict:
    for empresa in empresas:
        if empresa["id"] == empresa_id:
            return empresa
    raise HTTPException(status_code=404, detail="Empresa não encontrada")


def conta_por_id(plano_conta_id: str) -> dict | None:
    return next((conta for conta in plano_contas if conta["id"] == plano_conta_id), None)


def calcular_dre(empresa_id: str | None, competencia: str) -> dict:
    linhas = defaultdict(float)
    detalhamento = defaultdict(list)

    for item in lancamentos:
        if empresa_id and item["empresa_id"] != empresa_id:
            continue
        if item["competencia"] != competencia:
            continue
        conta = conta_por_id(item["plano_conta_id"])
        if not conta:
            continue
        linha = conta["dre_linha"]
        valor = float(item["valor"])
        linhas[linha] += valor
        detalhamento[linha].append({"descricao": item["descricao"], "conta": conta["nome"], "valor": valor, "tipo": item["tipo"]})

    receita = linhas["receita_bruta"]
    custos = linhas["custos_variaveis"]
    despesas = linhas["despesas_operacionais"]
    lucro_bruto = receita - custos
    resultado_operacional = lucro_bruto - despesas
    lucro_liquido = resultado_operacional

    def pct(valor: float) -> float:
        return 0 if receita == 0 else round((valor / receita) * 100, 2)

    return {
        "empresa_id": empresa_id,
        "competencia": competencia,
        "receita_bruta": round(receita, 2),
        "custos_variaveis": round(custos, 2),
        "lucro_bruto": round(lucro_bruto, 2),
        "despesas_operacionais": round(despesas, 2),
        "resultado_operacional": round(resultado_operacional, 2),
        "despesas_financeiras": 0,
        "lucro_liquido": round(lucro_liquido, 2),
        "investimentos": 0,
        "margem_bruta_percentual": pct(lucro_bruto),
        "margem_liquida_percentual": pct(lucro_liquido),
        "detalhamento": dict(detalhamento),
    }


def calcular_fluxo(empresa_id: str | None, data_inicio: str, data_fim: str) -> dict:
    filtrados = [m for m in movimentos if (not empresa_id or m["empresa_id"] == empresa_id) and data_inicio <= m["data_movimento"] <= data_fim]
    entradas = sum(float(m["valor"]) for m in filtrados if m["tipo"] == "entrada")
    saidas = sum(float(m["valor"]) for m in filtrados if m["tipo"] == "saida")
    por_dia = defaultdict(lambda: {"entradas": 0.0, "saidas": 0.0, "saldo": 0.0})
    for m in filtrados:
        if m["tipo"] == "entrada":
            por_dia[m["data_movimento"]]["entradas"] += float(m["valor"])
        else:
            por_dia[m["data_movimento"]]["saidas"] += float(m["valor"])
    for valores in por_dia.values():
        valores["saldo"] = round(valores["entradas"] - valores["saidas"], 2)
        valores["entradas"] = round(valores["entradas"], 2)
        valores["saidas"] = round(valores["saidas"], 2)
    return {
        "empresa_id": empresa_id,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "entradas": round(entradas, 2),
        "saidas": round(saidas, 2),
        "saldo_periodo": round(entradas - saidas, 2),
        "movimentos": sorted(filtrados, key=lambda m: m["data_movimento"], reverse=True),
        "por_dia": [{"data": data, **valores} for data, valores in sorted(por_dia.items())],
        "por_categoria": [],
    }


def dashboard(empresa_id: str, competencia: str) -> dict:
    empresa = empresa_ou_404(empresa_id)
    dre = calcular_dre(empresa_id, competencia)
    fluxo = calcular_fluxo(empresa_id, f"{competencia}-01", f"{competencia}-31")
    metas_resumo = []
    for meta in [m for m in metas if m["empresa_id"] == empresa_id and m["periodo"] == competencia]:
        realizado = 0
        if meta["tipo_meta"] == "receita":
            realizado = dre["receita_bruta"]
        elif meta["tipo_meta"] == "lucro":
            realizado = dre["lucro_liquido"]
        elif meta["tipo_meta"] == "caixa":
            realizado = fluxo["saldo_periodo"]
        progresso = 0 if meta["valor_meta"] == 0 else round((realizado / meta["valor_meta"]) * 100, 2)
        metas_resumo.append({**meta, "realizado": round(realizado, 2), "progresso": progresso})
    return {"empresa": empresa, "competencia": competencia, "dre": dre, "fluxo_caixa": fluxo, "metas": metas_resumo}


@app.get("/")
def root() -> dict:
    return {"app": "gestao-api", "version": "0.2.2", "status": "running", "docs": "/docs"}


@app.get("/version")
def version() -> dict:
    return {"app": "gestao-api", "version": "0.2.2", "status": "running", "routes_ok": True}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/empresas")
def listar_empresas() -> list[dict]:
    return empresas


@app.post("/empresas", status_code=201)
def criar_empresa(payload: EmpresaCreate) -> dict:
    empresa = {"id": str(uuid4()), "ativa": True, **payload.model_dump()}
    empresas.append(empresa)
    return empresa


@app.get("/empresas/{empresa_id}")
def obter_empresa(empresa_id: str) -> dict:
    return empresa_ou_404(empresa_id)


@app.get("/empresas/{empresa_id}/dashboard")
def dashboard_empresa(empresa_id: str, competencia: str = Query(default="2025-06")) -> dict:
    return dashboard(empresa_id, competencia)


@app.get("/empresas/{empresa_id}/plano-contas")
def listar_plano_contas(empresa_id: str) -> list[dict]:
    empresa_ou_404(empresa_id)
    return sorted([c for c in plano_contas if c["empresa_id"] == empresa_id], key=lambda c: c["codigo"])


@app.get("/empresas/{empresa_id}/lancamentos")
def listar_lancamentos(empresa_id: str, competencia: str | None = Query(default=None)) -> list[dict]:
    empresa_ou_404(empresa_id)
    itens = [l for l in lancamentos if l["empresa_id"] == empresa_id]
    if competencia:
        itens = [l for l in itens if l["competencia"] == competencia]
    return sorted(itens, key=lambda l: l["data_lancamento"], reverse=True)


@app.get("/empresas/{empresa_id}/dre")
def dre_empresa(empresa_id: str, competencia: str = Query(default="2025-06")) -> dict:
    empresa_ou_404(empresa_id)
    return calcular_dre(empresa_id, competencia)


@app.get("/dre/consolidado")
def dre_consolidado(competencia: str = Query(default="2025-06")) -> dict:
    return calcular_dre(None, competencia)


@app.get("/empresas/{empresa_id}/fluxo-caixa")
def fluxo_empresa(empresa_id: str, data_inicio: str = Query(default="2025-06-01"), data_fim: str = Query(default="2025-06-30")) -> dict:
    empresa_ou_404(empresa_id)
    return calcular_fluxo(empresa_id, data_inicio, data_fim)


@app.get("/fluxo-caixa/consolidado")
def fluxo_consolidado(data_inicio: str = Query(default="2025-06-01"), data_fim: str = Query(default="2025-06-30")) -> dict:
    return calcular_fluxo(None, data_inicio, data_fim)


@app.get("/empresas/{empresa_id}/movimentacoes-caixa")
def listar_movimentacoes(empresa_id: str) -> list[dict]:
    empresa_ou_404(empresa_id)
    return [m for m in movimentos if m["empresa_id"] == empresa_id]


@app.get("/empresas/{empresa_id}/metas")
def listar_metas(empresa_id: str, periodo: str | None = Query(default=None)) -> list[dict]:
    empresa_ou_404(empresa_id)
    itens = [m for m in metas if m["empresa_id"] == empresa_id]
    if periodo:
        itens = [m for m in itens if m["periodo"] == periodo]
    return itens
