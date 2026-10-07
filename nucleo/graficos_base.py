"""Elementos compartilhados pelas figuras, qualquer que seja a aba.

As abas crescem por pergunta — Q4, Q7, e as demais — e cada uma tem o seu módulo de
figuras. O que é comum (paleta das regiões, título, altura, eixo logarítmico do índice Q)
vive aqui, para não haver duas definições do mesmo elemento.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from nucleo.config import AZUL, CINZA, CORES_REGIAO, LARANJA

# O estilo de todos os gráficos, declarado uma vez. Sem isto cada figura herda o template
# padrão do Plotly, que traz fundo cinza-azulado — e a herança depende da ordem em que os
# módulos são importados, então o mesmo código gerava painéis diferentes. A figura do
# projeto é fundo branco, e é o que o desenho aprovado pede.
pio.templates.default = "plotly_white"

ALTURA = 460
ALTURA_ALTA = 640
MARGEM = {"l": 70, "r": 30, "t": 60, "b": 60}

# Legenda horizontal fica fora da área de desenho, abaixo dela. Com a margem padrão ela sai
# cortada na borda inferior, e ainda por cima por cima dos rótulos do eixo. Quem põe
# legenda embaixo usa estes dois valores juntos, para não haver duas medidas diferentes.
MARGEM_INFERIOR_AMPLA = {**MARGEM, "b": 120}
LEGENDA_ABAIXO = {"orientation": "h", "y": -0.16, "yanchor": "top"}

# Valores de referência do índice Q, para o eixo em escala logarítmica. Marcar o eixo
# com valores redondos legíveis é o que permite ler "10× mais" sem calcular log de cabeça.
VALORES_LOG_Q = (0.1, 0.25, 0.5, 1, 2, 5, 10, 50, 100, 500)


def titulo_figura(texto: str) -> dict[str, object]:
    """Título de figura no padrão do desenho aprovado."""
    return {"text": texto, "x": 0.01, "xanchor": "left", "font": {"size": 16, "color": AZUL}}


def nome_regiao(regiao: int) -> str:
    """Rótulo humano de uma região."""
    return f"Região {int(regiao)}"


def regioes_presentes(tabela: pd.DataFrame) -> list[int]:
    """Regiões existentes numa tabela, em ordem crescente."""
    return sorted(int(valor) for valor in tabela["regiao"].unique())


def cor_da_regiao(regiao: int) -> str:
    """Cor de uma região, com cinza para valores inesperados."""
    return CORES_REGIAO.get(int(regiao), CINZA)


def em_log10(valores: object) -> np.ndarray:
    """Log na base 10, protegido contra zero e negativo."""
    return np.log10(np.clip(np.asarray(valores, dtype=float), 1e-9, None))


def eixo_log_q() -> dict[str, object]:
    """Posições e rótulos do eixo do índice Q em escala logarítmica.

    `automargin` deixa o Plotly abrir a margem que o título do eixo precisa. Sem ele,
    o rótulo rotacionado é cortado na borda — o rótulo é longo e a margem é fixa.
    """
    posicoes = [float(np.log10(valor)) for valor in VALORES_LOG_Q]
    rotulos = [f"{valor:g}".replace(".", ",") for valor in VALORES_LOG_Q]
    return {"tickvals": posicoes, "ticktext": rotulos, "automargin": True}


def faixa_log(valores: object, folga: float = 1.6) -> list[float]:
    """Intervalo de um eixo logarítmico, em unidades de log10.

    Fixar o intervalo deixa o enquadramento determinístico: a mesma figura sai igual em
    qualquer execução, em vez de depender do alcance que o `autorange` escolher.
    """
    positivos = np.asarray(valores, dtype=float)
    positivos = positivos[positivos > 0]
    if positivos.size == 0:
        return []
    return [
        float(np.log10(positivos.min() / folga)),
        float(np.log10(positivos.max() * folga)),
    ]


def posicao_em_papel(valor: float, faixa: list[float]) -> float:
    """Fração do eixo logarítmico ocupada por um valor, para ancorar anotação.

    A anotação que acompanha `add_hline` não respeita um eixo logarítmico: ela fica presa
    ao topo da área de desenho, longe da linha que deveria rotular. Ancorar em
    coordenadas de papel, com a fração calculada aqui, põe o rótulo onde ele precisa
    estar — e não depende do `autorange`.
    """
    inicio, fim = faixa
    return (float(np.log10(valor)) - inicio) / (fim - inicio)


def marcar_paridade(figura: object, vertical: bool, proximo_de: float = 0.0) -> None:
    """Marca onde as duas distribuições coincidem (Q = 1).

    É a linha de referência mais importante da Q4: sem ela, um Q de 0,3 e um de 3
    pareceriam apenas dois números diferentes, e não lados opostos da paridade.
    """
    eixo = "x" if vertical else "y"
    atributo = "add_vline" if vertical else "add_hline"
    getattr(figura, atributo)(
        **{eixo: proximo_de},
        line_dash="dash",
        line_color=LARANJA,
        line_width=1.5,
        annotation_text="Q = 1 (paridade)",
        annotation_position="top right",
        annotation_font_size=11,
    )


def eixo_de_anos(anos: Iterable[int], passo: int = 2) -> dict[str, object]:
    """Posições e rótulos de um eixo de anos, sem casas decimais.

    O eixo numérico do Plotly rotula 2015,000 quando a malha não cai em inteiros. Fixar
    as posições evita isso e mantém a mesma malha em todas as figuras anuais.
    """
    presentes = sorted({int(ano) for ano in anos})
    if not presentes:
        return {}
    marcados = presentes[::passo]
    if marcados[-1] != presentes[-1]:
        marcados.append(presentes[-1])
    return {"tickvals": marcados, "ticktext": [str(ano) for ano in marcados]}


def marcar_ano_incompleto(figura: go.Figure, ano: int) -> None:
    """Sombreia o ano que a extração pegou em curso.

    Sem a marca, o último ponto de uma série anual parece queda de atividade quando é
    só um ano com menos meses — a leitura mais errada possível de um gráfico de fluxo.
    """
    figura.add_vrect(
        x0=ano - 0.5,
        x1=ano + 0.5,
        fillcolor=LARANJA,
        opacity=0.12,
        line_width=0,
        annotation_text="ano em curso",
        annotation_position="top left",
        annotation_font_size=11,
    )
