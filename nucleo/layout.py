"""Peças de layout reutilizáveis.

O slide 11 define um contrato para toda aba: três cartões no topo, uma evidência
principal à esquerda, um painel de resposta e limites à direita, e o rodapé de pisos
fixos. Este módulo implementa esse contrato uma única vez.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

import streamlit as st

from nucleo.config import CINZA
from nucleo.estilo import CLASSES

NEGRITO = re.compile(r"\*\*(.+?)\*\*")

ESTILO_ROTULO = (
    f"color:{CINZA}; font-size:0.7rem; letter-spacing:0.05em; "
    "text-transform:uppercase; margin-top:0.15rem;"
)
ESTILO_VALOR = "font-size:0.92rem; line-height:1.35; margin-bottom:0.4rem;"


def como_html(texto: str) -> str:
    """Converte `**x**` em `<b>x</b>`.

    O cabeçalho é HTML puro, então o Markdown não é interpretado e os asteriscos
    apareceriam literalmente na tela.
    """
    return NEGRITO.sub(r"<b>\1</b>", texto)


def cabecalho(titulo: str, pergunta: str = "") -> None:
    """Barra superior colada nas bordas, com a pergunta da aba como segunda linha."""
    segunda = (
        f'<div style="color:#C6D2E0; font-size:0.85rem; margin-top:0.2rem;">'
        f"{como_html(pergunta)}</div>"
        if pergunta
        else ""
    )
    st.markdown(
        f'<div class="{CLASSES["cabecalho"]}">'
        f'<div style="color:#FFFFFF; font-size:1.12rem; font-weight:700;">{titulo}</div>'
        f"{segunda}</div>",
        unsafe_allow_html=True,
    )


def cartao(titulo: str, linhas: Iterable[str]) -> None:
    """Um dos três cartões informativos do topo."""
    corpo = "".join(f'<div class="dash-linha">{linha}</div>' for linha in linhas)
    with st.container(border=True):
        st.markdown(f'<div class="dash-rotulo">{titulo}</div>{corpo}', unsafe_allow_html=True)


def tres_cartoes(
    cobertura: Iterable[str], filtros: Iterable[str], metodo: Iterable[str]
) -> None:
    """As três caixas do topo, na ordem do desenho."""
    caixas = (("Cobertura", cobertura), ("Filtros", filtros), ("Nota metodológica", metodo))
    for coluna, (titulo, linhas) in zip(st.columns(3), caixas):
        with coluna:
            cartao(titulo, linhas)


def definicoes(pares: Iterable[tuple[str, str]]) -> None:
    """Lista compacta de rótulo e valor — substitui métricas largas em coluna estreita."""
    st.markdown(
        "".join(
            f'<div style="{ESTILO_ROTULO}">{rotulo}</div><div style="{ESTILO_VALOR}">{valor}</div>'
            for rotulo, valor in pares
        ),
        unsafe_allow_html=True,
    )


def painel_resposta(
    titulo: str,
    resposta: str,
    indicadores: Iterable[tuple[str, str]],
    limites: Iterable[tuple[str, str]],
) -> None:
    """Painel fixo da aba: a resposta não muda quando o usuário troca de evidência.

    Os limites ficam **dentro** do mesmo cartão e visíveis, como no desenho aprovado —
    o produto precisa ser autocontido, sem depender de clique para revelar a ressalva.
    """
    with st.container(border=True):
        st.markdown(f"#### {titulo}")
        st.markdown(resposta)
        st.divider()
        definicoes(indicadores)
        st.divider()
        st.markdown("**O que sustenta esta resposta**")
        for rotulo, texto in limites:
            st.markdown(f"- **{rotulo}**: {texto}")


def rodape_pisos() -> None:
    """Rodapé do desenho: os pisos são decisões do projeto, não filtros do usuário."""
    st.markdown(
        f'<div class="{CLASSES["pisos"]}">'
        "<b>Pisos fixos (não filtros):</b> R ≥ 500 para HHI (Q2) e persistência (Q5); "
        "V_total ≥ 100 na janela 2023–2025 para os perfis (Q6–Q7); a árvore exige "
        "R_total ≥ 500 e V_total ≥ 100; R ≥ 5.000 na leitura destacada da Q4.</div>",
        unsafe_allow_html=True,
    )


def aviso_ausencia(titulo: str, detalhes: Iterable[str], instrucao: str) -> None:
    """Tela exibida enquanto os artefatos do notebook não estiverem presentes."""
    st.warning(f"**{titulo}**")
    st.markdown("Artefatos ainda ausentes:")
    for detalhe in detalhes:
        st.markdown(f"- `{detalhe}`")
    st.info(instrucao)
