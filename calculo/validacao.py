"""Referências independentes; nunca produzem os resultados do integrador."""

import math

from .integracao import RESOLUCOES, integrar_esfera, validar_parametros
from .geometria import validar_raio


def volume_analitico_esfera(raio):
    return 4.0 * math.pi * validar_raio(raio) ** 3 / 3.0


def massa_analitica_esfera(raio, densidade):
    parametros = validar_parametros(raio, densidade, 10)
    return parametros["densidade"] * volume_analitico_esfera(parametros["raio"])


def erro_absoluto(valor, referencia):
    return abs(valor - referencia)


def erro_relativo(valor, referencia):
    """Fração (não porcentagem); referência zero não possui erro relativo."""
    if referencia == 0:
        return None
    return erro_absoluto(valor, referencia) / abs(referencia)


def validar_resultado(resultado):
    p, g = resultado["parametros"], resultado["grandezas"]
    volume = volume_analitico_esfera(p["raio"])
    massa = massa_analitica_esfera(p["raio"], p["densidade"])
    erro_centro = math.hypot(*g["centro_massa"])
    return {"volume_referencia": volume, "massa_referencia": massa,
            "centro_referencia": (0.0, 0.0, 0.0),
            "erro_volume_absoluto": erro_absoluto(g["volume"], volume),
            "erro_volume_relativo": erro_relativo(g["volume"], volume),
            "erro_massa_absoluto": erro_absoluto(g["massa"], massa),
            "erro_massa_relativo": erro_relativo(g["massa"], massa),
            "erro_centro_absoluto": erro_centro,
            "erro_centro_normalizado": erro_centro / p["raio"]}


def estudo_refinamento(raio, densidade, resultado_atual=None):
    linhas = []
    for n in RESOLUCOES:
        parametros = validar_parametros(raio, densidade, n)
        if resultado_atual is not None and resultado_atual["parametros"] == parametros:
            resultado = resultado_atual
        else:
            resultado = integrar_esfera(raio, densidade, n)
        g, s, v = (resultado["grandezas"], resultado["estatisticas"],
                   validar_resultado(resultado))
        linhas.append({"n": n, "candidatos": s["candidatos"], "aceitos": s["aceitos"],
                       "volume": g["volume"], "massa": g["massa"],
                       "referencia_volume": v["volume_referencia"],
                       "erro_absoluto": v["erro_volume_absoluto"],
                       "erro_percentual": 100 * v["erro_volume_relativo"]})
    return linhas
