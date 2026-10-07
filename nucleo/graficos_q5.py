"""Figuras da aba Q5 — a persistência dos registros ao longo dos anos.

A pergunta "os registros se sustentam ou são pontuais?" tem uma armadilha: uma
nacionalidade com um único registro aparece com um único ano de presença, e isso não é um
caso de presença interrompida — é um caso sem massa para se observar. As duas figuras
separam os dois, marcando o piso de {piso} registros ativos.
"""

from __future__ import annotations

import plotly.graph_objects as go

from nucleo.config import AZUL, CINZA, LARANJA, PISO_REGISTROS
from nucleo.dados import Artefatos
from nucleo.graficos_base import (
    ALTURA,
    LEGENDA_ABAIXO,
    MARGEM_INFERIOR_AMPLA,
    titulo_figura,
)

ROTULO_ACIMA = f"com {PISO_REGISTROS} registros ou mais"
ROTULO_ABAIXO = f"abaixo de {PISO_REGISTROS} registros"


def distribuicao_da_persistencia(artefatos: Artefatos) -> go.Figure:
    """Quantos anos de presença cada nacionalidade tem, com e sem o piso.

    A camada cinza é o conjunto inteiro; a azul, o que passa do piso. A diferença entre as
    duas é o que o piso retira, e ela se concentra na cauda esquerda: se não houvesse
    marca, a distribuição sugeriria presença curta generalizada quando o que há ali são
    observações sem massa.
    """
    persistencia = artefatos.persistencia
    sustentadas = persistencia["registros_ativos_no_ultimo_ano"].ge(PISO_REGISTROS)
    figura = go.Figure()
    figura.add_trace(
        go.Histogram(
            x=persistencia["anos_com_vinculos"],
            name="todas as nacionalidades",
            marker_color=CINZA,
            opacity=0.55,
            xbins={"size": 1},
        )
    )
    figura.add_trace(
        go.Histogram(
            x=persistencia.loc[sustentadas, "anos_com_vinculos"],
            name=ROTULO_ACIMA,
            marker_color=AZUL,
            xbins={"size": 1},
        )
    )
    figura.update_xaxes(
        title_text="anos distintos com vínculo formal",
        tickmode="linear",
        dtick=1,
        range=[0.5, 16.5],
    )
    figura.update_yaxes(title_text="nacionalidades")
    figura.update_layout(
        height=ALTURA,
        margin=MARGEM_INFERIOR_AMPLA,
        barmode="overlay",
        bargap=0.1,
        title=titulo_figura("Anos de presença por nacionalidade"),
        legend=LEGENDA_ABAIXO,
    )
    return figura


def intervalo_versus_presenca(artefatos: Artefatos) -> go.Figure:
    """Anos de presença contra o intervalo aberto entre a primeira e a última aparição.

    A diagonal marca a presença contínua: quem está sobre ela aparece em todos os anos
    desde a estreia. Pontos abaixo têm buracos no meio — apareceu, sumiu e voltou. É esta
    figura que distingue "presença curta" de "presença interrompida", que a contagem de
    anos sozinha confunde.
    """
    persistencia = artefatos.persistencia.assign(
        intervalo=(
            artefatos.persistencia["ultimo_ano_vinculos"]
            - artefatos.persistencia["primeiro_ano_vinculos"]
            + 1
        )
    )
    sustentadas = persistencia["registros_ativos_no_ultimo_ano"].ge(PISO_REGISTROS)
    figura = go.Figure()
    figura.add_trace(
        go.Scatter(
            x=persistencia.loc[sustentadas, "intervalo"],
            y=persistencia.loc[sustentadas, "anos_com_vinculos"],
            mode="markers",
            name=ROTULO_ACIMA,
            marker={"color": AZUL, "size": 9, "opacity": 0.75},
        )
    )
    figura.add_trace(
        go.Scatter(
            x=persistencia.loc[~sustentadas, "intervalo"],
            y=persistencia.loc[~sustentadas, "anos_com_vinculos"],
            mode="markers",
            name=ROTULO_ABAIXO,
            marker={"color": LARANJA, "size": 11, "symbol": "diamond-open"},
        )
    )
    limite = float(persistencia["intervalo"].max())
    figura.add_trace(
        go.Scatter(
            x=[0, limite],
            y=[0, limite],
            mode="lines",
            name="presença contínua",
            line={"color": CINZA, "width": 1.5, "dash": "dash"},
        )
    )
    figura.update_xaxes(title_text="anos entre a primeira e a última aparição")
    figura.update_yaxes(title_text="anos com vínculo observado")
    figura.update_layout(
        height=ALTURA,
        margin=MARGEM_INFERIOR_AMPLA,
        title=titulo_figura("Presença contínua ou interrompida"),
        legend=LEGENDA_ABAIXO,
    )
    return figura
