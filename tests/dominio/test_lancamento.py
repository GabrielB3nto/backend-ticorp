"""Testes da entidade Lançamento."""

import pytest
from datetime import datetime, timedelta

from src.pontos.dominio.lancamento import Lancamento, TipoLancamento


class TestLancamento:
    """Testes de Lançamento — ADR-002: imutabilidade."""

    def test_criar_lancamento_valido(self):
        """Deve criar lançamento com campos obrigatórios."""
        agora = datetime.now()
        lancamento = Lancamento(
            id="lan_001",
            cliente_id="cli_001",
            tipo=TipoLancamento.COMPRA,
            pontos=100,
            data_criacao=agora,
            expira_em=agora + timedelta(days=365),
        )

        assert lancamento.id == "lan_001"
        assert lancamento.cliente_id == "cli_001"
        assert lancamento.tipo == TipoLancamento.COMPRA
        assert lancamento.pontos == 100

    def test_lancamento_frozen_nao_mutavel(self):
        """Deve garantir imutabilidade (frozen=True)."""
        agora = datetime.now()
        lancamento = Lancamento(
            id="lan_001",
            cliente_id="cli_001",
            tipo=TipoLancamento.COMPRA,
            pontos=100,
            data_criacao=agora,
        )

        with pytest.raises(AttributeError):
            lancamento.pontos = 200

    def test_lancamento_id_vazio(self):
        """Deve rejeitar id vazio."""
        agora = datetime.now()
        with pytest.raises(ValueError, match="id deve ser uma string não vazia"):
            Lancamento(
                id="",
                cliente_id="cli_001",
                tipo=TipoLancamento.COMPRA,
                pontos=100,
                data_criacao=agora,
            )

    def test_lancamento_pontos_zero(self):
        """Deve rejeitar pontos zero."""
        agora = datetime.now()
        with pytest.raises(ValueError, match="pontos deve ser um inteiro não-nulo"):
            Lancamento(
                id="lan_001",
                cliente_id="cli_001",
                tipo=TipoLancamento.COMPRA,
                pontos=0,
                data_criacao=agora,
            )

    def test_lancamento_pode_ter_pontos_negativos(self):
        """Deve permitir pontos negativos (resgate, devolução)."""
        agora = datetime.now()
        lancamento = Lancamento(
            id="lan_001",
            cliente_id="cli_001",
            tipo=TipoLancamento.RESGATE,
            pontos=-50,
            data_criacao=agora,
        )

        assert lancamento.pontos == -50

    def test_lancamento_compra_nao_expirado(self):
        """Deve indicar lançamento não expirado."""
        agora = datetime.now()
        lancamento = Lancamento.criar_lancamento_compra(
            id="lan_001",
            cliente_id="cli_001",
            pontos=100,
            data_criacao=agora,
        )

        # Referência em 6 meses: não expirou (expiração em 12)
        referencia = agora + timedelta(days=180)
        assert not lancamento.esta_expirado(referencia)

    def test_lancamento_compra_expirado_apos_12_meses(self):
        """Deve indicar lançamento expirado após 12 meses (ADR-003)."""
        agora = datetime.now()
        lancamento = Lancamento.criar_lancamento_compra(
            id="lan_001",
            cliente_id="cli_001",
            pontos=100,
            data_criacao=agora,
        )

        # Referência em 13 meses: expirou
        referencia = agora + timedelta(days=396)
        assert lancamento.esta_expirado(referencia)

    def test_lancamento_compra_expirou_exatamente_em_12_meses(self):
        """Deve indicar expiração exata em 12 meses."""
        agora = datetime.now()
        lancamento = Lancamento.criar_lancamento_compra(
            id="lan_001",
            cliente_id="cli_001",
            pontos=100,
            data_criacao=agora,
        )

        # Referência exatamente em 12 meses: expirou (>=)
        referencia = agora + timedelta(days=365)
        assert lancamento.esta_expirado(referencia)

    def test_lancamento_resgate_sem_expiracao(self):
        """Deve permitir lançamento RESGATE sem expira_em."""
        agora = datetime.now()
        lancamento = Lancamento(
            id="lan_001",
            cliente_id="cli_001",
            tipo=TipoLancamento.RESGATE,
            pontos=-50,
            data_criacao=agora,
            expira_em=None,
        )

        assert lancamento.expira_em is None
        assert not lancamento.esta_expirado(agora)
