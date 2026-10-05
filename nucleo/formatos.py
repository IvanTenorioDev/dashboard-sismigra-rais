"""Formatação de valores para exibição.

Evita que cada página reinvente o formato — e garante que todo número na tela use
vírgula decimal, como o leitor brasileiro espera.
"""

from __future__ import annotations

import pandas as pd

from nucleo.config import ATRIBUTOS_PERCENTUAIS, UNIDADES_ATRIBUTOS


def formatar_atributo(coluna: str, valor: float) -> str:
    """Formata um valor de atributo de perfil conforme a unidade da coluna."""
    if pd.isna(valor):
        return "—"
    if coluna in ATRIBUTOS_PERCENTUAIS:
        return formatar_percentual(valor)
    if UNIDADES_ATRIBUTOS.get(coluna) == "SM":
        return f"{valor:.2f} SM".replace(".", ",")
    return formatar_decimal(valor, 2)


def formatar_inteiro(valor: float) -> str:
    """Formata um número inteiro com separador de milhar brasileiro."""
    if pd.isna(valor):
        return "—"
    return f"{valor:,.0f}".replace(",", ".")


def formatar_decimal(valor: float, casas: int = 3) -> str:
    """Formata um decimal com vírgula e o número pedido de casas."""
    if pd.isna(valor):
        return "—"
    return f"{valor:.{casas}f}".replace(".", ",")


def formatar_percentual(valor: float, casas: int = 1) -> str:
    """Formata uma fração (0 a 1) como percentual."""
    if pd.isna(valor):
        return "—"
    return f"{valor:.{casas}%}".replace(".", ",")
