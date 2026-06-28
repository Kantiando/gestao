from collections import defaultdict
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Gestão Empresarial API", version="0.3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

EMPRESA_ID = "empresa-colorglass"


def novo_id(prefixo: str) -> str:
    return f"{prefixo}-{uuid4().hex[:10]}"


class EmpresaCreate(BaseModel):
    nome: str = Field(min_length=2)
    apelido: str | None = None
    cnpj: str | None = None


class DreCategoriaPayload(BaseModel):
    nome: str = Field(min_length=2)
    chave: str = Field(min_length=2)
    grupo: str = "operacional"
    ordem: int = 100
    sinal: str = "positivo"
    ativa: bool = True


class PlanoContaPayload(BaseModel):
    codigo: str = Field(min_length=1)
    nome: str = Field(min_length=2)
    tipo: str = "despesa_variavel"
    grupo: str = "Geral"
    dre_categoria_id: str | None = None
    ativo: bool = True


class MovimentoPayload(BaseModel):
    data_movimento: str
    competencia: str | None = None
    tipo: str
    descricao: str = Field(min_length=2)
    valor: float = Field(gt=0)
    plano_conta_id: str
    origem: str = "manual"
    banco: str | None = None
    conta_bancaria: str | None = None
    status: str = "confirmado"
    observacao: str | None = None


empresas = [{"id": EMPRESA_ID, "nome": "ColorGlass", "apelido": "ColorGlass", "cnpj": None, "ativa": True}]

dre_categorias = [
    {"id": "dre-receita", "empresa_id": EMPRESA_ID, "nome": "Receita Bruta", "chave": "receita_bruta", "grupo": "receita", "ordem": 10, "sinal": "positivo", "ativa": True},
    {"id": "dre-custos", "empresa_id": EMPRESA_ID, "nome": "Custos Variáveis", "chave": "custos_variaveis", "grupo": "custos", "ordem": 20, "sinal": "negativo", "ativa": True},
    {"id": "dre-despesas", "empresa_id": EMPRESA_ID, "nome": "Despesas Operacionais", "chave": "despesas_operacionais", "grupo": "despesas", "ordem": 30, "sinal": "negativo", "ativa": True},
    {"id": "dre-financeiras", "empresa_id": EMPRESA_ID, "nome": "Despesas Financeiras", "chave": "despesas_financeiras", "grupo": "financeiro", "ordem": 40, "sinal": "negativo", "ativa": True},
    {"id": "dre-investimentos", "empresa_id": EMPRESA_ID, "nome": "Investimentos", "chave": "investimentos", "grupo": "investimentos", "ordem": 50, "sinal": "neutro", "ativa": True},
]

plano_contas = [
    {"id": "pc-1", "empresa_id": EMPRESA_ID, "codigo": "1.1", "nome": "Vendas ColorGlass", "tipo": "receita", "grupo": "Receitas", "dre_categoria_id": "dre-receita", "ativo": True},
    {"id": "pc-2", "empresa_id": EMPRESA_ID, "codigo": "2.1", "nome": "Alumínio / Perfis", "tipo": "custo_variavel", "grupo": "Custos Variáveis", "dre_categoria_id": "dre-custos", "ativo": True},
    {"id": "pc-3", "empresa_id": EMPRESA_ID, "codigo": "2.2", "nome": "Vidro", "tipo": "custo_variavel", "grupo": "Custos Variáveis", "dre_categoria_id": "dre-custos", "ativo": True},
    {"id": "pc-4", "empresa_id": EMPRESA_ID, "codigo": "2.3", "nome": "Pintura", "tipo": "custo_variavel", "grupo": "Custos Variáveis", "dre_categoria_id": "dre-custos", "ativo": True},
    {"id": "pc-5", "empresa_id": EMPRESA_ID, "codigo": "2.4", "nome": "Insumos e acessórios", "tipo": "custo_variavel", "grupo": "Custos Variáveis", "dre_categoria_id": "dre-custos", "ativo": True},
    {"id": "pc-6", "empresa_id": EMPRESA_ID, "codigo": "2.5", "nome": "Frete", "tipo": "despesa_variavel", "grupo": "Despesas Variáveis", "dre_categoria_id": "dre-despesas", "ativo": True},
    {"id": "pc-7", "empresa_id": EMPRESA_ID, "codigo": "3.1", "nome": "Folha", "tipo": "despesa_fixa", "grupo": "Despesas Fixas", "dre_categoria_id": "dre-despesas", "ativo": True},
    {"id": "pc-8", "empresa_id": EMPRESA_ID, "codigo": "3.2", "nome": "Pró-labore", "tipo": "despesa_fixa", "grupo": "Despesas Fixas", "dre_categoria_id": "dre-despesas", "ativo": True},
    {"id": "pc-9", "empresa_id": EMPRESA_ID, "codigo": "3.3", "nome": "Sistemas", "tipo": "despesa_fixa", "grupo": "Despesas Fixas", "dre_categoria_id": "dre-despesas", "ativo": True},
    {"id": "pc-10", "empresa_id": EMPRESA_ID, "codigo": "3.4", "nome": "Comissão", "tipo": "despesa_variavel", "grupo": "Despesas Variáveis", "dre_categoria_id": "dre-despesas", "ativo": True},
    {"id": "pc-11", "empresa_id": EMPRESA_ID, "codigo": "3.5", "nome": "Outros gastos", "tipo": "despesa_variavel", "grupo": "Despesas Variáveis", "dre_categoria_id": "dre-despesas", "ativo": True},
]

