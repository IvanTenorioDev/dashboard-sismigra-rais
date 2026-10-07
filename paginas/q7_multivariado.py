"""Aba Q7 — Análise multivariada.

Segue o contrato do slide 11: três cartões no topo, a evidência principal à esquerda,
o painel de resposta e limites à direita — **fixo**, para que trocar de evidência não
troque a conclusão — e o rodapé de pisos.

A única liberdade que esta aba toma em relação ao desenho original é o seletor de
evidência: a Q7 tem várias provas e um único espaço para exibi-las.
"""

from __future__ import annotations

import streamlit as st

from nucleo import graficos, layout, textos
from nucleo.abas import CONTEUDO_POR_ABA, Conteudo
from nucleo.config import ABA_Q7, COLUNAS_ATRIBUTOS, ROTULOS_ATRIBUTOS
from nucleo.dados import Artefatos
from nucleo.formatos import formatar_atributo, formatar_decimal, formatar_inteiro

OPCOES_TOPO = ("10", "25", "50", "todas")
ALTURA_TABELA = 430
COLUNA_Q_FORMATADO = "Q (janela)"


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
    conteudo: Conteudo, artefatos: Artefatos, evidencia: textos.Evidencia, valores: dict[str, object]
) -> None:
    st.markdown(f"**{evidencia.titulo}**")
    if evidencia.chave == "quem":
        _tabela_das_nacionalidades(artefatos)
    else:
        layout.grafico(conteudo.figuras[evidencia.chave](artefatos))
    st.caption(textos.preencher(evidencia.leitura, valores))
    if evidencia.chave == "arvores":
        _regras_das_arvores(artefatos)


def renderizar(artefatos: Artefatos) -> None:
    """Desenha a aba Q7: a declaração comum, mais os dois recursos que só o app tem.

    Os cartões, os indicadores, os limites e a ponte vêm de `nucleo/abas.py`, como em
    qualquer outra aba. O que fica aqui é a tabela com controle de quantas nacionalidades
    exibir e as regras das árvores em expansores — nenhum dos dois cabe numa declaração.
    """
    conteudo = CONTEUDO_POR_ABA[ABA_Q7](artefatos)
    valores = conteudo.valores(artefatos)
    layout.cartoes(conteudo.cartoes)

    coluna_evidencia, coluna_resposta = st.columns([2, 1], gap="medium")

    with coluna_evidencia, st.container(border=True):
        evidencia = _seletor_de_evidencia()
        _renderizar_evidencia(conteudo, artefatos, evidencia, valores)

    with coluna_resposta:
        layout.painel_resposta(
            "Resposta + limites",
            textos.preencher(conteudo.resposta, valores),
            conteudo.indicadores(artefatos),
            (
                (rotulo, textos.preencher(texto, valores))
                for rotulo, texto in conteudo.limites
            ),
        )

    layout.ponte(
        "Onde isto toca o problema do projeto",
        textos.preencher(conteudo.ponte, valores),
    )
    layout.rodape_pisos(*artefatos.janela_dos_perfis)
