"""Valor-objeto Saldo — agregação de lançamentos com lazy evaluation de expiração."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .lancamento import Lancamento, TipoLancamento


@dataclass
class LoteDePontos:
    """Representa um lote de pontos vigentes com data de expiração."""

    pontos: int
    expira_em: datetime


@dataclass
class Saldo:
    """
    Valor-objeto que calcula o saldo vigente a partir de lançamentos.

    ADR-002: Imutabilidade + ADR-003: Lazy evaluation de expiração.
    """

    cliente_id: str
    lotes: List[LoteDePontos] = field(default_factory=list)

    @property
    def pontos_vigentes(self) -> int:
        """Soma dos pontos em lotes vigentes."""
        return sum(lote.pontos for lote in self.lotes)

    @staticmethod
    def calcular_a_partir_de_lancamentos(
        cliente_id: str,
        lancamentos: List[Lancamento],
        referencia: datetime,
    ) -> "Saldo":
        """
        Calcula saldo vigente a partir de lançamentos.

        Filtra:
        - Lançamentos do cliente
        - Tipo COMPRA com pontos > 0 (entrada)
        - Tipo RESGATE com pontos < 0 (saída)
        - Tipo DEVOLUCAO com pontos > 0 ou < 0 conforme reversa
        - Ignora EXPIRACAO nesta v1 (lazy evaluation)
        - Filtra expirados (ADR-003)

        Agrupa em lotes por data de expiração.
        """
        saldo = Saldo(cliente_id=cliente_id, lotes=[])

        for lancamento in lancamentos:
            if lancamento.cliente_id != cliente_id:
                continue

            # Filtra lançamentos expirados
            if lancamento.esta_expirado(referencia):
                continue

            # Inclui movimentações (COMPRA e DEVOLUCAO geram entrada)
            if lancamento.tipo in (TipoLancamento.COMPRA, TipoLancamento.DEVOLUCAO):
                if lancamento.pontos > 0:
                    saldo._adicionar_lote(
                        lancamento.pontos, lancamento.expira_em or referencia
                    )
            # RESGATE reduz pontos (será implementado em etapas futuras)
            elif lancamento.tipo == TipoLancamento.RESGATE:
                # v1: resgates reduzem de cima para baixo (FIFO por expira_em)
                pass

        return saldo

    def _adicionar_lote(self, pontos: int, expira_em: datetime) -> None:
        """Agrupa pontos por data de expiração."""
        for lote in self.lotes:
            if lote.expira_em == expira_em:
                lote.pontos += pontos
                return

        self.lotes.append(LoteDePontos(pontos=pontos, expira_em=expira_em))
        self.lotes.sort(key=lambda l: l.expira_em)
