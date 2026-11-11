-- Complementa o schema inicial com login tradicional e acesso restrito.
-- Execute em uma única transação, após 001_emprestai_schema.sql.

begin;

alter table public.usuarios
    add column senha_hash text;

create table public.sessoes_login (
    token_hash varchar(64) primary key,
    usuario_id uuid not null references public.usuarios(id),
    criado_em timestamptz not null default now(),
    expira_em timestamptz not null,
    constraint ck_sessoes_login_expiracao check (expira_em > criado_em)
);

create index ix_sessoes_login_usuario
    on public.sessoes_login (usuario_id);

alter table public.usuarios enable row level security;
alter table public.categorias enable row level security;
alter table public.equipamentos enable row level security;
alter table public.emprestimos enable row level security;
alter table public.historico_status_equipamento enable row level security;
alter table public.sessoes_login enable row level security;

revoke all on table
    public.usuarios,
    public.categorias,
    public.equipamentos,
    public.emprestimos,
    public.historico_status_equipamento,
    public.sessoes_login
from public, anon, authenticated;

revoke all on all sequences in schema public
from public, anon, authenticated;

revoke execute on function public.definir_atualizado_em()
from public, anon, authenticated;
revoke execute on function public.validar_novo_emprestimo()
from public, anon, authenticated;
revoke execute on function public.impedir_status_com_emprestimo_ativo()
from public, anon, authenticated;

create policy deny_anon on public.usuarios
    for all to anon using (false) with check (false);
create policy deny_authenticated on public.usuarios
    for all to authenticated using (false) with check (false);

create policy deny_anon on public.categorias
    for all to anon using (false) with check (false);
create policy deny_authenticated on public.categorias
    for all to authenticated using (false) with check (false);

create policy deny_anon on public.equipamentos
    for all to anon using (false) with check (false);
create policy deny_authenticated on public.equipamentos
    for all to authenticated using (false) with check (false);

create policy deny_anon on public.emprestimos
    for all to anon using (false) with check (false);
create policy deny_authenticated on public.emprestimos
    for all to authenticated using (false) with check (false);

create policy deny_anon on public.historico_status_equipamento
    for all to anon using (false) with check (false);
create policy deny_authenticated on public.historico_status_equipamento
    for all to authenticated using (false) with check (false);

create policy deny_anon on public.sessoes_login
    for all to anon using (false) with check (false);
create policy deny_authenticated on public.sessoes_login
    for all to authenticated using (false) with check (false);

commit;
