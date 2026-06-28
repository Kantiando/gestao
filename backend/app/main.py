from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT_MAIN = Path(__file__).resolve().parents[2] / "app" / "main.py"

if ROOT_MAIN.exists():
    spec = spec_from_file_location("gestao_root_app_main", ROOT_MAIN)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    app = module.app
else:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(title="Gestão Empresarial API", version="0.3.0-fallback")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    @app.get("/")
    def root():
        return {"app": "gestao-api", "status": "fallback", "version": "0.3.0-fallback"}

    @app.get("/version")
    def version():
        return {"app": "gestao-api", "version": "0.3.0-fallback"}

    @app.get("/empresas")
    def empresas():
        return [{"id": "empresa-colorglass", "nome": "ColorGlass", "apelido": "ColorGlass", "ativa": True}]
