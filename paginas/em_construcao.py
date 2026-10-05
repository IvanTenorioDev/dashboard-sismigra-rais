"""Aba ainda sem conteúdo.

Mantém o contrato de layout do slide 11 para que o grupo só precise preencher conteúdo:
três cartões, evidência principal, resposta e limites, rodapé de pisos.
"""

from __future__ import annotations

import streamlit as st

from nucleo import layout

CONTEUDO_PENDENTE = (
    "Esta aba ainda não foi implementada. O desenho abaixo é o contrato que ela deve "
    "seguir — o mesmo da Q7, que já está pronta e serve de referência."
)

INDICADORES_PENDENTES: tuple[tuple[str, str], ...] = (
    ("Indicador principal", "—"),
    ("Comparação", "—"),
)

LIMITES_PENDENTES: tuple[tuple[str, str], ...] = (
    ("Resultado sintético", "a resposta desta aba em uma frase"),
    ("Denominador explícito", "quantas unidades entram e quantas ficam de fora"),
    ("Critério de elegibilidade", "qual piso foi aplicado e por quê"),
    ("Cobertura observada", "o que os dados cobrem e o que não cobrem"),
    ("Interpretação permitida", "o que se pode afirmar a partir daqui"),
)


def renderizar(aba: str) -> None:
    """Desenha a aba vazia com o esqueleto do contrato de layout."""
    st.info(f"**{aba}** — {CONTEUDO_PENDENTE}")

    layout.tres_cartoes(
        ("fontes · anos · variáveis",),
        ("ano · nacionalidade · Top N",),
        ("unidade · cobertura · interpretação",),
    )

    coluna_evidencia, coluna_resposta = st.columns([2, 1], gap="medium")
    with coluna_evidencia, st.container(border=True):
        st.markdown("**Evidência principal**")
        st.caption("A figura da resposta vai aqui — uma por aba, escolhida em `nucleo/graficos.py`.")
    with coluna_resposta:
        layout.painel_resposta(
            "Resposta + limites",
            "A resposta desta aba em uma frase entra aqui.",
            INDICADORES_PENDENTES,
            LIMITES_PENDENTES,
        )

    layout.rodape_pisos()
