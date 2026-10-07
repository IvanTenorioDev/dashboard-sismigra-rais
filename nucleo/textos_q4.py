"""Narrativa da aba Q4 — a proporcionalidade entre registros e vínculos.

Mesmo registro técnico da Q7: leitor com formação quantitativa, sem didatismo e sem
metáfora onde cabe o termo. Nenhum número é escrito à mão — todos vêm de
`Artefatos.valores_q4_para_texto()` e são preenchidos por `nucleo.textos.preencher`.
"""

from __future__ import annotations

from nucleo.textos import Evidencia

RESPOSTA_SINTETICA = (
    "**Não.** A proporcionalidade entre as duas fontes é a exceção: **{pct_acima_1} das "
    "{n_elegiveis}** nacionalidades elegíveis têm Q > 1 — e concentram "
    "**{participacao_acima_1} dos vínculos**. A mediana do índice é {q_mediana}: a maioria é "
    "sub-representada no estoque de vínculos formais. E o desvio não é aleatório — a "
    "remuneração mediana cai de {salario_faixa_baixa} para {salario_faixa_alta} SM conforme "
    "Q sobe, com correlação de postos de {spearman_salario}."
)

LIMITES: tuple[tuple[str, str], ...] = (
    (
        "O que o índice mede",
        "Razão entre duas participações agregadas, em universos com conceitos de UF "
        "distintos: residência no SISMIGRA, estabelecimento empregador na RAIS. Não é taxa "
        "de emprego, de formalização nem probabilidade individual de inserção.",
    ),
    (
        "Limite superior e cauda",
        "O índice não tem limite superior: mediana {q_mediana}, máximo {q_maximo} "
        "({nacionalidade_q_maximo}, com {vinculos_q_maximo} vínculos). O ranking não deve "
        "ser lido no topo.",
    ),
    (
        "Tamanho do grupo",
        "A hipótese de que os extremos seriam artefato de denominador pequeno **não se "
        "sustenta**: a correlação de postos entre Q e volume de vínculos é {spearman_volume}. "
        "Os {n_extremos} casos com Q > 5 somam {pct_vinculos_extremos} dos vínculos.",
    ),
    (
        "Cobertura",
        "{n_elegiveis} nacionalidades com Q definido, somando os vínculos da janela. "
        "Ausência de dado não é interpretada como zero.",
    ),
    (
        "Interpretação permitida",
        "Comparar a participação de cada nacionalidade nas duas fontes e ordenar essa "
        "diferença. Inferência descritiva, condicionada a esta amostra.",
    ),
    (
        "Interpretação não permitida",
        "Causalidade; ler Q como medida de integração ou de sucesso de inserção; extrapolar "
        "para indivíduos.",
    ),
)

PONTE = (
    "A Q7 mostrou que a região de maior Q é a de menor remuneração. A Q4 mostra que a "
    "relação **não é efeito de agregação**: ela é monotônica ao longo de todas as "
    "nacionalidades — as medianas por faixa de Q são {faixas_salarios} SM — e a escolaridade "
    "superior cai no mesmo sentido. As {n_faixa_alta} nacionalidades com Q > 1,5 concentram "
    "{participacao_faixa_q_alto} dos vínculos da amostra."
)

ROTULOS_CURTOS: dict[str, str] = {
    "distribuicao": "Distribuição",
    "cauda": "Cauda",
    "remuneracao": "Remuneração",
    "faixas": "Faixas",
}

EVIDENCIAS: tuple[Evidencia, ...] = (
    Evidencia(
        chave="distribuicao",
        rotulo="Distribuição",
        titulo="Distribuição do índice Q entre as nacionalidades",
        leitura=(
            "O índice é assimétrico à direita: mediana {q_mediana} e máximo {q_maximo} — daí "
            "a escala logarítmica. A linha de paridade marca Q = 1, onde as duas "
            "distribuições coincidem. As {pct_acima_1} das nacionalidades à direita dessa "
            "linha concentram {participacao_acima_1} dos vínculos: a sobre-representação não "
            "é distribuída entre os grupos, é concentrada em poucos."
        ),
    ),
    Evidencia(
        chave="cauda",
        rotulo="Cauda",
        titulo="Índice Q contra volume de vínculos",
        leitura=(
            "Cada ponto é uma nacionalidade, posicionada pelo volume de vínculos e pelo "
            "índice. Se os valores extremos fossem artefato de denominador pequeno, se "
            "alinhariam à esquerda — e não é o que ocorre: a correlação de postos entre Q e "
            "volume é {spearman_volume}, praticamente nula. Os {n_extremos} casos com Q > 5 "
            "somam {pct_vinculos_extremos} dos vínculos e estão espalhados. A cauda é pesada "
            "e ilimitada, mas não enviesada pelo tamanho do grupo."
        ),
    ),
    Evidencia(
        chave="remuneracao",
        rotulo="Remuneração",
        titulo="Índice Q contra remuneração",
        leitura=(
            "A relação é monotônica e praticamente invisível na correlação linear: Pearson "
            "{pearson_salario}, **Spearman {spearman_salario}**. Os pontos laranja são as "
            "medianas por faixa de Q, e caem de forma ordenada — de {salario_faixa_baixa} a "
            "{salario_faixa_alta} SM. A divergência entre os dois coeficientes decorre da "
            "cauda: Pearson é dominado pelos valores extremos, Spearman não."
        ),
    ),
    Evidencia(
        chave="faixas",
        rotulo="Faixas",
        titulo="Perfil das nacionalidades por faixa de Q",
        leitura=(
            "A tabela quantifica o que a figura anterior mostra. Cada faixa de Q tem "
            "remuneração mediana menor que a anterior e menor proporção de escolaridade "
            "superior, com a concentração de vínculos na faixa de maior Q. É a evidência "
            "central da Q4 e a ponte para a Q7."
        ),
    ),
)

EVIDENCIA_PADRAO = EVIDENCIAS[0].chave


def rotulo_curto(evidencia: Evidencia) -> str:
    """Rótulo compacto de uma evidência da Q4, para o seletor."""
    return ROTULOS_CURTOS[evidencia.chave]
