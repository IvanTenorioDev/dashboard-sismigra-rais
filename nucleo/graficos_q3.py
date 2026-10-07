"""Figuras da aba Q3 — o fluxo de registros, ano a ano.

Duas armadilhas de leitura moram nesta série, e as duas figuras existem para desarmá-las:

  - **2017 não existe na fonte.** Não é zero, é ausência. A malha do eixo é construída
    sobre o intervalo completo para que a lacuna apareça como lacuna.
  - **2026 está em curso.** A extração foi feita antes do fim do ano civil, então o último
    ponto tem menos meses que os outros. Sem marca, ele lê como queda de fluxo.
"""

from __future__ import annotations

import plotly.graph_objects as go

from nucleo.config import AZUL, LARANJA
from nucleo.dados import Artefatos
from nucleo.graficos_base import (
    ALTURA,
    LEGENDA_ABAIXO,
    MARGEM,
    MARGEM_INFERIOR_AMPLA,
    eixo_de_anos,
    marcar_ano_incompleto,
    titulo_figura,
)


def fluxo_anual(artefatos: Artefatos) -> go.Figure:
    """Registros por ano, com a lacuna de 2017 visível e o ano em curso marcado.

    O eixo é fixado no intervalo completo de anos presentes, e não nos anos observados:
    é o que abre o espaço vazio de 2017. Uma malha só com o que existe ligaria 2016 a
    2018 e o leitor veria continuidade onde não houve.
    """
    fluxo = artefatos.fluxo
    anos = [int(ano) for ano in fluxo["ano"]]
    figura = go.Figure(
        go.Bar(x=fluxo["ano"], y=fluxo["registros_no_ano"], marker_color=AZUL)
    )
    for ano in sorted(artefatos.anos_incompletos()):
        marcar_ano_incompleto(figura, ano)
    figura.update_xaxes(
        **eixo_de_anos(range(min(anos), max(anos) + 1)),
        range=[min(anos) - 0.6, max(anos) + 0.6],
    )
    figura.update_yaxes(title_text="registros no ano")
    figura.update_layout(
        height=ALTURA,
        margin=MARGEM,
        bargap=0.25,
        showlegend=False,
        title=titulo_figura("Fluxo anual de registros — SISMIGRA"),
    )
    return figura


def composicao_do_amparo(artefatos: Artefatos) -> go.Figure:
    """A composição do fluxo por tipo de amparo, nos anos em que o campo existe.

    A tipologia de amparos só passou a ser publicada em 2021 — antes disso o campo não
    existe, e o gráfico fica vazio em vez de zero. O ano em curso entra com marcador vazado:
    a proporção de um ano parcial é observável, mas não é comparável à de um ano fechado.
    """
    fluxo = artefatos.fluxo.dropna(subset=["pct_acolhida"])
    incompletos = artefatos.anos_incompletos()
    fechados = fluxo.loc[~fluxo["ano"].isin(incompletos)]
    em_curso = fluxo.loc[fluxo["ano"].isin(incompletos)]
    figura = go.Figure()
    for rotulo, coluna, cor in (
        ("acolhida", "pct_acolhida", AZUL),
        ("trabalho", "pct_trabalho", LARANJA),
    ):
        figura.add_trace(
            go.Scatter(
                x=fechados["ano"],
                y=fechados[coluna],
                mode="lines+markers",
                name=rotulo,
                line={"color": cor, "width": 2},
                marker={"size": 8},
            )
        )
        figura.add_trace(
            go.Scatter(
                x=em_curso["ano"],
                y=em_curso[coluna],
                mode="markers",
                name=f"{rotulo} — ano em curso",
                marker={
                    "color": cor,
                    "size": 11,
                    "symbol": "circle-open",
                    "line": {"width": 2},
                },
            )
        )
    for ano in sorted(incompletos):
        marcar_ano_incompleto(figura, ano)
    figura.update_xaxes(**eixo_de_anos(fluxo["ano"], passo=1))
    figura.update_yaxes(title_text="participação no fluxo do ano", tickformat=".0%")
    figura.update_layout(
        height=ALTURA,
        margin=MARGEM_INFERIOR_AMPLA,
        title=titulo_figura("Composição do fluxo por tipo de amparo"),
        legend=LEGENDA_ABAIXO,
    )
    return figura
