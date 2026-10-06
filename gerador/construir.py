"""Gerador do dashboard estático.

Lê os mesmos artefatos que o notebook exporta (o contrato da FASE 9 não muda) e escreve
`docs/index.html`. Toda a camada analítica é reaproveitada:

  nucleo/dados.py       leitura, validação do esquema e valores derivados
  nucleo/graficos*.py   as figuras, por pergunta
  nucleo/textos*.py     a narrativa, por pergunta
  nucleo/formatos.py    formatação numérica brasileira

Cada aba **declara** o seu conteúdo num `Conteudo`, e um único renderizador monta o HTML.
O contrato do desenho aprovado fica implementado uma vez só, o que torna acrescentar a
próxima pergunta uma declaração em vez de código novo.

Uso:
    .venv/bin/python gerador/construir.py
"""

from __future__ import annotations

import sys
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import plotly.graph_objects as go

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from gerador import componentes  # noqa: E402
from nucleo import graficos, graficos_q4, graficos_q6, textos, textos_q4, textos_q6  # noqa: E402
from nucleo.config import (  # noqa: E402
    ABA_Q4,
    ABA_Q6,
    ABA_Q7,
    ABAS,
    COLUNAS_ATRIBUTOS,
    NACIONALIDADES_NA_TABELA,
    ROTULOS_ATRIBUTOS,
)
from nucleo.dados import DadosQ7, carregar, pasta_dados  # noqa: E402
from nucleo.formatos import (  # noqa: E402
    formatar_atributo,
    formatar_decimal,
    formatar_inteiro,
    formatar_percentual,
)

TITULO = "Dashboard analítico • SISMIGRA × RAIS-CTPS"

# `docs/` de propósito: é a pasta que o GitHub Pages sabe publicar (a outra opção é a
# raiz). O HTML sai autossuficiente, com os dados e os gráficos embutidos, então
# publicar o painel é só apontar o Pages para cá.
SAIDA = RAIZ / "docs"

PENDENTE = (
    "Esta aba ainda não foi implementada. O desenho abaixo é o contrato que ela deve "
    "seguir — o mesmo da Q7, que já está pronta e serve de referência."
)

LIMITES_PENDENTES = (
    "resultado sintético",
    "denominador explícito",
    "critério de elegibilidade",
    "cobertura observada",
    "interpretação permitida",
)

ConstrutorDeFigura = Callable[[DadosQ7], go.Figure]
ValoresDaNarrativa = Callable[[DadosQ7], dict[str, object]]


@dataclass(frozen=True)
class Conteudo:
    """O que uma aba declara. Como isso vira HTML é responsabilidade do renderizador."""

    cartoes: tuple[tuple[str, tuple[str, ...]], ...]
    evidencias: tuple[textos.Evidencia, ...]
    figuras: dict[str, ConstrutorDeFigura]
    valores: ValoresDaNarrativa
    rotulo_curto: Callable[[textos.Evidencia], str]
    resposta: str
    indicadores: Callable[[DadosQ7], list[tuple[str, str]]]
    limites: tuple[tuple[str, str], ...]
    ponte: str
    tabela: Callable[[DadosQ7], str] | None = None
    chave_tabela: str = ""


# ---------------------------------------------------------------------------
# Renderizador — implementa o contrato do desenho aprovado uma única vez
# ---------------------------------------------------------------------------


def _cartoes(conteudo: Conteudo) -> str:
    return componentes.linha_de_cartoes(
        tuple(componentes.cartao(titulo, linhas) for titulo, linhas in conteudo.cartoes)
    )


def _corpo_da_evidencia(
    conteudo: Conteudo,
    artefatos: DadosQ7,
    evidencia: textos.Evidencia,
    valores: dict[str, object],
    prefixo: str,
) -> str:
    if conteudo.tabela and evidencia.chave == conteudo.chave_tabela:
        corpo = conteudo.tabela(artefatos)
    else:
        figura = conteudo.figuras[evidencia.chave](artefatos)
        corpo = componentes.grafico(figura, f"fig-{prefixo}{evidencia.chave}")
    return corpo + componentes.leitura(textos.preencher(evidencia.leitura, valores))


