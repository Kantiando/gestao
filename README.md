# Gestão Empresarial Online

Sistema privado para gestão empresarial por empresa e visão consolidada geral da holding.

## Objetivo do core

A primeira versão não tem login, variáveis de ambiente ou Supabase. O foco é validar a estrutura principal:

- Gestão por empresa
- Visão geral consolidada
- Plano de contas
- Lançamentos financeiros
- DRE gerencial
- Metas
- Dashboard inicial

A empresa inicial cadastrada em memória é a ColorGlass.

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

## Deploy Render

O arquivo `render.yaml` já define dois serviços:

- `gestao-api`: backend FastAPI
- `gestao-web`: frontend React/Vite

Nesta fase não há variáveis de ambiente configuradas.
