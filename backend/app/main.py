from collections import defaultdict
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Gestão Empresarial API",
    description="Core inicial sem login, sem variáveis e sem banco externo.",
    version="0.2.0",
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


class MovimentacaoCaixaCreate(BaseModel):
    data_movimento: str
    tipo: str
    descricao: str
    valor: float = Field(gt=0)
    origem: str = "manual"
    banco: str | None = None
    conta_bancaria: str | None = None
    plano_conta_id: str | None = None
    status: str = "confirmado"
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
movimentacoes_caixa: dict[str, dict] = {}
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


def criar_movimentacao_caixa_base(empresa_id: str, payload: MovimentacaoCaixaCreate) -> dict:
    item = payload.model_dump()
    item.update({"id": novo_id(), "empresa_id": empresa_id})
    movimentacoes_caixa[item["id"]] = item
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

    def add_lancamento(nome_conta: str, descricao: str, tipo: str, valor: float) -> None:
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

    def add_caixa(data: str, nome_conta: str, descricao: str, tipo: str, valor: float) -> None:
        criar_movimentacao_caixa_base(
            empresa_id,
            MovimentacaoCaixaCreate(
                data_movimento=data,
                tipo=tipo,
                descricao=descricao,
                valor=valor,
                origem="manual",
                banco="Banco exemplo",
                conta_bancaria="Conta principal",
                plano_conta_id=contas_por_nome[nome_conta]["id"],
                status="confirmado",
            ),
        )

    add_lancamento("Vendas ColorGlass", "Receita junho/2025", "receita", 82379.72)
    add_lancamento("Insumos e acessórios", "Insumos junho/2025", "despesa", 13189.20)
    add_lancamento("Pintura", "Pintura junho/2025", "despesa", 10905.00)
    add_lancamento("Vidro", "Vidro junho/2025", "despesa", 9036.17)
    add_lancamento("Folha", "Folha junho/2025", "despesa", 9034.73)
    add_lancamento("Outros gastos", "Outros gastos junho/2025", "despesa", 4439.75)
    add_lancamento("Comissão", "Comissão junho/2025", "despesa", 2357.32)
    add_lancamento("Frete", "Frete junho/2025", "despesa", 2189.98)
    add_lancamento("Pró-labore", "Pró-labore junho/2025", "despesa", 2000.00)
    add_lancamento("Alumínio / Perfis", "Perfis junho/2025", "despesa", 1272.77)
    add_lancamento("Sistemas", "Sistemas junho/2025", "despesa", 414.00)

    add_caixa("2025-06-03", "Vendas ColorGlass", "Recebimentos de clientes", "entrada", 28000.00)
    add_caixa("2025-06-10", "Vendas ColorGlass", "Recebimentos de clientes", "entrada", 21000.00)
    add_caixa("2025-06-20", "Vendas ColorGlass", "Recebimentos de clientes", "entrada", 33379.72)
    add_caixa("2025-06-05", "Insumos e acessórios", "Pagamento insumos", "saida", 13189.20)
    add_caixa("2025-06-07", "Pintura", "Pagamento pintura", "saida", 10905.00)
    add_caixa("2025-06-11", "Vidro", "Pagamento vidro", "saida", 9036.17)
    add_caixa("2025-06-14", "Folha", "Pagamento folha", "saida", 9034.73)
    add_caixa("2025-06-16", "Outros gastos", "Pagamento outros gastos", "saida", 4439.75)
    add_caixa("2025-06-17", "Comissão", "Pagamento comissão", "saida", 2357.32)
    add_caixa("2025-06-21", "Frete", "Pagamento frete", "saida", 2189.98)
    add_caixa("2025-06-25", "Pró-labore", "Pagamento pró-labore", "saida", 2000.00)
    add_caixa("2025-06-26", "Alumínio / Perfis", "Pagamento perfis", "saida", 1272.77)
    add_caixa("2025-06-28", "Sistemas", "Pagamento sistemas", "saida", 414.00)

    criar_meta_base(empresa_id, MetaCreate(nome="Faturamento mensal", tipo_meta="receita", valor_meta=100000, periodo="2025-06"))
    criar_meta_base(empresa_id, MetaCreate(nome="Lucro líquido mínimo", tipo_meta="lucro", valor_meta=15000, periodo="2025-06"))


seed()


