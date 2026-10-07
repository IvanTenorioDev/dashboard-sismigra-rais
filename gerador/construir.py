"""Gerador do dashboard estático.

Escreve `docs/index.html` a partir das declarações de `nucleo/abas.py`. O conteúdo das abas
não é declarado aqui: este módulo é só o renderizador, que implementa uma vez o contrato do
desenho aprovado — três cartões no topo, evidência principal com seletor, painel de resposta
fixo e rodapé de pisos.

Uso:
    .venv/bin/python gerador/construir.py
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from nucleo import componentes, textos  # noqa: E402
from nucleo.abas import CONTEUDO_POR_ABA, Bloco, Conteudo  # noqa: E402
from nucleo.config import ABAS  # noqa: E402
from nucleo.dados import Artefatos, carregar, pasta_dados  # noqa: E402

TITULO = "Dashboard analítico • SISMIGRA × RAIS-CTPS"


def _subtitulo(artefatos: Artefatos) -> str:
    """Faixa de cobertura do cabeçalho, derivada dos artefatos.

    Não é uma faixa só. As fontes cobrem períodos diferentes — os vínculos formais desde
    2010, o estoque de registros ativos desde 2022 — e resumir as duas num intervalo
    único afirmaria que o lado mais curto existe nos anos em que não existe. Cada aba
    declara a própria cobertura; aqui ficam as duas que o projeto compara.
    """
    vinculos = artefatos.resumo_anual.dropna(subset=["vinculos_formais"])
    inicio_estoque, fim_estoque = artefatos.cobertura_do_estoque()
    return (
        "Projeto Integrador I · imigração registrada e vínculos formais · "
        f"vínculos {int(vinculos['ano'].min())}–{int(vinculos['ano'].max())} · "
        f"registros ativos {inicio_estoque}–{fim_estoque}"
    )


# `docs/` de propósito: é a pasta que o GitHub Pages sabe publicar (a outra opção é a
# raiz). O HTML sai autossuficiente, com os dados e os gráficos embutidos, então
# publicar o painel é só apontar o Pages para cá.
SAIDA = RAIZ / "docs"


# ---------------------------------------------------------------------------
# Renderizador — implementa o contrato do desenho aprovado uma única vez
# ---------------------------------------------------------------------------


def _cartoes(conteudo: Conteudo) -> str:
    return componentes.linha_de_cartoes(
        tuple(componentes.cartao(titulo, linhas) for titulo, linhas in conteudo.cartoes)
    )


def _corpo_da_evidencia(
    conteudo: Conteudo,
    artefatos: Artefatos,
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
    conteudo: Conteudo, artefatos: Artefatos, valores: dict[str, object], prefixo: str
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
    conteudo: Conteudo, artefatos: Artefatos, valores: dict[str, object]
) -> str:
    detalhado = ((rotulo, textos.preencher(texto, valores)) for rotulo, texto in conteudo.limites)
    resposta = componentes.para_html(textos.preencher(conteudo.resposta, valores))
    return (
        '<div class="cartao cartao-alto"><div class="titulo-bloco">Resposta + limites</div>'
        f'<div class="resposta">{resposta}</div>'
        f"{componentes.indicadores(conteudo.indicadores(artefatos))}"
        # O rótulo também passa pelo preenchimento: ele cita ano e piso, e um placeholder
        # não preenchido chegaria literal à tela.
        f"{componentes.lista_de_limites(textos.preencher(rotulo, valores) for rotulo, _ in conteudo.limites)}"
        f"{componentes.detalhamento(detalhado)}</div>"
    )


def _bloco(bloco: Bloco, artefatos: Artefatos) -> str:
    nota = (
        f'<div class="linha">{componentes.para_html(bloco.nota)}</div>' if bloco.nota else ""
    )
    return (
        '<div class="cartao cartao-alto bloco-extra">'
        f'<div class="titulo-bloco">{bloco.titulo}</div>'
        f"{nota}{bloco.tabela(artefatos)}</div>"
    )


def _secao(conteudo: Conteudo, artefatos: Artefatos, prefixo: str) -> str:
    valores = conteudo.valores(artefatos)
    resposta = _cartao_de_resposta(conteudo, artefatos, valores)
    if conteudo.evidencias:
        evidencias = _cartao_de_evidencia(conteudo, artefatos, valores, prefixo)
        principal = f'<div class="linha-principal">{evidencias}{resposta}</div>'
    else:
        # Aba sem figura: não há evidência a alternar, e a resposta ocupa a linha toda. O
        # seletor existe para trocar de evidência, não para preencher o cartão.
        principal = f'<div class="linha-principal linha-unica">{resposta}</div>'
    blocos = "".join(_bloco(bloco, artefatos) for bloco in conteudo.blocos)
    ponte = componentes.ponte(
        "Onde isto toca o problema do projeto",
        textos.preencher(conteudo.ponte, valores),
    )
    return f"{_cartoes(conteudo)}{principal}{blocos}{ponte}"


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
    # Sem aba pendente: uma pergunta nova sem declaração falha alto aqui, em vez de ir ao ar
    # com texto de espera.
    secoes = [
        _marcador(
            _secao(CONTEUDO_POR_ABA[nome](artefatos), artefatos, f"{slug}-"),
            slug,
            indice == 0,
        )
        for indice, (slug, nome) in enumerate(identificadas)
    ]
    html = componentes.pagina(
        TITULO,
        _subtitulo(artefatos),
        componentes.navegacao(identificadas, identificadas[0][0]),
        secoes,
        componentes.rodape_pisos(*artefatos.janela_dos_perfis),
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
