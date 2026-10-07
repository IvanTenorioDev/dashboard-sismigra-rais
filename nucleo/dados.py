"""Leitura dos artefatos exportados pelo notebook (FASE 9 e FASE 9b).

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
    ABAS,
    ARQUIVOS,
    COLUNAS_ATRIBUTOS,
    NACIONALIDADES_NA_TABELA,
    PISO_REGISTROS,
    PISO_VINCULOS,
    ROTULOS_ATRIBUTOS,
    pasta_dados,
)
from nucleo.formatos import formatar_decimal, formatar_inteiro, formatar_percentual

INSTRUCAO_GERACAO = (
    "Execute as FASES 9 e 9b do notebook Integrador_Base_Unificada_REV1.ipynb no Colab "
    "e copie os arquivos gerados para 'dados/q7/' neste projeto."
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
    "serie_anual": (
        "ano",
        "nacionalidade",
        "registros_ativos",
        "registros_no_ano",
        "vinculos_formais",
        "Q",
    ),
    "resumo_anual": (
        "ano",
        "registros_ativos",
        "registros_no_ano",
        "vinculos_formais",
        "nacionalidades_com_registros",
        "nacionalidades_com_vinculos",
        "razao_vinculos_por_registros",
    ),
    "uf_ano": ("ano", "uf", "vinculos_formais", "registros_ativos"),
    "concentracao_territorial": (
        "ano",
        "nacionalidade",
        "hhi_uf_registros",
        "uf_registros_dominante",
        "participacao_uf_registros_dominante",
        "hhi_uf_rais",
        "uf_rais_dominante",
        "participacao_uf_rais_dominante",
    ),
    "uf_top": ("ano", "uf", "posicao", "nacionalidade", "registros_ativos"),
    "fluxo": (
        "ano",
        "registros_no_ano",
        "nacionalidades",
        "registros_com_tipologia",
        "pct_acolhida",
        "pct_trabalho",
        "pct_feminino",
    ),
    "persistencia": (
        "nacionalidade",
        "anos_com_vinculos",
        "primeiro_ano_vinculos",
        "ultimo_ano_vinculos",
        "vinculos_formais_no_ultimo_ano",
        "anos_com_registros",
        "primeiro_ano_registros",
        "ultimo_ano_registros",
        "registros_ativos_no_ultimo_ano",
    ),
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
class Artefatos:
    """Todos os artefatos que o notebook exporta, em todos os grãos."""

    configuracao: dict[str, object]
    perfis: pd.DataFrame
    pca: pd.DataFrame
    cargas: pd.DataFrame
    variancia: pd.DataFrame
    diagnostico: pd.DataFrame
    regioes: pd.DataFrame
    arvores: pd.DataFrame
    serie_anual: pd.DataFrame
    resumo_anual: pd.DataFrame
    uf_ano: pd.DataFrame
    concentracao_territorial: pd.DataFrame
    uf_top: pd.DataFrame
    fluxo: pd.DataFrame
    persistencia: pd.DataFrame

    @property
    def k_escolhido(self) -> int:
        return int(self.configuracao["k_escolhido"])

    @property
    def n_elegiveis(self) -> int:
        return int(self.configuracao["elegiveis"])

    @property
    def n_universo(self) -> int:
        return int(self.configuracao["universo_com_Q_comparavel"])

    @property
    def janela_dos_perfis(self) -> tuple[int, int]:
        """Janela fixa dos perfis, como intervalo fechado de anos."""
        anos = self._lista_de_anos("janela")
        return min(anos), max(anos)

    def regiao_do_k(self) -> pd.Series:
        """Linha do diagnóstico correspondente ao k escolhido."""
        return self.diagnostico.loc[self.diagnostico["k"].eq(self.k_escolhido)].iloc[0]

    def tem(self, chave: str, coluna: str) -> bool:
        """Indica se um campo opcional está presente nos artefatos carregados."""
        return coluna in getattr(self, chave).columns

    def _cobertura_do_estoque(self) -> tuple[int, int]:
        """Primeiro e último ano civil com instantâneo de dezembro do SISMIGRA."""
        cobertura = self.configuracao.get("cobertura_estoque_sismigra")
        if not isinstance(cobertura, list) or len(cobertura) != 2:
            raise ValueError(
                "configuracao['cobertura_estoque_sismigra'] deveria ser "
                f"[ano_inicial, ano_final]; recebido {cobertura!r}. Rode a FASE 9 de novo."
            )
        return int(cobertura[0]), int(cobertura[1])

    def anos_incompletos(self) -> frozenset[int]:
        """Anos que a extração pegou em curso, e que não se comparam aos fechados.

        Um ano em curso tem menos meses que os outros, então uma série que o inclui cai
        no fim por razão de calendário, não de comportamento. A leitura usa o campo
        declarado pelo notebook quando ele existe; sem ele, deriva do fim da cobertura
        do estoque de dezembro — um instantâneo anual que para em 2025 só existe se a
        extração foi feita antes de dezembro de 2026.
        """
        declarado = self.configuracao.get("anos_incompletos")
        if isinstance(declarado, list):
            return frozenset(int(ano) for ano in declarado)
        _, ultimo_fechado = self._cobertura_do_estoque()
        ultimo_presente = max(int(self.fluxo["ano"].max()), ultimo_fechado)
        return frozenset(range(ultimo_fechado + 1, ultimo_presente + 1))

    def ano_com_os_dois_lados(self) -> int:
        """Último ano em que território tem estoque e vínculo na mesma linha.

        É o ano da leitura territorial: comparar participações de UF exige os dois lados,
        e o estoque do SISMIGRA não existe antes de 2022.
        """
        completos = self.uf_ano.dropna(subset=["registros_ativos", "vinculos_formais"])
        return int(completos["ano"].max())

    def concentracao_com_volume(self) -> pd.DataFrame:
        """HHI territorial por nacionalidade e ano, junto do volume que o sustenta.

        O HHI de uma nacionalidade com um único registro é 1 por construção. Sem o volume
        ao lado não há como separar concentração real de amostra de tamanho um — e é
        exatamente essa separação que decide quem entra na distribuição.
        """
        colunas = ("ano", "nacionalidade", "registros_ativos", "vinculos_formais")
        return self.concentracao_territorial.merge(
            self.serie_anual[[*colunas]], on=["ano", "nacionalidade"], how="left"
        )

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
            "q_maximo": formatar_decimal(indice.max(), 2),
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
    def associacao_de_atributos(self) -> pd.DataFrame:
        """Matriz de associação de postos entre os seis atributos de perfil.

        Postos e não Pearson pela mesma razão da Q4: `salario_medio_sm` tem cauda
        pesada (mediana de 1,74 SM e máximo acima de 36 SM), e uma única observação
        dessas dominaria o coeficiente linear.
        """
        return self.perfis[list(COLUNAS_ATRIBUTOS)].rank().corr()

    def resumo_dos_atributos(self) -> pd.DataFrame:
        """Distribuição de cada atributo entre as nacionalidades elegíveis."""
        linhas = []
        for coluna in COLUNAS_ATRIBUTOS:
            serie = self.perfis[coluna]
            linhas.append({
                "atributo": coluna,
                "rotulo": ROTULOS_ATRIBUTOS[coluna],
                "minimo": serie.min(),
                "primeiro_quartil": serie.quantile(0.25),
                "mediana": serie.median(),
                "terceiro_quartil": serie.quantile(0.75),
                "maximo": serie.max(),
            })
        return pd.DataFrame(linhas)

    def valores_q6_para_texto(self) -> dict[str, object]:
        """Números da Q6: dispersão e associação dos seis atributos de perfil."""
        resumo = self.resumo_dos_atributos().set_index("atributo")
        associacao = self.associacao_de_atributos()
        salario = resumo.loc["salario_medio_sm"]
        mediana_salario = float(salario["mediana"])
        razao_salario_maximo = float(salario["maximo"]) / mediana_salario
        maior_salario = self.perfis.loc[self.perfis["salario_medio_sm"].idxmax()]
        maior_parcial = self.perfis.loc[self.perfis["pct_tempo_parcial"].idxmax()]
        maior_hhi = self.perfis.loc[self.perfis["hhi_setorial"].idxmax()]
        isolamento_hhi = max(
            abs(float(associacao.loc["hhi_setorial", outra]))
            for outra in COLUNAS_ATRIBUTOS
            if outra != "hhi_setorial"
        )
        return {
            "n_elegiveis": self.n_elegiveis,
            "n_atributos": len(COLUNAS_ATRIBUTOS),
            "salario_mediano": formatar_decimal(mediana_salario, 3),
            "salario_minimo": formatar_decimal(float(salario["minimo"]), 3),
            "salario_maximo": formatar_decimal(float(salario["maximo"]), 3),
            "razao_salario_maximo": formatar_decimal(razao_salario_maximo, 1),
            "nacionalidade_salario_maximo": maior_salario["nacionalidade"],
            "superior_mediano": formatar_percentual(float(resumo.loc["pct_superior", "mediana"])),
            "superior_minimo": formatar_percentual(float(resumo.loc["pct_superior", "minimo"])),
            "superior_maximo": formatar_percentual(float(resumo.loc["pct_superior", "maximo"])),
            "mulheres_mediano": formatar_percentual(float(resumo.loc["pct_feminino", "mediana"])),
            "faixa_25_39_mediano": formatar_percentual(
                float(resumo.loc["pct_faixa_25_39", "mediana"])
            ),
            "parcial_mediano": formatar_percentual(
                float(resumo.loc["pct_tempo_parcial", "mediana"])
            ),
            "parcial_maximo": formatar_percentual(
                float(resumo.loc["pct_tempo_parcial", "maximo"])
            ),
            "nacionalidade_parcial_maximo": maior_parcial["nacionalidade"],
            "hhi_mediano": formatar_decimal(float(resumo.loc["hhi_setorial", "mediana"]), 3),
            "hhi_maximo": formatar_decimal(float(resumo.loc["hhi_setorial", "maximo"]), 3),
            "nacionalidade_hhi_maximo": maior_hhi["nacionalidade"],
            "associacao_salario_superior": formatar_decimal(
                float(associacao.loc["salario_medio_sm", "pct_superior"]), 2
            ),
            "isolamento_hhi": formatar_decimal(isolamento_hhi, 2),
        }

    def valores_q1_para_texto(self) -> dict[str, object]:
        """Números da Q1: a evolução dos dois lados da presença e da razão entre eles."""
        resumo = self.resumo_anual.sort_values("ano").reset_index(drop=True)
        vinculos = resumo.dropna(subset=["vinculos_formais"])
        estoque = resumo.dropna(subset=["registros_ativos"])
        razao = resumo.dropna(subset=["razao_vinculos_por_registros"])
        primeiro, ultimo = vinculos.iloc[0], vinculos.iloc[-1]
        ano_da_queda = vinculos.loc[vinculos["vinculos_formais"].diff().idxmin()]
        ano_anterior = vinculos.loc[vinculos["ano"].eq(ano_da_queda["ano"] - 1)].iloc[0]
        return {
            "primeiro_ano_vinculos": int(primeiro["ano"]),
            "ultimo_ano_vinculos": int(ultimo["ano"]),
            "vinculos_primeiro": formatar_inteiro(primeiro["vinculos_formais"]),
            "vinculos_ultimo": formatar_inteiro(ultimo["vinculos_formais"]),
            "crescimento_vinculos": formatar_percentual(
                ultimo["vinculos_formais"] / primeiro["vinculos_formais"] - 1
            ),
            "nacionalidades_primeiro": formatar_inteiro(
                primeiro["nacionalidades_com_vinculos"]
            ),
            "nacionalidades_ultimo": formatar_inteiro(ultimo["nacionalidades_com_vinculos"]),
            "primeiro_ano_estoque": int(estoque["ano"].min()),
            "ultimo_ano_estoque": int(estoque["ano"].max()),
            "n_anos_estoque": len(estoque),
            "registros_primeiro": formatar_inteiro(estoque["registros_ativos"].iloc[0]),
            "registros_ultimo": formatar_inteiro(estoque["registros_ativos"].iloc[-1]),
            "crescimento_registros": formatar_percentual(
                estoque["registros_ativos"].iloc[-1]
                / estoque["registros_ativos"].iloc[0]
                - 1
            ),
            "razao_primeira": formatar_percentual(razao["razao_vinculos_por_registros"].iloc[0]),
            "razao_ultima": formatar_percentual(razao["razao_vinculos_por_registros"].iloc[-1]),
            "razao_variacao": formatar_percentual(
                razao["razao_vinculos_por_registros"].iloc[-1]
                / razao["razao_vinculos_por_registros"].iloc[0]
                - 1
            ),
            "ano_da_queda": int(ano_da_queda["ano"]),
            "queda_vinculos": formatar_percentual(
                1 - ano_da_queda["vinculos_formais"] / ano_anterior["vinculos_formais"]
            ),
        }

    def valores_q2_para_texto(self) -> dict[str, object]:
        """Números da Q2: concentração territorial nos dois conceitos de UF."""
        ano = self.ano_com_os_dois_lados()
        tabela = self.uf_ano.loc[self.uf_ano["ano"].eq(ano)].copy()
        total_registros = float(tabela["registros_ativos"].sum())
        total_vinculos = float(tabela["vinculos_formais"].sum())
        tabela["pct_registros"] = tabela["registros_ativos"] / total_registros
        tabela["pct_vinculos"] = tabela["vinculos_formais"] / total_vinculos
        tabela["razao"] = tabela["registros_ativos"] / tabela["vinculos_formais"]
        mais_registros = tabela.loc[tabela["pct_registros"].idxmax()]
        mais_vinculos = tabela.loc[tabela["pct_vinculos"].idxmax()]
        concentradas = self.concentracao_com_volume()
        no_ano = concentradas.loc[concentradas["ano"].eq(ano)].dropna(
            subset=["hhi_uf_registros"]
        )
        sustentadas = no_ano.loc[no_ano["registros_ativos"].ge(PISO_REGISTROS)]
        primeiras = self.uf_top.loc[
            self.uf_top["ano"].eq(ano) & self.uf_top["posicao"].eq(1)
        ].set_index("uf")["registros_ativos"]
        peso_da_primeira = (
            primeiras / tabela.set_index("uf")["registros_ativos"]
        ).dropna()
        return {
            "uf_primeira_mais_pesada": peso_da_primeira.idxmax(),
            "peso_primeira_maximo": formatar_percentual(peso_da_primeira.max()),
            "uf_primeira_mais_diluida": peso_da_primeira.idxmin(),
            "peso_primeira_minimo": formatar_percentual(peso_da_primeira.min()),
            "ano_territorio": ano,
            "n_ufs": len(tabela),
            "uf_mais_registros": mais_registros["uf"],
            "pct_registros_uf_maior": formatar_percentual(mais_registros["pct_registros"]),
            "pct_vinculos_da_uf_maior": formatar_percentual(mais_registros["pct_vinculos"]),
            "uf_mais_vinculos": mais_vinculos["uf"],
            "pct_vinculos_uf_maior": formatar_percentual(mais_vinculos["pct_vinculos"]),
            "pct_registros_da_uf_com_mais_vinculos": formatar_percentual(
                mais_vinculos["pct_registros"]
            ),
            "top3_registros": formatar_percentual(tabela["pct_registros"].nlargest(3).sum()),
            "uf_razao_maior": tabela.loc[tabela["razao"].idxmax(), "uf"],
            "razao_maior": formatar_decimal(tabela["razao"].max(), 1),
            "uf_razao_menor": tabela.loc[tabela["razao"].idxmin(), "uf"],
            "razao_menor": formatar_decimal(tabela["razao"].min(), 1),
            "razao_pais": formatar_decimal(total_registros / total_vinculos, 1),
            "hhi_mediano": formatar_decimal(sustentadas["hhi_uf_registros"].median(), 2),
            "hhi_minimo": formatar_decimal(sustentadas["hhi_uf_registros"].min(), 2),
            "hhi_maximo": formatar_decimal(sustentadas["hhi_uf_registros"].max(), 2),
            "n_sustentadas": len(sustentadas),
            "n_no_ano": len(no_ano),
            "n_removidas": len(no_ano) - len(sustentadas),
            "piso_registros": formatar_inteiro(PISO_REGISTROS),
        }

    def valores_q3_para_texto(self) -> dict[str, object]:
        """Números da Q3: o fluxo anual e a composição por tipo de amparo."""
        fluxo = self.fluxo.sort_values("ano").reset_index(drop=True)
        incompletos = self.anos_incompletos()
        fechados = fluxo.loc[~fluxo["ano"].isin(incompletos)].reset_index(drop=True)
        mais_registros = fechados.loc[fechados["registros_no_ano"].idxmax()]
        queda = fechados.loc[fechados["registros_no_ano"].diff().idxmin()]
        ano_anterior = fechados.loc[fechados["ano"].eq(queda["ano"] - 1)].iloc[0]
        amparo = fluxo.dropna(subset=["pct_acolhida"])
        com_amparo = amparo.loc[~amparo["ano"].isin(incompletos)]
        abertura, fecho = com_amparo.iloc[0], com_amparo.iloc[-1]
        pico_acolhida = amparo.loc[amparo["pct_acolhida"].idxmax()]
        anos = {int(ano) for ano in fluxo["ano"]}
        lacunas = sorted(set(range(min(anos), max(anos) + 1)) - anos)
        return {
            "primeiro_ano_fluxo": int(fluxo["ano"].min()),
            "ultimo_ano_fluxo": int(fluxo["ano"].max()),
            "registros_primeiro": formatar_inteiro(fluxo["registros_no_ano"].iloc[0]),
            "registros_ultimo_fechado": formatar_inteiro(fecho["registros_no_ano"]),
            "crescimento_fluxo": formatar_percentual(
                fecho["registros_no_ano"] / fluxo["registros_no_ano"].iloc[0] - 1
            ),
            "maior_ano": int(mais_registros["ano"]),
            "maior_registros": formatar_inteiro(mais_registros["registros_no_ano"]),
            "queda_ano": int(queda["ano"]),
            "queda_percentual": formatar_percentual(
                1 - queda["registros_no_ano"] / ano_anterior["registros_no_ano"]
            ),
            "queda_ano_anterior": int(ano_anterior["ano"]),
            "lacunas": " e ".join(str(ano) for ano in lacunas),
            "n_lacunas": len(lacunas),
            "nacionalidades_primeiro": formatar_inteiro(fluxo["nacionalidades"].iloc[0]),
            "nacionalidades_pico": formatar_inteiro(fluxo["nacionalidades"].max()),
            "pct_feminino_primeiro": formatar_percentual(float(fluxo["pct_feminino"].iloc[0])),
            "pct_feminino_ultimo": formatar_percentual(
                float(fecho["pct_feminino"])
            ),
            "primeiro_ano_amparo": int(abertura["ano"]),
            "ultimo_ano_amparo": int(fecho["ano"]),
            "pct_acolhida_primeiro": formatar_percentual(float(abertura["pct_acolhida"])),
            "pct_acolhida_ultimo": formatar_percentual(float(fecho["pct_acolhida"])),
            "pct_trabalho_primeiro": formatar_percentual(float(abertura["pct_trabalho"])),
            "pct_trabalho_ultimo": formatar_percentual(float(fecho["pct_trabalho"])),
            "pico_acolhida_ano": int(pico_acolhida["ano"]),
            "pico_acolhida": formatar_percentual(float(pico_acolhida["pct_acolhida"])),
            "ano_em_curso": " e ".join(str(ano) for ano in sorted(incompletos)),
        }

    def valores_q5_para_texto(self) -> dict[str, object]:
        """Números da Q5: quantos anos de presença cada nacionalidade sustenta."""
        persistencia = self.persistencia.assign(
            intervalo=(
                self.persistencia["ultimo_ano_vinculos"]
                - self.persistencia["primeiro_ano_vinculos"]
                + 1
            )
        )
        com_volume = persistencia.loc[
            persistencia["registros_ativos_no_ultimo_ano"].ge(PISO_REGISTROS)
        ]
        maximo = int(persistencia["anos_com_vinculos"].max())
        completas = persistencia.loc[persistencia["anos_com_vinculos"].eq(maximo)]
        curtas = persistencia.loc[persistencia["anos_com_vinculos"].le(3)]
        com_lacuna = persistencia.loc[
            persistencia["intervalo"].gt(persistencia["anos_com_vinculos"])
        ]
        return {
            "n_total": len(persistencia),
            "n_sustentadas": len(com_volume),
            "n_removidas": len(persistencia) - len(com_volume),
            "piso_registros": formatar_inteiro(PISO_REGISTROS),
            "maximo_anos": maximo,
            "n_completas": len(completas),
            "pct_completas": formatar_percentual(len(completas) / len(persistencia)),
            "mediana_anos": formatar_decimal(persistencia["anos_com_vinculos"].median(), 0),
            "n_curtas": len(curtas),
            "n_curtas_sustentadas": int(
                curtas["registros_ativos_no_ultimo_ano"].ge(PISO_REGISTROS).sum()
            ),
            "maior_volume_curtas": formatar_inteiro(
                curtas["registros_ativos_no_ultimo_ano"].max()
            ),
            "n_com_lacuna": len(com_lacuna),
            "pct_com_lacuna": formatar_percentual(len(com_lacuna) / len(persistencia)),
            "primeiro_ano": int(persistencia["primeiro_ano_vinculos"].min()),
            "ultimo_ano": int(persistencia["ultimo_ano_vinculos"].max()),
        }

    def _lista_de_anos(self, chave: str) -> list[int]:
        """Lista de anos declarada no config, com erro explícito quando malformada."""
        valor = self.configuracao.get(chave)
        if not isinstance(valor, list):
            raise ValueError(
                f"configuracao['{chave}'] deveria ser uma lista de anos; recebido {valor!r}. "
                f"Rode a FASE 9 de novo."
            )
        return [int(ano) for ano in valor]

    def valores_metodo_para_texto(self) -> dict[str, object]:
        """Números da aba Método: as coberturas e o funil, em valores desta execução.

        A aba não depende de nenhum artefato novo — só do config e das duas séries que já
        sustentam a Q1 e a Q3. Ela existe para que as decisões fiquem num lugar só, com os
        números ao lado, em vez de espalhadas pelos limites de cada pergunta.
        """
        vinculos = self.resumo_anual.dropna(subset=["vinculos_formais"])
        fluxo = self.fluxo.dropna(subset=["registros_no_ano"])
        inicio_estoque, fim_estoque = self._cobertura_do_estoque()
        janela = self._lista_de_anos("janela")
        amparo = sorted(self._lista_de_anos("anos_com_tipologia_de_amparo"))
        anos_do_fluxo = {int(ano) for ano in fluxo["ano"]}
        lacunas = sorted(
            set(range(min(anos_do_fluxo), max(anos_do_fluxo) + 1)) - anos_do_fluxo
        )
        return {
            "n_na_janela": formatar_inteiro(self.configuracao["n_nacionalidades_na_janela"]),
            "n_com_q": formatar_inteiro(self.configuracao["universo_com_Q_comparavel"]),
            "n_com_atributos": formatar_inteiro(self.configuracao["com_os_6_atributos"]),
            "n_elegiveis": formatar_inteiro(self.n_elegiveis),
            "n_categorias_excluidas": formatar_inteiro(
                self.configuracao["categorias_nao_nacionais_excluidas"]
            ),
            "piso_vinculos": formatar_inteiro(PISO_VINCULOS),
            "piso_registros": formatar_inteiro(PISO_REGISTROS),
            "primeiro_ano_vinculos": int(vinculos["ano"].min()),
            "ultimo_ano_vinculos": int(vinculos["ano"].max()),
            "inicio_estoque": inicio_estoque,
            "fim_estoque": fim_estoque,
            "primeiro_ano_fluxo": int(fluxo["ano"].min()),
            "ultimo_ano_fluxo": int(fluxo["ano"].max()),
            "primeiro_ano_amparo": amparo[0],
            "ultimo_ano_amparo": amparo[-1],
            "lacunas_do_fluxo": " e ".join(str(ano) for ano in lacunas),
            "ano_em_curso": ", ".join(str(ano) for ano in sorted(self.anos_incompletos())),
            "janela_inicio": min(janela),
            "janela_fim": max(janela),
            "n_atributos": len(COLUNAS_ATRIBUTOS),
            "k_escolhido": self.k_escolhido,
            "acordo_minimo": formatar_decimal(
                self.configuracao["acordo_minimo_kmeans_ward"], 1
            ),
            "minimo_por_grupo": int(self.configuracao["minimo_nacionalidades_por_grupo"]),
            "semente": int(self.configuracao["semente"]),
            "repeticoes": int(self.configuracao["repeticoes_reamostragem"]),
            "n_artefatos": len(ARQUIVOS),
            "n_abas_de_resultado": len(ABAS) - 1,
        }


def artefatos_faltantes(pasta: Path | None = None) -> list[str]:
    """Lista os artefatos ainda ausentes, para a tela de aviso."""
    destino = pasta or pasta_dados()
    return [nome for nome in ARQUIVOS.values() if not (destino / nome).exists()]


def _caminho_existente(pasta: Path, chave: str) -> Path:
    caminho = pasta / ARQUIVOS[chave]
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
            f"{ARQUIVOS[chave]} sem as colunas obrigatórias: {ausentes}. "
            f"Rode as FASES 9 e 9b novamente: o esquema do artefato mudou."
        )
    return tabela


def carregar(pasta: Path | None = None) -> Artefatos:
    """Carrega e valida todos os artefatos exportados pelo notebook."""
    destino = pasta or pasta_dados()
    configuracao = json.loads(
        _caminho_existente(destino, "configuracao").read_text(encoding="utf-8")
    )
    tabelas = {chave: _ler_tabela(destino, chave) for chave in COLUNAS_OBRIGATORIAS}
    return Artefatos(configuracao=configuracao, **tabelas)
