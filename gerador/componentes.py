"""Peças de HTML do dashboard estático.

Cada função devolve uma string. Nada de template engine: o HTML é montado por
composição, o que mantém o projeto sem dependência além do Plotly.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

import plotly.graph_objects as go

from gerador import tema
from nucleo.config import PISO_REGISTROS, PISO_VINCULOS

NEGRITO = re.compile(r"\*\*(.+?)\*\*")
ITALICO = re.compile(r"\*(.+?)\*")


def para_html(texto: str) -> str:
    """Converte a marcação usada em `nucleo.textos` para HTML.

    Só negrito e itálico: é o que os textos usam, e converter Markdown inteiro
    seria trazer uma dependência para resolver um problema que não existe.
    """
    return ITALICO.sub(r"<i>\1</i>", NEGRITO.sub(r"<b>\1</b>", texto))


def cartao(titulo: str, linhas: Iterable[str]) -> str:
    """Um dos três cartões informativos do topo."""
    corpo = "".join(f'<div class="linha">{para_html(linha)}</div>' for linha in linhas)
    return f'<div class="cartao"><div class="rotulo">{titulo}</div>{corpo}</div>'


def linha_de_cartoes(cartoes: Sequence[str]) -> str:
    """As três caixas do topo, lado a lado."""
    return f'<div class="linha-cartoes">{"".join(cartoes)}</div>'


def indicadores(pares: Iterable[tuple[str, str]]) -> str:
    """Linha compacta de indicadores — mantém o cartão de resposta curto."""
    itens = "".join(f"<span>{rotulo}: <b>{valor}</b></span>" for rotulo, valor in pares)
    return f'<div class="indicadores">{itens}</div>'


def lista_de_limites(rotulos: Iterable[str]) -> str:
    """Os cinco limites, apenas com o rótulo — como no desenho aprovado."""
    itens = "".join(f"<li>{rotulo}</li>" for rotulo in rotulos)
    return f'<ul class="limites">{itens}</ul>'


def detalhamento(itens: Iterable[tuple[str, str]]) -> str:
    """O texto completo de cada limite, recolhido para não esticar o cartão."""
    paragrafos = "".join(
        f"<p><b>{rotulo}:</b> {para_html(texto)}</p>" for rotulo, texto in itens
    )
    return (
        '<details class="detalhe"><summary>Detalhamento de cada limite</summary>'
        f"{paragrafos}</details>"
    )


def seletor_de_evidencia(opcoes: Iterable[tuple[str, str]], ativa: str) -> str:
    """Botões que trocam a evidência exibida dentro do cartão."""
    botoes = "".join(
        f'<button class="opcao{" ativa" if chave == ativa else ""}" '
        f'data-evidencia="{chave}">{rotulo}</button>'
        for chave, rotulo in opcoes
    )
    return f'<div class="seletor">{botoes}</div>'


def evidencia(chave: str, conteudo: str, ativa: bool, prefixo: str = "") -> str:
    """Um bloco de evidência, visível só quando selecionado.

    O `prefixo` é o slug da aba. Sem ele, duas abas com uma evidência de mesmo nome —
    a Q4 e a Q6 têm ambas uma evidência `remuneracao` — produziriam ids repetidos no
    mesmo arquivo. Quem troca de evidência é o `data-evidencia`, não o id.
    """
    return (
        f'<div class="evidencia{" ativa" if ativa else ""}" '
        f'id="{prefixo}ev-{chave}" data-evidencia="{chave}">{conteudo}</div>'
    )


def grafico(figura: go.Figure, identificador: str) -> str:
    """Converte uma figura Plotly em HTML interativo, sem a barra de ferramentas.

    A altura e a margem vêm da própria figura. Cada módulo de figuras declara o
    enquadramento que quer, e sobrescrevê-lo aqui espremeria a grade de seis painéis da
    Q6 na altura de um gráfico único.

    O `id` do Plotly precisa ser **distinto** do id do bloco que o contém: o
    `Plotly.newPlot` resolve o alvo por `getElementById`, então um id repetido faz o
    gráfico ser desenhado no elemento externo — e o bloco de leitura é empurrado para
    fora do cartão.
    """
    return figura.to_html(
        full_html=False,
        include_plotlyjs=False,
        div_id=identificador,
        config={"displayModeBar": False, "responsive": True},
    )


def tabela(cabecalhos: Sequence[str], linhas: Sequence[Sequence[str]]) -> str:
    """Tabela simples, com os cabeçalhos no mesmo estilo dos demais rótulos."""
    th = "".join(f"<th>{nome}</th>" for nome in cabecalhos)
    tr = "".join(
        "<tr>" + "".join(f"<td>{celula}</td>" for celula in linha) + "</tr>" for linha in linhas
    )
    return f'<table class="tabela"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


def leitura(texto: str) -> str:
    """Como ler a evidência exibida."""
    return f'<div class="leitura">{para_html(texto)}</div>'


def ponte(rotulo: str, texto: str) -> str:
    """Bloco que liga o achado ao problema do projeto."""
    return (
        f'<div class="ponte"><div class="ponte-rotulo">{rotulo}</div>'
        f'<div class="ponte-texto">{para_html(texto)}</div></div>'
    )


def rodape_pisos(janela_inicio: int, janela_fim: int) -> str:
    """Faixa de pisos, dentro do painel e sempre à vista.

    Os valores vêm das constantes e a janela vem da execução, nunca de literais: este
    rodapé é a versão curta da tabela de pisos da aba Método, e as duas precisam contar a
    mesma história na mesma execução.
    """
    return (
        '<div class="pisos"><b>Pisos fixos (não filtros):</b> '
        f"R ≥ {PISO_REGISTROS} para HHI (Q2) e persistência (Q5); "
        f"V_total ≥ {PISO_VINCULOS} na janela {janela_inicio}–{janela_fim} para os perfis "
        f"(Q6–Q7) e para a leitura da Q4; a árvore exige R_total ≥ {PISO_REGISTROS} e "
        f"V_total ≥ {PISO_VINCULOS}.</div>"
    )


def navegacao(abas: Sequence[tuple[str, str]], ativa: str) -> str:
    """Lista de botões da sidebar, com o ativo em laranja."""
    botoes = "".join(
        f'<button class="aba-nav{" ativa" if slug == ativa else ""}" '
        f'data-aba="{slug}">{nome}</button>'
        for slug, nome in abas
    )
    return f'<nav class="navegacao">{botoes}</nav>'


def pagina(titulo: str, navegacao_html: str, secoes: Sequence[str], rodape: str) -> str:
    """Documento completo: painel branco, cabeçalho azul, sidebar, conteúdo e rodapé."""
    corpo = "".join(secoes)
    return (
        "<!DOCTYPE html>\n<html lang='pt-BR'>\n<head>\n"
        "<meta charset='utf-8'>\n"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>\n"
        f"<title>{titulo}</title>\n"
        "<script src='https://cdn.plot.ly/plotly-3.0.1.min.js' charset='utf-8'></script>\n"
        f"<style>{tema.CSS}</style>\n"
        "</head>\n<body>\n"
        '<div class="painel">\n'
        f'<header class="cabecalho">{titulo}</header>\n'
        '<div class="corpo">\n'
        f"{navegacao_html}\n"
        '<div class="coluna">\n'
        f'<div class="conteudo">{corpo}</div>\n'
        f"{rodape}\n"
        "</div>\n</div>\n</div>\n"
        f"<script>{_JAVASCRIPT}</script>\n"
        "</body>\n</html>\n"
    )


_JAVASCRIPT = """
function redimensionar(raiz) {
  raiz.querySelectorAll('.js-plotly-plot').forEach(function (elemento) {
    if (elemento.offsetParent !== null && window.Plotly) {
      window.Plotly.Plots.resize(elemento);
    }
  });
}

