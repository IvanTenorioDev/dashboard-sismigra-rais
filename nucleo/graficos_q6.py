"""Figuras da aba Q6 — o perfil dos vínculos formais de cada nacionalidade.

São três, e cada uma responde a uma pergunta sobre o conjunto dos seis atributos:

1. *O que é típico e o que é extremo em cada atributo?* — distribuição dos seis;
2. *Os atributos medem coisas distintas ou repetem a mesma informação?* — matriz de
   associação de postos;
3. *Como os dois atributos mais acoplados se organizam juntos?* — remuneração contra
   qualificação.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from nucleo.config import (
    ATRIBUTOS_PERCENTUAIS,
    AZUL,
    CINZA,
    COLUNAS_ATRIBUTOS,
    ROTULOS_ATRIBUTOS,
)
from nucleo.dados import DadosQ7
from nucleo.formatos import formatar_decimal, formatar_percentual
from nucleo.graficos_base import (
    ALTURA,
    ALTURA_ALTA,
    MARGEM,
    cor_da_regiao,
    faixa_log,
    nome_regiao,
    posicao_em_papel,
    regioes_presentes,
    titulo_figura,
)

LINHAS_DA_GRADE = 2
COLUNAS_DA_GRADE = 3

# Escala divergente nas cores do tema: azul para associação negativa, laranja para
# positiva. Os extremos são tintas claras de propósito — o valor é escrito em cada
# célula, e um fundo saturado tornaria o número ilegível.
ESCALA_DE_ASSOCIACAO = [[0.0, "#9FB6CE"], [0.5, "#FFFFFF"], [1.0, "#EFB27A"]]

# Dois atributos têm a massa concentrada num extremo e um ponto muito acima: sem escala
# logarítmica, a caixa fica espremida contra a borda e a distribuição não se lê.
ATRIBUTOS_EM_LOG = ("salario_medio_sm", "hhi_setorial")

# Os rótulos automáticos de um eixo logarítmico marcam 2, 3, 4… e se sobrepõem na altura
# desta grade. Ticks redondos resolvem — e são os mesmos no painel e no eixo de salário da
# figura de remuneração contra qualificação.
TICKS_EM_LOG: dict[str, tuple[float, ...]] = {
    "salario_medio_sm": (1, 2, 5, 10, 20),
    "hhi_setorial": (0.01, 0.05, 0.1, 0.5),
}


def _rotulos_de_tick(valores: tuple[float, ...]) -> list[str]:
    """Rótulos de tick com vírgula decimal, sem zeros à direita."""
    return [f"{valor:g}".replace(".", ",") for valor in valores]


def perfil_dos_atributos(artefatos: DadosQ7) -> go.Figure:
    """Distribuição de cada um dos seis atributos entre as nacionalidades elegíveis.

    Uma grade e não um gráfico único: os atributos têm unidades e escalas diferentes
    (salários mínimos, percentuais, índice de concentração) e não compartilham eixo.
    """
    figura = make_subplots(
        rows=LINHAS_DA_GRADE,
        cols=COLUNAS_DA_GRADE,
        subplot_titles=[ROTULOS_ATRIBUTOS[coluna] for coluna in COLUNAS_ATRIBUTOS],
        horizontal_spacing=0.06,
        vertical_spacing=0.20,
    )
    for posicao, coluna in enumerate(COLUNAS_ATRIBUTOS):
        linha, grade = divmod(posicao, COLUNAS_DA_GRADE)
        figura.add_trace(
            go.Box(
                x=artefatos.perfis[coluna],
                name=ROTULOS_ATRIBUTOS[coluna],
                boxpoints="all",
                jitter=0.55,
                pointpos=0,
                marker=dict(size=4, color=AZUL, opacity=0.40, line=dict(width=0)),
                line=dict(color=AZUL, width=1.4),
                fillcolor="rgba(31,58,95,0.08)",
                hovertemplate="%{x}<extra></extra>",
                showlegend=False,
            ),
            row=linha + 1,
            col=grade + 1,
        )
        if coluna in ATRIBUTOS_EM_LOG:
            ticks = TICKS_EM_LOG[coluna]
            figura.update_xaxes(
                type="log",
                tickvals=list(ticks),
                ticktext=_rotulos_de_tick(ticks),
                row=linha + 1,
                col=grade + 1,
            )
        if coluna in ATRIBUTOS_PERCENTUAIS:
            figura.update_xaxes(tickformat=".0%", row=linha + 1, col=grade + 1)
    figura.update_layout(
        template="plotly_white",
        height=ALTURA_ALTA,
        margin=MARGEM,
        boxgap=0.35,
    )
    figura.update_yaxes(showticklabels=False, showgrid=False)
    return figura


def associacao_entre_atributos(artefatos: DadosQ7) -> go.Figure:
    """Associação de postos entre os seis atributos, no triângulo inferior.

    O triângulo superior fica vazio porque a matriz é simétrica: repetir os mesmos
    coeficientes espelhados sugere duas leituras onde só existe uma.
    """
    matriz = artefatos.associacao_de_atributos()
    rotulos = [ROTULOS_ATRIBUTOS[coluna] for coluna in COLUNAS_ATRIBUTOS]
    valores = matriz.to_numpy(dtype=float)
    espelhado = np.triu(np.ones_like(valores, dtype=bool), k=0)
    exibidos = np.where(espelhado, np.nan, valores)
    escritos = [
        [
            "" if espelhado[linha, coluna] else formatar_decimal(valores[linha, coluna], 2)
            for coluna in range(len(rotulos))
        ]
        for linha in range(len(rotulos))
    ]
    figura = go.Figure(go.Heatmap(
        z=exibidos,
        x=rotulos,
        y=rotulos,
        text=escritos,
        texttemplate="%{text}",
        textfont=dict(size=11, color=AZUL),
        zmin=-1,
        zmax=1,
        colorscale=ESCALA_DE_ASSOCIACAO,
        xgap=4,
        ygap=4,
        hovertemplate="%{y} × %{x}<br>associação de postos = %{z:.2f}<extra></extra>",
    ))
    figura.update_layout(
        template="plotly_white",
        height=ALTURA_ALTA,
        margin=MARGEM,
        title=titulo_figura("Associação de postos entre os atributos de perfil"),
    )
    figura.update_yaxes(autorange="reversed")
    return figura


def _rotulo_do_maior_salario(perfis: pd.DataFrame) -> go.Scatter:
    """Identifica o ponto fora de escala, como traço e não como anotação.

    Anotação com referência de dados não renderiza de forma confiável quando o eixo é
    logarítmico — o mesmo problema já corrigido na Q4.
    """
    maior = perfis.nlargest(1, "salario_medio_sm")
    return go.Scatter(
        x=maior["pct_superior"],
        y=maior["salario_medio_sm"],
        mode="markers+text",
        name="maior remuneração",
        text=[
            f"{nome} · {formatar_decimal(salario, 1)} SM"
            for nome, salario in zip(maior["nacionalidade"], maior["salario_medio_sm"])
        ],
        textposition="top center",
        textfont=dict(size=11, color=CINZA),
        marker=dict(size=12, color=CINZA, symbol="circle-open", line=dict(width=1.8)),
        hovertemplate="<b>%{text}</b><extra></extra>",
    )


def remuneracao_versus_qualificacao(artefatos: DadosQ7) -> go.Figure:
    """Remuneração contra qualificação — os dois atributos mais acoplados.

    As medianas dos dois atributos cruzam o plano em quatro quadrantes, e é nos
    quadrantes opostos que as regiões se separam.
    """
    perfis = artefatos.perfis
    mediana_salario = float(perfis["salario_medio_sm"].median())
    mediana_superior = float(perfis["pct_superior"].median())
    faixa_salario = faixa_log(perfis["salario_medio_sm"], 1.6)
    figura = go.Figure()
    for regiao in regioes_presentes(perfis):
        recorte = perfis[perfis["regiao"].eq(regiao)]
        figura.add_trace(go.Scatter(
            x=recorte["pct_superior"],
            y=recorte["salario_medio_sm"],
            mode="markers",
            name=nome_regiao(regiao),
            marker=dict(size=10, color=cor_da_regiao(regiao), opacity=0.78),
            customdata=np.column_stack([recorte["nacionalidade"], recorte["Q_medio"]]),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>superior completo = %{x:.1%}"
                "<br>salário médio = %{y:.2f} SM<br>Q = %{customdata[1]:.2f}<extra></extra>"
            ),
        ))
    figura.add_trace(_rotulo_do_maior_salario(perfis))
    figura.add_hline(
        y=mediana_salario,
        line_dash="dash",
        line_color=CINZA,
        line_width=1,
    )
    figura.add_annotation(
        x=0.005,
        y=posicao_em_papel(mediana_salario, faixa_salario),
        xref="paper",
        yref="paper",
        xanchor="left",
        yanchor="bottom",
        showarrow=False,
        text=f"mediana do salário · {formatar_decimal(mediana_salario, 2)} SM",
        font=dict(size=11, color=CINZA),
    )
    figura.add_vline(
        x=mediana_superior,
        line_dash="dash",
        line_color=CINZA,
        line_width=1,
        annotation_text=f"mediana da escolaridade · {formatar_percentual(mediana_superior)}",
        annotation_position="bottom right",
        annotation_font_size=11,
    )
    figura.update_layout(
        template="plotly_white",
        height=ALTURA,
        margin=MARGEM,
        title=titulo_figura("Remuneração contra qualificação — os dois atributos mais acoplados"),
        legend=dict(orientation="h", y=-0.2, title_text=""),
    )
    figura.update_xaxes(
        title_text="vínculos com ensino superior completo",
        tickformat=".0%",
    )
    figura.update_yaxes(
        type="log",
        title_text="salário médio (salários mínimos)",
        tickvals=list(TICKS_EM_LOG["salario_medio_sm"]),
        ticktext=_rotulos_de_tick(TICKS_EM_LOG["salario_medio_sm"]),
        range=faixa_salario,
    )
    return figura
