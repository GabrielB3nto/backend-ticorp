"""Consultas PostgreSQL para o Programa de Pontos."""

from datetime import date, datetime, time, timedelta, timezone
from math import floor
from uuid import UUID

from .database import conectar


def _numero(valor) -> int:
    return int(valor or 0)


class RepositorioPontosPostgres:
    def resumo_dashboard(self) -> dict:
        with conectar() as conexao, conexao.cursor() as cursor:
            cursor.execute(
                """
                select
                    (select count(*) from clientes) as clientes_ativos,
                    coalesce(sum(pontos) filter (
                        where tipo = 'COMPRA'
                          and criado_em >= date_trunc('month', now())
                    ), 0) as pontos_emitidos,
                    coalesce(-sum(pontos) filter (
                        where tipo = 'RESGATE'
                          and criado_em >= date_trunc('month', now())
                    ), 0) as pontos_resgatados,
                    coalesce(sum(pontos) filter (
                        where expira_em is null or expira_em > now()
                    ), 0) as saldo_circulacao
                from lancamentos
                """
            )
            resumo = cursor.fetchone()

            cursor.execute(
                """
                with dias as (
                    select generate_series(
                        date_trunc('month', current_date)::date,
                        current_date,
                        interval '1 day'
                    )::date as dia
                )
                select
                    to_char(dias.dia, 'YYYY-MM-DD') as data,
                    coalesce(sum(l.pontos) filter (
                        where l.tipo = 'COMPRA' and l.pontos > 0
                    ), 0) as emitidos,
                    coalesce(-sum(l.pontos) filter (
                        where l.tipo = 'RESGATE' and l.pontos < 0
                    ), 0) as resgatados
                from dias
                left join lancamentos l on l.criado_em::date = dias.dia
                group by dias.dia
                order by dias.dia
                """
            )
            serie = [
                {"data": linha["data"], "emitidos": _numero(linha["emitidos"]), "resgatados": _numero(linha["resgatados"])}
                for linha in cursor.fetchall()
            ]

            cursor.execute(
                """
                select c.id::text, c.nome,
                    coalesce(sum(l.pontos) filter (
                        where l.expira_em is null or l.expira_em > now()
                    ), 0) as pontos
                from clientes c
                left join lancamentos l on l.cliente_id = c.id
                group by c.id, c.nome
                order by pontos desc, c.nome
                limit 4
                """
            )
            ranking = [
                {"id": linha["id"], "nome": linha["nome"], "pontos": _numero(linha["pontos"])}
                for linha in cursor.fetchall()
            ]

            cursor.execute(
                """
                select c.nome, l.tipo, l.pontos, l.descricao, l.criado_em
                from lancamentos l
                join clientes c on c.id = l.cliente_id
                order by l.criado_em desc
                limit 8
                """
            )
            atividades = [
                {
                    "cliente": linha["nome"],
                    "tipo": linha["tipo"],
                    "pontos": _numero(linha["pontos"]),
                    "descricao": linha["descricao"],
                    "criado_em": linha["criado_em"].isoformat(),
                }
                for linha in cursor.fetchall()
            ]

        return {
            "clientes_ativos": _numero(resumo["clientes_ativos"]),
            "pontos_emitidos": _numero(resumo["pontos_emitidos"]),
            "pontos_resgatados": _numero(resumo["pontos_resgatados"]),
            "saldo_circulacao": _numero(resumo["saldo_circulacao"]),
            "serie": serie,
            "ranking": ranking,
            "atividades": atividades,
        }

    def saldo_cliente(self, cliente_id: UUID, referencia: date) -> dict | None:
        inicio = datetime.combine(referencia, time.min, tzinfo=timezone.utc)
        fim = inicio + timedelta(days=1)
        limite_30 = fim + timedelta(days=30)
        with conectar() as conexao, conexao.cursor() as cursor:
            cursor.execute("select id::text, nome from clientes where id = %s", (cliente_id,))
            cliente = cursor.fetchone()
            if not cliente:
                return None

            cursor.execute(
                """
                select tipo, pontos, descricao, criado_em, expira_em
                from lancamentos
                where cliente_id = %s and criado_em < %s
                order by criado_em
                """,
                (cliente_id, fim),
            )
            lancamentos = cursor.fetchall()

        lotes = []
        expirado = 0
        expira_em_30_dias = 0
        saldo = 0
        for lancamento in lancamentos:
            pontos = _numero(lancamento["pontos"])
            expira_em = lancamento["expira_em"]
            if expira_em and expira_em <= inicio:
                if pontos > 0:
                    expirado += pontos
                status = "expirado"
            elif expira_em and expira_em < limite_30:
                saldo += pontos
                expira_em_30_dias += max(pontos, 0)
                status = "expirando"
            else:
                saldo += pontos
                status = "ativo"
            if lancamento["tipo"] == "COMPRA":
                lotes.append(
                    {
                        "compra_em": lancamento["criado_em"].date().isoformat(),
                        "pontos": pontos,
                        "expira_em": expira_em.date().isoformat() if expira_em else None,
                        "status": status,
                    }
                )

        return {
            "cliente": cliente,
            "saldo": saldo,
            "expirado": expirado,
            "expira_em_30_dias": expira_em_30_dias,
            "lotes": lotes,
        }

    def registrar_compra(self, cliente_id: UUID, valor: float, data_compra: date) -> int:
        pontos = floor(valor)
        if pontos <= 0:
            raise ValueError("A compra precisa gerar ao menos 1 ponto.")
        criado_em = datetime.combine(data_compra, time.min, tzinfo=timezone.utc)
        expira_em = criado_em + timedelta(days=365)
        with conectar() as conexao, conexao.cursor() as cursor:
            cursor.execute("select 1 from clientes where id = %s", (cliente_id,))
            if not cursor.fetchone():
                raise LookupError("Cliente não encontrado.")
            cursor.execute(
                """
                insert into lancamentos (cliente_id, tipo, pontos, descricao, criado_em, expira_em)
                values (%s, 'COMPRA', %s, %s, %s, %s)
                """,
                (cliente_id, pontos, f"Compra de R$ {valor:.2f}", criado_em, expira_em),
            )
        return pontos
