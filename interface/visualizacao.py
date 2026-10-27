"""Cena Plotly; a superfície é ilustrativa, as amostras vêm do motor."""

from itertools import product

import numpy as np
import plotly.graph_objects as go

AZUL = "#2463A0"
LARANJA = "#BC5C18"


def criar_superficie_esfera(raio):
    theta, phi = np.meshgrid(np.linspace(0, 2 * np.pi, 60),
                             np.linspace(0, np.pi, 36))
    return go.Surface(
        x=raio * np.sin(phi) * np.cos(theta),
        y=raio * np.sin(phi) * np.sin(theta), z=raio * np.cos(phi),
        colorscale=[[0, AZUL], [1, AZUL]], showscale=False,
        opacity=0.13, name="Superfície de referência", showlegend=True,
        hoverinfo="skip")


def selecionar_pontos_visuais(resultado, limite=3000):
    """Índices lineares determinísticos; k varia mais rapidamente (ordem C)."""
    if limite < 1:
        raise ValueError("O limite visual deve ser positivo.")
    aceitos = np.flatnonzero(resultado["discretizacao"]["mascara"].ravel())
    if len(aceitos) <= limite:
        return aceitos
    return aceitos[np.linspace(0, len(aceitos) - 1, limite, dtype=int)]


def criar_pontos_amostragem(resultado, indices):
    pontos = resultado["discretizacao"]["pontos"].reshape(-1, 3)[indices]
    n = resultado["parametros"]["resolucao"]
    ijk = np.stack(np.unravel_index(indices, (n, n, n)), axis=-1)
    return go.Scatter3d(
        x=pontos[:, 0], y=pontos[:, 1], z=pontos[:, 2], customdata=ijk,
        mode="markers", marker=dict(size=2, color=AZUL, opacity=0.5),
        name="Pontos médios aceitos",
        hovertemplate="i=%{customdata[0]}, j=%{customdata[1]}, k=%{customdata[2]}"
                      "<br>x=%{x:.4f} m<br>y=%{y:.4f} m<br>z=%{z:.4f} m<extra></extra>")


def criar_marcador_centro(resultado):
    x, y, z = resultado["grandezas"]["centro_massa"]
    return go.Scatter3d(x=[x], y=[y], z=[z], mode="markers",
                        marker=dict(size=7, color="#26323F", symbol="diamond"),
                        name="Centro de massa",
                        hovertemplate="Centro: (%{x:.3e}, %{y:.3e}, %{z:.3e}) m<extra></extra>")


def criar_celula_selecionada(celula):
    """Doze arestas da caixa real, sem sugerir recorte exato na fronteira."""
    vertices = np.array(list(product(*celula["limites"])))
    xyz = [[], [], []]
    for a in range(8):
        for b in range(a + 1, 8):
            if (a ^ b) in (1, 2, 4):
                for eixo in range(3):
                    xyz[eixo].extend([vertices[a, eixo], vertices[b, eixo], None])
    caixa = go.Scatter3d(x=xyz[0], y=xyz[1], z=xyz[2], mode="lines",
                         line=dict(color=LARANJA, width=6), name="Célula selecionada",
                         hoverinfo="skip")
    x, y, z = celula["ponto"]
    ponto = go.Scatter3d(
        x=[x], y=[y], z=[z], mode="markers",
        marker=dict(color=LARANJA, size=7, symbol="x"), name="Amostra selecionada",
        hovertemplate=f"Índices {celula['indices']}<br>"
                      "(%{x:.4f}, %{y:.4f}, %{z:.4f}) m<extra></extra>")
    return caixa, ponto


def configurar_cena(figura, raio, revisao):
    eixo = dict(range=[-raio * 1.12, raio * 1.12], backgroundcolor="#FAFBFC",
                gridcolor="#DFE5EB", zerolinecolor="#CCD4DD")
    figura.update_layout(
        template="plotly_white", height=520, margin=dict(l=0, r=0, t=5, b=0),
        font=dict(family="Arial", color="#26323F"),
        legend=dict(orientation="h", y=-0.06, x=0),
        scene=dict(xaxis=dict(eixo, title="x (m)"), yaxis=dict(eixo, title="y (m)"),
                   zaxis=dict(eixo, title="z (m)"), aspectmode="cube",
                   camera=dict(eye=dict(x=1.65, y=1.65, z=1.15))),
        uirevision=revisao)
    return figura


def criar_visualizacao_esfera(resultado, celula, mostrar_pontos=True):
    # Reserva uma vaga para a amostra selecionada, desenhada em outra trace.
    indices = selecionar_pontos_visuais(resultado, limite=2999)
    indices = indices[indices != celula["indice_linear"]]
    figura = go.Figure([criar_superficie_esfera(resultado["parametros"]["raio"])])
    if mostrar_pontos:
        figura.add_trace(criar_pontos_amostragem(resultado, indices))
    figura.add_trace(criar_marcador_centro(resultado))
    figura.add_traces(list(criar_celula_selecionada(celula)))
    p = resultado["parametros"]
    configurar_cena(figura, p["raio"], str(tuple(p.values())))
    desenhados = (len(indices) if mostrar_pontos else 0) + 1
    return figura, desenhados
