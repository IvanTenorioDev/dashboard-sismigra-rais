"""Narrativa da aba Método & limites — a decisão declarada de todo o painel.

Esta é a única aba sem figura, e por um motivo: as outras perguntam algo sobre os dados,
esta pergunta algo sobre o método. Não há distribuição a mostrar, há decisões a enumerar —
e o lugar de uma enumeração é uma tabela, não um gráfico.

O que fica aqui não é novo: são as decisões que aparecem nos limites de cada aba, reunidas
num só lugar e com os números desta execução ao lado. Nenhum número é escrito à mão.
"""

from __future__ import annotations

from nucleo.textos import Evidencia

RESPOSTA_SINTETICA = (
    "O painel mede uma coisa só — a presença de cada nacionalidade em duas fontes que contam "
    "coisas diferentes — e a mede sob duas decisões que valem para todas as abas. A primeira é "
    "a **unidade**: nacionalidade agregada na janela {janela_inicio}–{janela_fim}, nunca "
    "indivíduo. A segunda é a **regra de ausência**: dado que não existe sai vazio e nunca "
    "zero, porque zero é uma afirmação sobre o mundo e vazio é uma afirmação sobre a base. "
    "Sobre elas assentam um funil de quatro etapas, que leva de {n_na_janela} nacionalidades a "
    "{n_elegiveis} elegíveis, dois pisos de massa mínima ({piso_vinculos} vínculos e "
    "{piso_registros} registros) e {n_atributos} atributos de perfil. O painel não recalcula "
    "nada: os {n_artefatos} artefatos que alimentam as abas de resultado são congelados pelo "
    "notebook e apenas apresentados aqui."
)

LIMITES: tuple[tuple[str, str], ...] = (
    (
        "Unidade de análise",
        "Nacionalidade × ano. Nenhuma das duas fontes tem identificador de indivíduo, então "
        "toda leitura é de grupo — e uma afirmação sobre a nacionalidade mediana não é uma "
        "afirmação sobre o imigrante mediano. É falácia ecológica, e vale para as "
        "{n_abas_de_resultado} abas de resultado.",
    ),
    (
        "Causalidade",
        "Todas as associações do painel são descritivas. Nenhuma estima efeito, e nenhuma "
        "distingue seleção de retorno — nem as de coeficiente alto, como a associação de "
        "remuneração e escolaridade da Q6 ou o gradiente da Q4.",
    ),
    (
        "Cobertura desigual entre as fontes",
        "Vínculos formais de {primeiro_ano_vinculos} a {ultimo_ano_vinculos}; estoque de "
        "registros de {inicio_estoque} a {fim_estoque}; fluxo de {primeiro_ano_fluxo} a "
        "{ultimo_ano_fluxo}, sem 2017; tipologia de amparo a partir de {primeiro_ano_amparo}. "
        "Apenas {inicio_estoque}–{fim_estoque} tem os dois lados observados, e é por isso que a "
        "janela do índice Q é um subconjunto dela.",
    ),
    (
        "Ano em curso",
        "{ano_em_curso} é um ano civil incompleto na data da extração — o estoque de dezembro "
        "ainda não existe. Ele aparece marcado em todas as séries anuais e fica fora do traçado "
        "principal. Sem a marca, o último ponto leria como queda de atividade.",
    ),
    (
        "Categorias administrativas",
        "A coluna de nacionalidade traz rótulos que não são nacionalidades — `-`, "
        "`NAO ESPECIFICADO`, `NATURALIDADE BRASILEIRA`. As {n_categorias_excluidas} linhas com "
        "esses rótulos saem antes do funil e não entram em nenhuma contagem do painel.",
    ),
    (
        "Reprodutibilidade e integridade",
        "Semente {semente}, {repeticoes} reamostragens e parâmetros congelados no config da "
        "execução. O painel falha alto quando um dos {n_artefatos} artefatos falta ou chega com "
        "esquema diferente, em vez de exibir um número incerto em silêncio.",
    ),
)

PONTE = (
    "O problema do projeto pede uma leitura da inserção laboral dos imigrantes que nenhuma das "
    "duas bases responde isoladamente: a RAIS não sabe quem é imigrante sem o recorte de "
    "nacionalidade, e o SISMIGRA não sabe se a pessoa trabalha. **O método é a resposta a essa "
    "restrição** — comparar participações em vez de contagens, declarar o piso em vez de "
    "escondê-lo na amostra, e recusar a leitura do topo do ranking de Q. O que ele entrega é um "
    "gradiente associativo robusto entre representação e remuneração; o que ele declara não "
    "entregar é uma medida de integração bem-sucedida."
)

NOTA_FUNIL = (
    "Os três filtros são cumulativos e a ordem importa: uma nacionalidade só entra na etapa "
    "seguinte se passou pela anterior. Não há imputação em nenhuma etapa — uma nacionalidade "
    "com Q indefinido não é preenchida, é excluída."
)

NOTA_COBERTURA = (
    "As quatro linhas não são quatro recortes do mesmo dado: são quatro unidades diferentes, "
    "com coberturas diferentes. **Nenhuma aba soma duas delas**, e a comparação de nível entre "
    "linhas não é válida."
)

NOTA_PISOS = (
    "Um piso não é filtro de tela: é o mínimo de massa para que uma razão ou um índice de "
    "concentração signifiquem algo. Abaixo deles a estatística existe e é vazia de conteúdo — "
    "uma nacionalidade com um único registro tem HHI igual a 1 porque está numa UF só."
)

NOTA_DECISOES = (
    "Cada decisão abaixo foi tomada contra uma alternativa que parecia razoável. O registro "
    "fica aqui para que a escolha não pareça a única possível, nem a mais natural."
)

NOTA_NAO_FAZ = (
    "A lista do que o painel se recusa a fazer é parte do resultado: cada linha corresponde a "
    "uma leitura que os dados permitiriam mas não sustentariam."
)

EVIDENCIAS: tuple[Evidencia, ...] = ()


def rotulo_curto(evidencia: Evidencia) -> str:
    """A aba não declara evidências, então não há rótulo de seletor a produzir."""
    raise ValueError(
        f"a aba Método não declara evidências; foi pedido rótulo para {evidencia.chave!r}. "
        f"Declare a evidência em EVIDENCIAS ou remova a chamada."
    )
