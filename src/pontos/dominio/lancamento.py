"""Entidade Lançamento — ADR-002: lançamentos imutáveis."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class TipoLancamento(Enum):
    """Tipos de lançamento."""

    COMPRA = "COMPRA"
    DEVOLUCAO = "DEVOLUCAO"
    RESGATE = "RESGATE"
    EXPIRACAO = "EXPIRACAO"


@dataclass(frozen=True)
class Lancamento:
    """
    Representa um lançamento imutável de pontos.

    ADR-002: Cada operação cria um novo lançamento;
    o saldo é calculado a partir do histórico.
    """

    id: str
    cliente_id: str
    tipo: TipoLancamento
    pontos: int
    data_criacao: datetime
    expira_em: Optional[datetime] = None

    def __post_init__(self):
        """Valida campos obrigatórios."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("Lancamento.id deve ser uma string não vazia")
        if not self.cliente_id or not isinstance(self.cliente_id, str):
            raise ValueError("Lancamento.cliente_id deve ser uma string não vazia")
        if not isinstance(self.tipo, TipoLancamento):
            raise ValueError("Lancamento.tipo deve ser um TipoLancamento válido")
        if not isinstance(self.pontos, int) or self.pontos == 0:
            raise ValueError("Lancamento.pontos deve ser um inteiro não-nulo")
        if not isinstance(self.data_criacao, datetime):
            raise ValueError("Lancamento.data_criacao deve ser um datetime")
        if self.expira_em is not None and not isinstance(self.expira_em, datetime):
            raise ValueError("Lancamento.expira_em deve ser um datetime ou None")

    def esta_expirado(self, referencia: datetime) -> bool:
        """
        Verifica se o lançamento expirou.

        ADR-003: Expiração em 12 meses. Lazy evaluation em calcular_saldo.
        """
        if self.expira_em is None:
            return False
        return referencia >= self.expira_em

    @staticmethod
    def criar_lancamento_compra(
        id: str,
        cliente_id: str,
        pontos: int,
        data_criacao: datetime,
    ) -> "Lancamento":
        """Cria lançamento de compra com expiração em 12 meses."""
        expira_em = data_criacao + timedelta(days=365)
        return Lancamento(
            id=id,
            cliente_id=cliente_id,
            tipo=TipoLancamento.COMPRA,
            pontos=pontos,
            data_criacao=data_criacao,
            expira_em=expira_em,
        )
