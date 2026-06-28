# Gestão Empresarial Online

Sistema privado para gestão empresarial por empresa e visão consolidada geral da holding.

## Objetivo do core

A primeira versão não tem login, variáveis de ambiente ou Supabase. O foco é validar a estrutura principal:

- Gestão por empresa
- Visão geral consolidada
- Plano de contas
- Lançamentos financeiros para DRE
- Movimentações de caixa/banco
- Fluxo de caixa
- DRE gerencial
- Metas
- Dashboard inicial

A empresa inicial cadastrada em memória é a ColorGlass.

## Diferença entre DRE e fluxo de caixa

A DRE trabalha por competência. Ela responde se a empresa deu lucro ou prejuízo no período gerencial.

O fluxo de caixa trabalha por data real de entrada e saída no banco/caixa. Ele será alimentado futuramente por importação bancária, conciliação ou integração com banco.

Exemplo:

```txt
Venda feita em junho, recebida em julho:
- entra na DRE de junho
- entra no fluxo de caixa de julho
```

## Estrutura

```txt
backend/   FastAPI com dados temporários em memória
frontend/  React + Vite
database/  futura área de migrations SQL
```

## Rodar backend local

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend:

```txt
http://localhost:8000
```

Docs:

```txt
http://localhost:8000/docs
```

## Rodar frontend local

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```txt
http://localhost:5173
```

## Rotas principais do core

```txt
/empresas
/empresas/{empresa_id}/dashboard
/empresas/{empresa_id}/plano-contas
/empresas/{empresa_id}/lancamentos
/empresas/{empresa_id}/dre
/empresas/{empresa_id}/movimentacoes-caixa
/empresas/{empresa_id}/fluxo-caixa
/dre/consolidado
/fluxo-caixa/consolidado
```

## Deploy Render

O arquivo `render.yaml` já define dois serviços:

- `gestao-api`: backend FastAPI
- `gestao-web`: frontend React/Vite

Nesta fase não há variáveis de ambiente configuradas.
