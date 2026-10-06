"""Narrativa da aba Q7.

A prosa vive aqui, não no código de layout. A regra que o slide 11 estabelece é que o
painel de resposta **não muda** quando o usuário troca de evidência: a conclusão vem do
conjunto, não de um gráfico isolado.
"""

from __future__ import annotations

from dataclasses import dataclass

from nucleo.config import ABA_Q7

PERGUNTAS: dict[str, str] = {
    "Q1 Presença": "Como evolui a presença de imigrantes no estoque de registros ativos?",
    "Q2 Território": "Onde essa presença se concentra no território, e quão concentrada ela é?",
    "Q3 Registros": "Como se comporta o fluxo de novos registros, ano a ano?",
    "Q4 Representação": (
        "A presença nos vínculos formais é proporcional à presença nos registros? (índice Q)"
    ),
    "Q5 Persistência": "Os registros se sustentam ao longo do tempo ou são pontuais?",
    "Q6 Atributos": "Qual é o perfil dos vínculos formais de cada nacionalidade?",
    ABA_Q7: (
        "Existem partições discretas de inserção laboral entre as nacionalidades, ou um "
        "contínuo? E quais atributos de perfil discriminam a sobre-representação nos vínculos "
        "formais?"
    ),
    "Método & limites": (
        "Quais decisões metodológicas sustentam tudo que está nas outras abas?"
    ),
}

# Rótulos do seletor de evidência. Curtos de propósito: oito opções longas quebram
# em duas linhas e sujam o cartão, que no desenho aprovado tem um único gráfico.
ROTULOS_CURTOS: dict[str, str] = {
    "gradiente": "Gradiente",
    "cargas": "Eixo",
    "regioes": "Regiões",
    "composicao": "Tamanho",
    "regra_k": "Regra de k",
    "estabilidade": "Robustez",
    "arvores": "Árvores",
    "quem": "Tabela",
}


def rotulo_curto(evidencia: "Evidencia") -> str:
    """Rótulo compacto de uma evidência, para o seletor."""
    return ROTULOS_CURTOS[evidencia.chave]


def preencher(texto: str, valores: dict[str, object]) -> str:
    """Preenche os números da narrativa com os valores desta execução.

    Nenhum número destes textos é escrito à mão: todos vêm de
    `DadosQ7.valores_para_texto`. Um valor fixado no texto divergiria em silêncio na
    próxima execução do notebook — foi o que aconteceu com a concordância KMeans × Ward
    em k=2, registrada como 0,007 e que passou a 0,43 quando a elegibilidade foi corrigida.
    """
    return texto.format(**valores)


RESPOSTA_SINTETICA = (
    "Um **contínuo**, não três tipos discretos. As nacionalidades se ordenam ao longo de um "
    "eixo de qualificação–remuneração; a partição em {k} regiões é uma decisão analítica, e a "
    "silhueta de {silhueta} quantifica a fragilidade dessas fronteiras. A separação é "
    "convenção de leitura, não descoberta de categorias."
)

DENOMINADOR_EXPLICITO = (
    "**{n_elegiveis}** nacionalidades elegíveis de **{n_universo}** presentes simultaneamente "
    "nas duas fontes. Unidade de análise: nacionalidade × ano, com vínculos agregados — "
    "nenhuma das bases possui identificador de indivíduo."
)

CRITERIO_ELEGIBILIDADE = (
    "Três filtros cumulativos: Q definido, seis atributos sem dado ausente e "
    "V_total ≥ 100 na janela 2023–2025. Sem imputação. O piso assegura massa mínima para as "
    "medianas; não valida a estrutura encontrada."
)

COBERTURA_OBSERVADA = (
    "RAIS-CTPS (estoque em 31/12) e SISMIGRA-ATIVOS (posição de dezembro), harmonizados em "
    "nacionalidade × ano. A ausência de identificador individual em ambas as fontes restringe "
    "a integração ao nível agregado: comparam-se distribuições, nunca registros."
)

INTERPRETACAO_PERMITIDA = (
    "Ordenar os perfis e identificar os atributos associados a cada posição. Inferência "
    "descritiva, condicionada a esta amostra e a estes denominadores."
)

INTERPRETACAO_PROIBIDA = (
    "Causalidade; tratar as regiões como categorias naturais ou jurídicas; extrapolar para "
    "indivíduos (Q não é taxa de emprego nem de formalização); interpretar Q como medida de "
    "integração."
)

RESPOSTA_ANCORADA_NO_PROBLEMA = (
    "A região de maior Q (**{q_regiao_maior}**, região {regiao_maior_q}) é também a de menor "
    "remuneração mediana (**{salario_regiao_maior_q} SM**) e a de menor proporção de "
    "escolaridade superior (**{superior_regiao_maior_q}**). Sobre-representação no estoque de "
    "vínculos não implica inserção favorável: implica presença proporcionalmente maior em "
    "vínculos de baixa remuneração. É a ambiguidade que o índice Q isolado não resolve — e a "
    "justificativa do tratamento multivariado."
)


@dataclass(frozen=True)
class Evidencia:
    """Uma evidência do bloco principal, com o rótulo do seletor e como lê-la."""

    chave: str
    rotulo: str
    titulo: str
    leitura: str