def _cartao_de_evidencia(
    conteudo: Conteudo, artefatos: DadosQ7, valores: dict[str, object], prefixo: str
) -> str:
    opcoes = ((item.chave, conteudo.rotulo_curto(item)) for item in conteudo.evidencias)
    blocos = (
        componentes.evidencia(
            item.chave,
            _corpo_da_evidencia(conteudo, artefatos, item, valores, prefixo),
            indice == 0,
            prefixo,
        )
        for indice, item in enumerate(conteudo.evidencias)
    )
    return (
        '<div class="cartao cartao-alto"><div class="titulo-bloco">Evidência principal</div>'
        f"{componentes.seletor_de_evidencia(opcoes, conteudo.evidencias[0].chave)}"
        f"{''.join(blocos)}</div>"
    )


def _cartao_de_resposta(
    conteudo: Conteudo, artefatos: DadosQ7, valores: dict[str, object]
) -> str:
    detalhado = ((rotulo, textos.preencher(texto, valores)) for rotulo, texto in conteudo.limites)
    resposta = componentes.para_html(textos.preencher(conteudo.resposta, valores))
    return (
        '<div class="cartao cartao-alto"><div class="titulo-bloco">Resposta + limites</div>'
        f'<div class="resposta">{resposta}</div>'
        f"{componentes.indicadores(conteudo.indicadores(artefatos))}"
        f"{componentes.lista_de_limites(rotulo for rotulo, _ in conteudo.limites)}"
        f"{componentes.detalhamento(detalhado)}</div>"
    )


def _secao(conteudo: Conteudo, artefatos: DadosQ7, prefixo: str) -> str:
    valores = conteudo.valores(artefatos)
    evidencias = _cartao_de_evidencia(conteudo, artefatos, valores, prefixo)
    resposta = _cartao_de_resposta(conteudo, artefatos, valores)
    ponte = componentes.ponte(
        "Onde isto toca o problema do projeto",
        textos.preencher(conteudo.ponte, valores),
    )
    return (
        f"{_cartoes(conteudo)}"
        f'<div class="linha-principal">{evidencias}{resposta}</div>'
        f"{ponte}"
    )


# ---------------------------------------------------------------------------
# Q7 — Análise multivariada
# ---------------------------------------------------------------------------


def _tabela_q7(artefatos: DadosQ7) -> str:
    ordenada = (
        artefatos.perfis.sort_values("Q_medio", ascending=False).head(NACIONALIDADES_NA_TABELA)
    )
    cabecalhos = (
        "Nacionalidade",
        "Região",
        "Q",
        "Vínculos",
        *(ROTULOS_ATRIBUTOS[coluna] for coluna in COLUNAS_ATRIBUTOS),
    )
    linhas = [
        (
            linha["nacionalidade"],
            f"{int(linha['regiao'])}",
            formatar_decimal(linha["Q_medio"], 2),
            formatar_inteiro(linha["V_total"]),
            *(formatar_atributo(coluna, linha[coluna]) for coluna in COLUNAS_ATRIBUTOS),
        )
        for _, linha in ordenada.iterrows()
    ]
    return componentes.tabela(cabecalhos, linhas)


def _indicadores_q7(artefatos: DadosQ7) -> list[tuple[str, str]]:
    resumo = graficos.resumo_numerico(artefatos)
    return [
        ("Regiões", resumo["Regiões"]),
        ("Silhueta", resumo["Silhueta no k escolhido"]),
        ("KMeans × Ward", resumo["KMeans × Ward"]),
        ("Estabilidade", resumo["Estabilidade (média)"] + " de média"),
    ]


