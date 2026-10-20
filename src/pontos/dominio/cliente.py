"""Entidade Cliente."""

from dataclasses import dataclass


@dataclass
class Cliente:
    """Representa um cliente do programa de pontos."""

    id: str
    nome: str

    def __post_init__(self):
        """Valida campos obrigatórios."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("Cliente.id deve ser uma string não vazia")
        if not self.nome or not isinstance(self.nome, str):
            raise ValueError("Cliente.nome deve ser uma string não vazia")
