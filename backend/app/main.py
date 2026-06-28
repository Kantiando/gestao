from collections import defaultdict
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Gestão Empresarial API", version="0.3.1-backend")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

EMPRESA_ID = "empresa-colorglass"
empresas = [{"id": EMPRESA_ID, "nome": "ColorGlass", "apelido": "ColorGlass", "cnpj": None, "ativa": True}]

dre_categorias = [
    {"id": "dre-receita", "empresa_id": EMPRESA_ID, "nome": "Receita Bruta", "chave": "receita_bruta", "grupo": "receita", "ordem": 10, "sinal": "positivo", "ativa": True},
    {"id": "dre-custos", "empresa_id": EMPRESA_ID, "nome": "Custos Variáveis", "chave": "custos_variaveis", "grupo": "custos", "ordem": 20, "sinal": "negativo", "ativa": True},
    {"id": "dre-despesas", "empresa_id": EMPRESA_ID, "nome": "Despesas Operacionais", "chave": "despesas_operacionais", "grupo": "despesas", "ordem": 30, "sinal": "negativo", "ativa": True},
]

plano_contas = [
    {"id": "pc-1", "empresa_id": EMPRESA_ID, "codigo": "1.1", "nome": "Vendas ColorGlass", "tipo": "receita", "grupo": "Receitas", "dre_categoria_id": "dre-receita", "ativo": True},
    {"id": "pc-2", "empresa_id": EMPRESA_ID, "codigo": "2.1", "nome": "Alumínio / Perfis", "tipo": "custo_variavel", "grupo": "Custos", "dre_categoria_id": "dre-custos", "ativo": True},
    {"id": "pc-3", "empresa_id": EMPRESA_ID, "codigo": "2.2", "nome": "Vidro", "tipo": "custo_variavel", "grupo": "Custos", "dre_categoria_id": "dre-custos", "ativo": True},
    {"id": "pc-4", "empresa_id": EMPRESA_ID, "codigo": "2.3", "nome": "Pintura", "tipo": "custo_variavel", "grupo": "Custos", "dre_categoria_id": "dre-custos", "ativo": True},
    {"id": "pc-5", "empresa_id": EMPRESA_ID, "codigo": "2.4", "nome": "Insumos e acessórios", "tipo": "custo_variavel", "grupo": "Custos", "dre_categoria_id": "dre-custos", "ativo": True},
    {"id": "pc-6", "empresa_id": EMPRESA_ID, "codigo": "3.1", "nome": "Folha", "tipo": "despesa_fixa", "grupo": "Despesas", "dre_categoria_id": "dre-despesas", "ativo": True},
    {"id": "pc-7", "empresa_id": EMPRESA_ID, "codigo": "3.2", "nome": "Sistemas", "tipo": "despesa_fixa", "grupo": "Despesas", "dre_categoria_id": "dre-despesas", "ativo": True},
]