movimentos = [
    {"id": "m-1", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-03", "competencia": "2025-06", "tipo": "entrada", "descricao": "Recebimentos de clientes", "valor": 28000.00, "plano_conta_id": "pc-1", "origem": "manual", "status": "confirmado"},
    {"id": "m-2", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-10", "competencia": "2025-06", "tipo": "entrada", "descricao": "Recebimentos de clientes", "valor": 21000.00, "plano_conta_id": "pc-1", "origem": "manual", "status": "confirmado"},
    {"id": "m-3", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-20", "competencia": "2025-06", "tipo": "entrada", "descricao": "Recebimentos de clientes", "valor": 33379.72, "plano_conta_id": "pc-1", "origem": "manual", "status": "confirmado"},
    {"id": "m-4", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-05", "competencia": "2025-06", "tipo": "saida", "descricao": "Pagamento insumos", "valor": 13189.20, "plano_conta_id": "pc-5", "origem": "manual", "status": "confirmado"},
    {"id": "m-5", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-07", "competencia": "2025-06", "tipo": "saida", "descricao": "Pagamento pintura", "valor": 10905.00, "plano_conta_id": "pc-4", "origem": "manual", "status": "confirmado"},
    {"id": "m-6", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-11", "competencia": "2025-06", "tipo": "saida", "descricao": "Pagamento vidro", "valor": 9036.17, "plano_conta_id": "pc-3", "origem": "manual", "status": "confirmado"},
    {"id": "m-7", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-14", "competencia": "2025-06", "tipo": "saida", "descricao": "Pagamento folha", "valor": 9034.73, "plano_conta_id": "pc-7", "origem": "manual", "status": "confirmado"},
    {"id": "m-8", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-16", "competencia": "2025-06", "tipo": "saida", "descricao": "Pagamento outros gastos", "valor": 4439.75, "plano_conta_id": "pc-11", "origem": "manual", "status": "confirmado"},
    {"id": "m-9", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-17", "competencia": "2025-06", "tipo": "saida", "descricao": "Pagamento comissão", "valor": 2357.32, "plano_conta_id": "pc-10", "origem": "manual", "status": "confirmado"},
    {"id": "m-10", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-21", "competencia": "2025-06", "tipo": "saida", "descricao": "Pagamento frete", "valor": 2189.98, "plano_conta_id": "pc-6", "origem": "manual", "status": "confirmado"},
]

metas = [
    {"id": "meta-1", "empresa_id": EMPRESA_ID, "nome": "Faturamento mensal", "tipo_meta": "receita", "valor_meta": 100000, "periodo": "2025-06", "ativa": True},
    {"id": "meta-2", "empresa_id": EMPRESA_ID, "nome": "Lucro líquido mínimo", "tipo_meta": "lucro", "valor_meta": 15000, "periodo": "2025-06", "ativa": True},
]


def empresa_ou_404(empresa_id: str) -> dict:
    for empresa in empresas:
        if empresa["id"] == empresa_id:
            return empresa
    raise HTTPException(status_code=404, detail="Empresa não encontrada")


def item_ou_404(lista: list[dict], item_id: str, nome: str) -> dict:
    for item in lista:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"{nome} não encontrado")


def conta_por_id(conta_id: str | None) -> dict | None:
    return next((conta for conta in plano_contas if conta["id"] == conta_id), None)


def dre_categoria_por_id(categoria_id: str | None) -> dict | None:
    return next((categoria for categoria in dre_categorias if categoria["id"] == categoria_id), None)


def movimento_com_contexto(movimento: dict) -> dict:
    conta = conta_por_id(movimento.get("plano_conta_id"))
    categoria = dre_categoria_por_id(conta.get("dre_categoria_id") if conta else None)
    return {
        **movimento,
        "conta": conta["nome"] if conta else "Sem conta",
        "categoria": conta["nome"] if conta else "Sem conta",
        "dre_categoria": categoria["nome"] if categoria else "Sem DRE",
        "dre_categoria_id": categoria["id"] if categoria else None,
        "dre_chave": categoria["chave"] if categoria else "nao_classificado",
    }


def calcular_fluxo(empresa_id: str | None, data_inicio: str, data_fim: str) -> dict:
    filtrados = [movimento_com_contexto(m) for m in movimentos if (not empresa_id or m["empresa_id"] == empresa_id) and data_inicio <= m["data_movimento"] <= data_fim]
    entradas = sum(float(m["valor"]) for m in filtrados if m["tipo"] == "entrada")
    saidas = sum(float(m["valor"]) for m in filtrados if m["tipo"] == "saida")
    por_dia = defaultdict(lambda: {"entradas": 0.0, "saidas": 0.0, "saldo": 0.0})
    for m in filtrados:
        campo = "entradas" if m["tipo"] == "entrada" else "saidas"
        por_dia[m["data_movimento"]][campo] += float(m["valor"])
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
    }


def calcular_dre(empresa_id: str | None, competencia: str) -> dict:
    linhas = defaultdict(float)
    detalhamento = defaultdict(list)
    categorias = sorted(dre_categorias, key=lambda c: c["ordem"])
    for m in movimentos:
        if empresa_id and m["empresa_id"] != empresa_id:
            continue
        if m.get("competencia") != competencia:
            continue
        conta = conta_por_id(m.get("plano_conta_id"))
        categoria = dre_categoria_por_id(conta.get("dre_categoria_id") if conta else None)
        if not categoria:
            continue
        chave = categoria["chave"]
        valor = float(m["valor"])
        linhas[chave] += valor
        detalhamento[chave].append({"descricao": m["descricao"], "conta": conta["nome"], "valor": valor, "tipo": m["tipo"]})

    receita = linhas["receita_bruta"]
    custos = linhas["custos_variaveis"]
    despesas = linhas["despesas_operacionais"]
    financeiras = linhas["despesas_financeiras"]
    investimentos = linhas["investimentos"]
    lucro_bruto = receita - custos
    resultado_operacional = lucro_bruto - despesas
    lucro_liquido = resultado_operacional - financeiras
    margem = 0 if receita == 0 else round((lucro_liquido / receita) * 100, 2)
    linhas_customizadas = []
    for categoria in categorias:
        chave = categoria["chave"]
        linhas_customizadas.append({**categoria, "valor": round(linhas[chave], 2), "detalhamento": detalhamento[chave]})
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
        "margem_liquida_percentual": margem,
        "linhas_customizadas": linhas_customizadas,
        "detalhamento": dict(detalhamento),
    }


def dashboard(empresa_id: str, competencia: str) -> dict:
    empresa = empresa_ou_404(empresa_id)
    dre = calcular_dre(empresa_id, competencia)
    fluxo = calcular_fluxo(empresa_id, f"{competencia}-01", f"{competencia}-31")
    metas_resumo = []
    for meta in [m for m in metas if m["empresa_id"] == empresa_id and m["periodo"] == competencia]:
        realizado = dre["receita_bruta"] if meta["tipo_meta"] == "receita" else dre["lucro_liquido"]
        progresso = 0 if meta["valor_meta"] == 0 else round((realizado / meta["valor_meta"]) * 100, 2)
        metas_resumo.append({**meta, "realizado": round(realizado, 2), "progresso": progresso})
    return {"empresa": empresa, "competencia": competencia, "dre": dre, "fluxo_caixa": fluxo, "metas": metas_resumo}


@app.get("/")
def root() -> dict:
    return {"app": "gestao-api", "version": "0.3.0", "status": "running"}


@app.get("/version")
def version() -> dict:
    return {"app": "gestao-api", "version": "0.3.0", "crud_operacional": True}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/empresas")
def listar_empresas() -> list[dict]:
    return empresas


@app.post("/empresas", status_code=201)
def criar_empresa(payload: EmpresaCreate) -> dict:
    empresa = {"id": novo_id("empresa"), "ativa": True, **payload.model_dump()}
    empresas.append(empresa)
    return empresa


@app.get("/empresas/{empresa_id}/dashboard")
def obter_dashboard(empresa_id: str, competencia: str = Query(default="2025-06")) -> dict:
    return dashboard(empresa_id, competencia)


@app.get("/empresas/{empresa_id}/dre-categorias")
def listar_dre_categorias(empresa_id: str) -> list[dict]:
    empresa_ou_404(empresa_id)
    return sorted([c for c in dre_categorias if c["empresa_id"] == empresa_id], key=lambda c: c["ordem"])


@app.post("/empresas/{empresa_id}/dre-categorias", status_code=201)
def criar_dre_categoria(empresa_id: str, payload: DreCategoriaPayload) -> dict:
    empresa_ou_404(empresa_id)
    item = {"id": novo_id("dre"), "empresa_id": empresa_id, **payload.model_dump()}
    dre_categorias.append(item)
    return item


@app.put("/empresas/{empresa_id}/dre-categorias/{categoria_id}")
def editar_dre_categoria(empresa_id: str, categoria_id: str, payload: DreCategoriaPayload) -> dict:
    empresa_ou_404(empresa_id)
    item = item_ou_404(dre_categorias, categoria_id, "Categoria DRE")
    item.update(payload.model_dump())
    return item


@app.delete("/empresas/{empresa_id}/dre-categorias/{categoria_id}")
def apagar_dre_categoria(empresa_id: str, categoria_id: str) -> dict:
    empresa_ou_404(empresa_id)
    if any(c.get("dre_categoria_id") == categoria_id for c in plano_contas):
        raise HTTPException(status_code=400, detail="Categoria está em uso no plano de contas")
    dre_categorias[:] = [c for c in dre_categorias if c["id"] != categoria_id]
    return {"ok": True}


@app.get("/empresas/{empresa_id}/plano-contas")
def listar_plano_contas(empresa_id: str) -> list[dict]:
    empresa_ou_404(empresa_id)
    itens = []
    for conta in sorted([c for c in plano_contas if c["empresa_id"] == empresa_id], key=lambda c: c["codigo"]):
        categoria = dre_categoria_por_id(conta.get("dre_categoria_id"))
        itens.append({**conta, "dre_categoria": categoria["nome"] if categoria else "Sem DRE", "dre_chave": categoria["chave"] if categoria else None})
    return itens


@app.post("/empresas/{empresa_id}/plano-contas", status_code=201)
def criar_plano_conta(empresa_id: str, payload: PlanoContaPayload) -> dict:
    empresa_ou_404(empresa_id)
    if payload.dre_categoria_id:
        item_ou_404(dre_categorias, payload.dre_categoria_id, "Categoria DRE")
    item = {"id": novo_id("pc"), "empresa_id": empresa_id, **payload.model_dump()}
    plano_contas.append(item)
    return item


@app.put("/empresas/{empresa_id}/plano-contas/{conta_id}")
def editar_plano_conta(empresa_id: str, conta_id: str, payload: PlanoContaPayload) -> dict:
    empresa_ou_404(empresa_id)
    item = item_ou_404(plano_contas, conta_id, "Conta")
    item.update(payload.model_dump())
    return item


@app.delete("/empresas/{empresa_id}/plano-contas/{conta_id}")
def apagar_plano_conta(empresa_id: str, conta_id: str) -> dict:
    empresa_ou_404(empresa_id)
    if any(m.get("plano_conta_id") == conta_id for m in movimentos):
        raise HTTPException(status_code=400, detail="Conta está em uso em lançamentos de caixa")
    plano_contas[:] = [c for c in plano_contas if c["id"] != conta_id]
    return {"ok": True}


@app.get("/empresas/{empresa_id}/lancamentos")
def listar_lancamentos(empresa_id: str, competencia: str | None = Query(default=None)) -> list[dict]:
    empresa_ou_404(empresa_id)
    itens = [movimento_com_contexto(m) for m in movimentos if m["empresa_id"] == empresa_id]
    if competencia:
        itens = [m for m in itens if m.get("competencia") == competencia]
    return sorted(itens, key=lambda m: m["data_movimento"], reverse=True)


@app.get("/empresas/{empresa_id}/movimentacoes-caixa")
def listar_movimentacoes(empresa_id: str, data_inicio: str | None = None, data_fim: str | None = None) -> list[dict]:
    empresa_ou_404(empresa_id)
    itens = [movimento_com_contexto(m) for m in movimentos if m["empresa_id"] == empresa_id]
    if data_inicio:
        itens = [m for m in itens if m["data_movimento"] >= data_inicio]
    if data_fim:
        itens = [m for m in itens if m["data_movimento"] <= data_fim]
    return sorted(itens, key=lambda m: m["data_movimento"], reverse=True)


@app.post("/empresas/{empresa_id}/movimentacoes-caixa", status_code=201)
def criar_movimentacao(empresa_id: str, payload: MovimentoPayload) -> dict:
    empresa_ou_404(empresa_id)
    conta = item_ou_404(plano_contas, payload.plano_conta_id, "Conta")
    if conta["empresa_id"] != empresa_id:
        raise HTTPException(status_code=400, detail="Conta não pertence à empresa")
    item = {"id": novo_id("mov"), "empresa_id": empresa_id, **payload.model_dump()}
    if not item.get("competencia"):
        item["competencia"] = item["data_movimento"][:7]
    movimentos.append(item)
    return movimento_com_contexto(item)


@app.put("/empresas/{empresa_id}/movimentacoes-caixa/{movimento_id}")
def editar_movimentacao(empresa_id: str, movimento_id: str, payload: MovimentoPayload) -> dict:
    empresa_ou_404(empresa_id)
    item = item_ou_404(movimentos, movimento_id, "Movimentação")
    item.update(payload.model_dump())
    if not item.get("competencia"):
        item["competencia"] = item["data_movimento"][:7]
    return movimento_com_contexto(item)


@app.delete("/empresas/{empresa_id}/movimentacoes-caixa/{movimento_id}")
def apagar_movimentacao(empresa_id: str, movimento_id: str) -> dict:
    empresa_ou_404(empresa_id)
    movimentos[:] = [m for m in movimentos if m["id"] != movimento_id]
    return {"ok": True}


@app.get("/empresas/{empresa_id}/fluxo-caixa")
def fluxo_empresa(empresa_id: str, data_inicio: str = Query(default="2025-06-01"), data_fim: str = Query(default="2025-06-30")) -> dict:
    empresa_ou_404(empresa_id)
    return calcular_fluxo(empresa_id, data_inicio, data_fim)


@app.get("/fluxo-caixa/consolidado")
def fluxo_consolidado(data_inicio: str = Query(default="2025-06-01"), data_fim: str = Query(default="2025-06-30")) -> dict:
    return calcular_fluxo(None, data_inicio, data_fim)


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
    itens = [m for m in metas if m["empresa_id"] == empresa_id]
    if periodo:
        itens = [m for m in itens if m["periodo"] == periodo]
    return itens
