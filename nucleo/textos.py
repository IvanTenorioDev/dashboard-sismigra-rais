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
        "Existem **grupos distintos** de inserção laboral entre as nacionalidades — ou um "
        "**contínuo**? E quais atributos acompanham a sobre-representação nos vínculos formais?"
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

RESPOSTA_SINTETICA = (
    "Um **gradiente**, não três tipos naturais. As nacionalidades se ordenam ao longo de "
    "um eixo de qualificação e remuneração, e o corte em três regiões é uma escolha "
    "analítica — a silhueta de 0,27 diz que as fronteiras são frouxas, não que os grupos "
    "sejam evidentes."
)

DENOMINADOR_EXPLICITO = (
    "**101** nacionalidades elegíveis de **184** comparáveis entre as duas fontes. "
    "Não são pessoas: cada linha é uma nacionalidade, com o total de vínculos da janela."
)

CRITERIO_ELEGIBILIDADE = (
    "Três cortes: **Q comparável** (a nacionalidade aparece nas duas fontes), os **seis "
    "atributos observados** e **soma de vínculos na janela 2023–2025 ≥ 100**. Não se "
    "imputa dado ausente, e o piso é de massa estatística — não valida os grupos."
)

COBERTURA_OBSERVADA = (
    "RAIS-CTPS (estoque em 31/12) e SISMIGRA-ATIVOS (fotografia de dezembro), "
    "harmonizados por **nacionalidade × ano**. Não existe identificador individual em "
    "nenhuma das fontes, então a comparação é sempre entre distribuições."
)

INTERPRETACAO_PERMITIDA = (
    "Descrever **como os perfis se ordenam** e quais atributos acompanham cada posição. "
    "Resultado associativo, válido para esta amostra e estes denominadores."
)

INTERPRETACAO_PROIBIDA = (
    "Afirmar causalidade, tratar as regiões como categorias naturais ou jurídicas, "
    "extrapolar para pessoas (o índice Q não é taxa de emprego) e ler o índice Q como "
    "medida de integração."
)

RESPOSTA_ANCORADA_NO_PROBLEMA = (
    "A região de **maior Q é também a de menor salário** (≈ 1,6 SM) e a **menor "
    "escolaridade superior**. Sobre-representação nos vínculos formais **não** significa "
    "inserção mais favorável: significa presença proporcionalmente maior numa base de "
    "vínculos de baixa remuneração. É exatamente o tipo de leitura que o índice Q "
    "isolado esconde — e a razão de a análise ser multivariada."
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
        titulo="Os dois primeiros componentes principais",
        leitura=(
            "Cada ponto é uma nacionalidade. A cor é a região atribuída pelo algoritmo — "
            "as cores se **interpenetram** no plano, e isso não é defeito do gráfico: é o "
            "achado. Os dois eixos retêm 56,1% da variabilidade, ou seja, **43,9% da "
            "informação não está neste plano** e nenhuma leitura visual o substitui."
        ),
    ),
    Evidencia(
        chave="cargas",
        rotulo="O que define o eixo",
        titulo="Peso de cada atributo nos componentes",
        leitura=(
            "O primeiro componente é dominado por **qualificação e remuneração**, com "
            "sinais opostos entre superior completo e trabalho em tempo parcial. Isso dá "
            "nome ao eixo: não é 'ser estrangeiro', é **posição no mercado de trabalho "
            "formal brasileiro**."
        ),
    ),
    Evidencia(
        chave="regioes",
        rotulo="As regiões",
        titulo="Perfil mediano de cada região",
        leitura=(
            "A cor indica posição **relativa dentro de cada coluna** — o valor real está "
            "escrito na célula. O contraste é de escala salarial (≈ 1,6 SM contra ≈ 6,7 SM), "
            "não de cinco graus intermediários: por isso falamos de duas pontas e um meio."
        ),
    ),
    Evidencia(
        chave="composicao",
        rotulo="Tamanho das regiões",
        titulo="Quantas nacionalidades e quantos vínculos em cada região",
        leitura=(
            "A região com mais nacionalidades concentra a maior parte **dos casos**, mas "
            "não necessariamente dos vínculos. Distinguir contagem de nacionalidades de "
            "volume de vínculos evita o erro de tratar 57 países pequenos como equivalentes "
            "a 57 países grandes."
        ),
    ),
    Evidencia(
        chave="regra_k",
        rotulo="A regra de k",
        titulo="Por que três regiões e não cinco",
        leitura=(
            "Mostramos **todos** os k avaliados, inclusive os descartados. k = 5 a 8 "
            "produzem grupos de uma única nacionalidade — não são regiões. E k = 2 é "
            "recusado por outro motivo: KMeans e Ward discordam quase por completo "
            "(ARI ≈ 0,007), então os 'dois grupos' seriam efeito do algoritmo, não do "
            "dado. Note que a silhueta é **baixa em todos os k**: a estrutura é fraca, e "
            "dizer isso faz parte do resultado."
        ),
    ),
    Evidencia(
        chave="estabilidade",
        rotulo="Robustez",
        titulo="Quanto a partição oscila sob reamostragem",
        leitura=(
            "Cada ponto é uma reamostragem de 80% dos casos. A faixa é larga, e é por isso "
            "que o dashboard exibe **a faixa e o mínimo**, não só a média. Um k cuja média é "
            "alta mas cujo mínimo é baixo não é um k estável — é um k sortudo."
        ),
    ),
    Evidencia(
        chave="arvores",
        rotulo="As árvores",
        titulo="Duas árvores, dois alvos, um limite comum",
        leitura=(
            "Comparamos sempre contra o **baseline da classe majoritária**: sem isso, uma "
            "acurácia de 0,84 pareceria excelente mesmo quando o baseline já é 0,60. "
            "Os dois alvos não são igualmente exigentes: a árvore B compara apenas os "
            "**tercis extremos** de remuneração (o terço do meio é descartado), então a "
            "tarefa é mais fácil por construção, e qualificação e salário caminham juntos "
            "por definição do mercado. A leitura honesta de B é *'qualificação separa bem "
            "os extremos'* — **não** *'qualificação explica o salário'*. As regras são "
            "descritivas desta amostra e não estabelecem causalidade."
        ),
    ),
    Evidencia(
        chave="quem",
        rotulo="Quem está onde",
        titulo="As nacionalidades e sua região",
        leitura=(
            "A tabela é a base de tudo que está acima — nenhum ponto dos gráficos existe "
            "fora dela. É o artefato a conferir quando um número do slide não bater com o "
            "do dashboard."
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
