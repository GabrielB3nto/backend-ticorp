-- Role de runtime restrita; a senha deve ser provisionada fora do repositório.
-- Execute em uma única transação, após 002_auth_sessions_and_rls.sql.

begin;

create role emprestai_runtime
    login
    noinherit
    nosuperuser
    nocreatedb
    nocreaterole
    noreplication
    nobypassrls;

create schema app_private;
revoke all on schema app_private from public, anon, authenticated;
grant usage on schema public, app_private to emprestai_runtime;

create function app_private.lock_login_user(p_email text)
returns table (id uuid, email varchar, ativo boolean, senha_hash text)
language sql
volatile
security definer
set search_path = pg_catalog, public, pg_temp
as $$
    select u.id, u.email, u.ativo, u.senha_hash
    from public.usuarios as u
    where pg_catalog.lower(u.email) = p_email
    for share of u
$$;

create function app_private.lock_equipment_for_loan(p_equipment_id uuid)
returns table (
    id uuid,
    nome varchar,
    patrimonio varchar,
    status_operacional varchar,
    categoria varchar
)
language sql
volatile
security definer
set search_path = pg_catalog, public, pg_temp
as $$
    select e.id, e.nome, e.patrimonio, e.status_operacional, c.nome
    from public.equipamentos as e
    join public.categorias as c on c.id = e.categoria_id
    where e.id = p_equipment_id
    for update of e
$$;

create function app_private.lock_user_for_loan(p_usuario_id uuid)
returns table (id uuid, ativo boolean)
language sql
volatile
security definer
set search_path = pg_catalog, public, pg_temp
as $$
    select u.id, u.ativo
    from public.usuarios as u
    where u.id = p_usuario_id
    for share of u
$$;

create function app_private.lock_session_for_loan(p_token_hash text)
returns table (usuario_id uuid, expira_em timestamptz)
language sql
volatile
security definer
set search_path = pg_catalog, public, pg_temp
as $$
    select s.usuario_id, s.expira_em
    from public.sessoes_login as s
    where s.token_hash = p_token_hash
    for share of s
$$;

alter function public.validar_novo_emprestimo() security definer;
alter function public.validar_novo_emprestimo()
    set search_path = pg_catalog, public, pg_temp;

revoke all on function app_private.lock_login_user(text)
    from public, anon, authenticated;
revoke all on function app_private.lock_equipment_for_loan(uuid)
    from public, anon, authenticated;
revoke all on function app_private.lock_user_for_loan(uuid)
    from public, anon, authenticated;
revoke all on function app_private.lock_session_for_loan(text)
    from public, anon, authenticated;
revoke all on function public.validar_novo_emprestimo()
    from public, anon, authenticated;

grant execute on function app_private.lock_login_user(text)
    to emprestai_runtime;
grant execute on function app_private.lock_equipment_for_loan(uuid)
    to emprestai_runtime;
grant execute on function app_private.lock_user_for_loan(uuid)
    to emprestai_runtime;
grant execute on function app_private.lock_session_for_loan(text)
    to emprestai_runtime;
grant execute on function public.validar_novo_emprestimo()
    to emprestai_runtime;

grant select (id, email, ativo) on public.usuarios to emprestai_runtime;
grant select (id, nome) on public.categorias to emprestai_runtime;
grant select (id, nome, patrimonio, categoria_id, status_operacional)
    on public.equipamentos to emprestai_runtime;
grant select (id, equipamento_id, usuario_id, retirado_em, previsto_para, devolvido_em)
    on public.emprestimos to emprestai_runtime;
grant insert (equipamento_id, usuario_id, retirado_em, previsto_para)
    on public.emprestimos to emprestai_runtime;
grant select (token_hash, usuario_id, criado_em, expira_em)
    on public.sessoes_login to emprestai_runtime;
grant insert (token_hash, usuario_id, criado_em, expira_em)
    on public.sessoes_login to emprestai_runtime;
grant delete on public.sessoes_login to emprestai_runtime;

create policy runtime_select on public.usuarios
    for select to emprestai_runtime using (true);
create policy runtime_select on public.categorias
    for select to emprestai_runtime using (true);
create policy runtime_select on public.equipamentos
    for select to emprestai_runtime using (true);
create policy runtime_select on public.emprestimos
    for select to emprestai_runtime using (true);
create policy runtime_insert on public.emprestimos
    for insert to emprestai_runtime with check (true);
create policy runtime_select on public.sessoes_login
    for select to emprestai_runtime using (true);
create policy runtime_insert on public.sessoes_login
    for insert to emprestai_runtime with check (true);
create policy runtime_delete on public.sessoes_login
    for delete to emprestai_runtime using (true);

commit;
