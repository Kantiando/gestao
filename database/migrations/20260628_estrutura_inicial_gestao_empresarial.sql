-- Estrutura inicial do banco de dados do Gestão Empresarial Online.
-- Aplicada no Supabase em 2026-06-28.
-- Objetivo: alimentar o site com gestão por empresa, DRE, fluxo de caixa, metas e importações bancárias.

create extension if not exists "pgcrypto";

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists public.empresas (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  apelido text,
  cnpj text,
  ativa boolean not null default true,
  observacao text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint empresas_nome_unique unique (nome)
);

create table if not exists public.contas_bancarias (
  id uuid primary key default gen_random_uuid(),
  empresa_id uuid not null references public.empresas(id) on delete cascade,
  nome text not null,
  banco text,
  agencia text,
  conta text,
  tipo_conta text default 'corrente',
  saldo_inicial numeric(14,2) not null default 0,
  data_saldo_inicial date,
  ativa boolean not null default true,
  observacao text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint contas_bancarias_empresa_nome_unique unique (empresa_id, nome)
);

create table if not exists public.plano_contas (
  id uuid primary key default gen_random_uuid(),
  empresa_id uuid not null references public.empresas(id) on delete cascade,
  categoria_pai_id uuid references public.plano_contas(id) on delete set null,
  codigo text not null,
  nome text not null,
  tipo text not null,
  grupo text not null,
  dre_linha text not null,
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint plano_contas_empresa_codigo_unique unique (empresa_id, codigo),
  constraint plano_contas_tipo_check check (tipo in ('receita','custo_variavel','despesa_fixa','despesa_variavel','despesa_financeira','investimento','transferencia','distribuicao_lucro','ativo','passivo')),
  constraint plano_contas_dre_linha_check check (dre_linha in ('receita_bruta','deducoes_receita','custos_variaveis','despesas_operacionais','despesas_financeiras','outras_receitas','investimentos','distribuicao_lucro','nao_aplica'))
);

create table if not exists public.entidades (
  id uuid primary key default gen_random_uuid(),
  empresa_id uuid not null references public.empresas(id) on delete cascade,
  nome text not null,
  tipo text not null default 'outro',
  documento text,
  email text,
  telefone text,
  observacao text,
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint entidades_tipo_check check (tipo in ('cliente','fornecedor','cliente_fornecedor','funcionario','banco','outro'))
);

create table if not exists public.lancamentos_dre (
  id uuid primary key default gen_random_uuid(),
  empresa_id uuid not null references public.empresas(id) on delete cascade,
  plano_conta_id uuid not null references public.plano_contas(id) on delete restrict,
  entidade_id uuid references public.entidades(id) on delete set null,
  data_lancamento date not null,
  competencia_mes date not null,
  tipo text not null,
  descricao text not null,
  valor numeric(14,2) not null check (valor > 0),
  status text not null default 'realizado',
  forma_pagamento text,
  observacao text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint lancamentos_dre_tipo_check check (tipo in ('receita','despesa')),
  constraint lancamentos_dre_status_check check (status in ('previsto','realizado','cancelado')),
  constraint lancamentos_dre_competencia_mes_check check (competencia_mes = date_trunc('month', competencia_mes)::date)
);

create table if not exists public.movimentacoes_caixa (
  id uuid primary key default gen_random_uuid(),
  empresa_id uuid not null references public.empresas(id) on delete cascade,
  conta_bancaria_id uuid references public.contas_bancarias(id) on delete set null,
  plano_conta_id uuid references public.plano_contas(id) on delete set null,
  lancamento_dre_id uuid references public.lancamentos_dre(id) on delete set null,
  entidade_id uuid references public.entidades(id) on delete set null,
  data_movimento date not null,
  tipo text not null,
  descricao text not null,
  valor numeric(14,2) not null check (valor > 0),
  origem text not null default 'manual',
  banco text,
  conta_bancaria_texto text,
  documento text,
  identificador_externo text,
  status text not null default 'confirmado',
  observacao text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint movimentacoes_caixa_tipo_check check (tipo in ('entrada','saida','transferencia')),
  constraint movimentacoes_caixa_origem_check check (origem in ('manual','banco','importacao','integracao')),
  constraint movimentacoes_caixa_status_check check (status in ('pendente','confirmado','conciliado','ignorado'))
);

