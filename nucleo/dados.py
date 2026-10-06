"""Leitura dos artefatos da Q7 exportados pela FASE 9 do notebook.

O dashboard não recalcula nada: lê os arquivos e valida o esquema. Se um artefato
faltar ou vier com coluna inesperada, o erro é explícito — melhor falhar alto do que
exibir um número errado em silêncio.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from nucleo.config import (
    ARQUIVOS_Q7,
    COLUNAS_ATRIBUTOS,
    NACIONALIDADES_NA_TABELA,
    pasta_dados,
)
from nucleo.formatos import formatar_decimal, formatar_inteiro, formatar_percentual

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

# Campos que a Q4 usa quando existem, mas que não invalidam os artefatos gerados
# antes de o contrato prevê-los. A Q4 degrada com aviso em vez de falhar.
COLUNAS_OPCIONAIS: dict[str, tuple[str, ...]] = {
    "perfis": ("R_total", "anos_observados"),
}

# Faixas do índice Q usadas pela Q4. Os cortes são redondos de propósito: 1 é a paridade
# (as duas fontes coincidem) e 1,5 separa a sobre-representação moderada da acentuada.
FAIXAS_Q: tuple[tuple[float, float, str], ...] = (
    (0.0, 0.5, "Q ≤ 0,5"),
    (0.5, 1.0, "0,5 < Q ≤ 1"),
    (1.0, 1.5, "1 < Q ≤ 1,5"),
    (1.5, float("inf"), "Q > 1,5"),
)


def correlacoes(x: pd.Series, y: pd.Series) -> tuple[float, float]:
    """Pearson e Spearman entre duas séries.

    Spearman é calculado sobre os postos, sem depender do scipy — e é ele que importa
    para o índice Q, cuja cauda pesada torna o Pearson enganoso.
    """
    pares = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(pares) < 3:
        return float("nan"), float("nan")
    pearson = float(np.corrcoef(pares["x"], pares["y"])[0, 1])
    spearman = float(np.corrcoef(pares["x"].rank(), pares["y"].rank())[0, 1])
    return pearson, spearman


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

    def tem(self, chave: str, coluna: str) -> bool:
        """Indica se um campo opcional está presente nos artefatos carregados."""
        return coluna in getattr(self, chave).columns

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

    def _valores_da_particao(self) -> dict[str, object]:
        linha = self.regiao_do_k()
        rejeitados = self.diagnostico.loc[~self.diagnostico["admissivel"], "k"]
        em_k2 = self.diagnostico.loc[self.diagnostico["k"].eq(2), "ari_kmeans_ward"]
        return {
            "n_elegiveis": self.n_elegiveis,
            "n_universo": self.n_universo,
            "k": self.k_escolhido,
            "silhueta": formatar_decimal(linha["silhueta"]),
            "acordo": formatar_decimal(linha["ari_kmeans_ward"]),
            "acordo_k2": formatar_decimal(em_k2.iloc[0]) if len(em_k2) else "indisponível",
            "acordo_minimo": formatar_decimal(self.configuracao["acordo_minimo_kmeans_ward"], 2),
            "minimo_grupo": int(self.configuracao["minimo_nacionalidades_por_grupo"]),
            "primeiro_k_inadmissivel": int(rejeitados.min()) if len(rejeitados) else 9,
            "repeticoes": int(self.configuracao["repeticoes_reamostragem"]),
            "ari_media": formatar_decimal(linha["ari_estabilidade"]),
            "ari_minimo": formatar_decimal(linha["ari_minimo"]),
            "n_tabela": NACIONALIDADES_NA_TABELA,
        }

    def _valores_das_regioes(self) -> dict[str, object]:
        regioes = self.regioes.sort_values("regiao")
        salarios = [float(valor) for valor in regioes["salario_medio_sm"]]
        com_maior_q = regioes.loc[regioes["Q_mediano"].idxmax()]
        variancia = float(self.variancia["variancia_acumulada"].max())
        return {
            "salarios": " · ".join(formatar_decimal(valor, 2) for valor in salarios),
            "razao_salarios": formatar_decimal(max(salarios) / min(salarios), 1),
            "regiao_maior_q": int(com_maior_q["regiao"]),
            "q_regiao_maior": formatar_decimal(com_maior_q["Q_mediano"], 2),
            "salario_regiao_maior_q": formatar_decimal(com_maior_q["salario_medio_sm"], 2),
            "superior_regiao_maior_q": formatar_percentual(com_maior_q["pct_superior"], 0),
            "variancia_acumulada": formatar_percentual(variancia),
            "variancia_restante": formatar_percentual(1 - variancia),
            "carga_superior_pc1": formatar_decimal(
                self.cargas.loc[self.cargas["atributo"].eq("pct_superior"), "PC1"].iloc[0]
            ),
            "participacao_maior": formatar_percentual(regioes["participacao_vinculos"].max()),
            "n_maior": int(regioes.loc[regioes["participacao_vinculos"].idxmax(), "n_nacionalidades"]),
        }

    def _valores_das_arvores(self) -> dict[str, object]:
        if self.arvores.empty:
            return {}
        referencia = self.arvores.iloc[0]
        return {
            "profundidade": int(referencia.get("max_profundidade", 3)),
            "min_folha": int(referencia.get("min_amostras_folha", 5)),
            "ganho": formatar_decimal(referencia.get("ganho_minimo_impureza", 0.03), 2),
        }

    def valores_para_texto(self) -> dict[str, object]:
        """Números desta execução para preencher a narrativa.

        A narrativa em `nucleo/textos.py` usa `str.format` com estes campos passados
        como argumento. Um número escrito à mão no texto divergiria em silêncio na
        próxima execução do notebook; assim ele acompanha os dados.
        """
        valores: dict[str, object] = {}
        for parcial in (self._valores_da_particao(), self._valores_das_regioes(), self._valores_das_arvores()):
            valores.update(parcial)
        return valores

    def faixas_de_q(self) -> pd.DataFrame:
        """Perfil das nacionalidades por faixa do índice Q — a tabela central da Q4."""
        linhas = []
        for inicio, fim, rotulo in FAIXAS_Q:
            recorte = self.perfis[self.perfis["Q_medio"].gt(inicio) & self.perfis["Q_medio"].le(fim)]
            linhas.append({
                "faixa": rotulo,
                "nacionalidades": len(recorte),
                "salario_mediano": recorte["salario_medio_sm"].median(),
                "superior_completo": recorte["pct_superior"].median(),
                "vinculos": recorte["V_total"].sum(),
            })
        quadro = pd.DataFrame(linhas)
        quadro["participacao_vinculos"] = quadro["vinculos"] / quadro["vinculos"].sum()
        return quadro

    def valores_q4_para_texto(self) -> dict[str, object]:
        """Números da Q4: distribuição do índice, concentração e associações."""
        indice = self.perfis["Q_medio"]
        acima = self.perfis[self.perfis["Q_medio"].gt(1)]
        extremos = self.perfis[self.perfis["Q_medio"].gt(5)]
        maior = self.perfis.loc[indice.idxmax()]
        faixas = self.faixas_de_q()
        pearson_salario, spearman_salario = correlacoes(
            self.perfis["Q_medio"], self.perfis["salario_medio_sm"]
        )
        _, spearman_volume = correlacoes(self.perfis["Q_medio"], self.perfis["V_total"])
        return {
            "n_elegiveis": self.n_elegiveis,
            "n_acima_1": len(acima),
            "pct_acima_1": formatar_percentual(len(acima) / len(self.perfis)),
            "participacao_acima_1": formatar_percentual(
                acima["V_total"].sum() / self.perfis["V_total"].sum()
            ),
            "n_abaixo_1": int(self.perfis["Q_medio"].le(1).sum()),
            "q_mediana": formatar_decimal(indice.median(), 2),
            "q_minimo": formatar_decimal(indice.min(), 2),
            "q_maximo": formatar_decimal(indice.max(), 1),
            "nacionalidade_q_maximo": maior["nacionalidade"],
            "vinculos_q_maximo": formatar_inteiro(maior["V_total"]),
            "n_extremos": len(extremos),
            "pct_vinculos_extremos": formatar_percentual(
                extremos["V_total"].sum() / self.perfis["V_total"].sum()
            ),
            "pearson_salario": formatar_decimal(pearson_salario, 3),
            "spearman_salario": formatar_decimal(spearman_salario, 3),
            "spearman_volume": formatar_decimal(spearman_volume, 3),
            "salario_faixa_baixa": formatar_decimal(faixas["salario_mediano"].max(), 3),
            "salario_faixa_alta": formatar_decimal(faixas["salario_mediano"].min(), 3),
            "faixas_salarios": " · ".join(
                formatar_decimal(valor, 3) for valor in faixas["salario_mediano"]
            ),
            "n_faixa_alta": int(faixas["nacionalidades"].iloc[-1]),
            "participacao_faixa_q_alto": formatar_percentual(
                faixas.loc[faixas["faixa"].str.startswith("Q > 1,5"), "participacao_vinculos"].iloc[0]
            ),
        }


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
