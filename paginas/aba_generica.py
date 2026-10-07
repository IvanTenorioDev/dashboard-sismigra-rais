"""Aba genérica — monta qualquer aba a partir da declaração dela.

O painel estático e este app leem a **mesma** declaração: os cartões do topo, a evidência
com o seu seletor, o painel de resposta e limites, e os blocos de largura total. O que muda
entre as duas telas é só o renderizador — a declaração é uma fonte, não duas, e é por isso
que acrescentar uma pergunta não exige escrever uma página nova.

A Q7 fica de fora: ela traz dois recursos que não cabem numa declaração — a tabela com
controle de quantas nacionalidades exibir e as regras das árvores em expansores. As outras
sete abas passam por aqui.

A declaração vive em `gerador/construir.py` porque foi lá que nasceu, junto do painel
estático. As duas telas a importam de lá: a dependência aponta para o módulo que detém o
contrato, não para o renderizador.
"""

from __future__ import annotations

import streamlit as st

from gerador.construir import CONTEUDO_POR_ABA, Conteudo
from nucleo import layout, textos
from nucleo.dados import Artefatos

TITULO_RESPOSTA = "Resposta + limites"


def _seletor(conteudo: Conteudo) -> textos.Evidencia:
    """Seletor compacto: rótulos curtos cabem em uma única linha."""
    por_rotulo = {conteudo.rotulo_curto(item): item for item in conteudo.evidencias}
    rotulos = list(por_rotulo)
    if hasattr(st, "segmented_control"):
        escolhido = st.segmented_control(
            "Evidência", rotulos, default=rotulos[0], label_visibility="collapsed"
        )
    else:
        escolhido = st.radio("Evidência", rotulos, horizontal=True, label_visibility="collapsed")
    return por_rotulo[escolhido or rotulos[0]]


def _mostrar_evidencia(
    conteudo: Conteudo, artefatos: Artefatos, evidencia: textos.Evidencia
) -> None:
    """Uma evidência é uma figura ou uma tabela — a tabela substitui a figura da sua chave."""
    if conteudo.tabela and evidencia.chave == conteudo.chave_tabela:
        st.markdown(conteudo.tabela(artefatos), unsafe_allow_html=True)
        return
    layout.grafico(conteudo.figuras[evidencia.chave](artefatos))


def _limites_preenchidos(
    conteudo: Conteudo, valores: dict[str, object]
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (textos.preencher(rotulo, valores), textos.preencher(texto, valores))
        for rotulo, texto in conteudo.limites
    )


def renderizar(aba: str, artefatos: Artefatos) -> None:
    """Desenha a aba declarada, inteira."""
    conteudo = CONTEUDO_POR_ABA[aba](artefatos)
    valores = conteudo.valores(artefatos)
    layout.cartoes(conteudo.cartoes)

    resposta = (
        TITULO_RESPOSTA,
        textos.preencher(conteudo.resposta, valores),
        conteudo.indicadores(artefatos),
        _limites_preenchidos(conteudo, valores),
    )
    if not conteudo.evidencias:
        # Aba sem figura: não há evidência a alternar, e o painel ocupa a largura toda — o
        # mesmo arranjo que o painel estático usa.
        layout.painel_resposta(*resposta)
    else:
        coluna_evidencia, coluna_resposta = st.columns([1.55, 1], gap="medium")
        with coluna_evidencia, st.container(border=True):
            st.markdown("#### Evidência principal")
            evidencia = _seletor(conteudo)
            _mostrar_evidencia(conteudo, artefatos, evidencia)
            layout.leitura(textos.preencher(evidencia.leitura, valores))
        with coluna_resposta:
            layout.painel_resposta(*resposta)

    layout.blocos(
        (
            bloco.titulo,
            textos.preencher(bloco.nota, valores),
            bloco.tabela(artefatos),
        )
        for bloco in conteudo.blocos
    )
    layout.ponte(
        "Onde isto toca o problema do projeto",
        textos.preencher(conteudo.ponte, valores),
    )
    layout.rodape_pisos(*artefatos.janela_dos_perfis)
