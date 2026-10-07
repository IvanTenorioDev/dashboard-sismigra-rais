"""Narrativa da aba Q1 — a evolução da presença ao longo dos anos.

Mesmo registro técnico da Q4, da Q6 e da Q7: leitor com formação quantitativa, sem
didatismo e sem metáfora onde cabe o termo. Nenhum número é escrito à mão — todos vêm de
`Artefatos.valores_q1_para_texto()` e são preenchidos por `nucleo.textos.preencher`.
"""

from __future__ import annotations

from nucleo.textos import Evidencia

RESPOSTA_SINTETICA = (
    "A presença cresce nos dois lados, **em ritmos diferentes e sobre coberturas "
    "diferentes**. Os vínculos formais saem de {vinculos_primeiro} em {primeiro_ano_vinculos} "
    "para {vinculos_ultimo} em {ultimo_ano_vinculos} — {crescimento_vinculos} em quinze anos, "
    "com uma única queda anual, em {ano_da_queda} (−{queda_vinculos}). O estoque de registros "
    "ativos só é observável a partir de {primeiro_ano_estoque}, e nos {n_anos_estoque} anos em "
    "que existe cresce {crescimento_registros}. Como os dois lados não cobrem o mesmo período, "
    "**a razão entre eles é a única medida comparável** — e ela sobe de {razao_primeira} para "
    "{razao_ultima}, uma variação de {razao_variacao}. O número de origens presentes acompanha: "
    "{nacionalidades_primeiro} nacionalidades com vínculo em {primeiro_ano_vinculos}, "
    "{nacionalidades_ultimo} em {ultimo_ano_vinculos}."
)

LIMITES: tuple[tuple[str, str], ...] = (
    (
        "Coberturas desiguais",
        "Os vínculos formais existem de {primeiro_ano_vinculos} a {ultimo_ano_vinculos}; o "
        "estoque de registros ativos, apenas de {primeiro_ano_estoque} a {ultimo_ano_estoque}. "
        "**Nenhum total desta aba soma os dois lados**, e nenhuma comparação de nível entre eles "
        "é válida — são unidades diferentes, em séries de extensões diferentes.",
    ),
    (
        "O que cada lado conta",
        "Vínculo formal é posto de trabalho na RAIS-CTPS, contado uma vez por vínculo. Registro "
        "ativo é registro na base migratória, contado uma vez por registro. Uma mesma pessoa pode "
        "sustentar vários registros e nenhum vínculo, ou o inverso — e a base não permite "
        "identificá-la em nenhum dos dois casos.",
    ),
    (
        "A queda de {ano_da_queda}",
        "É a única queda anual da série e vale {queda_vinculos}. Esta aba não oferece elemento "
        "para atribuir causa: seria preciso o detalhamento por nacionalidade e por UF, que a Q2 "
        "trata para outro recorte e para um único ano.",
    ),
    (
        "Estoque não é saldo",
        "O crescimento medido é de estoque em 31/12 de cada ano. Ele não é o saldo líquido de "
        "entradas e saídas do ano, e não distingue chegada recente de formalização de quem já "
        "estava no país.",
    ),
    (
        "Por que a Q4 usa só {n_anos_estoque} anos",
        "A razão entre os lados exige os dois observados. Isso restringe o cálculo a "
        "{primeiro_ano_estoque}–{ultimo_ano_estoque}, e a janela 2023–2025 das abas Q6 e Q7 é um "
        "subconjunto disso, escolhido por já estar sob a tipologia de amparos publicada.",
    ),
)

PONTE = (
    "A Q1 estabelece o que as outras abas pressupõem: a presença cresce nos dois lados, com "
    "cobertura desigual, e é a **razão** entre os lados — não cada lado em si — que mede "
    "conversão. A Q4 toma essa razão como objeto. A Q2 mostra que ela não se distribui por igual "
    "no território. A Q3 mostra que o fluxo que a alimenta mudou de composição."
)

ROTULOS_CURTOS: dict[str, str] = {
    "evolucao": "Evolução",
    "razao": "Conversão",
    "diversidade": "Diversidade",
    "anos": "Série anual",
}

EVIDENCIAS: tuple[Evidencia, ...] = (
    Evidencia(
        chave="evolucao",
        rotulo="Evolução",
        titulo="Os dois lados da presença, cada um na sua escala",
        leitura=(
            "Cada painel tem escala própria, porque os totais diferem em uma ordem de grandeza "
            "— cerca de {registros_primeiro} registros contra {vinculos_primeiro} vínculos no "
            "primeiro ano em que ambos existem. **O painel de baixo começa depois de propósito**: "
            "não há recorte anterior a {primeiro_ano_estoque} para o estoque de registros, e "
            "esticar a série até {primeiro_ano_vinculos} produziria uma linha que não existe nos "
            "dados. O lado dos vínculos é o único que permite leitura de longo prazo."
        ),
    ),
    Evidencia(
        chave="razao",
        rotulo="Conversão",
        titulo="Vínculos formais por registro ativo",
        leitura=(
            "Quatro pontos, porque são quatro os anos com os dois lados observados. A razão sobe "
            "de {razao_primeira} em {primeiro_ano_estoque} para {razao_ultima} em "
            "{ultimo_ano_estoque} — {razao_variacao}. A leitura: a conversão de presença em "
            "vínculo formal **acelera**, e não apenas acompanha o crescimento do estoque, que no "
            "mesmo intervalo foi de {crescimento_registros}. É esta razão, e não o nível dos "
            "lados, que o índice Q da Q4 compara entre nacionalidades."
        ),
    ),
    Evidencia(
        chave="diversidade",
        rotulo="Diversidade",
        titulo="Nacionalidades presentes em cada ano",
        leitura=(
            "O crescimento é também de variedade de origem: {nacionalidades_primeiro} "
            "nacionalidades com vínculo em {primeiro_ano_vinculos} e {nacionalidades_ultimo} em "
            "{ultimo_ano_vinculos}. As duas linhas têm coberturas diferentes, e a lacuna é a "
            "mesma da primeira figura. Vale notar o formato: a curva de vínculos cresce de forma "
            "quase monotônica, sem o patamar que se veria se a entrada de novas origens tivesse "
            "parado."
        ),
    ),
    Evidencia(
        chave="anos",
        rotulo="Série anual",
        titulo="Série anual consolidada",
        leitura=(
            "O material de consulta da aba: os dois lados, a razão entre eles e o número de "
            "origens presentes, ano a ano. As células vazias antes de {primeiro_ano_estoque} não "
            "são zero — o estoque de registros simplesmente não existe naquele ano."
        ),
    ),
)

EVIDENCIA_PADRAO = EVIDENCIAS[0].chave


def rotulo_curto(evidencia: Evidencia) -> str:
    """Rótulo compacto de uma evidência da Q1, para o seletor."""
    return ROTULOS_CURTOS[evidencia.chave]
