"""Figuras da aba Q2 — onde a presença se concentra e quão concentrada ela é.

As duas fontes têm conceitos de UF diferentes: o SISMIGRA registra a **residência** da
pessoa, a RAIS registra o **estabelecimento** onde o vínculo existe. Esta aba nunca soma
os dois lados — apresenta-os lado a lado, e é a divergência entre eles que responde à
pergunta.
"""

from __future__ import annotations

import plotly.graph_objects as go

from nucleo.config import AZUL, LARANJA, PISO_REGISTROS
from nucleo.dados import Artefatos
from nucleo.graficos_base import (
    ALTURA,
    ALTURA_ALTA,
    LEGENDA_ABAIXO,
    MARGEM,
    MARGEM_INFERIOR_AMPLA,
    titulo_figura,
)


def concentracao_por_uf(artefatos: Artefatos) -> go.Figure:
    """Participação de cada UF nos dois lados, no último ano com ambos observados.

    As barras são participações, não contagens: o total de registros é cerca de cinco
    vezes o de vínculos, e comparar níveis diria apenas isso. A pergunta é se a mesma UF
    pesa o mesmo nos dois lados — e a resposta está na distância entre os dois pares.
    """
    ano = artefatos.ano_com_os_dois_lados()
    tabela = artefatos.uf_ano.loc[artefatos.uf_ano["ano"].eq(ano)]
    ordenado = tabela.assign(
        pct_registros=tabela["registros_ativos"] / tabela["registros_ativos"].sum(),
        pct_vinculos=tabela["vinculos_formais"] / tabela["vinculos_formais"].sum(),
    ).sort_values("pct_registros")
    figura = go.Figure()
    figura.add_trace(
        go.Bar(
            y=ordenado["uf"],
            x=ordenado["pct_registros"],
            orientation="h",
            name="registros ativos (residência)",
            marker_color=LARANJA,
        )
    )
    figura.add_trace(
        go.Bar(
            y=ordenado["uf"],
            x=ordenado["pct_vinculos"],
            orientation="h",
            name="vínculos formais (estabelecimento)",
            marker_color=AZUL,
        )
    )
    figura.update_xaxes(title_text="participação no total do país", tickformat=".0%")
    figura.update_layout(
        height=ALTURA_ALTA + 80,
        margin=MARGEM_INFERIOR_AMPLA,
        barmode="group",
        bargap=0.25,
        title=titulo_figura(f"Participação de cada UF nos dois lados — {ano}"),
        legend=LEGENDA_ABAIXO,
    )
    return figura


def registros_por_vinculo(artefatos: Artefatos) -> go.Figure:
    """Quantos registros ativos cada vínculo formal sustenta, UF por UF.

    A razão entre os totais do país é uma só; esta figura mostra que ela não vale para
    lugar nenhum em particular. Nas UFs de fronteira e de rota recente há muitos registros
    para poucos vínculos; nas de colonização antiga, o inverso.
    """
    ano = artefatos.ano_com_os_dois_lados()
    tabela = artefatos.uf_ano.loc[artefatos.uf_ano["ano"].eq(ano)].copy()
    tabela["razao"] = tabela["registros_ativos"] / tabela["vinculos_formais"]
    ordenado = tabela.sort_values("razao")
    figura = go.Figure(
        go.Bar(
            y=ordenado["uf"],
            x=ordenado["razao"],
            orientation="h",
            marker_color=LARANJA,
            text=[f"{valor:.1f}".replace(".", ",") for valor in ordenado["razao"]],
            textposition="outside",
        )
    )
    figura.update_xaxes(
        title_text=f"registros ativos por vínculo formal — {ano}",
        range=[0, float(ordenado["razao"].max()) * 1.15],
    )
    figura.update_layout(
        height=ALTURA_ALTA,
        margin=MARGEM,
        title=titulo_figura("Registros por vínculo, em cada UF"),
        showlegend=False,
    )
    return figura


def hhi_por_nacionalidade(artefatos: Artefatos) -> go.Figure:
    """Distribuição do HHI territorial entre as nacionalidades que sustentam o índice.

    O piso de {piso} registros não é decoração: sem ele, toda nacionalidade com um único
    registro tem HHI igual a 1 — está numa UF só porque tem uma observação só. Esses casos
    encheriam a cauda direita e a leitura sairia "as nacionalidades são extremamente
    concentradas", que é uma afirmação sobre o tamanho da amostra, não sobre o território.
    """
    ano = artefatos.ano_com_os_dois_lados()
    base = artefatos.concentracao_com_volume()
    sustentadas = base.loc[
        base["ano"].eq(ano) & base["registros_ativos"].ge(PISO_REGISTROS)
    ].dropna(subset=["hhi_uf_registros"])
    mediana = float(sustentadas["hhi_uf_registros"].median())
    figura = go.Figure(
        go.Histogram(
            x=sustentadas["hhi_uf_registros"],
            nbinsx=24,
            marker_color=AZUL,
        )
    )
    figura.add_vline(
        x=mediana,
        line_dash="dash",
        line_color=LARANJA,
        line_width=2,
        annotation_text=f"mediana {mediana:.2f}".replace(".", ","),
        annotation_position="top right",
        annotation_font_size=11,
    )
    figura.update_xaxes(title_text="HHI territorial dos registros ativos (1 = uma UF só)")
    figura.update_yaxes(title_text="nacionalidades")
    figura.update_layout(
        height=ALTURA,
        margin=MARGEM,
        title=titulo_figura(f"Concentração territorial por nacionalidade — {ano}"),
        showlegend=False,
        bargap=0.05,
    )
    return figura