movimentos = [
    {"id": "m-1", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-03", "competencia": "2025-06", "tipo": "entrada", "descricao": "Recebimentos de clientes", "valor": 82379.72, "plano_conta_id": "pc-1", "origem": "manual", "status": "confirmado"},
    {"id": "m-2", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-05", "competencia": "2025-06", "tipo": "saida", "descricao": "Pagamento insumos", "valor": 13189.20, "plano_conta_id": "pc-5", "origem": "manual", "status": "confirmado"},
    {"id": "m-3", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-07", "competencia": "2025-06", "tipo": "saida", "descricao": "Pagamento pintura", "valor": 10905.00, "plano_conta_id": "pc-4", "origem": "manual", "status": "confirmado"},
    {"id": "m-4", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-11", "competencia": "2025-06", "tipo": "saida", "descricao": "Pagamento vidro", "valor": 9036.17, "plano_conta_id": "pc-3", "origem": "manual", "status": "confirmado"},
    {"id": "m-5", "empresa_id": EMPRESA_ID, "data_movimento": "2025-06-14", "competencia": "2025-06", "tipo": "saida", "descricao": "Pagamento folha", "valor": 9034.73, "plano_conta_id": "pc-6", "origem": "manual", "status": "confirmado"},
]

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
    status: str = "confirmado"


def novo_id(prefixo): return f"{prefixo}-{uuid4().hex[:8]}"
def empresa_ou_404(empresa_id):
    if empresa_id != EMPRESA_ID: raise HTTPException(404, "Empresa não encontrada")
def conta(conta_id): return next((c for c in plano_contas if c["id"] == conta_id), None)
def cat(cat_id): return next((c for c in dre_categorias if c["id"] == cat_id), None)

def mov_ctx(m):
    c = conta(m.get("plano_conta_id")); d = cat(c.get("dre_categoria_id") if c else None)
    return {**m, "conta": c["nome"] if c else "Sem conta", "dre_categoria": d["nome"] if d else "Sem DRE", "dre_chave": d["chave"] if d else None}

def calc_fluxo(empresa_id, inicio, fim):
    itens = [mov_ctx(m) for m in movimentos if (empresa_id is None or m["empresa_id"] == empresa_id) and inicio <= m["data_movimento"] <= fim]
    ent = sum(m["valor"] for m in itens if m["tipo"] == "entrada"); sai = sum(m["valor"] for m in itens if m["tipo"] == "saida")
    return {"empresa_id": empresa_id, "data_inicio": inicio, "data_fim": fim, "entradas": round(ent,2), "saidas": round(sai,2), "saldo_periodo": round(ent-sai,2), "movimentos": sorted(itens, key=lambda x: x["data_movimento"], reverse=True), "por_dia": []}

def calc_dre(empresa_id, competencia):
    linhas = defaultdict(float); detalhes = defaultdict(list)
    for m in movimentos:
        if empresa_id and m["empresa_id"] != empresa_id: continue
        if m.get("competencia") != competencia: continue
        c = conta(m["plano_conta_id"]); d = cat(c.get("dre_categoria_id") if c else None)
        if not d: continue
        linhas[d["chave"]] += m["valor"]; detalhes[d["chave"]].append({"descricao": m["descricao"], "conta": c["nome"], "valor": m["valor"]})
    receita = linhas["receita_bruta"]; custos = linhas["custos_variaveis"]; despesas = linhas["despesas_operacionais"]
    lucro = receita - custos - despesas
    custom = [{**d, "valor": round(linhas[d["chave"]],2), "detalhamento": detalhes[d["chave"]]} for d in sorted(dre_categorias, key=lambda x: x["ordem"])]
    return {"empresa_id": empresa_id, "competencia": competencia, "receita_bruta": round(receita,2), "custos_variaveis": round(custos,2), "lucro_bruto": round(receita-custos,2), "despesas_operacionais": round(despesas,2), "resultado_operacional": round(lucro,2), "lucro_liquido": round(lucro,2), "margem_liquida_percentual": 0 if receita == 0 else round(lucro/receita*100,2), "linhas_customizadas": custom, "detalhamento": dict(detalhes)}

@app.get("/")
def root(): return {"app":"gestao-api","version":"0.3.1-backend","status":"ok"}
@app.get("/health")
def health(): return {"status":"ok"}
@app.get("/version")
def version(): return {"app":"gestao-api","version":"0.3.1-backend","rootDir":"backend"}
@app.get("/empresas")
def listar_empresas(): return empresas
@app.get("/empresas/{empresa_id}/dashboard")
def dashboard(empresa_id: str, competencia: str = Query("2025-06")):
    empresa_ou_404(empresa_id); return {"empresa": empresas[0], "competencia": competencia, "dre": calc_dre(empresa_id, competencia), "fluxo_caixa": calc_fluxo(empresa_id, f"{competencia}-01", f"{competencia}-31"), "metas": []}
@app.get("/empresas/{empresa_id}/dre-categorias")
def listar_categorias(empresa_id: str): empresa_ou_404(empresa_id); return sorted(dre_categorias, key=lambda x:x["ordem"])
@app.post("/empresas/{empresa_id}/dre-categorias", status_code=201)
def criar_categoria(empresa_id: str, p: DreCategoriaPayload): empresa_ou_404(empresa_id); item={"id":novo_id("dre"),"empresa_id":empresa_id,**p.model_dump()}; dre_categorias.append(item); return item
@app.put("/empresas/{empresa_id}/dre-categorias/{item_id}")
def editar_categoria(empresa_id: str, item_id: str, p: DreCategoriaPayload): empresa_ou_404(empresa_id); item=cat(item_id); item.update(p.model_dump()); return item
@app.delete("/empresas/{empresa_id}/dre-categorias/{item_id}")
def apagar_categoria(empresa_id: str, item_id: str): empresa_ou_404(empresa_id); dre_categorias[:] = [x for x in dre_categorias if x["id"] != item_id]; return {"ok":True}
@app.get("/empresas/{empresa_id}/plano-contas")
def listar_contas(empresa_id: str): empresa_ou_404(empresa_id); return [{**c,"dre_categoria":cat(c.get("dre_categoria_id"))["nome"] if cat(c.get("dre_categoria_id")) else "Sem DRE"} for c in plano_contas]
@app.post("/empresas/{empresa_id}/plano-contas", status_code=201)
def criar_conta(empresa_id: str, p: PlanoContaPayload): empresa_ou_404(empresa_id); item={"id":novo_id("pc"),"empresa_id":empresa_id,**p.model_dump()}; plano_contas.append(item); return item
@app.put("/empresas/{empresa_id}/plano-contas/{item_id}")
def editar_conta(empresa_id: str, item_id: str, p: PlanoContaPayload): empresa_ou_404(empresa_id); item=conta(item_id); item.update(p.model_dump()); return item
@app.delete("/empresas/{empresa_id}/plano-contas/{item_id}")
def apagar_conta(empresa_id: str, item_id: str): empresa_ou_404(empresa_id); plano_contas[:] = [x for x in plano_contas if x["id"] != item_id]; return {"ok":True}
@app.get("/empresas/{empresa_id}/movimentacoes-caixa")
def listar_movs(empresa_id: str, data_inicio: str | None = None, data_fim: str | None = None): empresa_ou_404(empresa_id); return [mov_ctx(m) for m in movimentos if (not data_inicio or m["data_movimento"] >= data_inicio) and (not data_fim or m["data_movimento"] <= data_fim)]
@app.post("/empresas/{empresa_id}/movimentacoes-caixa", status_code=201)
def criar_mov(empresa_id: str, p: MovimentoPayload): empresa_ou_404(empresa_id); item={"id":novo_id("mov"),"empresa_id":empresa_id,**p.model_dump()}; item["competencia"] = item.get("competencia") or item["data_movimento"][:7]; movimentos.append(item); return mov_ctx(item)
@app.put("/empresas/{empresa_id}/movimentacoes-caixa/{item_id}")
def editar_mov(empresa_id: str, item_id: str, p: MovimentoPayload): empresa_ou_404(empresa_id); item=next(x for x in movimentos if x["id"]==item_id); item.update(p.model_dump()); return mov_ctx(item)
@app.delete("/empresas/{empresa_id}/movimentacoes-caixa/{item_id}")
def apagar_mov(empresa_id: str, item_id: str): empresa_ou_404(empresa_id); movimentos[:] = [x for x in movimentos if x["id"] != item_id]; return {"ok":True}
@app.get("/empresas/{empresa_id}/lancamentos")
def lancamentos(empresa_id: str, competencia: str | None = None): empresa_ou_404(empresa_id); return [mov_ctx(m) for m in movimentos if not competencia or m.get("competencia") == competencia]
@app.get("/empresas/{empresa_id}/fluxo-caixa")
def fluxo_empresa(empresa_id: str, data_inicio: str = Query("2025-06-01"), data_fim: str = Query("2025-06-30")): empresa_ou_404(empresa_id); return calc_fluxo(empresa_id, data_inicio, data_fim)
@app.get("/fluxo-caixa/consolidado")
def fluxo_consolidado(data_inicio: str = Query("2025-06-01"), data_fim: str = Query("2025-06-30")): return calc_fluxo(None, data_inicio, data_fim)
@app.get("/empresas/{empresa_id}/dre")
def dre_empresa(empresa_id: str, competencia: str = Query("2025-06")): empresa_ou_404(empresa_id); return calc_dre(empresa_id, competencia)
@app.get("/dre/consolidado")
def dre_consolidado(competencia: str = Query("2025-06")): return calc_dre(None, competencia)
@app.get("/empresas/{empresa_id}/metas")
def metas(empresa_id: str): empresa_ou_404(empresa_id); return []
