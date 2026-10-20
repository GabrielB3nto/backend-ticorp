"""Testes do valor-objeto Saldo com lazy evaluation de expiração."""

import pytest
from datetime import datetime, timedelta

from src.pontos.dominio.saldo import Saldo, LoteDePontos
from src.pontos.dominio.lancamento import Lancamento, TipoLancamento


class TestSaldo:
    """Testes de Saldo — ADR-002 + ADR-003."""

    def test_saldo_vazio(self):
        """Deve criar saldo vazio."""
        saldo = Saldo(cliente_id="cli_001")

        assert saldo.cliente_id == "cli_001"
        assert saldo.pontos_vigentes == 0
        assert len(saldo.lotes) == 0

    def test_calcular_saldo_uma_compra(self):
        """Deve calcular saldo com uma compra."""
        agora = datetime.now()
        cliente_id = "cli_001"

        lancamento = Lancamento.criar_lancamento_compra(
            id="lan_001",
            cliente_id=cliente_id,
            pontos=100,
            data_criacao=agora,
        )

        saldo = Saldo.calcular_a_partir_de_lancamentos(
            cliente_id=cliente_id,
            lancamentos=[lancamento],
            referencia=agora,
        )

        assert saldo.pontos_vigentes == 100
        assert len(saldo.lotes) == 1
        assert saldo.lotes[0].pontos == 100

    def test_calcular_saldo_multiplas_compras_mesma_expiracao(self):
        """Deve agregar múltiplas compras com mesma data de expiração."""
        agora = datetime.now()
        cliente_id = "cli_001"

        lancamento1 = Lancamento.criar_lancamento_compra(
            id="lan_001",
            cliente_id=cliente_id,
            pontos=100,
            data_criacao=agora,
        )
        lancamento2 = Lancamento.criar_lancamento_compra(
            id="lan_002",
            cliente_id=cliente_id,
            pontos=50,
            data_criacao=agora,
        )

        saldo = Saldo.calcular_a_partir_de_lancamentos(
            cliente_id=cliente_id,
            lancamentos=[lancamento1, lancamento2],
            referencia=agora,
        )

        assert saldo.pontos_vigentes == 150
        assert len(saldo.lotes) == 1
        assert saldo.lotes[0].pontos == 150

    def test_calcular_saldo_multiplas_compras_datas_diferentes(self):
        """Deve criar lotes separados para datas de expiração diferentes."""
        agora = datetime.now()
        cliente_id = "cli_001"

        # Lançamento 1: expira em 12 meses
        lancamento1 = Lancamento.criar_lancamento_compra(
            id="lan_001",
            cliente_id=cliente_id,
            pontos=100,
            data_criacao=agora,
        )

        # Lançamento 2: data 30 dias depois, expira em 12 meses depois disso
        data_compra2 = agora + timedelta(days=30)
        lancamento2 = Lancamento.criar_lancamento_compra(
            id="lan_002",
            cliente_id=cliente_id,
            pontos=50,
            data_criacao=data_compra2,
        )

        saldo = Saldo.calcular_a_partir_de_lancamentos(
            cliente_id=cliente_id,
            lancamentos=[lancamento1, lancamento2],
            referencia=agora,
        )

        assert saldo.pontos_vigentes == 150
        assert len(saldo.lotes) == 2
        assert saldo.lotes[0].pontos == 100
        assert saldo.lotes[1].pontos == 50

    def test_calcular_saldo_ignora_cliente_diferente(self):
        """Deve ignorar lançamentos de outro cliente."""
        agora = datetime.now()

        lancamento = Lancamento.criar_lancamento_compra(
            id="lan_001",
            cliente_id="cli_002",
            pontos=100,
            data_criacao=agora,
        )

        saldo = Saldo.calcular_a_partir_de_lancamentos(
            cliente_id="cli_001",
            lancamentos=[lancamento],
            referencia=agora,
        )

        assert saldo.pontos_vigentes == 0

    def test_calcular_saldo_ignora_expirados(self):
        """Deve ignorar lançamentos expirados (ADR-003: lazy eval)."""
        agora = datetime.now()
        cliente_id = "cli_001"

        lancamento = Lancamento.criar_lancamento_compra(
            id="lan_001",
            cliente_id=cliente_id,
            pontos=100,
            data_criacao=agora,
        )

        # Referência em 13 meses: lançamento expirou
        referencia = agora + timedelta(days=396)

        saldo = Saldo.calcular_a_partir_de_lancamentos(
            cliente_id=cliente_id,
            lancamentos=[lancamento],
            referencia=referencia,
        )

        assert saldo.pontos_vigentes == 0

    def test_calcular_saldo_mix_vigentes_e_expirados(self):
        """Deve calcular apenas pontos vigentes."""
        agora = datetime.now()
        cliente_id = "cli_001"

        # Compra 1: feita há 13 meses (já expirada)
        lancamento1 = Lancamento.criar_lancamento_compra(
            id="lan_001",
            cliente_id=cliente_id,
            pontos=100,
            data_criacao=agora - timedelta(days=396),
        )

        # Compra 2: feita há 6 meses (ainda vigente)
        lancamento2 = Lancamento.criar_lancamento_compra(
            id="lan_002",
            cliente_id=cliente_id,
            pontos=50,
            data_criacao=agora - timedelta(days=180),
        )

        saldo = Saldo.calcular_a_partir_de_lancamentos(
            cliente_id=cliente_id,
            lancamentos=[lancamento1, lancamento2],
            referencia=agora,
        )

        # Apenas compra 2 conta (compra 1 expirou)
        assert saldo.pontos_vigentes == 50

    def test_lote_de_pontos(self):
        """Deve criar lote com pontos e data de expiração."""
        agora = datetime.now()
        lote = LoteDePontos(pontos=100, expira_em=agora + timedelta(days=365))

        assert lote.pontos == 100
        assert lote.expira_em == agora + timedelta(days=365)

    def test_saldo_lotes_ordenados_por_expiracao(self):
        """Deve manter lotes ordenados por data de expiração (FIFO)."""
        agora = datetime.now()
        cliente_id = "cli_001"

        # Compra 3: feita há 30 dias
        lancamento3 = Lancamento.criar_lancamento_compra(
            id="lan_003",
            cliente_id=cliente_id,
            pontos=75,
            data_criacao=agora - timedelta(days=30),
        )

        # Compra 1: feita hoje
        lancamento1 = Lancamento.criar_lancamento_compra(
            id="lan_001",
            cliente_id=cliente_id,
            pontos=100,
            data_criacao=agora,
        )

        # Compra 2: feita há 15 dias
        lancamento2 = Lancamento.criar_lancamento_compra(
            id="lan_002",
            cliente_id=cliente_id,
            pontos=50,
            data_criacao=agora - timedelta(days=15),
        )

        # Adiciona em ordem aleatória
        saldo = Saldo.calcular_a_partir_de_lancamentos(
            cliente_id=cliente_id,
            lancamentos=[lancamento3, lancamento1, lancamento2],
            referencia=agora,
        )

        # Lotes devem estar ordenados por expira_em (mais próximo primeiro)
        assert len(saldo.lotes) == 3
        assert saldo.lotes[0].pontos == 100  # Compra 1 expira primeiro
        assert saldo.lotes[1].pontos == 50  # Compra 2
        assert saldo.lotes[2].pontos == 75  # Compra 3 expira por último
