"""Componentes Streamlit. Recebem resultados; não executam integrações."""

import streamlit as st


def numero(valor, casas=6):
    if valor != 0 and abs(valor) < 10 ** (-casas):
        return f"{valor:.3e}"
    return f"{valor:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def renderizar_cabecalho():
    st.title("IntegraSol")
    st.write("Laboratório visual de integração múltipla.")



def renderizar_parametros(restaurar):
    with st.sidebar:
        st.header("Parâmetros")
        st.caption("Esfera centrada na origem. Coordenadas em metros.")
        raio = st.number_input("Raio R (m)", min_value=0.5, max_value=3.0,
                               step=0.1, key="raio", format="%.2f")
        densidade = st.number_input("Densidade ρ₀ (kg/m³)", min_value=0.5,
                                    max_value=3.0, step=0.1, key="densidade", format="%.2f")
        resolucao = st.select_slider("Subdivisões por eixo (n)", options=[10, 20, 40],
                                     key="resolucao")
        st.caption("n³ pontos candidatos na caixa [-R, R]³.")
        calcular = st.button("Calcular", type="primary", width="stretch")
        st.button("Restaurar exemplo", on_click=restaurar, width="stretch")
        st.divider()
        st.caption("Exemplo inicial: R = 2 m, ρ₀ = 1 kg/m³, n = 40.")
    return {"raio": raio, "densidade": densidade, "resolucao": resolucao}, calcular


def renderizar_resultados(resultado, validacao):
    p, g, s = (resultado["parametros"], resultado["grandezas"], resultado["estatisticas"])
    st.caption(f"Execução exibida: R = {numero(p['raio'], 2)} m · "
               f"ρ₀ = {numero(p['densidade'], 2)} kg/m³ · n = {p['resolucao']}")
    colunas = st.columns(3)
    colunas[0].metric("Volume aproximado (m³)", numero(g["volume"]))
    colunas[1].metric("Massa aproximada (kg)", numero(g["massa"]))
    colunas[2].metric("Erro relativo de volume (%)",
                      numero(100 * validacao["erro_volume_relativo"]))
    centro = "; ".join(numero(x) for x in g["centro_massa"])
    st.write(f"**Centro de massa (m):** ({centro})")
    st.caption(f"{s['candidatos']:,} candidatos · {s['aceitos']:,} aceitos · "
               f"motor: {s['tempo_execucao'] * 1000:.2f} ms (sem renderização)")


def renderizar_indices(n):
    st.subheader("Região e célula selecionada")
    st.caption(f"Índices de 0 a {n - 1}. A seleção consulta a execução armazenada.")
    colunas = st.columns(3)
    indices = tuple(int(col.number_input(nome, min_value=0, max_value=n - 1,
                                        step=1, key=f"indice_{nome}"))
                    for col, nome in zip(colunas, ("i", "j", "k")))
    mostrar = st.checkbox("Mostrar pontos de amostragem", value=True)
    return indices, mostrar


def renderizar_inspetor(celula):
    st.subheader("Inspeção de uma contribuição")
    estado = "aceito" if celula["pertence"] else "rejeitado"
    st.write(f"**Célula {celula['indices']} · ponto médio {estado}**")
    st.caption("A caixa laranja é a célula inteira. O método testa apenas seu ponto médio; "
               "células na fronteira não são recortadas na superfície da esfera.")
    x, y, z = celula["ponto"]
    dx, dy, dz = celula["passos"]
    linhas = [
        {"Grandeza": "Ponto médio (x, y, z)", "Valor": "; ".join(numero(a) for a in (x,y,z)), "Unidade": "m"},
        {"Grandeza": "Passos (Δx, Δy, Δz)", "Valor": "; ".join(numero(a) for a in (dx,dy,dz)), "Unidade": "m"},
        {"Grandeza": "Jacobiano |J|", "Valor": numero(celula["jacobiano"]), "Unidade": "1"},
        {"Grandeza": "Pertencimento: x² + y² + z² ≤ R²",
         "Valor": f"{numero(celula['distancia_quadrada'])} ≤ {numero(celula['raio_quadrado'])}: {celula['pertence']}", "Unidade": "m²"},
        {"Grandeza": "Elemento da caixa |J|ΔxΔyΔz", "Valor": numero(celula["dv_caixa"]), "Unidade": "m³"},
        {"Grandeza": "Peso χE |J|ΔxΔyΔz", "Valor": numero(celula["peso"]), "Unidade": "m³"},
        {"Grandeza": "Densidade ρ₀", "Valor": numero(celula["densidade"]), "Unidade": "kg/m³"},
        {"Grandeza": "Contribuição Δm = ρ₀w", "Valor": numero(celula["contribuicao_massa"]), "Unidade": "kg"},
        {"Grandeza": "Parcelas (xΔm, yΔm, zΔm)", "Valor": "; ".join(numero(a) for a in celula["contribuicoes_momentos"]), "Unidade": "kg·m"},
    ]
    st.dataframe(linhas, hide_index=True, width="stretch")
    if not celula["pertence"]:
        st.info("O ponto médio está fora da esfera. Esta célula tem peso e contribuição de massa iguais a zero.")


