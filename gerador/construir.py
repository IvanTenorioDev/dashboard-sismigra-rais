"""Gerador do dashboard estático.

Lê os mesmos artefatos que o notebook exporta (o contrato da FASE 9 não muda) e escreve
`docs/index.html`. Toda a camada analítica é reaproveitada:

  nucleo/dados.py     leitura e validação do esquema
  nucleo/graficos.py  as figuras
  nucleo/textos.py    a narrativa
  nucleo/formatos.py  formatação numérica brasileira

O que muda é só a apresentação: em vez de o Streamlit desenhar, o HTML é gerado.

Uso:
    .venv/bin/python gerador/construir.py
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from gerador import componentes, tema  # noqa: E402
from nucleo import graficos, textos  # noqa: E402
from nucleo.config import ABA_Q7, ABAS, COLUNAS_ATRIBUTOS, ROTULOS_ATRIBUTOS  # noqa: E402
from nucleo.dados import DadosQ7, carregar, pasta_dados  # noqa: E402
from nucleo.formatos import formatar_atributo, formatar_decimal, formatar_inteiro  # noqa: E402

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

FIGURAS = {
    "gradiente": graficos.dispersao_pca,
    "cargas": graficos.cargas_pca,
    "regioes": graficos.mapa_regioes,
    "composicao": graficos.composicao_regioes,
    "regra_k": graficos.diagnostico_k,
    "estabilidade": graficos.estabilidade_por_k,
    "arvores": graficos.arvores_comparacao,
}


def _cartoes(artefatos: DadosQ7) -> str:
    inicio, fim = artefatos.configuracao["janela"]
    return componentes.linha_de_cartoes(
        (
            componentes.cartao(
                "Cobertura",
                (
                    "RAIS-CTPS (estoque em 31/12) · SISMIGRA-ATIVOS (dezembro)",
                    f"Anos: {inicio}–{fim} — janela fixa",
                    "Variáveis: índice Q + 6 atributos de perfil",
                ),
            ),
            componentes.cartao(
                "Filtros",
                (
                    f"Ano: fixo em {inicio}–{fim}",
                    f"Nacionalidade: as {artefatos.n_elegiveis} elegíveis",
                    "Top N: só no tamanho da tabela",
                ),
            ),
            componentes.cartao(
                "Nota metodológica",
                (
                    "Unidade: nacionalidade — nunca indivíduo",
                    f"Cobertura: {artefatos.n_elegiveis} de {artefatos.n_universo} comparáveis",
                    "Interpretação: gradiente associativo, não causal",
                ),
            ),
        )
    )


def _tabela_nacionalidades(artefatos: DadosQ7) -> str:
    tabela = artefatos.perfis.copy()
    ordenada = tabela.sort_values("Q_medio", ascending=False).head(60)
    cabecalhos = ("Nacionalidade", "Região", "Q", "Vínculos", *(ROTULOS_ATRIBUTOS[c] for c in COLUNAS_ATRIBUTOS))
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
    nota = componentes.leitura(
        f"As {len(ordenada)} nacionalidades de maior Q, das {len(tabela)} elegíveis. "
        "Esta tabela é a base de todos os gráficos desta aba."
    )
    return componentes.tabela(cabecalhos, linhas) + nota


def _bloco_de_evidencia(artefatos: DadosQ7, evidencia: textos.Evidencia, ativa: bool) -> str:
    if evidencia.chave == "quem":
        corpo = _tabela_nacionalidades(artefatos)
    else:
        figura = FIGURAS[evidencia.chave](artefatos)
        corpo = componentes.grafico(figura, f"q7-{evidencia.chave}") + componentes.leitura(
            evidencia.leitura
        )
    return componentes.evidencia(evidencia.chave, corpo, ativa)


def _cartao_de_evidencia(artefatos: DadosQ7) -> str:
    opcoes = ((e.chave, textos.rotulo_curto(e)) for e in textos.EVIDENCIAS)
    blocos = (
        _bloco_de_evidencia(artefatos, evidencia, indice == 0)
        for indice, evidencia in enumerate(textos.EVIDENCIAS)
    )
    return (
        '<div class="cartao cartao-alto"><div class="titulo-bloco">Evidência principal</div>'
        f"{componentes.seletor_de_evidencia(opcoes, textos.EVIDENCIAS[0].chave)}"
        f"{''.join(blocos)}</div>"
    )


def _cartao_de_resposta(artefatos: DadosQ7) -> str:
    resumo = graficos.resumo_numerico(artefatos)
    limites = (
        ("Denominador", textos.DENOMINADOR_EXPLICITO),
        ("Critério de elegibilidade", textos.CRITERIO_ELEGIBILIDADE),
        ("Cobertura observada", textos.COBERTURA_OBSERVADA),
        ("Interpretação permitida", textos.INTERPRETACAO_PERMITIDA),
        ("Interpretação não permitida", textos.INTERPRETACAO_PROIBIDA),
    )
    indicadores = componentes.indicadores((
        ("Regiões", resumo["Regiões"]),
        ("Silhueta", resumo["Silhueta no k escolhido"]),
        ("KMeans × Ward", resumo["KMeans × Ward"]),
        ("Estabilidade", resumo["Estabilidade (média)"] + " de média"),
    ))
    return (
        '<div class="cartao cartao-alto"><div class="titulo-bloco">Resposta + limites</div>'
        f'<div class="resposta">{componentes.para_html(textos.RESPOSTA_SINTETICA)}</div>'
        f"{indicadores}"
        f"{componentes.lista_de_limites(rotulo for rotulo, _ in limites)}"
        f"{componentes.detalhamento(limites)}</div>"
    )


def _secao_q7(artefatos: DadosQ7) -> str:
    return (
        f"{_cartoes(artefatos)}"
        f'<div class="linha-principal">{_cartao_de_evidencia(artefatos)}'
        f"{_cartao_de_resposta(artefatos)}</div>"
        f"{componentes.ponte('Onde isto toca o problema do projeto', textos.RESPOSTA_ANCORADA_NO_PROBLEMA)}"
    )


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


def _secao(conteudo: str, slug: str, ativa: bool) -> str:
    classe = "secao ativa" if ativa else "secao"
    return f'<section class="{classe}" id="secao-{slug}">{conteudo}</section>'


def construir(destino: Path = SAIDA / "index.html") -> Path:
    """Gera o dashboard completo em um único arquivo."""
    artefatos = carregar()
    identificadas = [(_slug(aba), aba) for aba in ABAS]
    secoes = [
        _secao(
            _secao_q7(artefatos) if nome == ABA_Q7 else _secao_pendente(nome),
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
