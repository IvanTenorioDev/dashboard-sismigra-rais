"""Leitura dos artefatos da Q7 exportados pela FASE 9 do notebook.

O dashboard não recalcula nada: lê os arquivos e valida o esquema. Se um artefato
faltar ou vier com coluna inesperada, o erro é explícito — melhor falhar alto do que
exibir um número errado em silêncio.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from nucleo.config import ARQUIVOS_Q7, COLUNAS_ATRIBUTOS, pasta_dados

INSTRUCAO_GERACAO = (
    "Execute a FASE 9 do notebook Integrador_Base_Unificada_REV1.ipynb no Colab e "
    "copie a pasta 'dashboard' gerada para 'dados/q7/' neste projeto."
)


class ArtefatosAusentes(FileNotFoundError):
    """Levantado quando a FASE 9 do notebook ainda não foi executada."""


COLUNAS_OBRIGATORIAS: dict[str, tuple[str, ...]] = {
    "perfis": ("nacionalidade", "regiao", "V_total", "Q_medio", *COLUNAS_ATRIBUTOS),
    "pca": ("nacionalidade", "regiao", "PC1", "PC2"),
    "cargas": ("atributo", "PC1", "PC2"),
    "variancia": ("componente", "variancia_explicada", "variancia_acumulada"),
    "diagnostico": (
        "k",
        "inercia",
        "silhueta",
        "ari_kmeans_ward",
        "ari_estabilidade",
        "ari_desvio",
        "menor_grupo",
        "admissivel",
    ),
    "regioes": (
        "regiao",
        "n_nacionalidades",
        "vinculos_na_janela",
        "Q_mediano",
        *COLUNAS_ATRIBUTOS,
    ),
    "arvores": ("arvore", "descricao_alvo", "acuracia_cv", "baseline", "regra"),
}


@dataclass(frozen=True)
class DadosQ7:
    """Conjunto completo dos artefatos da Q7."""

    configuracao: dict[str, object]
    perfis: pd.DataFrame
    pca: pd.DataFrame
    cargas: pd.DataFrame
    variancia: pd.DataFrame
    diagnostico: pd.DataFrame
    regioes: pd.DataFrame
    arvores: pd.DataFrame

    @property
    def k_escolhido(self) -> int:
        return int(self.configuracao["k_escolhido"])

    @property
    def n_elegiveis(self) -> int:
        return int(self.configuracao["elegiveis"])

    @property
    def n_universo(self) -> int:
        return int(self.configuracao["universo_com_Q_comparavel"])

    def regiao_do_k(self) -> pd.Series:
        """Linha do diagnóstico correspondente ao k escolhido."""
        return self.diagnostico.loc[self.diagnostico["k"].eq(self.k_escolhido)].iloc[0]

    def valores_de_estabilidade(self, k: int) -> list[float]:
        """Valores individuais de ARI das reamostragens para um dado k."""
        if "ari_valores" not in self.diagnostico.columns:
            return []
        linha = self.diagnostico.loc[self.diagnostico["k"].eq(k)]
        if linha.empty:
            return []
        return [
            float(parte)
            for parte in str(linha.iloc[0]["ari_valores"]).split("|")
            if parte.strip()
        ]


def artefatos_faltantes(pasta: Path | None = None) -> list[str]:
    """Lista os artefatos ainda ausentes, para a tela de aviso."""
    destino = pasta or pasta_dados()
    return [nome for nome in ARQUIVOS_Q7.values() if not (destino / nome).exists()]


def _caminho_existente(pasta: Path, chave: str) -> Path:
    caminho = pasta / ARQUIVOS_Q7[chave]
    if not caminho.exists():
        raise ArtefatosAusentes(f"artefato ausente: {caminho}. {INSTRUCAO_GERACAO}")
    return caminho


def _ler_tabela(pasta: Path, chave: str) -> pd.DataFrame:
    tabela = pd.read_csv(_caminho_existente(pasta, chave), encoding="utf-8-sig")
    ausentes = [
        coluna for coluna in COLUNAS_OBRIGATORIAS[chave] if coluna not in tabela.columns
    ]
    if ausentes:
        raise ValueError(
            f"{ARQUIVOS_Q7[chave]} sem as colunas obrigatórias: {ausentes}. "
            f"Rode a FASE 9 novamente: o esquema do artefato mudou."
        )
    return tabela


def carregar(pasta: Path | None = None) -> DadosQ7:
    """Carrega e valida todos os artefatos da Q7."""
    destino = pasta or pasta_dados()
    configuracao = json.loads(
        _caminho_existente(destino, "configuracao").read_text(encoding="utf-8")
    )
    tabelas = {chave: _ler_tabela(destino, chave) for chave in COLUNAS_OBRIGATORIAS}
    return DadosQ7(configuracao=configuracao, **tabelas)
