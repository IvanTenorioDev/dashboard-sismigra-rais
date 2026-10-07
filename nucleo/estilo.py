"""Folha de estilo do dashboard.

O desenho aprovado (slide 11) tem uma identidade própria que o tema do Streamlit não
cobre: itens de navegação como botões, barra superior colada nas bordas e cartões com
raio e borda específicos. Tudo isso vive aqui — nenhuma página injeta CSS por conta
própria, para não haver duas fontes de verdade visual.
"""

from __future__ import annotations

import streamlit as st

from nucleo.config import AZUL, CINZA, CSS_TABELA, LARANJA

CLASSES = {
    "cabecalho": "dash-cabecalho",
    "pisos": "dash-pisos",
}

CSS = f"""
<style>
/* --- Barra superior colada nas bordas, como no desenho aprovado ------------- */
.block-container {{
    padding-top: 0;
    padding-left: 1rem;
    padding-right: 1rem;
    max-width: 1500px;
}}
.{CLASSES["cabecalho"]} {{
    background: {AZUL};
    margin: 0 -1rem 1rem -1rem;
    padding: 0.9rem 1.1rem;
    border-radius: 0;
}}

/* --- Barra de ferramentas do Streamlit: fora do desenho -------------------
   O cabeçalho fixo do Streamlit fica sobre o conteúdo e cortava a primeira
   linha da barra azul. Escondido, a barra encosta no topo como no desenho.   */
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], #MainMenu {{
    display: none;
}}

/* --- Navegação como lista de botões, sem os círculos do radio --------------
   A estrutura renderizada é:
     label > span(oculto, com o input) + div > div(círculo) + div(rótulo)
   Por isso o círculo é `label > div > div:first-child` — o seletor ingênuo
   `label > div:first-child` nunca casa, porque o primeiro filho é o span.     */
section[data-testid="stSidebar"] {{
    background: #FFFFFF;
    border-right: 1px solid #E1E6EB;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > div {{
    width: 100%;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label {{
    display: flex;
    align-items: center;
    width: 100%;
    border: 1px solid #E1E6EB;
    border-radius: 0.45rem;
    background: #FFFFFF;
    padding: 0.42rem 0.7rem;
    margin-bottom: 0.32rem;
    cursor: pointer;
    transition: border-color 0.12s ease;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label > div > div:first-child {{
    display: none;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label p {{
    font-size: 0.9rem;
    margin: 0;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
    border-color: {LARANJA};
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
    background: {LARANJA};
    border-color: {LARANJA};
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {{
    color: #FFFFFF;
    font-weight: 600;
}}

/* --- Cartões com o mesmo raio do desenho ----------------------------------- */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 0.65rem;
    border-color: #E1E6EB;
}}

/* --- Títulos dos cartões informativos em caixa alta e baixa, em laranja ---- */
.dash-rotulo {{
    color: {LARANJA};
    font-size: 0.95rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}}
.dash-linha {{
    color: {CINZA};
    font-size: 0.86rem;
    line-height: 1.35;
}}

/* --- Rodapé de pisos --------------------------------------------------------
   No desenho aprovado essa linha aparece na primeira tela. Como é o último
   elemento da página, `position: sticky` não tem espaço para grudar — a mesma
   informação fica permanentemente visível na sidebar, que não rola.          */
.{CLASSES["pisos"]} {{
    color: #1A1A1A;
    font-size: 0.8rem;
    border-top: 1px solid #E1E6EB;
    padding-top: 0.6rem;
    margin-top: 0.8rem;
}}
.{CLASSES["pisos"]} b {{ color: {LARANJA}; }}
{CSS_TABELA}
</style>
"""


def aplicar() -> None:
    """Injeta a folha de estilo. Chamar uma única vez, no início do app."""
    st.markdown(CSS, unsafe_allow_html=True)
