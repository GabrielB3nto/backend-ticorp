from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

SAO_PAULO = ZoneInfo('America/Sao_Paulo')


def calcular_vencimento(retirado_em: datetime):
    if retirado_em.tzinfo is None or retirado_em.utcoffset() is None:
        raise ValueError('Informe um horário com fuso.')
    vencimento = retirado_em.astimezone(SAO_PAULO).date()
    dias = 0
    while dias < 14:
        vencimento += timedelta(days=1)
        if vencimento.weekday() < 5:
            dias += 1
    return vencimento


def esta_atrasado(previsto_para, referencia: datetime):
    if referencia.tzinfo is None or referencia.utcoffset() is None:
        raise ValueError('Informe um horário com fuso.')
    return referencia.astimezone(SAO_PAULO).date() > previsto_para
