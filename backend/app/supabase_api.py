from collections import defaultdict
from datetime import date
from json import dumps, loads
from os import getenv
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

SUPABASE_URL = getenv("SUPABASE_URL", "https://jgdqwebhjfcrhrygxtul.supabase.co")
SUPABASE_KEY = getenv("SUPABASE_KEY", "sb_publishable_9uEjN9A-INLXDhObIHKAAw_Rdew6XLX")

app = FastAPI(title="Gestao Empresarial API", version="0.4.2-no-cors")

class MovimentoPayload(BaseModel):
    data_movimento: str
    tipo: str
    descricao: str = Field(min_length=2)
    valor: float = Field(gt=0)
    plano_conta_id: str | None = None
    origem: str = "manual"
    banco: str | None = "Unicred"
    conta_bancaria_texto: str | None = "489670"
    documento: str | None = None
    status: str = "confirmado"
    observacao: str | None = None

class PlanoContaPayload(BaseModel):
    codigo: str
    nome: str
    tipo: str = "despesa_variavel"
    grupo: str = "Geral"
    dre_linha: str = "despesas_operacionais"
    dre_categoria_id: str | None = None
    ativo: bool = True

class DreCategoriaPayload(BaseModel):
    nome: str
    chave: str
    grupo: str = "operacional"
    ordem: int = 100
    sinal: str = "positivo"
    ativa: bool = True

def check_config():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Supabase nao configurado")

def q(params):
    return urlencode(params, doseq=True, safe="*,.()")

def rest(path, method="GET", body=None):
    check_config()
    data = dumps(body).encode() if body is not None else None
    req = Request(
        f"{SUPABASE_URL}/rest/v1/{path}",
        data=data,
        method=method,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
    )
    try:
        with urlopen(req, timeout=20) as resp:
            text = resp.read().decode()
            return loads(text) if text else []
    except HTTPError as exc:
        raise HTTPException(status_code=exc.code, detail=exc.read().decode())

def empresa_ou_404(empresa_id):
    rows = rest("empresas?" + q({"id": f"eq.{empresa_id}", "select": "*"}))
    if not rows:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada")
    return rows[0]

def periodo(competencia):
    ano, mes = [int(x) for x in competencia.split("-")]
    inicio = date(ano, mes, 1)
    if mes == 12:
        fim = date(ano, 12, 31)
    else:
        proximo = date(ano, mes + 1, 1)
        fim = date.fromordinal(proximo.toordinal() - 1)
    return inicio.isoformat(), fim.isoformat()

def categorias(empresa_id):
    return rest("dre_categorias?" + q({"empresa_id": f"eq.{empresa_id}", "select": "*", "order": "ordem.asc"}))

def contas(empresa_id):
    cats = {c["id"]: c for c in categorias(empresa_id)}
    rows = rest("plano_contas?" + q({"empresa_id": f"eq.{empresa_id}", "select": "*", "order": "codigo.asc"}))
    result = []
    for row in rows:
        cat = cats.get(row.get("dre_categoria_id"))
        result.append({**row, "dre_categoria": cat.get("nome") if cat else "Sem DRE", "dre_chave": cat.get("chave") if cat else row.get("dre_linha")})
    return result

def movimentos(empresa_id, data_inicio=None, data_fim=None):
    params = {"empresa_id": f"eq.{empresa_id}", "select": "*", "order": "data_movimento.desc", "limit": "2000"}
    if data_inicio:
        params["data_movimento"] = f"gte.{data_inicio}"
    rows = rest("movimentacoes_caixa?" + q(params))
    if data_fim:
        rows = [r for r in rows if r["data_movimento"] <= data_fim]
    plano = {c["id"]: c for c in contas(empresa_id)}
    result = []
    for row in rows:
        conta = plano.get(row.get("plano_conta_id"))
        result.append({**row, "conta": conta.get("nome") if conta else "Sem conta", "categoria": conta.get("nome") if conta else "Sem conta", "dre_categoria": conta.get("dre_categoria") if conta else "Sem DRE", "dre_chave": conta.get("dre_chave") if conta else "nao_aplica"})
    return result

