"""Regressões do estado e da ligação entre visualização e cálculo real."""

from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from calculo import integracao
from interface.visualizacao import criar_visualizacao_esfera, selecionar_pontos_visuais

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_visualizacao_preserva_motor_e_limita_pontos():
    resultado = integracao.integrar_esfera(2, 1, 40)
    pesos = resultado["discretizacao"]["pesos"].copy()
    indices = selecionar_pontos_visuais(resultado)
    assert len(indices) == 3000
    np.testing.assert_array_equal(indices, selecionar_pontos_visuais(resultado))
    assert np.all(resultado["discretizacao"]["mascara"].ravel()[indices])
    celula = integracao.inspecionar_celula(resultado, 0, 0, 0)
    figura, contagem = criar_visualizacao_esfera(resultado, celula)
    assert contagem <= 3000
    assert figura.data[-1].x[0] == celula["ponto"][0]
    assert figura.layout.scene.aspectmode == "cube"
    # Ponto selecionado está presente mesmo quando rejeitado pela máscara.
    assert len(figura.data[-1].x) == 1
    assert len(figura.data[1].x) + 1 == contagem
    for ponto, ijk in zip(zip(figura.data[1].x, figura.data[1].y, figura.data[1].z),
                          figura.data[1].customdata):
        np.testing.assert_array_equal(ponto, resultado["discretizacao"]["pontos"][tuple(ijk)])
    np.testing.assert_array_equal(pesos, resultado["discretizacao"]["pesos"])


def test_fluxo_estado_inspecao_e_recalculo(monkeypatch):
    original = integracao.integrar_esfera
    chamadas = []
    def registrar(**parametros):
        chamadas.append(parametros)
        return original(**parametros)
    monkeypatch.setattr(integracao, "integrar_esfera", registrar)
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    assert not app.exception
    assert app.session_state["resultado"] is None
    app.button[0].click().run()
    assert not app.exception
    assert len(chamadas) == 1
    assert app.session_state["resultado"]["grandezas"]["volume"] == pytest.approx(33.552)
    app.number_input(key="indice_i").set_value(0).run()
    assert not app.exception
    assert len(chamadas) == 1
    # Alterar raio não mistura parâmetros pendentes com os resultados anteriores.
    app.number_input(key="raio").set_value(1.0).run()
    assert not app.exception
    assert len(app.warning) == 1
    assert app.session_state["resultado"]["parametros"]["raio"] == 2
    assert len(chamadas) == 1
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["resultado"]["grandezas"]["volume"] == pytest.approx(4.194)
    assert len(chamadas) == 2
    app.number_input(key="indice_k").set_value(39).run()
    app.select_slider[0].set_value(10).run()
    app.button[0].click().run()
    assert not app.exception
    assert app.number_input(key="indice_k").value < 10
    app.button[1].click().run()
    assert not app.exception
    assert app.session_state["resultado"]["parametros"] == dict(raio=2.,densidade=1.,resolucao=40)
    assert app.number_input(key="indice_i").value == 20
    assert len(app.warning) == 0
