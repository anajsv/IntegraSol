"""Somas de Riemann: grade -> máscara -> pesos -> massa -> momentos."""

from numbers import Integral, Real
from time import perf_counter

import numpy as np

from .coordenadas import elemento_volume_cartesiano, jacobiano_cartesiano
from .geometria import obter_limites_esfera, pertence_esfera, validar_raio

RESOLUCOES = (10, 20, 40)


def validar_parametros(raio, densidade, resolucao):
    raio = validar_raio(raio)
    if (isinstance(densidade, (bool, np.bool_))
            or not isinstance(densidade, Real)
            or not np.isfinite(densidade) or densidade <= 0):
        raise ValueError("A densidade deve ser positiva e finita.")
    if (isinstance(resolucao, (bool, np.bool_))
            or not isinstance(resolucao, Integral)
            or resolucao not in RESOLUCOES):
        raise ValueError("Escolha a resolução inteira 10, 20 ou 40.")
    return {"raio": raio, "densidade": float(densidade),
            "resolucao": int(resolucao)}


def gerar_pontos_medios(inicio, fim, n):
    if isinstance(n, bool) or not isinstance(n, Integral) or n <= 0:
        raise ValueError("A quantidade de subdivisões deve ser inteira positiva.")
    if not np.isfinite(inicio) or not np.isfinite(fim) or fim <= inicio:
        raise ValueError("Os limites devem ser finitos e crescentes.")
    passo = (fim - inicio) / n
    return inicio + (np.arange(n, dtype=np.float64) + 0.5) * passo


def gerar_discretizacao(raio, resolucao):
    limites = obter_limites_esfera(raio)
    eixo = gerar_pontos_medios(*limites[0], resolucao)
    pontos = np.stack(np.meshgrid(eixo, eixo, eixo, indexing="ij"), axis=-1)
    passo = (limites[0][1] - limites[0][0]) / resolucao
    return {"pontos": pontos, "passos": (passo,) * 3,
            "mascara": pertence_esfera(pontos, raio),
            "jacobiano": jacobiano_cartesiano(), "limites": limites}


def calcular_pesos(mascara, passos):
    return mascara * elemento_volume_cartesiano(*passos)


def calcular_contribuicoes(pesos, densidade):
    return pesos * densidade


def calcular_volume(pesos):
    return float(np.sum(pesos, dtype=np.float64))


def calcular_massa(contribuicoes):
    return float(np.sum(contribuicoes, dtype=np.float64))


def calcular_momentos(pontos, contribuicoes):
    return tuple(float(np.sum(pontos[..., e] * contribuicoes, dtype=np.float64))
                 for e in range(3))


def calcular_centro_massa(momentos, massa):
    if not np.isfinite(massa) or massa <= 0:
        raise ValueError("Massa positiva e finita é necessária para calcular o centro.")
    return tuple(float(q / massa) for q in momentos)


def integrar_esfera(raio, densidade, resolucao):
    """Retorna arrays em ordem [i,j,k]; nenhuma fórmula analítica é usada."""
    inicio = perf_counter()
    parametros = validar_parametros(raio, densidade, resolucao)
    grade = gerar_discretizacao(parametros["raio"], parametros["resolucao"])
    with np.errstate(over="ignore", invalid="ignore", under="ignore"):
        pesos = calcular_pesos(grade["mascara"], grade["passos"])
        contribuicoes = calcular_contribuicoes(pesos, parametros["densidade"])
        volume = calcular_volume(pesos)
        massa = calcular_massa(contribuicoes)
        momentos = calcular_momentos(grade["pontos"], contribuicoes)
    if not np.all(np.isfinite((volume, massa, *momentos))) or volume <= 0:
        raise ValueError("Parâmetros fora da faixa numérica suportada.")
    centro = calcular_centro_massa(momentos, massa)
    grade.update(pesos=pesos, contribuicoes=contribuicoes)
    return {
        "parametros": parametros,
        "grandezas": {"volume": volume, "massa": massa,
                      "momentos": momentos, "centro_massa": centro},
        "discretizacao": grade,
        "estatisticas": {"candidatos": parametros["resolucao"] ** 3,
                         "aceitos": int(np.count_nonzero(grade["mascara"])),
                         "tempo_execucao": perf_counter() - inicio},
    }


def inspecionar_celula(resultado, i, j, k):
    """Consulta uma célula preservada; não executa uma nova integração."""
    n = resultado["parametros"]["resolucao"]
    for indice in (i, j, k):
        if (isinstance(indice, (bool, np.bool_))
                or not isinstance(indice, Integral) or not 0 <= indice < n):
            raise ValueError(f"Os índices devem ser inteiros entre 0 e {n - 1}.")
    indices = (int(i), int(j), int(k))
    grade = resultado["discretizacao"]
    ponto = grade["pontos"][indices]
    dm = float(grade["contribuicoes"][indices])
    return {
        "indices": indices, "indice_linear": (i * n + j) * n + k,
        "ponto": tuple(float(x) for x in ponto),
        "passos": grade["passos"], "jacobiano": grade["jacobiano"],
        "pertence": bool(grade["mascara"][indices]),
        "peso": float(grade["pesos"][indices]),
        "dv_caixa": elemento_volume_cartesiano(*grade["passos"]),
        "densidade": resultado["parametros"]["densidade"],
        "contribuicao_massa": dm,
        "contribuicoes_momentos": tuple(float(x * dm) for x in ponto),
        "distancia_quadrada": float(np.dot(ponto, ponto)),
        "raio_quadrado": resultado["parametros"]["raio"] ** 2,
        "limites": tuple((float(x - h / 2), float(x + h / 2))
                         for x, h in zip(ponto, grade["passos"])),
    }
