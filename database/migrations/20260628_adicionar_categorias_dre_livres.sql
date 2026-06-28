-- Adiciona categorias livres da DRE e vincula o plano de contas a essas categorias.

create table if not exists public.dre_categorias (
  id uuid primary key default gen_random_uuid(),
  empresa_id uuid not null references public.empresas(id) on delete cascade,
  nome text not null,
  chave text not null,
  grupo text not null default 'operacional',
  ordem integer not null default 100,
  sinal text not null default 'positivo',
  ativa boolean not null default true,
  observacao text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint dre_categorias_empresa_chave_unique unique (empresa_id, chave),
  constraint dre_categorias_sinal_check check (sinal in ('positivo', 'negativo', 'neutro'))
);

alter table public.plano_contas
add column if not exists dre_categoria_id uuid references public.dre_categorias(id) on delete set null;

create index if not exists idx_dre_categorias_empresa_ordem on public.dre_categorias(empresa_id, ordem);
create index if not exists idx_plano_contas_dre_categoria on public.plano_contas(dre_categoria_id);

with empresas_base as (
  select id from public.empresas
), categorias as (
  select * from (values
    ('Receita Bruta', 'receita_bruta', 'receita', 10, 'positivo'),
    ('Custos Variaveis', 'custos_variaveis', 'custos', 20, 'negativo'),
    ('Despesas Operacionais', 'despesas_operacionais', 'despesas', 30, 'negativo'),
    ('Despesas Financeiras', 'despesas_financeiras', 'financeiro', 40, 'negativo'),
    ('Investimentos', 'investimentos', 'investimentos', 50, 'neutro')
  ) as c(nome, chave, grupo, ordem, sinal)
)
insert into public.dre_categorias (empresa_id, nome, chave, grupo, ordem, sinal)
select e.id, c.nome, c.chave, c.grupo, c.ordem, c.sinal
from empresas_base e
cross join categorias c
on conflict (empresa_id, chave) do nothing;

update public.plano_contas pc
set dre_categoria_id = dc.id
from public.dre_categorias dc
where dc.empresa_id = pc.empresa_id
  and dc.chave = pc.dre_linha
  and pc.dre_categoria_id is null;
