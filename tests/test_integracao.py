"""Conferências do método, propriedades físicas e rastreabilidade da grade."""

import math
import subprocess
import sys

import numpy as np
import pytest

from calculo.coordenadas import elemento_volume_cartesiano, jacobiano_cartesiano
from calculo.geometria import obter_limites_esfera, pertence_esfera
from calculo.integracao import (calcular_centro_massa, gerar_pontos_medios,
                               inspecionar_celula, integrar_esfera)
from calculo.validacao import (erro_absoluto, erro_relativo, estudo_refinamento,
                              validar_resultado, volume_analitico_esfera)


@pytest.mark.parametrize("campo,valor", [
    ("raio", 0), ("raio", -1), ("raio", float("nan")),
    ("raio", float("inf")), ("raio", True), ("raio", "2"),
    ("densidade", 0), ("densidade", -1), ("densidade", float("nan")),
    ("densidade", float("inf")), ("densidade", True), ("densidade", "1"),
    ("resolucao", 0), ("resolucao", 15), ("resolucao", 20.0),
    ("resolucao", True), ("resolucao", "40"),
])
def test_parametros_invalidos(campo, valor):
    parametros = dict(raio=2, densidade=1, resolucao=10)
    parametros[campo] = valor
    with pytest.raises(ValueError):
        integrar_esfera(**parametros)


def test_pontos_medios_e_limites():
    np.testing.assert_allclose(gerar_pontos_medios(-2, 2, 4), [-1.5, -.5, .5, 1.5])
    assert obter_limites_esfera(2) == ((-2, 2),) * 3


@pytest.mark.parametrize("inicio,fim,n", [(0, 0, 4), (2, -2, 4), (0, 1, 0),
                                         (0, 1, 2.5), (0, 1, True)])
def test_discretizacao_invalida(inicio, fim, n):
    with pytest.raises(ValueError):
        gerar_pontos_medios(inicio, fim, n)


def test_mascara_inclui_fronteira():
    pontos = [[0, 0, 0], [2, 0, 0], [2.01, 0, 0], [1.5, 1.5, 1.5]]
    np.testing.assert_array_equal(pertence_esfera(pontos, 2), [True, True, False, False])


def test_jacobiano_e_elemento():
    assert jacobiano_cartesiano() == 1
    assert elemento_volume_cartesiano(.1, .2, .3) == pytest.approx(.006)
    with pytest.raises(ValueError):
        elemento_volume_cartesiano(0, .2, .3)


@pytest.mark.parametrize("n,aceitos,volume", [(10, 552, 35.328),
                                           (20, 4224, 33.792), (40, 33552, 33.552)])
def test_referencia_numerica(n, aceitos, volume):
    r = integrar_esfera(2, 1, n)
    d, g = r["discretizacao"], r["grandezas"]
    assert r["estatisticas"]["candidatos"] == n ** 3
    assert r["estatisticas"]["aceitos"] == aceitos
    assert d["pontos"].shape == (n, n, n, 3)
    assert d["pontos"].dtype == np.float64
    assert d["pesos"].shape == d["mascara"].shape == (n, n, n)
    assert g["volume"] == pytest.approx(volume, abs=1e-10)
    assert g["massa"] == pytest.approx(volume, abs=1e-10)
    np.testing.assert_allclose(g["momentos"], 0, atol=1e-12)
    np.testing.assert_allclose(g["centro_massa"], 0, atol=1e-13)
    assert np.all(d["pesos"][~d["mascara"]] == 0)
    np.testing.assert_allclose(d["pesos"][d["mascara"]], (4/n) ** 3)
    if n == 40:
        assert validar_resultado(r)["erro_volume_relativo"] < .01


def test_soma_independente_com_lacos():
    # Conferência sem meshgrid, máscara vetorial ou referências analíticas.
    r = integrar_esfera(2, 1.7, 10)
    volume = massa = 0.0
    momentos = np.zeros(3)
    for i in range(10):
        for j in range(10):
            for k in range(10):
                x, y, z = (-2 + (a + .5) * .4 for a in (i, j, k))
                if x*x + y*y + z*z <= 4:
                    volume += .4 ** 3
                    dm = 1.7 * .4 ** 3
                    massa += dm
                    momentos += np.array([x, y, z]) * dm
    assert r["grandezas"]["volume"] == pytest.approx(volume, abs=1e-10)
    assert r["grandezas"]["massa"] == pytest.approx(massa, abs=1e-10)
    np.testing.assert_allclose(r["grandezas"]["momentos"], momentos, atol=1e-11)