def _conteudo_q7(artefatos: DadosQ7) -> Conteudo:
    inicio, fim = artefatos.configuracao["janela"]
    return Conteudo(
        cartoes=(
            (
                "Cobertura",
                (
                    "RAIS-CTPS (estoque em 31/12) · SISMIGRA-ATIVOS (dezembro)",
                    f"Anos: {inicio}–{fim} — janela fixa",
                    "Variáveis: índice Q + 6 atributos de perfil",
                ),
            ),
            (
                "Filtros",
                (
                    f"Ano: fixo em {inicio}–{fim}",
                    f"Nacionalidade: as {artefatos.n_elegiveis} elegíveis",
                    "Top N: só no tamanho da tabela",
                ),
            ),
            (
                "Nota metodológica",
                (
                    "Unidade: nacionalidade — nunca indivíduo",
                    f"Cobertura: {artefatos.n_elegiveis} de {artefatos.n_universo} comparáveis",
                    "Interpretação: gradiente associativo, não causal",
                ),
            ),
        ),
        evidencias=textos.EVIDENCIAS,
        figuras={
            "gradiente": graficos.dispersao_pca,
            "cargas": graficos.cargas_pca,
            "regioes": graficos.mapa_regioes,
            "composicao": graficos.composicao_regioes,
            "regra_k": graficos.diagnostico_k,
            "estabilidade": graficos.estabilidade_por_k,
            "arvores": graficos.arvores_comparacao,
        },
        valores=lambda dados: dados.valores_para_texto(),
        rotulo_curto=textos.rotulo_curto,
        resposta=textos.RESPOSTA_SINTETICA,
        indicadores=_indicadores_q7,
        limites=(
            ("Denominador", textos.DENOMINADOR_EXPLICITO),
            ("Critério de elegibilidade", textos.CRITERIO_ELEGIBILIDADE),
            ("Cobertura observada", textos.COBERTURA_OBSERVADA),
            ("Interpretação permitida", textos.INTERPRETACAO_PERMITIDA),
            ("Interpretação não permitida", textos.INTERPRETACAO_PROIBIDA),
        ),
        ponte=textos.RESPOSTA_ANCORADA_NO_PROBLEMA,
        tabela=_tabela_q7,
        chave_tabela="quem",
    )


# ---------------------------------------------------------------------------
# Q4 — Representação: o índice Q
# ---------------------------------------------------------------------------


def _tabela_q4(artefatos: DadosQ7) -> str:
    faixas = artefatos.faixas_de_q()
    cabecalhos = (
        "Faixa de Q",
        "Nacionalidades",
        "Salário mediano",
        "Superior completo",
        "Vínculos na janela",
        "Participação",
    )
    linhas = [
        (
            linha["faixa"],
            formatar_inteiro(linha["nacionalidades"]),
            formatar_decimal(linha["salario_mediano"], 3) + " SM",
            formatar_percentual(linha["superior_completo"]),
            formatar_inteiro(linha["vinculos"]),
            formatar_percentual(linha["participacao_vinculos"]),
        )
        for _, linha in faixas.iterrows()
    ]
    return componentes.tabela(cabecalhos, linhas)


def _indicadores_q4(artefatos: DadosQ7) -> list[tuple[str, str]]:
    valores = artefatos.valores_q4_para_texto()
    return [
        ("Nacionalidades com Q > 1", f"{valores['n_acima_1']} de {valores['n_elegiveis']}"),
        ("Mediana do índice", str(valores["q_mediana"])),
        ("Spearman(Q, remuneração)", str(valores["spearman_salario"])),
        (
            "Extremos (Q > 5)",
            f"{valores['n_extremos']} casos · {valores['pct_vinculos_extremos']} dos vínculos",
        ),
    ]


