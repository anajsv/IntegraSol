"""Domínio cartesiano da esfera centrada na origem."""

from numbers import Real

import numpy as np


def validar_raio(raio):
    if isinstance(raio, (bool, np.bool_)) or not isinstance(raio, Real):
        raise ValueError("O raio deve ser um número real positivo e finito.")
    if not np.isfinite(raio) or raio <= 0:
        raise ValueError("O raio deve ser positivo e finito.")
    return float(raio)


def obter_limites_esfera(raio):
    raio = validar_raio(raio)
    return ((-raio, raio),) * 3


def pertence_esfera(pontos, raio):
    """Aceita arrays (..., 3); a fronteira pertence à região."""
    raio = validar_raio(raio)
    pontos = np.asarray(pontos, dtype=np.float64)
    # Normalizar evita elevar raios muito grandes ao quadrado.
    return np.sum((pontos / raio) ** 2, axis=-1) <= 1.0