def empresa_ou_404(empresa_id: str) -> dict:
    empresa = empresas.get(empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa


def conta_ou_none(plano_conta_id: str | None) -> dict | None:
    if not plano_conta_id:
        return None
    return plano_contas.get(plano_conta_id)


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


def calcular_fluxo_caixa(empresa_id: str | None, data_inicio: str, data_fim: str) -> dict:
    movimentos = []
    totais_por_dia = defaultdict(lambda: {"entradas": 0.0, "saidas": 0.0, "saldo": 0.0})
    totais_por_categoria = defaultdict(lambda: {"entradas": 0.0, "saidas": 0.0, "saldo": 0.0})

    entradas = 0.0
    saidas = 0.0

    for movimento in movimentacoes_caixa.values():
        if empresa_id and movimento["empresa_id"] != empresa_id:
            continue
        if movimento["data_movimento"] < data_inicio or movimento["data_movimento"] > data_fim:
            continue

        conta = conta_ou_none(movimento.get("plano_conta_id"))
        categoria = conta["nome"] if conta else "Sem categoria"
        valor = float(movimento["valor"])
        tipo = movimento["tipo"]

        if tipo == "entrada":
            entradas += valor
            totais_por_dia[movimento["data_movimento"]]["entradas"] += valor
            totais_por_categoria[categoria]["entradas"] += valor
        else:
            saidas += valor
            totais_por_dia[movimento["data_movimento"]]["saidas"] += valor
            totais_por_categoria[categoria]["saidas"] += valor

        movimentos.append({**movimento, "categoria": categoria})

    for item in totais_por_dia.values():
        item["saldo"] = item["entradas"] - item["saidas"]
        item["entradas"] = round(item["entradas"], 2)
        item["saidas"] = round(item["saidas"], 2)
        item["saldo"] = round(item["saldo"], 2)

    for item in totais_por_categoria.values():
        item["saldo"] = item["entradas"] - item["saidas"]
        item["entradas"] = round(item["entradas"], 2)
        item["saidas"] = round(item["saidas"], 2)
        item["saldo"] = round(item["saldo"], 2)

    movimentos_ordenados = sorted(movimentos, key=lambda item: item["data_movimento"], reverse=True)

    return {
        "empresa_id": empresa_id,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "entradas": round(entradas, 2),
        "saidas": round(saidas, 2),
        "saldo_periodo": round(entradas - saidas, 2),
        "movimentos": movimentos_ordenados,
        "por_dia": [
            {"data": data, **valores}
            for data, valores in sorted(totais_por_dia.items())
        ],
        "por_categoria": [
            {"categoria": categoria, **valores}
            for categoria, valores in sorted(totais_por_categoria.items())
        ],
    }


def dashboard_empresa(empresa_id: str, competencia: str) -> dict:
    empresa = empresa_ou_404(empresa_id)
    dre = calcular_dre(empresa_id, competencia)
    fluxo = calcular_fluxo_caixa(empresa_id, f"{competencia}-01", f"{competencia}-31")
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
        elif meta["tipo_meta"] == "caixa":
            realizado = fluxo["saldo_periodo"]

        progresso = 0 if meta["valor_meta"] == 0 else min((realizado / meta["valor_meta"]) * 100, 999)
        metas_resumo.append({**meta, "realizado": round(realizado, 2), "progresso": round(progresso, 2)})

    return {"empresa": empresa, "competencia": competencia, "dre": dre, "fluxo_caixa": fluxo, "metas": metas_resumo}


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


@app.get("/empresas/{empresa_id}/movimentacoes-caixa")
def listar_movimentacoes_caixa(
    empresa_id: str,
    data_inicio: str | None = Query(default=None),
    data_fim: str | None = Query(default=None),
) -> list[dict]:
    empresa_ou_404(empresa_id)
    itens = [m for m in movimentacoes_caixa.values() if m["empresa_id"] == empresa_id]
    if data_inicio:
        itens = [m for m in itens if m["data_movimento"] >= data_inicio]
    if data_fim:
        itens = [m for m in itens if m["data_movimento"] <= data_fim]
    return sorted(itens, key=lambda item: item["data_movimento"], reverse=True)


@app.post("/empresas/{empresa_id}/movimentacoes-caixa", status_code=201)
def criar_movimentacao_caixa(empresa_id: str, payload: MovimentacaoCaixaCreate) -> dict:
    empresa_ou_404(empresa_id)
    if payload.tipo not in {"entrada", "saida"}:
        raise HTTPException(status_code=400, detail="Tipo deve ser entrada ou saida")
    if payload.plano_conta_id:
        conta = plano_contas.get(payload.plano_conta_id)
        if not conta or conta["empresa_id"] != empresa_id:
            raise HTTPException(status_code=400, detail="Conta inválida para esta empresa")
    return criar_movimentacao_caixa_base(empresa_id, payload)


@app.get("/empresas/{empresa_id}/fluxo-caixa")
def fluxo_caixa_empresa(
    empresa_id: str,
    data_inicio: str = Query(default="2025-06-01"),
    data_fim: str = Query(default="2025-06-30"),
) -> dict:
    empresa_ou_404(empresa_id)
    return calcular_fluxo_caixa(empresa_id, data_inicio, data_fim)


@app.get("/fluxo-caixa/consolidado")
def fluxo_caixa_consolidado(
    data_inicio: str = Query(default="2025-06-01"),
    data_fim: str = Query(default="2025-06-30"),
) -> dict:
    return calcular_fluxo_caixa(None, data_inicio, data_fim)


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
