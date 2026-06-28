from collections import defaultdict
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Gestão Empresarial API",
    description="Core inicial sem login, sem variáveis e sem banco externo.",
    version="0.1.0",
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


class PlanoContaCreate(BaseModel):
    codigo: str
    nome: str
    tipo: str
    grupo: str
    dre_linha: str
    ativo: bool = True


class LancamentoCreate(BaseModel):
    plano_conta_id: str
    data_lancamento: str
    competencia: str
    tipo: str
    descricao: str
    valor: float = Field(gt=0)
    status: str = "pago"
    forma_pagamento: str | None = None
    observacao: str | None = None


class MetaCreate(BaseModel):
    nome: str
    tipo_meta: str
    valor_meta: float = Field(gt=0)
    periodo: str
    ativa: bool = True


empresas: dict[str, dict] = {}
plano_contas: dict[str, dict] = {}
lancamentos: dict[str, dict] = {}
metas: dict[str, dict] = {}


def novo_id() -> str:
    return str(uuid4())


def criar_empresa_base(payload: EmpresaCreate) -> dict:
    item = payload.model_dump()
    item.update({"id": novo_id(), "ativa": True})
    empresas[item["id"]] = item
    return item


def criar_conta_base(empresa_id: str, payload: PlanoContaCreate) -> dict:
    item = payload.model_dump()
    item.update({"id": novo_id(), "empresa_id": empresa_id})
    plano_contas[item["id"]] = item
    return item


def criar_lancamento_base(empresa_id: str, payload: LancamentoCreate) -> dict:
    item = payload.model_dump()
    item.update({"id": novo_id(), "empresa_id": empresa_id})
    lancamentos[item["id"]] = item
    return item


def criar_meta_base(empresa_id: str, payload: MetaCreate) -> dict:
    item = payload.model_dump()
    item.update({"id": novo_id(), "empresa_id": empresa_id})
    metas[item["id"]] = item
    return item


def seed() -> None:
    if empresas:
        return

    colorglass = criar_empresa_base(EmpresaCreate(nome="ColorGlass", apelido="ColorGlass"))
    empresa_id = colorglass["id"]

    contas_seed = [
        ("1.1", "Vendas ColorGlass", "receita", "Receitas", "receita_bruta"),
        ("2.1", "Alumínio / Perfis", "custo_variavel", "Custos Variáveis", "custos_variaveis"),
        ("2.2", "Vidro", "custo_variavel", "Custos Variáveis", "custos_variaveis"),
        ("2.3", "Pintura", "custo_variavel", "Custos Variáveis", "custos_variaveis"),
        ("2.4", "Insumos e acessórios", "custo_variavel", "Custos Variáveis", "custos_variaveis"),
        ("2.5", "Frete", "despesa_variavel", "Despesas Variáveis", "despesas_operacionais"),
        ("3.1", "Folha", "despesa_fixa", "Despesas Fixas", "despesas_operacionais"),
        ("3.2", "Pró-labore", "despesa_fixa", "Despesas Fixas", "despesas_operacionais"),
        ("3.3", "Sistemas", "despesa_fixa", "Despesas Fixas", "despesas_operacionais"),
        ("3.4", "Comissão", "despesa_variavel", "Despesas Variáveis", "despesas_operacionais"),
        ("3.5", "Outros gastos", "despesa_variavel", "Despesas Variáveis", "despesas_operacionais"),
        ("4.1", "Máquinas e equipamentos", "investimento", "Investimentos", "investimentos"),
    ]

    contas_por_nome = {}
    for codigo, nome, tipo, grupo, dre_linha in contas_seed:
        conta = criar_conta_base(
            empresa_id,
            PlanoContaCreate(codigo=codigo, nome=nome, tipo=tipo, grupo=grupo, dre_linha=dre_linha),
        )
        contas_por_nome[nome] = conta

    def add(nome_conta: str, descricao: str, tipo: str, valor: float) -> None:
        criar_lancamento_base(
            empresa_id,
            LancamentoCreate(
                plano_conta_id=contas_por_nome[nome_conta]["id"],
                data_lancamento="2025-06-30",
                competencia="2025-06",
                tipo=tipo,
                descricao=descricao,
                valor=valor,
                status="pago",
                forma_pagamento="manual",
            ),
        )

    add("Vendas ColorGlass", "Receita junho/2025", "receita", 82379.72)
    add("Insumos e acessórios", "Insumos junho/2025", "despesa", 13189.20)
    add("Pintura", "Pintura junho/2025", "despesa", 10905.00)
    add("Vidro", "Vidro junho/2025", "despesa", 9036.17)
    add("Folha", "Folha junho/2025", "despesa", 9034.73)
    add("Outros gastos", "Outros gastos junho/2025", "despesa", 4439.75)
    add("Comissão", "Comissão junho/2025", "despesa", 2357.32)
    add("Frete", "Frete junho/2025", "despesa", 2189.98)
    add("Pró-labore", "Pró-labore junho/2025", "despesa", 2000.00)
    add("Alumínio / Perfis", "Perfis junho/2025", "despesa", 1272.77)
    add("Sistemas", "Sistemas junho/2025", "despesa", 414.00)

    criar_meta_base(empresa_id, MetaCreate(nome="Faturamento mensal", tipo_meta="receita", valor_meta=100000, periodo="2025-06"))
    criar_meta_base(empresa_id, MetaCreate(nome="Lucro líquido mínimo", tipo_meta="lucro", valor_meta=15000, periodo="2025-06"))


