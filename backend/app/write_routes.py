from fastapi import HTTPException

from app import supabase_api as api


def movimento_payload(empresa_id: str, payload: api.MovimentoPayload) -> dict:
    data = payload.model_dump()
    return {
        "empresa_id": empresa_id,
        "data_movimento": data.get("data_movimento"),
        "tipo": data.get("tipo"),
        "descricao": data.get("descricao"),
        "valor": data.get("valor"),
        "plano_conta_id": data.get("plano_conta_id"),
        "origem": data.get("origem") or "manual",
        "banco": data.get("banco"),
        "conta_bancaria_texto": data.get("conta_bancaria_texto"),
        "documento": data.get("documento"),
        "status": data.get("status") or "realizado",
        "observacao": data.get("observacao"),
    }


@api.app.post("/empresas/{empresa_id}/movimentacoes-caixa", status_code=201)
def criar_movimentacao(empresa_id: str, payload: api.MovimentoPayload):
    api.empresa_ou_404(empresa_id)
    body = movimento_payload(empresa_id, payload)
    rows = api.rest("movimentacoes_caixa", "POST", [body])
    if not rows:
        raise HTTPException(status_code=500, detail="Movimentacao nao foi criada")
    return rows[0]


@api.app.put("/empresas/{empresa_id}/movimentacoes-caixa/{movimento_id}")
def editar_movimentacao(empresa_id: str, movimento_id: str, payload: api.MovimentoPayload):
    api.empresa_ou_404(empresa_id)
    body = movimento_payload(empresa_id, payload)
    body.pop("empresa_id", None)
    path = f"movimentacoes_caixa?id=eq.{movimento_id}&empresa_id=eq.{empresa_id}"
    rows = api.rest(path, "PATCH", body)
    if not rows:
        raise HTTPException(status_code=404, detail="Movimentacao nao encontrada")
    return rows[0]


@api.app.delete("/empresas/{empresa_id}/movimentacoes-caixa/{movimento_id}")
def remover_movimentacao(empresa_id: str, movimento_id: str):
    api.empresa_ou_404(empresa_id)
    path = f"movimentacoes_caixa?id=eq.{movimento_id}&empresa_id=eq.{empresa_id}"
    api.rest(path, "DELETE")
    return {"ok": True}
