"""Testes da entidade Cliente."""

import pytest

from src.pontos.dominio.cliente import Cliente


class TestCliente:
    """Testes de Cliente."""

    def test_criar_cliente_valido(self):
        """Deve criar cliente com id e nome válidos."""
        cliente = Cliente(id="cli_001", nome="João Silva")

        assert cliente.id == "cli_001"
        assert cliente.nome == "João Silva"

    def test_cliente_id_vazio(self):
        """Deve rejeitar id vazio."""
        with pytest.raises(ValueError, match="id deve ser uma string não vazia"):
            Cliente(id="", nome="João Silva")

    def test_cliente_nome_vazio(self):
        """Deve rejeitar nome vazio."""
        with pytest.raises(ValueError, match="nome deve ser uma string não vazia"):
            Cliente(id="cli_001", nome="")

    def test_cliente_id_none(self):
        """Deve rejeitar id None."""
        with pytest.raises(ValueError, match="id deve ser uma string não vazia"):
            Cliente(id=None, nome="João Silva")

    def test_cliente_nome_none(self):
        """Deve rejeitar nome None."""
        with pytest.raises(ValueError, match="nome deve ser uma string não vazia"):
            Cliente(id="cli_001", nome=None)
