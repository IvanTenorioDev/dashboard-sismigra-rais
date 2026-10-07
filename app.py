"""Ponto de entrada do dashboard analítico SISMIGRA × RAIS-CTPS.

A navegação é organizada pelas perguntas do projeto, não pelas técnicas — decisão
registrada no slide 11 da proposta de validação.
"""

from __future__ import annotations

import streamlit as st

from nucleo import estilo, layout, textos
from nucleo.config import ABA_Q7, ABAS, PISO_REGISTROS, PISO_VINCULOS
from nucleo.dados import (
    INSTRUCAO_GERACAO,
    ArtefatosAusentes,
    Artefatos,
    artefatos_faltantes,
    carregar,
)
from paginas import aba_generica, q7_multivariado

TITULO = "Dashboard analítico • SISMIGRA × RAIS-CTPS"
SUBTITULO = "Projeto Integrador I · imigração registrada e vínculos formais · 2022–2025"


def _aba_pedida() -> str:
    """Aba indicada na URL (`?aba=Q7 Multivariado`), para permitir link direto."""
    try:
        pedida = str(st.query_params.get("aba", ""))
    except Exception:  # noqa: BLE001 — fora de um contexto de requisição
        return ABAS[0]
    return pedida if pedida in ABAS else ABAS[0]


def _navegacao() -> str:
    """Sidebar com as abas, na ordem do desenho aprovado."""
    with st.sidebar:
        st.markdown("**Navegação por pergunta**")
        st.caption("Cada aba entrega uma resposta analítica verificável e explicita seus limites.")
        aba = st.radio(
            "Pergunta", ABAS, index=ABAS.index(_aba_pedida()), label_visibility="collapsed"
        )
        st.divider()
        st.caption(
            "Pisos de elegibilidade são fixos por decisão metodológica: "
            f"R ≥ {PISO_REGISTROS} · V_total ≥ {PISO_VINCULOS} (perfis e Q4) · "
            f"R_total ≥ {PISO_REGISTROS} na árvore."
        )
    return str(aba)


def _avisar_se_sintetico(artefatos: Artefatos) -> None:
    """Impede que artefatos de teste sejam lidos como resultado real."""
    if artefatos.configuracao.get("fixture"):
        st.error(
            "**Dados sintéticos.** Esta execução está apontada para artefatos gerados por "
            "`testes/validar.py`. Os números servem apenas para conferir o layout — não são "
            "resultados do projeto."
        )


def main() -> None:
    st.set_page_config(
        page_title="Dashboard SISMIGRA × RAIS-CTPS",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    estilo.aplicar()
    aba = _navegacao()
    layout.cabecalho(TITULO, textos.PERGUNTAS.get(aba, SUBTITULO))

    try:
        artefatos = carregar()
    except ArtefatosAusentes:
        layout.aviso_ausencia(
            "Os dados ainda não foram gerados", artefatos_faltantes(), INSTRUCAO_GERACAO
        )
        return
    except ValueError as erro:
        st.error(f"Os artefatos existem, mas o esquema não confere: {erro}")
        return

    _avisar_se_sintetico(artefatos)
    if aba == ABA_Q7:
        q7_multivariado.renderizar(artefatos)
        return
    aba_generica.renderizar(aba, artefatos)


main()
