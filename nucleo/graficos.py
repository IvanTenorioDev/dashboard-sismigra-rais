"""Figuras da aba Q7 — análise multivariada da inserção laboral.

As figuras nascem aqui e as páginas apenas escolhem qual exibir. O que é comum a todas
as abas — paleta das regiões, título, altura — vem de `nucleo/graficos_base.py`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from nucleo.config import AZUL, CINZA, COLUNAS_ATRIBUTOS, LARANJA, ROTULOS_ATRIBUTOS
from nucleo.dados import DadosQ7
from nucleo.formatos import formatar_atributo, formatar_decimal, formatar_percentual
from nucleo.graficos_base import (
    ALTURA,
    ALTURA_ALTA,
    MARGEM,
    cor_da_regiao,
    nome_regiao,
    regioes_presentes,
    titulo_figura,
)


def dispersao_pca(artefatos: DadosQ7) -> go.Figure:
    """Dispersão das nacionalidades nos dois primeiros componentes principais."""
    # V_total já vem no arquivo de coordenadas; pedir de novo do perfil colidiria na junção.
    complementares = ("Q_medio", "salario_medio_sm", "pct_superior")
    pontos = artefatos.pca.join(
        artefatos.perfis.set_index("nacionalidade")[list(complementares)], on="nacionalidade"
    )
    campos = ("nacionalidade", *complementares, "V_total")
    figura = go.Figure()
    for regiao in regioes_presentes(pontos):
        recorte = pontos[pontos["regiao"].eq(regiao)]
        figura.add_trace(go.Scatter(
            x=recorte["PC1"], y=recorte["PC2"], mode="markers", name=nome_regiao(regiao),
            marker=dict(size=9, color=cor_da_regiao(regiao), line=dict(width=0.6, color="white")),
            customdata=np.column_stack([recorte[campo].to_numpy() for campo in campos]),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>Q = %{customdata[1]:.2f}"
                "<br>Salário = %{customdata[2]:.2f} SM<br>Superior = %{customdata[3]:.1%}"
                "<br>Vínculos na janela = %{customdata[4]:,.0f}<extra></extra>"
            ),
        ))
    variancia = artefatos.variancia.set_index("componente")["variancia_explicada"]
    figura.update_layout(
        template="plotly_white", height=ALTURA, margin=MARGEM, hoverlabel=dict(font=dict(size=12)),
        title=titulo_figura("Projeção das nacionalidades em PC1 × PC2, por região"),
        legend=dict(orientation="h", y=-0.18, title_text=""),
    )
    figura.update_xaxes(title_text=f"PC1 ({formatar_percentual(variancia.get('PC1', float('nan')))} da variância)")
    figura.update_yaxes(title_text=f"PC2 ({formatar_percentual(variancia.get('PC2', float('nan')))} da variância)")
    return figura


def cargas_pca(artefatos: DadosQ7) -> go.Figure:
    """Peso de cada atributo em PC1 e PC2 — a direção do gradiente."""
    cargas = artefatos.cargas.copy()
    cargas["rotulo"] = cargas["atributo"].map(ROTULOS_ATRIBUTOS).fillna(cargas["atributo"])
    figura = go.Figure()
    for componente, cor in (("PC1", AZUL), ("PC2", LARANJA)):
        figura.add_trace(go.Bar(
            y=cargas["rotulo"], x=cargas[componente], orientation="h", name=componente,
            marker_color=cor,
            hovertemplate=f"%{{y}}<br>{componente} = %{{x:.3f}}<extra></extra>",
        ))
    figura.update_layout(
        template="plotly_white", height=ALTURA, margin=MARGEM, barmode="group",
        title=titulo_figura("Cargas dos atributos nos componentes principais"),
        legend=dict(orientation="h", y=-0.18, title_text=""),
    )
    figura.update_xaxes(title_text="carga (correlação atributo–componente)")
    return figura


def mapa_regioes(artefatos: DadosQ7) -> go.Figure:
    """Mapa de calor do perfil mediano das regiões, em desvios-padrão dentro da coluna."""
    regioes = artefatos.regioes.sort_values("regiao").reset_index(drop=True)
    colunas = list(COLUNAS_ATRIBUTOS)
    valores = regioes[colunas].to_numpy(dtype=float)
    desvios = np.where(valores.std(axis=0) == 0, 1.0, valores.std(axis=0))
    textos = [
        [formatar_atributo(coluna, regioes.loc[linha, coluna]) for coluna in colunas]
        for linha in range(len(regioes))
    ]
    figura = go.Figure(go.Heatmap(
        z=(valores - valores.mean(axis=0)) / desvios,
        x=[ROTULOS_ATRIBUTOS[coluna] for coluna in colunas],
        y=[f"{nome_regiao(regiao)} · {int(n)} nac." for regiao, n in zip(regioes["regiao"], regioes["n_nacionalidades"])],
        text=textos, texttemplate="%{text}", textfont=dict(size=12, color="#1A1A1A"),
        colorscale="RdBu_r", zmid=0, colorbar=dict(title="posição relativa<br>(desvios-padrão)"),
        hovertemplate="%{y}<br>%{x}: %{text}<extra></extra>",
    ))
    figura.update_layout(
        template="plotly_white", height=ALTURA, margin=MARGEM,
        title=titulo_figura("Medianas por região, com valores observados nas células"),
    )
    figura.update_yaxes(autorange="reversed")
    return figura


def faixas_de_q(artefatos: DadosQ7) -> go.Figure:
    """Distribuição do índice Q dentro de cada região."""
    figura = go.Figure()
    for regiao in regioes_presentes(artefatos.perfis):
        recorte = artefatos.perfis[artefatos.perfis["regiao"].eq(regiao)]
        figura.add_trace(go.Box(
            y=recorte["Q_medio"], name=nome_regiao(regiao), marker_color=cor_da_regiao(regiao),
            boxpoints="all", jitter=0.4, pointpos=0, marker=dict(size=5, opacity=0.6),
            hovertemplate="<b>%{text}</b><br>Q = %{y:.2f}<extra></extra>",
            text=recorte["nacionalidade"],
        ))
    figura.add_hline(y=1.0, line_dash="dash", line_color=LARANJA, annotation_text="Q = 1 (paridade)", annotation_position="top left")
    figura.update_layout(
        template="plotly_white", height=ALTURA, margin=MARGEM, showlegend=False,
        title=titulo_figura("Distribuição do índice Q por região"),
    )
    figura.update_yaxes(title_text="índice Q na janela (mediana por nacionalidade)")
    return figura


PAINEIS_DIAGNOSTICO: tuple[tuple[int, int, str, str, str | None], ...] = (
    (1, 1, "inercia", AZUL, None),
    (1, 2, "silhueta", AZUL, None),
    (2, 1, "ari_kmeans_ward", AZUL, None),
    (2, 2, "ari_estabilidade", LARANJA, "ari_desvio"),
)


def _barras_de_erro(diagnostico: pd.DataFrame, coluna: str | None) -> dict[str, object] | None:
    """Barras de erro só nos painéis que têm uma medida de dispersão."""
    if coluna is None:
        return None
    return {"type": "data", "array": diagnostico[coluna], "color": CINZA}


def diagnostico_k(artefatos: DadosQ7) -> go.Figure:
    """Os quatro critérios usados para escolher k, com o k escolhido destacado."""
    diagnostico = artefatos.diagnostico.sort_values("k")
    figura = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Inércia intra-cluster", "Coeficiente de silhueta", "Concordância KMeans × Ward (ARI)", "ARI sob reamostragem"),
    )
    for linha, coluna, campo, cor, desvio in PAINEIS_DIAGNOSTICO:
        figura.add_trace(
            go.Scatter(
                x=diagnostico["k"], y=diagnostico[campo], mode="lines+markers", name=campo,
                line=dict(color=cor), marker=dict(size=8),
                error_y=_barras_de_erro(diagnostico, desvio),
                hovertemplate="k = %{x}<br>%{y:.3f}<extra></extra>", showlegend=False,
            ),
            row=linha, col=coluna,
        )
        figura.add_vline(x=artefatos.k_escolhido, line_dash="dash", line_color=LARANJA, row=linha, col=coluna)
    figura.update_layout(
        template="plotly_white", height=ALTURA_ALTA, margin=MARGEM, hovermode="x unified",
        title=titulo_figura("Critérios de escolha de k — linha tracejada no k escolhido"),
    )
    figura.update_xaxes(dtick=1, title_text="k")
    return figura


def estabilidade_por_k(artefatos: DadosQ7) -> go.Figure:
    """Dispersão dos ARI individuais de cada reamostragem, por k."""
    figura = go.Figure()
    for k in sorted(int(valor) for valor in artefatos.diagnostico["k"]):
        valores = artefatos.valores_de_estabilidade(k)
        if not valores:
            continue
        figura.add_trace(go.Box(
            y=valores, name=f"k={k}", boxpoints="all", jitter=0.5, pointpos=0,
            marker=dict(size=4, opacity=0.5, color=LARANJA),
            line=dict(color=AZUL),
            hovertemplate=f"k={k}<br>ARI = %{{y:.3f}}<extra></extra>",
            fillcolor="rgba(31,58,95,0.08)",
        ))
    figura.update_layout(
        template="plotly_white", height=ALTURA, margin=MARGEM, showlegend=False,
        title=titulo_figura("ARI sob reamostragem, por k (80% dos casos, 30 repetições)"),
    )
    figura.update_yaxes(title_text="ARI contra a partição de referência")
    return figura


def arvores_comparacao(artefatos: DadosQ7) -> go.Figure:
    """Acurácia em validação cruzada contra o baseline ingênuo de cada árvore."""
    arvores = artefatos.arvores.copy()
    arvores["rotulo"] = arvores["descricao_alvo"]
    figura = go.Figure()
    figura.add_trace(go.Bar(
        name="Acurácia em validação cruzada", x=arvores["rotulo"], y=arvores["acuracia_cv"],
        marker_color=AZUL, error_y=dict(type="data", array=arvores["desvio_cv"], color=CINZA),
        hovertemplate="%{x}<br>acurácia = %{y:.3f}<extra></extra>",
    ))
    figura.add_trace(go.Bar(
        name="Baseline (classe majoritária)", x=arvores["rotulo"], y=arvores["baseline"],
        marker_color=CINZA,
        hovertemplate="%{x}<br>baseline = %{y:.3f}<extra></extra>",
    ))
    figura.update_layout(
        template="plotly_white", height=ALTURA, margin=MARGEM, barmode="group", bargap=0.35,
        title=titulo_figura("Acurácia em validação cruzada contra o classificador majoritário"),
        legend=dict(orientation="h", y=-0.25, title_text=""),
    )
    figura.update_yaxes(title_text="acurácia", range=[0, 1.05])
    return figura


def composicao_regioes(artefatos: DadosQ7) -> go.Figure:
    """Quantas nacionalidades e quantos vínculos cada região concentra."""
    regioes = artefatos.regioes.sort_values("regiao")
    figura = make_subplots(specs=[[{"secondary_y": True}]])
    figura.add_trace(
        go.Bar(
            x=[nome_regiao(valor) for valor in regioes["regiao"]],
            y=regioes["n_nacionalidades"], name="Nacionalidades",
            marker_color=[cor_da_regiao(valor) for valor in regioes["regiao"]],
            text=[f"{int(valor)}" for valor in regioes["n_nacionalidades"]], textposition="outside",
            hovertemplate="%{x}<br>%{y} nacionalidades<extra></extra>",
        ),
        secondary_y=False,
    )
    figura.add_trace(
        go.Scatter(
            x=[nome_regiao(valor) for valor in regioes["regiao"]],
            y=regioes["participacao_vinculos"], name="Participação nos vínculos", mode="lines+markers+text",
            line=dict(color=LARANJA, width=3), marker=dict(size=11),
            text=[formatar_percentual(valor) for valor in regioes["participacao_vinculos"]],
            textposition="top center",
            hovertemplate="%{x}<br>%{y:.1%} dos vínculos<extra></extra>",
        ),
        secondary_y=True,
    )
    figura.update_layout(
        template="plotly_white", height=ALTURA, margin=MARGEM,
        title=titulo_figura("Nacionalidades e volume de vínculos por região"),
        legend=dict(orientation="h", y=-0.2, title_text=""),
    )
    figura.update_yaxes(title_text="nacionalidades elegíveis", secondary_y=False)
    figura.update_yaxes(title_text="participação nos vínculos", tickformat=".0%", secondary_y=True)
    return figura


def perfil_da_linha(artefatos: DadosQ7, nacionalidade: str) -> pd.DataFrame:
    """Tabela de leitura de uma nacionalidade, para o bloco de consulta."""
    linha = artefatos.perfis.loc[artefatos.perfis["nacionalidade"].eq(nacionalidade)]
    if linha.empty:
        return pd.DataFrame(columns=("Atributo", "Valor"))
    registro = linha.iloc[0]
    return pd.DataFrame({
        "Atributo": [ROTULOS_ATRIBUTOS[coluna] for coluna in COLUNAS_ATRIBUTOS],
        "Valor": [formatar_atributo(coluna, registro[coluna]) for coluna in COLUNAS_ATRIBUTOS],
    })


def texto_da_regra(artefatos: DadosQ7, arvore: str) -> str:
    """A regra em texto de uma árvore, pronta para exibição monoespaçada."""
    linha = artefatos.arvores.loc[artefatos.arvores["arvore"].eq(arvore)]
    return "" if linha.empty else str(linha.iloc[0]["regra"])


def resumo_numerico(artefatos: DadosQ7) -> dict[str, str]:
    """Indicadores do painel de resposta, já formatados."""
    linha = artefatos.regiao_do_k()
    return {
        "Regiões": f"{artefatos.k_escolhido}",
        "Silhueta no k escolhido": formatar_decimal(linha["silhueta"]),
        "KMeans × Ward": formatar_decimal(artefatos.configuracao.get("ari_kmeans_ward", float("nan"))),
        "Estabilidade (média)": formatar_decimal(linha["ari_estabilidade"]),
        "Estabilidade (mínimo)": formatar_decimal(linha["ari_minimo"]),
    }
