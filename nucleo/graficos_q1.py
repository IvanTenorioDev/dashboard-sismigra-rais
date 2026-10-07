"""Figuras da aba Q1 — a evolução da presença ao longo dos anos.

O que esta aba precisa deixar visível é que os dois lados da razão Q **não têm a mesma
cobertura**: os vínculos formais existem desde 2010, o estoque de registros ativos só a
partir de 2022. Um eixo único esconderia isso atrás da diferença de escala — o estoque é
uma ordem de grandeza maior que o vínculo no mesmo ano.
"""

from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from nucleo.config import AZUL, LARANJA
from nucleo.dados import Artefatos
from nucleo.graficos_base import (
    ALTURA,
    ALTURA_ALTA,
    LEGENDA_ABAIXO,
    MARGEM,
    MARGEM_INFERIOR_AMPLA,
    eixo_de_anos,
    titulo_figura,
)


def evolucao_da_presenca(artefatos: Artefatos) -> go.Figure:
    """Os dois lados empilhados, com o mesmo eixo de anos e escalas próprias.

    Vínculo e registro não se somam nem se comparam em nível: um é posto de trabalho
    formal no fim do ano, o outro é registro ativo na base migratória. O painel duplo
    permite ler os dois crescimentos sem que o maior esmague o menor, e expõe a lacuna de
    cobertura — o painel de baixo simplesmente começa depois.
    """
    resumo = artefatos.resumo_anual
    figura = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.16,
        subplot_titles=(
            "Vínculos formais — RAIS-CTPS, estoque em 31/12",
            "Registros ativos — SISMIGRA, estoque de dezembro",
        ),
    )
    figura.add_trace(
        go.Bar(x=resumo["ano"], y=resumo["vinculos_formais"], marker_color=AZUL),
        row=1,
        col=1,
    )
    figura.add_trace(
        go.Scatter(
            x=resumo["ano"],
            y=resumo["registros_ativos"],
            mode="lines+markers",
            line={"color": LARANJA, "width": 2},
            marker={"size": 8},
        ),
        row=2,
        col=1,
    )
    figura.update_yaxes(title_text="vínculos", row=1, col=1)
    figura.update_yaxes(title_text="registros", row=2, col=1)
    figura.update_xaxes(eixo_de_anos(resumo["ano"]), row=2, col=1)
    figura.update_layout(
        height=ALTURA_ALTA,
        margin=MARGEM,
        showlegend=False,
        bargap=0.25,
    )
    return figura


def razao_entre_os_lados(artefatos: Artefatos) -> go.Figure:
    """Vínculos por registro, nos anos em que os dois lados existem.

    É a leitura direta da convergência: a razão sobe quando o estoque migratório passa a
    se converter em vínculo formal a uma taxa maior. Só há quatro pontos porque só há
    quatro anos com os dois lados observados.
    """
    resumo = artefatos.resumo_anual.dropna(subset=["razao_vinculos_por_registros"])
    figura = go.Figure(
        go.Scatter(
            x=resumo["ano"],
            y=resumo["razao_vinculos_por_registros"],
            mode="lines+markers+text",
            text=[
                f"{valor:.1%}".replace(".", ",")
                for valor in resumo["razao_vinculos_por_registros"]
            ],
            textposition="top center",
            line={"color": LARANJA, "width": 2},
            marker={"size": 10},
        )
    )
    figura.update_yaxes(title_text="vínculos por registro", tickformat=".0%")
    figura.update_xaxes(eixo_de_anos(resumo["ano"], passo=1))
    figura.update_layout(
        height=ALTURA,
        margin=MARGEM,
        showlegend=False,
        title=titulo_figura("Vínculos formais por registro ativo"),
    )
    return figura


def diversidade_por_ano(artefatos: Artefatos) -> go.Figure:
    """Quantas nacionalidades aparecem em cada ano, em cada lado.

    Mostra que o crescimento não é só de volume: o número de origens presentes também
    sobe. As duas linhas têm coberturas diferentes, e a lacuna é intencional.
    """
    resumo = artefatos.resumo_anual
    figura = go.Figure()
    figura.add_trace(
        go.Scatter(
            x=resumo["ano"],
            y=resumo["nacionalidades_com_vinculos"],
            mode="lines+markers",
            name="com vínculos formais",
            line={"color": AZUL, "width": 2},
        )
    )
    figura.add_trace(
        go.Scatter(
            x=resumo["ano"],
            y=resumo["nacionalidades_com_registros"],
            mode="lines+markers",
            name="com registros ativos",
            line={"color": LARANJA, "width": 2},
        )
    )
    figura.update_yaxes(title_text="nacionalidades")
    figura.update_xaxes(eixo_de_anos(resumo["ano"]))
    figura.update_layout(
        height=ALTURA,
        margin=MARGEM_INFERIOR_AMPLA,
        title=titulo_figura("Nacionalidades presentes em cada ano"),
        legend=LEGENDA_ABAIXO,
    )
    return figura