EVIDENCIAS: tuple[Evidencia, ...] = (
    Evidencia(
        chave="gradiente",
        rotulo="Direção do gradiente",
        titulo="Projeção das nacionalidades em PC1 × PC2",
        leitura=(
            "As {n_elegiveis} nacionalidades projetadas nos dois primeiros componentes. A cor "
            "indica a partição atribuída pelo KMeans. As regiões se **sobrepõem** no plano — "
            "coerente com a silhueta de {silhueta} e não um artefato da projeção. PC1 e PC2 "
            "retêm {variancia_acumulada} da variância; os {variancia_restante} restantes não "
            "estão representados aqui, e nenhuma leitura visual os substitui."
        ),
    ),
    Evidencia(
        chave="cargas",
        rotulo="O que define o eixo",
        titulo="Cargas dos atributos nos componentes principais",
        leitura=(
            "Correlações entre atributo e componente. PC1 é um eixo de qualificação–"
            "remuneração: `pct_superior` ({carga_superior_pc1}) e `salario_medio_sm` carregam "
            "no mesmo sentido, e `pct_tempo_parcial` no sentido oposto. PC2 contrasta estrutura "
            "etária e composição de gênero. O eixo não separa nacionalidades por origem — "
            "posiciona-as na estrutura ocupacional brasileira."
        ),
    ),
    Evidencia(
        chave="regioes",
        rotulo="As regiões",
        titulo="Medianas por região, com valores observados nas células",
        leitura=(
            "A cor indica posição relativa **dentro da coluna**; o valor observado está na "
            "célula. As medianas de remuneração são {salarios} SM — razão de {razao_salarios}× "
            "entre extremos, com patamar intermediário. A proporção de escolaridade superior "
            "acompanha a mesma ordenação. Não há gradação uniforme ao longo das três regiões."
        ),
    ),
    Evidencia(
        chave="composicao",
        rotulo="Tamanho das regiões",
        titulo="Nacionalidades e volume de vínculos por região",
        leitura=(
            "Contagem de nacionalidades e volume de vínculos não são proporcionais: "
            "{n_maior} nacionalidades concentram {participacao_maior} dos vínculos da janela. "
            "As duas ponderações são relatadas porque respondem a perguntas distintas — "
            "quantos países, e quanta força de trabalho."
        ),
    ),
    Evidencia(
        chave="regra_k",
        rotulo="A regra de k",
        titulo="Critérios de escolha de k",
        leitura=(
            "Todos os k avaliados são exibidos, inclusive os rejeitados. k ≥ "
            "{primeiro_k_inadmissivel} produzem grupos de tamanho 1 — inadmissíveis pelo piso "
            "de {minimo_grupo} nacionalidades. k=2 é rejeitado por critério distinto: a "
            "concordância KMeans × Ward cai a {acordo_k2}, abaixo do limiar de "
            "{acordo_minimo}, o que caracteriza partição sensível ao método. Em k={k} a "
            "concordância é de {acordo} e a silhueta, {silhueta} — valor baixo em todos os k, "
            "o que indica estrutura fraca."
        ),
    ),
    Evidencia(
        chave="estabilidade",
        rotulo="Robustez",
        titulo="ARI sob reamostragem — distribuição por k",
        leitura=(
            "Reamostragem sem reposição de 80% dos casos, {repeticoes} repetições, semente "
            "fixa. Reportam-se média ({ari_media}), desvio-padrão e mínimo ({ari_minimo}): a "
            "média isolada não distingue partição estável de uma cuja estabilidade depende de "
            "quais casos entram. O mínimo delimita a cauda inferior da distribuição."
        ),
    ),
    Evidencia(
        chave="arvores",
        rotulo="As árvores",
        titulo="Ganho sobre o classificador majoritário",
        leitura=(
            "Validação cruzada estratificada, com regularização por `max_depth={profundidade}`, "
            "`min_samples_leaf={min_folha}` e `min_impurity_decrease={ganho}`. A referência é o "
            "classificador majoritário. O alvo da árvore A (Q > 1) não figura entre os "
            "preditores; o da árvore B é construído sobre os **tercis extremos** de "
            "remuneração, com o terço intermediário descartado — o que eleva a separabilidade "
            "por construção. A leitura adequada de B é associação entre qualificação e "
            "extremos de remuneração; não estima efeito de qualificação sobre remuneração. "
            "Ambas produzem regras descritivas desta amostra."
        ),
    ),
    Evidencia(
        chave="quem",
        rotulo="Tabela",
        titulo="Tabela de rastreabilidade",
        leitura=(
            "As {n_tabela} nacionalidades de maior Q, com partição, índice Q, volume de "
            "vínculos na janela e os seis atributos de perfil. Nenhum ponto dos gráficos "
            "anteriores existe fora desta tabela."
        ),
    ),
)

EVIDENCIA_PADRAO = EVIDENCIAS[0].chave


def evidencia_por_chave(chave: str) -> Evidencia:
    """Busca uma evidência pelo seu identificador."""
    for evidencia in EVIDENCIAS:
        if evidencia.chave == chave:
            return evidencia
    raise KeyError(f"evidência desconhecida: {chave!r}. Disponíveis: {[e.chave for e in EVIDENCIAS]}")
