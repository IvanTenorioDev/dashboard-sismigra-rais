"""Figuras da aba Q4 — o índice Q e o que ele mede.

São três, e cada uma responde a uma objeção diferente:

1. *Como o índice se distribui?* — histograma em escala logarítmica;
2. *Os valores extremos são artefato de denominador pequeno?* — índice contra volume;
3. *O índice diz algo sobre remuneração?* — índice contra salário, com a mediana de
   cada faixa sobreposta.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from nucleo.config import AZUL, CINZA, LARANJA
from nucleo.dados import FAIXAS_Q, Artefatos
from nucleo.formatos import formatar_decimal, formatar_inteiro
from nucleo.graficos_base import (
    ALTURA,
    MARGEM,
    cor_da_regiao,
    eixo_log_q,
    em_log10,
    faixa_log,
    marcar_paridade,
    nome_regiao,
    regioes_presentes,
    titulo_figura,
)

POSICOES_DO_ROTULO = ("top center", "bottom center")


def distribuicao_q(artefatos: Artefatos) -> go.Figure:
    """Histograma do índice em escala logarítmica, com a linha de paridade."""
    indice = artefatos.perfis["Q_medio"]
    mediana = float(indice.median())
    figura = go.Figure(go.Histogram(
        x=em_log10(indice),
        nbinsx=28,
        marker_color=AZUL,
        hovertemplate="posição %{x:.2f}<br>%{y} nacionalidade(s)<extra></extra>",
    ))
    marcar_paridade(figura, vertical=True)
    figura.add_vline(
        x=float(np.log10(mediana)),
        line_color=CINZA,
        line_width=1.5,
        annotation_text=f"mediana {formatar_decimal(mediana, 2)}",
        annotation_position="bottom left",
        annotation_font_size=11,
    )
    figura.update_layout(
        template="plotly_white",
        height=ALTURA,
        margin=MARGEM,
        bargap=0.06,
        title=titulo_figura("Distribuição do índice Q entre as nacionalidades elegíveis"),
    )
    figura.update_xaxes(title_text="índice Q (escala logarítmica)", **eixo_log_q())
    figura.update_yaxes(title_text="nacionalidades", automargin=True)
    return figura


def _rotulos_dos_extremos(perfis: pd.DataFrame, quantos: int = 3) -> go.Scatter:
    """Rotula os maiores índices, como traço e não como anotação.

    Anotação com referência de dados não renderiza de forma confiável aqui, e a
    informação precisa estar à vista: sem o rótulo, o extremo superior fica sem
    identificação e o leitor não sabe de quem é o ponto solto.

    As posições alternam porque dois dos maiores índices ficam à mesma altura: com o
    rótulo sempre acima, um texto cobre o outro.
    """
    maiores = perfis.nlargest(quantos, "Q_medio")
    return go.Scatter(
        x=maiores["V_total"],
        y=em_log10(maiores["Q_medio"]),
        mode="markers+text",
        name="maiores índices",
        text=[
            f"{nome} · {formatar_inteiro(volume)}"
            for nome, volume in zip(maiores["nacionalidade"], maiores["V_total"])
        ],
        textposition=[POSICOES_DO_ROTULO[i % len(POSICOES_DO_ROTULO)] for i in range(len(maiores))],
        textfont=dict(size=11, color=CINZA),
        marker=dict(size=11, color=CINZA, symbol="circle-open", line=dict(width=1.6)),
        hovertemplate="<b>%{text}</b><extra></extra>",
    )


def q_versus_volume(artefatos: Artefatos) -> go.Figure:
    """Índice contra volume de vínculos — onde os valores extremos realmente estão."""
    perfis = artefatos.perfis
    limite_de_q = faixa_log(perfis["Q_medio"], 1.1)
    figura = go.Figure()
    for regiao in regioes_presentes(perfis):
        recorte = perfis[perfis["regiao"].eq(regiao)]
        figura.add_trace(go.Scatter(
            x=recorte["V_total"],
            y=em_log10(recorte["Q_medio"]),
            mode="markers",
            name=nome_regiao(regiao),
            marker=dict(size=10, color=cor_da_regiao(regiao), line=dict(width=0.6, color="white")),
            customdata=np.column_stack([recorte["nacionalidade"], recorte["Q_medio"]]),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>Q = %{customdata[1]:.2f}"
                "<br>vínculos na janela = %{x:,.0f}<extra></extra>"
            ),
        ))
    marcar_paridade(figura, vertical=False)
    figura.add_trace(_rotulos_dos_extremos(perfis))
    figura.update_layout(
        template="plotly_white",
        height=ALTURA,
        margin=MARGEM,
        title=titulo_figura("Índice Q contra volume de vínculos — a cauda não segue o tamanho"),
        legend=dict(orientation="h", y=-0.2, title_text=""),
    )
    figura.update_xaxes(
        type="log",
        title_text="vínculos na janela (escala logarítmica)",
        range=faixa_log(perfis["V_total"], 1.8),
    )
    figura.update_yaxes(
        title_text="índice Q (escala logarítmica)",
        range=[limite_de_q[0], limite_de_q[1] + 0.55],
        **eixo_log_q(),
    )
    return figura


def q_versus_remuneracao(artefatos: Artefatos) -> go.Figure:
    """Índice contra remuneração, com a mediana de cada faixa de Q sobreposta."""
    perfis = artefatos.perfis
    faixas = artefatos.faixas_de_q()
    figura = go.Figure()
    for regiao in regioes_presentes(perfis):
        recorte = perfis[perfis["regiao"].eq(regiao)]
        figura.add_trace(go.Scatter(
            x=em_log10(recorte["Q_medio"]),
            y=recorte["salario_medio_sm"],
            mode="markers",
            name=nome_regiao(regiao),
            marker=dict(size=10, color=cor_da_regiao(regiao), opacity=0.75),
            customdata=np.column_stack([recorte["nacionalidade"], recorte["Q_medio"]]),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>Q = %{customdata[1]:.2f}"
                "<br>salário médio = %{y:.2f} SM<extra></extra>"
            ),
        ))
    centros, alturas = [], []
    for inicio, fim, _ in FAIXAS_Q:
        recorte = perfis[perfis["Q_medio"].gt(inicio) & perfis["Q_medio"].le(fim)]
        if len(recorte):
            centros.append(float(np.log10(recorte["Q_medio"].median())))
            alturas.append(float(recorte["salario_medio_sm"].median()))
    figura.add_trace(go.Scatter(
        x=centros,
        y=alturas,
        mode="lines+markers",
        name="mediana da faixa de Q",
        line=dict(color=LARANJA, width=3),
        marker=dict(size=15, color=LARANJA, line=dict(width=1.5, color="white")),
        hovertemplate="mediana da faixa<br>salário = %{y:.2f} SM<extra></extra>",
    ))
    marcar_paridade(figura, vertical=True)
    figura.update_layout(
        template="plotly_white",
        height=ALTURA,
        margin=MARGEM,
        title=titulo_figura("Índice Q contra remuneração — a queda é monotônica"),
        legend=dict(orientation="h", y=-0.2, title_text=""),
    )
    figura.update_xaxes(title_text="índice Q (escala logarítmica)", **eixo_log_q())
    figura.update_yaxes(title_text="salário médio (salários mínimos)")
    return figura
