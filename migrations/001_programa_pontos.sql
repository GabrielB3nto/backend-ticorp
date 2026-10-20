-- Schema inicial do Programa de Pontos. Execute em uma única transação.
begin;

create extension if not exists pgcrypto;

create table if not exists clientes (
    id uuid primary key default gen_random_uuid(),
    nome varchar(120) not null check (btrim(nome) <> ''),
    email varchar(254) not null check (btrim(email) <> ''),
    criado_em timestamptz not null default now()
);

create unique index if not exists ux_clientes_email_ci
    on clientes (lower(email));

create table if not exists lancamentos (
    id uuid primary key default gen_random_uuid(),
    cliente_id uuid not null references clientes(id),
    tipo varchar(20) not null check (
        tipo in ('COMPRA', 'RESGATE', 'DEVOLUCAO', 'EXPIRACAO')
    ),
    pontos integer not null check (pontos <> 0),
    descricao varchar(255) not null check (btrim(descricao) <> ''),
    criado_em timestamptz not null default now(),
    expira_em timestamptz,
    constraint ck_lancamento_expiracao_compra check (
        (tipo = 'COMPRA' and expira_em is not null)
        or (tipo <> 'COMPRA')
    )
);

create index if not exists ix_lancamentos_cliente_data
    on lancamentos (cliente_id, criado_em desc);

create index if not exists ix_lancamentos_tipo_data
    on lancamentos (tipo, criado_em desc);

create or replace function impedir_alteracao_lancamento()
returns trigger
language plpgsql
as $$
begin
    raise exception 'Lançamentos do Programa de Pontos são imutáveis.';
end;
$$;

drop trigger if exists tr_lancamentos_imutaveis on lancamentos;
create trigger tr_lancamentos_imutaveis
before update or delete on lancamentos
for each row execute function impedir_alteracao_lancamento();

commit;
