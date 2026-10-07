"""Aba Q7 — Análise multivariada.

Segue o contrato do slide 11: três cartões no topo, a evidência principal à esquerda,
o painel de resposta e limites à direita — **fixo**, para que trocar de evidência não
troque a conclusão — e o rodapé de pisos.

A única liberdade que esta aba toma em relação ao desenho original é o seletor de
evidência: a Q7 tem várias provas e um único espaço para exibi-las.
"""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from nucleo import graficos, layout, textos
from nucleo.config import COLUNAS_ATRIBUTOS, ROTULOS_ATRIBUTOS
from nucleo.dados import Artefatos
from nucleo.formatos import formatar_atributo, formatar_decimal, formatar_inteiro

OPCOES_TOPO = ("10", "25", "50", "todas")
ALTURA_TABELA = 430
COLUNA_Q_FORMATADO = "Q (janela)"

FIGURAS: dict[str, Callable[[Artefatos], object]] = {
    "gradiente": graficos.dispersao_pca,
    "cargas": graficos.cargas_pca,
    "regioes": graficos.mapa_regioes,
    "composicao": graficos.composicao_regioes,
    "regra_k": graficos.diagnostico_k,
    "estabilidade": graficos.estabilidade_por_k,
    "arvores": graficos.arvores_comparacao,
}


def _linhas_cobertura(artefatos: Artefatos) -> list[str]:
    inicio, fim = artefatos.configuracao["janela"]
    return [
        "RAIS-CTPS (estoque em 31/12) · SISMIGRA-ATIVOS (fotografia de dezembro)",
        f"Anos: {inicio}–{fim} — janela fixa",
        "Variáveis: índice Q + 6 atributos de perfil",
    ]


def _linhas_filtros(artefatos: Artefatos) -> list[str]:
    return [
        f"Ano: fixo em {artefatos.configuracao['janela'][0]}–{artefatos.configuracao['janela'][1]}",
        f"Nacionalidade: as {artefatos.n_elegiveis} elegíveis (a estrutura depende do conjunto)",
        "Top N: só no tamanho da tabela, não no cálculo",
    ]


def _linhas_metodo(artefatos: Artefatos) -> list[str]:
    return [
        "Unidade: nacionalidade — nunca indivíduo",
        f"Cobertura: {artefatos.n_elegiveis} de {artefatos.n_universo} comparáveis entre as fontes",
        "Interpretação: gradiente associativo, não causal",
    ]


def _indicadores(artefatos: Artefatos) -> list[tuple[str, str]]:
    resumo = graficos.resumo_numerico(artefatos)
    return [
        ("Regiões (k escolhido)", resumo["Regiões"]),
        ("Coesão (silhueta)", resumo["Silhueta no k escolhido"]),
        ("Concordância KMeans × Ward", resumo["KMeans × Ward"]),
        (
            "Estabilidade sob reamostragem",
            f"{resumo['Estabilidade (média)']} de média · {resumo['Estabilidade (mínimo)']} no pior caso",
        ),
    ]


def _limites() -> list[tuple[str, str]]:
    return [
        ("Denominador", textos.DENOMINADOR_EXPLICITO),
        ("Critério de elegibilidade", textos.CRITERIO_ELEGIBILIDADE),
        ("Cobertura observada", textos.COBERTURA_OBSERVADA),
        ("Interpretação permitida", textos.INTERPRETACAO_PERMITIDA),
        ("Interpretação não permitida", textos.INTERPRETACAO_PROIBIDA),
    ]


def _seletor_de_evidencia() -> textos.Evidencia:
    """Seletor compacto: rótulos curtos cabem em uma única linha."""
    por_rotulo = {textos.rotulo_curto(evidencia): evidencia for evidencia in textos.EVIDENCIAS}
    rotulos = list(por_rotulo)
    if hasattr(st, "segmented_control"):
        escolhido = st.segmented_control(
            "Evidência", rotulos, default=rotulos[0], label_visibility="collapsed"
        )
    else:
        escolhido = st.radio("Evidência", rotulos, horizontal=True, label_visibility="collapsed")
    return por_rotulo[escolhido or rotulos[0]]


def _tabela_das_nacionalidades(artefatos: Artefatos) -> None:
    tabela = artefatos.perfis.copy()
    tabela[COLUNA_Q_FORMATADO] = tabela["Q_medio"].map(lambda valor: formatar_decimal(valor, 2))
    tabela["Vínculos na janela"] = tabela["V_total"].map(formatar_inteiro)
    for coluna in COLUNAS_ATRIBUTOS:
        tabela[ROTULOS_ATRIBUTOS[coluna]] = tabela[coluna].map(
            lambda valor, nome=coluna: formatar_atributo(nome, valor)
        )
    colunas = [
        "nacionalidade", "regiao", COLUNA_Q_FORMATADO, "Vínculos na janela", *ROTULOS_ATRIBUTOS.values()
    ]
    tabela = tabela[colunas].rename(columns={"nacionalidade": "Nacionalidade", "regiao": "Região"})
    tabela = tabela.sort_values(
        COLUNA_Q_FORMATADO,
        ascending=False,
        key=lambda serie: serie.str.replace(",", ".").astype(float),
    )
    quantidade = st.selectbox("Quantas nacionalidades exibir", OPCOES_TOPO, index=1)
    if quantidade != "todas":
        tabela = tabela.head(int(quantidade))
    st.dataframe(tabela, hide_index=True, height=ALTURA_TABELA)


def _regras_das_arvores(artefatos: Artefatos) -> None:
    for _, linha in artefatos.arvores.iterrows():
        with st.expander(f"Regra lida — {linha['descricao_alvo']}"):
            st.code(graficos.texto_da_regra(artefatos, linha["arvore"]), language="text")
            st.caption(
                f"acurácia em validação cruzada {formatar_decimal(linha['acuracia_cv'])} · "
                f"baseline {formatar_decimal(linha['baseline'])} · "
                f"{int(linha['folhas'])} folhas"
            )


def _renderizar_evidencia(
    artefatos: Artefatos, evidencia: textos.Evidencia, valores: dict[str, object]
) -> None:
    st.markdown(f"**{evidencia.titulo}**")
    if evidencia.chave == "quem":
        _tabela_das_nacionalidades(artefatos)
    else:
        layout.grafico(FIGURAS[evidencia.chave](artefatos))
    st.caption(textos.preencher(evidencia.leitura, valores))
    if evidencia.chave == "arvores":
        _regras_das_arvores(artefatos)


def renderizar(artefatos: Artefatos) -> None:
    """Desenha a aba Q7 inteira."""
    valores = artefatos.valores_para_texto()
    layout.tres_cartoes(
        _linhas_cobertura(artefatos), _linhas_filtros(artefatos), _linhas_metodo(artefatos)
    )

    coluna_evidencia, coluna_resposta = st.columns([2, 1], gap="medium")

    with coluna_evidencia, st.container(border=True):
        evidencia = _seletor_de_evidencia()
        _renderizar_evidencia(artefatos, evidencia, valores)

    with coluna_resposta:
        limites = _limites()
        layout.painel_resposta(
            "Resposta + limites",
            textos.preencher(textos.RESPOSTA_SINTETICA, valores),
            _indicadores(artefatos),
            ((rotulo, textos.preencher(texto, valores)) for rotulo, texto in limites),
        )

    layout.ponte(
        "Onde isto toca o problema do projeto",
        textos.preencher(textos.RESPOSTA_ANCORADA_NO_PROBLEMA, valores),
    )
    layout.rodape_pisos(*artefatos.janela_dos_perfis)