def fluxo(empresa_id, data_inicio, data_fim):
    rows = movimentos(empresa_id, data_inicio, data_fim)
    entradas = sum(float(r["valor"]) for r in rows if r["tipo"] == "entrada")
    saidas = sum(float(r["valor"]) for r in rows if r["tipo"] == "saida")
    return {"empresa_id": empresa_id, "data_inicio": data_inicio, "data_fim": data_fim, "entradas": round(entradas, 2), "saidas": round(saidas, 2), "saldo_periodo": round(entradas - saidas, 2), "movimentos": rows, "por_dia": []}

def dre(empresa_id, competencia):
    inicio, fim = periodo(competencia)
    rows = movimentos(empresa_id, inicio, fim)
    valores = defaultdict(float)
    for row in rows:
        valores[row.get("dre_chave") or "nao_aplica"] += float(row["valor"])
    receita = valores["receita_bruta"] + valores["outras_receitas"]
    custos = valores["custos_variaveis"]
    despesas = valores["despesas_operacionais"]
    investimentos = valores["investimentos"]
    lucro = receita - custos - despesas
    linhas = [{**c, "valor": round(valores[c["chave"]], 2)} for c in categorias(empresa_id)]
    return {"empresa_id": empresa_id, "competencia": competencia, "receita_bruta": round(receita, 2), "custos_variaveis": round(custos, 2), "lucro_bruto": round(receita - custos, 2), "despesas_operacionais": round(despesas, 2), "resultado_operacional": round(lucro, 2), "lucro_liquido": round(lucro, 2), "investimentos": round(investimentos, 2), "margem_liquida_percentual": 0 if receita == 0 else round(lucro / receita * 100, 2), "linhas_customizadas": linhas}

@app.get("/")
def root(): return {"app": "gestao-api", "version": "0.4.2-no-cors"}
@app.get("/health")
def health(): return {"status": "ok"}
@app.get("/version")
def version(): return {"app": "gestao-api", "version": "0.4.2-no-cors", "database": "supabase", "cors": "removed"}
@app.get("/empresas")
def get_empresas(): return rest("empresas?" + q({"select": "*", "ativa": "eq.true", "order": "nome.asc"}))
@app.get("/empresas/{empresa_id}/dashboard")
def get_dashboard(empresa_id: str, competencia: str = Query("2026-06")):
    emp = empresa_ou_404(empresa_id); inicio, fim = periodo(competencia)
    return {"empresa": emp, "competencia": competencia, "dre": dre(empresa_id, competencia), "fluxo_caixa": fluxo(empresa_id, inicio, fim), "metas": []}
@app.get("/empresas/{empresa_id}/dre-categorias")
def get_categorias(empresa_id: str): empresa_ou_404(empresa_id); return categorias(empresa_id)
@app.get("/empresas/{empresa_id}/plano-contas")
def get_contas(empresa_id: str): empresa_ou_404(empresa_id); return contas(empresa_id)
@app.get("/empresas/{empresa_id}/movimentacoes-caixa")
def get_movs(empresa_id: str, data_inicio: str | None = None, data_fim: str | None = None): empresa_ou_404(empresa_id); return movimentos(empresa_id, data_inicio, data_fim)
@app.get("/empresas/{empresa_id}/lancamentos")
def get_lancamentos(empresa_id: str, competencia: str | None = None):
    empresa_ou_404(empresa_id)
    if competencia:
        inicio, fim = periodo(competencia); return movimentos(empresa_id, inicio, fim)
    return movimentos(empresa_id)
@app.get("/empresas/{empresa_id}/fluxo-caixa")
def get_fluxo(empresa_id: str, data_inicio: str = Query("2026-03-31"), data_fim: str = Query("2026-06-26")): empresa_ou_404(empresa_id); return fluxo(empresa_id, data_inicio, data_fim)
@app.get("/empresas/{empresa_id}/dre")
def get_dre(empresa_id: str, competencia: str = Query("2026-06")): empresa_ou_404(empresa_id); return dre(empresa_id, competencia)
@app.get("/empresas/{empresa_id}/metas")
def get_metas(empresa_id: str): empresa_ou_404(empresa_id); return []