def renderizar_explicacao(resultado):
    p, g = resultado["parametros"], resultado["grandezas"]
    with st.expander("Como o computador calculou?", expanded=False):
        st.markdown("**1. Região.** A esfera está contida na caixa cartesiana [-R, R]³.")
        st.latex(r"E=\{(x,y,z):x^2+y^2+z^2\leq R^2\},\quad |J|=1")
        st.markdown("**2. Discretização.** n subdivisões em cada eixo; amostragem no ponto médio.")
        st.latex(r"\Delta x=\Delta y=\Delta z=\frac{2R}{n},\qquad x_i=-R+(i+\tfrac12)\Delta x")
        st.write(f"Nesta execução: R = {numero(p['raio'], 2)} m; n = {p['resolucao']}.")
        st.markdown("**3. Contribuição.** O indicador χE vale 1 dentro da esfera e 0 fora.")
        st.latex(r"w_{ijk}=\chi_E(x_i,y_j,z_k)|J|\Delta x\Delta y\Delta z,\quad \Delta m_{ijk}=\rho_0w_{ijk}")
        st.markdown("**4. Soma.** Todas as amostras entram nos acumuladores, inclusive as de peso zero.")
        st.latex(r"V_n=\sum_{ijk}w_{ijk},\quad M_n=\sum_{ijk}\Delta m_{ijk}")
        st.latex(r"Q_x=\sum_{ijk}x_i\Delta m_{ijk},\ Q_y=\sum_{ijk}y_j\Delta m_{ijk},\ Q_z=\sum_{ijk}z_k\Delta m_{ijk}")
        st.latex(r"C_n=(Q_x/M_n,\ Q_y/M_n,\ Q_z/M_n)")
        st.write("Primeiros momentos (Qx, Qy, Qz), em kg·m: "
                 + "; ".join(numero(q) for q in g["momentos"]))
        st.caption("Qx é o primeiro momento em relação ao plano yz. Não é momento de inércia. "
                   "O pequeno resíduo no centro decorre da aritmética de ponto flutuante.")


def renderizar_validacao(validacao, refinamento):
    st.subheader("Validação e refinamento")
    st.write(f"Referência independente: **V = {numero(validacao['volume_referencia'], 8)} m³**; "
             f"**M = {numero(validacao['massa_referencia'], 8)} kg**; C = (0, 0, 0) m.")
    st.caption("Vref = 4πR³/3 e Mref = ρ₀Vref são usados apenas para comparação.")
    st.dataframe([
        {"n": l["n"], "Candidatos": l["candidatos"], "Aceitos": l["aceitos"],
         "Volume (m³)": l["volume"], "Massa (kg)": l["massa"],
         "Vref (m³)": l["referencia_volume"], "Erro absoluto (m³)": l["erro_absoluto"],
         "Erro relativo (%)": l["erro_percentual"]} for l in refinamento
    ], hide_index=True, width="stretch", column_config={
        nome: st.column_config.NumberColumn(format="%.6f") for nome in
        ("Volume (m³)", "Massa (kg)", "Vref (m³)", "Erro absoluto (m³)", "Erro relativo (%)")})
    st.write(f"Erro absoluto da massa: {numero(validacao['erro_massa_absoluto'])} kg. "
             f"Erro relativo: {numero(100 * validacao['erro_massa_relativo'])}%.")
    st.write(f"Erro absoluto do centro ‖Cₙ‖: {numero(validacao['erro_centro_absoluto'])} m. "
             f"Erro normalizado ‖Cₙ‖/R: {numero(validacao['erro_centro_normalizado'])}.")
    st.caption("O erro relativo do centro não é definido, pois a referência é zero. "
               "O refinamento mantém raio e densidade fixos. A fronteira cartesiana pode causar "
               "oscilações no erro; redução monotônica não é uma garantia geral.")
