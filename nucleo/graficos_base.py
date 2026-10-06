"""Elementos compartilhados pelas figuras, qualquer que seja a aba.

As abas crescem por pergunta — Q4, Q7, e as demais — e cada uma tem o seu módulo de
figuras. O que é comum (paleta das regiões, título, altura, eixo logarítmico do índice Q)
vive aqui, para não haver duas definições do mesmo elemento.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from nucleo.config import AZUL, CINZA, CORES_REGIAO, LARANJA

ALTURA = 460
ALTURA_ALTA = 640
MARGEM = {"l": 70, "r": 30, "t": 60, "b": 60}

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
