from backend.app.main import app


@app.get("/version")
def version() -> dict:
    return {
        "app": "gestao-api",
        "version": "0.2.1",
        "status": "running",
        "routes_expected": [
            "/dre/consolidado",
            "/fluxo-caixa/consolidado",
            "/empresas/{empresa_id}/dashboard",
            "/empresas/{empresa_id}/fluxo-caixa",
        ],
    }