def _conteudo_q4(artefatos: DadosQ7) -> Conteudo:
    inicio, fim = artefatos.configuracao["janela"]
    return Conteudo(
        cartoes=(
            (
                "Cobertura",
                (
                    "RAIS-CTPS (vínculos) e SISMIGRA-ATIVOS (registros), dezembro de cada ano",
                    f"Anos: {inicio}–{fim} — janela fixa",
                    "Variável: índice Q por nacionalidade",
                ),
            ),
            (
                "Filtros",
                (
                    f"Ano: fixo em {inicio}–{fim} (a leitura por ano é da Q5)",
                    f"Nacionalidade: as {artefatos.n_elegiveis} com Q definido e volume mínimo",
                    "Top N: só no tamanho da tabela",
                ),
            ),
            (
                "Nota metodológica",
                (
                    "Q = participação nos vínculos ÷ participação nos registros",
                    "Denominadores com conceitos de UF distintos",
                    "Associação descritiva — não mede integração",
                ),
            ),
        ),
        evidencias=textos_q4.EVIDENCIAS,
        figuras={
            "distribuicao": graficos_q4.distribuicao_q,
            "cauda": graficos_q4.q_versus_volume,
            "remuneracao": graficos_q4.q_versus_remuneracao,
        },
        valores=lambda dados: dados.valores_q4_para_texto(),
        rotulo_curto=textos_q4.rotulo_curto,
        resposta=textos_q4.RESPOSTA_SINTETICA,
        indicadores=_indicadores_q4,
        limites=textos_q4.LIMITES,
        ponte=textos_q4.PONTE,
        tabela=_tabela_q4,
        chave_tabela="faixas",
    )


# ---------------------------------------------------------------------------
# Q6 — Perfil dos vínculos formais
# ---------------------------------------------------------------------------


def _tabela_q6(artefatos: DadosQ7) -> str:
    ordenada = artefatos.perfis.sort_values("salario_medio_sm", ascending=False)
    cabecalhos = (
        "Nacionalidade",
        *(ROTULOS_ATRIBUTOS[coluna] for coluna in COLUNAS_ATRIBUTOS),
        "Vínculos",
    )
    linhas = [
        (
            linha["nacionalidade"],
            *(formatar_atributo(coluna, linha[coluna]) for coluna in COLUNAS_ATRIBUTOS),
            formatar_inteiro(linha["V_total"]),
        )
        for _, linha in ordenada.iterrows()
    ]
    return componentes.tabela(cabecalhos, linhas)


def _indicadores_q6(artefatos: DadosQ7) -> list[tuple[str, str]]:
    valores = artefatos.valores_q6_para_texto()
    total = valores["n_atributos"]
    return [
        ("Atributos observados", f"{total} de {total}"),
        ("Nacionalidades com perfil completo", str(valores["n_elegiveis"])),
        (
            "Associação mais forte",
            f"{valores['associacao_salario_superior']} (remuneração × escolaridade)",
        ),
        ("Atributo mais isolado", f"concentração setorial · {valores['isolamento_hhi']}"),
    ]


def _conteudo_q6(artefatos: DadosQ7) -> Conteudo:
    inicio, fim = artefatos.configuracao["janela"]
    total_de_atributos = len(COLUNAS_ATRIBUTOS)
    return Conteudo(
        cartoes=(
            (
                "Cobertura",
                (
                    "RAIS-CTPS (estoque em 31/12) — atributo do vínculo, não da pessoa",
                    f"Anos: {inicio}–{fim} — janela fixa, sem leitura de trajetória",
                    f"Variáveis: {total_de_atributos} atributos de perfil",
                ),
            ),
            (
                "Filtros",
                (
                    f"Ano: fixo em {inicio}–{fim}",
                    f"Nacionalidade: as {artefatos.n_elegiveis} com os seis atributos observados",
                    f"Tabela: as {artefatos.n_elegiveis} elegíveis, sem corte",
                ),
            ),
            (
                "Nota metodológica",
                (
                    "Unidade: nacionalidade — nunca indivíduo",
                    f"Cobertura: {total_de_atributos} de {total_de_atributos} atributos "
                    f"para as {artefatos.n_elegiveis}",
                    "Associação descritiva — não mede efeito de qualificação",
                ),
            ),
        ),
        evidencias=textos_q6.EVIDENCIAS,
        figuras={
            "perfil": graficos_q6.perfil_dos_atributos,
            "acoplamento": graficos_q6.associacao_entre_atributos,
            "remuneracao": graficos_q6.remuneracao_versus_qualificacao,
        },
        valores=lambda dados: dados.valores_q6_para_texto(),
        rotulo_curto=textos_q6.rotulo_curto,
        resposta=textos_q6.RESPOSTA_SINTETICA,
        indicadores=_indicadores_q6,
        limites=textos_q6.LIMITES,
        ponte=textos_q6.PONTE,
        tabela=_tabela_q6,
        chave_tabela="nacionalidades",
    )


