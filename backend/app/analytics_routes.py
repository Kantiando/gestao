from collections import defaultdict

from fastapi import Query

from app import supabase_api as api


def dre_por_periodo(empresa_id: str, data_inicio: str, data_fim: str) -> dict:
    rows = api.movimentos(empresa_id, data_inicio, data_fim)
    cats = api.categorias(empresa_id)
    valores = defaultdict(float)
    entradas_por_chave = defaultdict(float)
    saidas_por_chave = defaultdict(float)
    detalhes = defaultdict(list)

    for row in rows:
        chave = row.get("dre_chave") or "nao_aplica"
        valor = float(row["valor"])
        if row["tipo"] == "entrada":
            entradas_por_chave[chave] += valor
        else:
            saidas_por_chave[chave] += valor
        valores[chave] += valor
        detalhes[chave].append({
            "data_movimento": row["data_movimento"],
            "descricao": row["descricao"],
            "conta": row.get("conta"),
            "tipo": row["tipo"],
            "valor": valor,
        })

    receita = entradas_por_chave["receita_bruta"] + entradas_por_chave["outras_receitas"]
    custos = saidas_por_chave["custos_variaveis"]
    despesas = saidas_por_chave["despesas_operacionais"]
    financeiras = saidas_por_chave["despesas_financeiras"]
    investimentos = saidas_por_chave["investimentos"]
    lucro_bruto = receita - custos
    resultado = lucro_bruto - despesas - financeiras

    linhas = []
    for cat in cats:
        chave = cat["chave"]
        linhas.append({
            **cat,
            "entradas": round(entradas_por_chave[chave], 2),
            "saidas": round(saidas_por_chave[chave], 2),
            "valor": round(valores[chave], 2),
            "detalhamento": detalhes[chave],
        })

    return {
        "empresa_id": empresa_id,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "receita_bruta": round(receita, 2),
        "custos_variaveis": round(custos, 2),
        "lucro_bruto": round(lucro_bruto, 2),
        "despesas_operacionais": round(despesas, 2),
        "despesas_financeiras": round(financeiras, 2),
        "resultado_operacional": round(resultado, 2),
        "lucro_liquido": round(resultado, 2),
        "investimentos": round(investimentos, 2),
        "margem_liquida_percentual": 0 if receita == 0 else round(resultado / receita * 100, 2),
        "linhas_customizadas": linhas,
    }


def participacao_plano_contas(empresa_id: str, data_inicio: str, data_fim: str, incluir_nao_aplica: bool = False) -> dict:
    rows = api.movimentos(empresa_id, data_inicio, data_fim)
    contas = {conta["id"]: conta for conta in api.contas(empresa_id)}
    acumulado = defaultdict(lambda: {"entradas": 0.0, "saidas": 0.0, "quantidade": 0})

    for row in rows:
        conta_id = row.get("plano_conta_id") or "sem_conta"
        conta = contas.get(conta_id)
        if not incluir_nao_aplica and conta and conta.get("dre_chave") == "nao_aplica":
            continue
        valor = float(row["valor"])
        acumulado[conta_id]["quantidade"] += 1
        if row["tipo"] == "entrada":
            acumulado[conta_id]["entradas"] += valor
        else:
            acumulado[conta_id]["saidas"] += valor

    total_saidas = sum(v["saidas"] for v in acumulado.values())
    total_entradas = sum(v["entradas"] for v in acumulado.values())
    itens = []
    for conta_id, valores in acumulado.items():
        conta = contas.get(conta_id, {})
        saidas = valores["saidas"]
        entradas = valores["entradas"]
        itens.append({
            "plano_conta_id": conta_id,
            "codigo": conta.get("codigo"),
            "nome": conta.get("nome", "Sem conta"),
            "tipo": conta.get("tipo"),
            "grupo": conta.get("grupo"),
            "dre_categoria": conta.get("dre_categoria", "Sem DRE"),
            "dre_chave": conta.get("dre_chave"),
            "quantidade": valores["quantidade"],
            "entradas": round(entradas, 2),
            "saidas": round(saidas, 2),
            "participacao_saidas_percentual": 0 if total_saidas == 0 else round(saidas / total_saidas * 100, 2),
            "participacao_entradas_percentual": 0 if total_entradas == 0 else round(entradas / total_entradas * 100, 2),
        })

    itens.sort(key=lambda item: item["saidas"], reverse=True)
    return {
        "empresa_id": empresa_id,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "total_entradas": round(total_entradas, 2),
        "total_saidas": round(total_saidas, 2),
        "contas": itens,
    }


@api.app.get("/empresas/{empresa_id}/dre-periodo")
def get_dre_periodo(empresa_id: str, data_inicio: str = Query("2026-03-31"), data_fim: str = Query("2026-06-26")):
    api.empresa_ou_404(empresa_id)
    return dre_por_periodo(empresa_id, data_inicio, data_fim)


@api.app.get("/empresas/{empresa_id}/plano-contas/participacao")
def get_participacao(empresa_id: str, data_inicio: str = Query("2026-03-31"), data_fim: str = Query("2026-06-26"), incluir_nao_aplica: bool = Query(False)):
    api.empresa_ou_404(empresa_id)
    return participacao_plano_contas(empresa_id, data_inicio, data_fim, incluir_nao_aplica)
