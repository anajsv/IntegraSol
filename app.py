"""Ponto de entrada: coordena motor, estado, validação e apresentação."""

import streamlit as st

from calculo import integracao, validacao
from interface import componentes as ui
from interface.visualizacao import criar_visualizacao_esfera


def restaurar_exemplo():
    st.session_state.update(raio=2.0, densidade=1.0, resolucao=40,
                            resultado=None, validacao=None, refinamento=None,
                            indice_i=20, indice_j=20, indice_k=20,
                            calcular_exemplo=True)


def main():
    st.set_page_config(page_title="IntegraSol | Cálculo III", layout="wide")
    for chave, valor in {"raio": 2.0, "densidade": 1.0, "resolucao": 40,
                         "resultado": None, "calcular_exemplo": False}.items():
        st.session_state.setdefault(chave, valor)
    ui.renderizar_cabecalho()
    parametros, calcular = ui.renderizar_parametros(restaurar_exemplo)
    calcular = st.session_state.pop("calcular_exemplo", False) or calcular
    if calcular:
        try:
            with st.spinner("Somando contribuições e conferindo referências..."):
                resultado = integracao.integrar_esfera(**parametros)
                conferencia = validacao.validar_resultado(resultado)
                refinamento = validacao.estudo_refinamento(
                    parametros["raio"], parametros["densidade"], resultado)
            st.session_state.update(resultado=resultado, validacao=conferencia,
                                    refinamento=refinamento)
        except ValueError as erro:
            st.error(str(erro))
    resultado = st.session_state.resultado
    if resultado is None:
        st.info("Ajuste os parâmetros e clique em Calcular para iniciar a soma de Riemann.")
        return
    if parametros != resultado["parametros"]:
        st.warning("Parâmetros alterados. Clique em Calcular para atualizar. "
                   "Os resultados, a cena e o inspetor ainda pertencem à execução indicada abaixo.")
    else:
        st.caption("Resultado atualizado para os parâmetros selecionados.")
    ui.renderizar_resultados(resultado, st.session_state.validacao)
    st.divider()
    n = resultado["parametros"]["resolucao"]
    for eixo in ("i", "j", "k"):
        chave = f"indice_{eixo}"
        if chave not in st.session_state or st.session_state[chave] >= n:
            st.session_state[chave] = n // 2
    indices, mostrar = ui.renderizar_indices(n)
    celula = integracao.inspecionar_celula(resultado, *indices)
    figura, desenhados = criar_visualizacao_esfera(resultado, celula, mostrar)
    st.plotly_chart(figura, width="stretch", theme=None, key="cena",
                    config={"displaylogo": False})
    st.caption(f"{desenhados} pontos médios desenhados (inclui o selecionado, mesmo fora da esfera). "
               "Seleção determinística de até 3.000 pontos; o motor soma todos os candidatos. "
               "Arraste para girar e use a roda do mouse para aproximar.")
    ui.renderizar_inspetor(celula)
    ui.renderizar_explicacao(resultado)
    st.divider()
    ui.renderizar_validacao(st.session_state.validacao, st.session_state.refinamento)
    st.divider()
    st.caption("Protótipo educacional · Núcleo próprio de pontos médios · "
               "Limitações: esfera na origem, densidade constante, resolução até 40.")


if __name__ == "__main__":
    main()