@pytest.mark.parametrize("raio", [.5, 1, 2, 3])
def test_escala_do_raio(raio):
    unitario = integrar_esfera(1, 1, 40)
    r = integrar_esfera(raio, 1, 40)
    assert r["grandezas"]["volume"] == pytest.approx(unitario["grandezas"]["volume"] * raio**3)
    assert r["estatisticas"]["aceitos"] == 33552
    assert validar_resultado(r)["erro_volume_relativo"] < .01


@pytest.mark.parametrize("densidade", [.5, 1, 1.7, 3])
def test_densidade_escala_massa(densidade):
    r = integrar_esfera(2, densidade, 20)
    assert r["grandezas"]["massa"] == pytest.approx(densidade * r["grandezas"]["volume"])
    np.testing.assert_allclose(r["grandezas"]["centro_massa"], 0, atol=1e-13)


@pytest.mark.parametrize("indices,pertence", [((20, 20, 20), True), ((0, 0, 0), False),
                                            ((0, 20, 20), True), ((39, 39, 39), False)])
def test_inspecao(indices, pertence):
    r = integrar_esfera(2, 1.7, 40)
    celula = inspecionar_celula(r, *indices)
    d = r["discretizacao"]
    assert celula["pertence"] is pertence
    np.testing.assert_array_equal(celula["ponto"], d["pontos"][indices])
    assert celula["peso"] == d["pesos"][indices]
    assert celula["contribuicao_massa"] == d["contribuicoes"][indices]
    assert celula["indice_linear"] == np.ravel_multi_index(indices, (40,40,40))
    np.testing.assert_allclose(celula["contribuicoes_momentos"],
                               d["pontos"][indices] * d["contribuicoes"][indices])
    for (lo, hi), ponto in zip(celula["limites"], celula["ponto"]):
        assert (lo + hi) / 2 == pytest.approx(ponto)
        assert hi - lo == pytest.approx(.1)


@pytest.mark.parametrize("indices", [(-1,0,0), (10,0,0), (1.2,0,0), (True,0,0)])
def test_indices_invalidos(indices):
    with pytest.raises(ValueError):
        inspecionar_celula(integrar_esfera(2, 1, 10), *indices)


def test_referencias_e_erros():
    assert volume_analitico_esfera(2) == pytest.approx(32 * math.pi / 3)
    assert erro_absoluto(9, 10) == 1
    assert erro_relativo(9, 10) == pytest.approx(.1)
    assert erro_relativo(-9, -10) == pytest.approx(.1)
    assert erro_relativo(0, 0) is None
    v = validar_resultado(integrar_esfera(2, 1.7, 40))
    assert v["massa_referencia"] == pytest.approx(1.7 * 32 * math.pi / 3)
    assert v["erro_centro_normalizado"] == pytest.approx(v["erro_centro_absoluto"] / 2)
    with pytest.raises(ValueError):
        calcular_centro_massa((0,0,0), 0)


def test_refinamento_preserva_parametros_e_reutiliza_resultado(monkeypatch):
    from calculo import validacao
    atual = integrar_esfera(1.5, 2.2, 20)
    original = validacao.integrar_esfera
    chamadas = []
    def registrar(raio, densidade, n):
        chamadas.append((raio, densidade, n))
        return original(raio, densidade, n)
    monkeypatch.setattr(validacao, "integrar_esfera", registrar)
    linhas = estudo_refinamento(1.5, 2.2, atual)
    assert chamadas == [(1.5, 2.2, 10), (1.5, 2.2, 40)]
    assert [l["n"] for l in linhas] == [10,20,40]
    for linha in linhas:
        assert linha["massa"] == pytest.approx(2.2 * linha["volume"])
        assert linha["referencia_volume"] == pytest.approx(4 * math.pi * 1.5**3 / 3)


def test_nucleo_nao_importa_interface():
    processo = subprocess.run([sys.executable, "-c",
        "import sys; from calculo.integracao import integrar_esfera; "
        "integrar_esfera(2,1,10); "
        "assert not any(x in sys.modules for x in ['streamlit','plotly','interface'])"],
        capture_output=True, text=True)
    assert processo.returncode == 0, processo.stderr
