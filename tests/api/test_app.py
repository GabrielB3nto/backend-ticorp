from uuid import UUID

from fastapi.testclient import TestClient

import src.pontos.api.app as modulo_api


class RepositorioFalso:
    def resumo_dashboard(self):
        return {
            "clientes_ativos": 1,
            "pontos_emitidos": 120,
            "pontos_resgatados": 0,
            "saldo_circulacao": 120,
            "serie": [],
            "ranking": [],
            "atividades": [],
        }

    def saldo_cliente(self, cliente_id: UUID, referencia):
        return None

    def registrar_compra(self, cliente_id: UUID, valor: float, data):
        return 10


def test_dashboard_retorna_agregados_do_repositorio(monkeypatch):
    monkeypatch.setattr(modulo_api, "repositorio", RepositorioFalso())
    resposta = TestClient(modulo_api.app).get("/dashboard/resumo")

    assert resposta.status_code == 200
    assert resposta.json()["pontos_emitidos"] == 120


def test_saldo_de_cliente_inexistente_retorna_404(monkeypatch):
    monkeypatch.setattr(modulo_api, "repositorio", RepositorioFalso())
    resposta = TestClient(modulo_api.app).get(
        "/clientes/11111111-1111-1111-1111-111111111111/saldo"
    )

    assert resposta.status_code == 404


def test_compra_retorna_pontos_gerados(monkeypatch):
    monkeypatch.setattr(modulo_api, "repositorio", RepositorioFalso())
    resposta = TestClient(modulo_api.app).post(
        "/compras",
        json={
            "cliente_id": "11111111-1111-1111-1111-111111111111",
            "valor": 10.9,
            "data": "2026-10-19",
        },
    )

    assert resposta.status_code == 201
    assert resposta.json() == {"pontos_gerados": 10}