seed()


def empresa_ou_404(empresa_id: str) -> dict:
    empresa = empresas.get(empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa


def calcular_dre(empresa_id: str | None, competencia: str) -> dict:
    linhas = defaultdict(float)
    detalhamento = defaultdict(list)

    for lancamento in lancamentos.values():
        if empresa_id and lancamento["empresa_id"] != empresa_id:
            continue
        if lancamento["competencia"] != competencia:
            continue

        conta = plano_contas.get(lancamento["plano_conta_id"])
        if not conta:
            continue

        linha = conta["dre_linha"]
        valor = float(lancamento["valor"])
        linhas[linha] += valor
        detalhamento[linha].append({
            "descricao": lancamento["descricao"],
            "conta": conta["nome"],
            "valor": valor,
            "tipo": lancamento["tipo"],
        })

    receita = linhas["receita_bruta"]
    custos = linhas["custos_variaveis"]
    despesas = linhas["despesas_operacionais"]
    financeiras = linhas["despesas_financeiras"]
    investimentos = linhas["investimentos"]
    lucro_bruto = receita - custos
    resultado_operacional = lucro_bruto - despesas
    lucro_liquido = resultado_operacional - financeiras

    def percentual(valor: float) -> float:
        return 0 if receita == 0 else round((valor / receita) * 100, 2)

    return {
        "empresa_id": empresa_id,
        "competencia": competencia,
        "receita_bruta": round(receita, 2),
        "custos_variaveis": round(custos, 2),
        "lucro_bruto": round(lucro_bruto, 2),
        "despesas_operacionais": round(despesas, 2),
        "resultado_operacional": round(resultado_operacional, 2),
        "despesas_financeiras": round(financeiras, 2),
        "lucro_liquido": round(lucro_liquido, 2),
        "investimentos": round(investimentos, 2),
        "margem_bruta_percentual": percentual(lucro_bruto),
        "margem_liquida_percentual": percentual(lucro_liquido),
        "detalhamento": dict(detalhamento),
    }


def dashboard_empresa(empresa_id: str, competencia: str) -> dict:
    empresa = empresa_ou_404(empresa_id)
    dre = calcular_dre(empresa_id, competencia)
    metas_empresa = [m for m in metas.values() if m["empresa_id"] == empresa_id and m["periodo"] == competencia]

    metas_resumo = []
    for meta in metas_empresa:
        realizado = 0
        if meta["tipo_meta"] == "receita":
            realizado = dre["receita_bruta"]
        elif meta["tipo_meta"] == "lucro":
            realizado = dre["lucro_liquido"]
        elif meta["tipo_meta"] == "margem":
            realizado = dre["margem_liquida_percentual"]

        progresso = 0 if meta["valor_meta"] == 0 else min((realizado / meta["valor_meta"]) * 100, 999)
        metas_resumo.append({**meta, "realizado": round(realizado, 2), "progresso": round(progresso, 2)})

    return {"empresa": empresa, "competencia": competencia, "dre": dre, "metas": metas_resumo}


@app.get("/")
def root() -> dict:
    return {"app": "Gestão Empresarial API", "status": "running", "docs": "/docs"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/empresas")
def listar_empresas() -> list[dict]:
    return list(empresas.values())


@app.post("/empresas", status_code=201)
def criar_empresa(payload: EmpresaCreate) -> dict:
    return criar_empresa_base(payload)


@app.get("/empresas/{empresa_id}")
def obter_empresa(empresa_id: str) -> dict:
    return empresa_ou_404(empresa_id)


@app.get("/empresas/{empresa_id}/dashboard")
def obter_dashboard_empresa(empresa_id: str, competencia: str = Query(default="2025-06")) -> dict:
    return dashboard_empresa(empresa_id, competencia)


@app.get("/empresas/{empresa_id}/plano-contas")
def listar_plano_contas(empresa_id: str) -> list[dict]:
    empresa_ou_404(empresa_id)
    return sorted([c for c in plano_contas.values() if c["empresa_id"] == empresa_id], key=lambda c: c["codigo"])


@app.post("/empresas/{empresa_id}/plano-contas", status_code=201)
def criar_plano_conta(empresa_id: str, payload: PlanoContaCreate) -> dict:
    empresa_ou_404(empresa_id)
    return criar_conta_base(empresa_id, payload)


@app.get("/empresas/{empresa_id}/lancamentos")
def listar_lancamentos(empresa_id: str, competencia: str | None = Query(default=None)) -> list[dict]:
    empresa_ou_404(empresa_id)
    itens = [l for l in lancamentos.values() if l["empresa_id"] == empresa_id]
    if competencia:
        itens = [l for l in itens if l["competencia"] == competencia]
    return sorted(itens, key=lambda l: l["data_lancamento"], reverse=True)


@app.post("/empresas/{empresa_id}/lancamentos", status_code=201)
def criar_lancamento(empresa_id: str, payload: LancamentoCreate) -> dict:
    empresa_ou_404(empresa_id)
    conta = plano_contas.get(payload.plano_conta_id)
    if not conta or conta["empresa_id"] != empresa_id:
        raise HTTPException(status_code=400, detail="Conta inválida para esta empresa")
    return criar_lancamento_base(empresa_id, payload)


@app.get("/empresas/{empresa_id}/dre")
def dre_empresa(empresa_id: str, competencia: str = Query(default="2025-06")) -> dict:
    empresa_ou_404(empresa_id)
    return calcular_dre(empresa_id, competencia)


@app.get("/dre/consolidado")
def dre_consolidado(competencia: str = Query(default="2025-06")) -> dict:
    return calcular_dre(None, competencia)


@app.get("/empresas/{empresa_id}/metas")
def listar_metas(empresa_id: str, periodo: str | None = Query(default=None)) -> list[dict]:
    empresa_ou_404(empresa_id)
    itens = [m for m in metas.values() if m["empresa_id"] == empresa_id]
    if periodo:
        itens = [m for m in itens if m["periodo"] == periodo]
    return itens


@app.post("/empresas/{empresa_id}/metas", status_code=201)
def criar_meta(empresa_id: str, payload: MetaCreate) -> dict:
    empresa_ou_404(empresa_id)
    return criar_meta_base(empresa_id, payload)
