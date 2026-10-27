"""Fator de volume no sistema cartesiano (transformação identidade)."""

import numpy as np


def jacobiano_cartesiano():
    return 1.0


def elemento_volume_cartesiano(dx, dy, dz):
    passos = np.asarray((dx, dy, dz), dtype=np.float64)
    if not np.all(np.isfinite(passos)) or np.any(passos <= 0):
        raise ValueError("Os passos devem ser positivos e finitos.")
    with np.errstate(over="ignore", under="ignore"):
        dv = float(np.prod(passos) * abs(jacobiano_cartesiano()))
    if not np.isfinite(dv) or dv <= 0:
        raise ValueError("Elemento de volume fora da faixa numérica suportada.")
    return dv