# As abas que já declaram conteúdo. A validação deriva daqui o que esperar do HTML, em
# vez de manter uma contagem paralela que envelhece em silêncio.
CONTEUDO_POR_ABA: dict[str, Callable[[DadosQ7], Conteudo]] = {
    ABA_Q7: _conteudo_q7,
    ABA_Q4: _conteudo_q4,
    ABA_Q6: _conteudo_q6,
}


def _secao_pendente(aba: str) -> str:
    cartoes = componentes.linha_de_cartoes(
        tuple(
            componentes.cartao(titulo, (texto,))
            for titulo, texto in (
                ("Cobertura", "fontes · anos · variáveis"),
                ("Filtros", "ano · nacionalidade · Top N"),
                ("Nota metodológica", "unidade · cobertura · interpretação"),
            )
        )
    )
    evidencia = (
        '<div class="cartao cartao-alto"><div class="titulo-bloco">Evidência principal</div>'
        '<div class="linha">A figura da resposta vai aqui — uma por aba.</div></div>'
    )
    resposta = (
        '<div class="cartao cartao-alto"><div class="titulo-bloco">Resposta + limites</div>'
        f"{componentes.lista_de_limites(LIMITES_PENDENTES)}</div>"
    )
    return (
        f"{componentes.aviso(f'**{aba}** — {PENDENTE}')}"
        f"{cartoes}"
        f'<div class="linha-principal">{evidencia}{resposta}</div>'
    )


def _slug(nome: str) -> str:
    """Identificador de aba para a URL: 'Q7 Multivariado' -> 'q7-multivariado'."""
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return "-".join(sem_acento.lower().replace("&", " ").split())


def _marcador(conteudo: str, slug: str, ativa: bool) -> str:
    classe = "secao ativa" if ativa else "secao"
    return f'<section class="{classe}" id="secao-{slug}">{conteudo}</section>'


def construir(destino: Path = SAIDA / "index.html") -> Path:
    """Gera o dashboard completo em um único arquivo."""
    artefatos = carregar()
    identificadas = [(_slug(aba), aba) for aba in ABAS]
    secoes = [
        _marcador(
            _secao(CONTEUDO_POR_ABA[nome](artefatos), artefatos, f"{slug}-")
            if nome in CONTEUDO_POR_ABA
            else _secao_pendente(nome),
            slug,
            indice == 0,
        )
        for indice, (slug, nome) in enumerate(identificadas)
    ]
    html = componentes.pagina(
        TITULO,
        componentes.navegacao(identificadas, identificadas[0][0]),
        secoes,
        componentes.rodape_pisos(),
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")
    return destino


def main() -> int:
    try:
        destino = construir()
    except FileNotFoundError as erro:
        print(f"não há artefatos em {pasta_dados()}.\n{erro}")
        return 1
    tamanho = destino.stat().st_size / 1024
    print(f"gerado: {destino} ({tamanho:,.0f} KB)")
    print(f"artefatos: {pasta_dados()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