create table if not exists public.importacoes_bancarias (
  id uuid primary key default gen_random_uuid(),
  empresa_id uuid not null references public.empresas(id) on delete cascade,
  conta_bancaria_id uuid references public.contas_bancarias(id) on delete set null,
  nome_arquivo text,
  origem text not null default 'csv',
  status text not null default 'processada',
  total_registros integer not null default 0,
  total_entradas numeric(14,2) not null default 0,
  total_saidas numeric(14,2) not null default 0,
  observacao text,
  created_at timestamptz not null default now(),
  constraint importacoes_bancarias_origem_check check (origem in ('csv','ofx','api','manual')),
  constraint importacoes_bancarias_status_check check (status in ('pendente','processada','erro','cancelada'))
);

create table if not exists public.metas (
  id uuid primary key default gen_random_uuid(),
  empresa_id uuid not null references public.empresas(id) on delete cascade,
  plano_conta_id uuid references public.plano_contas(id) on delete set null,
  nome text not null,
  tipo_meta text not null,
  valor_meta numeric(14,2) not null check (valor_meta > 0),
  periodo_inicio date not null,
  periodo_fim date not null,
  ativa boolean not null default true,
  observacao text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint metas_tipo_meta_check check (tipo_meta in ('receita','lucro','margem','caixa','despesa','custo','personalizada')),
  constraint metas_periodo_check check (periodo_fim >= periodo_inicio)
);

create index if not exists idx_contas_bancarias_empresa on public.contas_bancarias(empresa_id);
create index if not exists idx_plano_contas_empresa on public.plano_contas(empresa_id);
create index if not exists idx_entidades_empresa on public.entidades(empresa_id);
create index if not exists idx_lancamentos_dre_empresa_competencia on public.lancamentos_dre(empresa_id, competencia_mes);
create index if not exists idx_lancamentos_dre_plano_conta on public.lancamentos_dre(plano_conta_id);
create index if not exists idx_movimentacoes_caixa_empresa_data on public.movimentacoes_caixa(empresa_id, data_movimento);
create index if not exists idx_movimentacoes_caixa_conta_data on public.movimentacoes_caixa(conta_bancaria_id, data_movimento);
create unique index if not exists idx_movimentacoes_caixa_identificador_externo_unique on public.movimentacoes_caixa(empresa_id, origem, identificador_externo) where identificador_externo is not null;
create index if not exists idx_metas_empresa_periodo on public.metas(empresa_id, periodo_inicio, periodo_fim);

-- Triggers de updated_at.
drop trigger if exists trg_empresas_updated_at on public.empresas;
create trigger trg_empresas_updated_at before update on public.empresas for each row execute function public.set_updated_at();

drop trigger if exists trg_contas_bancarias_updated_at on public.contas_bancarias;
create trigger trg_contas_bancarias_updated_at before update on public.contas_bancarias for each row execute function public.set_updated_at();

drop trigger if exists trg_plano_contas_updated_at on public.plano_contas;
create trigger trg_plano_contas_updated_at before update on public.plano_contas for each row execute function public.set_updated_at();

drop trigger if exists trg_entidades_updated_at on public.entidades;
create trigger trg_entidades_updated_at before update on public.entidades for each row execute function public.set_updated_at();

drop trigger if exists trg_lancamentos_dre_updated_at on public.lancamentos_dre;
create trigger trg_lancamentos_dre_updated_at before update on public.lancamentos_dre for each row execute function public.set_updated_at();

drop trigger if exists trg_movimentacoes_caixa_updated_at on public.movimentacoes_caixa;
create trigger trg_movimentacoes_caixa_updated_at before update on public.movimentacoes_caixa for each row execute function public.set_updated_at();

drop trigger if exists trg_metas_updated_at on public.metas;
create trigger trg_metas_updated_at before update on public.metas for each row execute function public.set_updated_at();
