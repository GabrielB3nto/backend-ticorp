from datetime import date, datetime, timezone

import pytest

from src.prazo import SAO_PAULO, calcular_vencimento, esta_atrasado


@pytest.mark.parametrize('inicio, esperado', [
    ((2026, 11, 9), date(2026, 11, 27)),
    ((2026, 11, 13), date(2026, 12, 3)),
    ((2026, 11, 14), date(2026, 12, 3)),
    ((2026, 12, 18), date(2027, 1, 7)),
])
def test_vencimento_exemplos_aprovados(inicio, esperado):
    assert calcular_vencimento(datetime(*inicio, 12, tzinfo=SAO_PAULO)) == esperado


def test_vencimento_usa_data_local():
    assert calcular_vencimento(datetime(2026, 11, 10, 2, tzinfo=timezone.utc)) == date(2026, 11, 27)


def test_vencimento_sem_fuso_rejeitado():
    with pytest.raises(ValueError):
        calcular_vencimento(datetime(2026, 11, 9, 12))


def test_vencimento_hoje_nao_atrasado():
    assert not esta_atrasado(date(2026, 11, 27), datetime(2026, 11, 28, 2, 59, 59, tzinfo=timezone.utc))


def test_atraso_comeca_meia_noite_local():
    assert esta_atrasado(date(2026, 11, 27), datetime(2026, 11, 28, 3, tzinfo=timezone.utc))


def test_atraso_sem_fuso_rejeitado():
    with pytest.raises(ValueError):
        esta_atrasado(date(2026, 11, 27), datetime(2026, 11, 28))