function ativar(slug) {
  var destino = document.getElementById('secao-' + slug);
  if (!destino) { return; }
  document.querySelectorAll('.aba-nav').forEach(function (botao) {
    botao.classList.toggle('ativa', botao.dataset.aba === slug);
  });
  document.querySelectorAll('.secao').forEach(function (secao) {
    secao.classList.toggle('ativa', secao === destino);
  });
  if (window.history.replaceState) {
    window.history.replaceState(null, '', '#' + slug);
  }
  redimensionar(destino);
}

document.querySelectorAll('.aba-nav').forEach(function (botao) {
  botao.addEventListener('click', function () { ativar(botao.dataset.aba); });
});

document.querySelectorAll('.seletor').forEach(function (grupo) {
  grupo.querySelectorAll('.opcao').forEach(function (botao) {
    botao.addEventListener('click', function () {
      var cartao = grupo.closest('.cartao-alto');
      var chave = botao.dataset.evidencia;
      grupo.querySelectorAll('.opcao').forEach(function (outro) {
        outro.classList.toggle('ativa', outro === botao);
      });
      cartao.querySelectorAll('.evidencia').forEach(function (bloco) {
        bloco.classList.toggle('ativa', bloco.dataset.evidencia === chave);
      });
      redimensionar(cartao);
    });
  });
});

// Os gráficos nascem com largura zero, porque o bloco de evidência começa escondido
// pelo CSS. Ativar a aba visível redimensiona o que estiver à vista.
window.addEventListener('load', function () {
  var inicial = window.location.hash.slice(1) ||
    document.querySelector('.aba-nav').dataset.aba;
  ativar(inicial);
});
"""
