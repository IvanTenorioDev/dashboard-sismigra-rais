"""Narrativa da aba Q6 — o perfil dos vínculos formais de cada nacionalidade.

Mesmo registro técnico da Q4 e da Q7: leitor com formação quantitativa, sem didatismo e
sem metáfora onde cabe o termo. Nenhum número é escrito à mão — todos vêm de
`Artefatos.valores_q6_para_texto()` e são preenchidos por `nucleo.textos.preencher`.
"""

from __future__ import annotations

from nucleo.textos import Evidencia

RESPOSTA_SINTETICA = (
    "Os vínculos formais de cada nacionalidade são descritos por {n_atributos} atributos, e "
    "todos os {n_atributos} estão observados para as {n_elegiveis} — não há perfil "
    "incompleto na base. O perfil mediano é de {salario_mediano} salário mínimo, "
    "{superior_mediano} com ensino superior, {mulheres_mediano} de mulheres e "
    "{faixa_25_39_mediano} na faixa de 25 a 39 anos. **Mas a mediana esconde a distância "
    "entre os extremos**: a remuneração vai de {salario_minimo} a {salario_maximo} salários "
    "mínimos, e a escolaridade superior de {superior_minimo} a {superior_maximo}. E os seis "
    "atributos não medem a mesma coisa — remuneração e escolaridade caminham juntas numa "
    "associação de postos de {associacao_salario_superior}, enquanto a concentração setorial "
    "é o atributo mais isolado, com no máximo {isolamento_hhi} de associação com qualquer "
    "outro."
)

LIMITES: tuple[tuple[str, str], ...] = (
    (
        "O que os seis atributos cobrem",
        "Remuneração, escolaridade superior, composição de gênero, estrutura etária, "
        "concentração setorial e incidência de tempo parcial. São atributos do **vínculo**, "
        "calculados sobre o estoque da RAIS-CTPS — não descrevem a população imigrante como "
        "um todo, e sim os vínculos formais que ela mantém.",
    ),
    (
        "Cobertura",
        "{n_atributos} de {n_atributos} atributos observados para as {n_elegiveis} "
        "nacionalidades elegíveis. A cobertura é total **por construção**: uma nacionalidade "
        "com qualquer atributo não observado não entra no elegível, e por isso não aparece "
        "em nenhuma distribuição desta aba.",
    ),
    (
        "Mediana de grupo, não de pessoa",
        "Cada valor é uma mediana ou proporção calculada sobre os vínculos daquela "
        "nacionalidade. A nacionalidade mediana não é o imigrante mediano: são duas "
        "estatísticas com unidades diferentes, e confundi-las é falácia ecológica.",
    ),
    (
        "Configuração, não juízo",
        "Nenhum dos seis atributos é bom ou ruim em si. Remuneração alta e concentração "
        "setorial alta são descrições do estoque de vínculos, não medidas de integração ou "
        "de sucesso.",
    ),
    (
        "Associação, não causa",
        "A associação de postos de {associacao_salario_superior} entre remuneração e "
        "escolaridade mede covarição nesta amostra. Ela não estima o efeito de estudar mais, "
        "e não distingue seleção de retorno.",
    ),
    (
        "Recorte temporal",
        "Os seis atributos são médias da janela 2023–2025. Nada nesta aba descreve mudança "
        "ao longo do tempo: a leitura de fluxo e a de persistência são outras perguntas do "
        "projeto.",
    ),
)

PONTE = (
    "A Q4 estabeleceu que a sobrerrepresentação nos vínculos formais coincide com menor "
    "remuneração. A Q6 mostra **com que configuração de atributos** isso acontece: "
    "remuneração e escolaridade superior se movem juntas, e é esse par acoplado — não os "
    "seis atributos isolados — que organiza a diferenciação entre as nacionalidades. É essa "
    "configuração conjunta que a Q7 testa como partição, e é por isso que dois componentes "
    "bastam para resumir seis atributos."
)

ROTULOS_CURTOS: dict[str, str] = {
    "perfil": "Perfil e dispersão",
    "acoplamento": "Acoplamento",
    "remuneracao": "Remuneração × qualificação",
    "nacionalidades": "Nacionalidades",
}

EVIDENCIAS: tuple[Evidencia, ...] = (
    Evidencia(
        chave="perfil",
        rotulo="Perfil e dispersão",
        titulo="Distribuição dos seis atributos entre as nacionalidades",
        leitura=(
            "Cada painel é um atributo, com as {n_elegiveis} nacionalidades visíveis como "
            "pontos e a caixa marcando a mediana e o intervalo interquartil. **Nenhum dos "
            "seis é aproximadamente constante** — todos separam nacionalidades. A "
            "concentração setorial é a mais larga, chegando a {hhi_maximo} em "
            "{nacionalidade_hhi_maximo} contra uma mediana de {hhi_mediano}. O tempo "
            "parcial é o mais concentrado junto de zero, com mediana de {parcial_mediano} e "
            "máximo de {parcial_maximo} em {nacionalidade_parcial_maximo}."
        ),
    ),
    Evidencia(
        chave="acoplamento",
        rotulo="Acoplamento",
        titulo="Associação de postos entre os seis atributos",
        leitura=(
            "A matriz responde se os seis atributos medem coisas distintas. **Não "
            "inteiramente**: remuneração e escolaridade superior têm associação de postos de "
            "{associacao_salario_superior}, praticamente redundantes entre si, e o tempo "
            "parcial acompanha as duas. No extremo oposto, a concentração setorial é o "
            "atributo mais isolado, com no máximo {isolamento_hhi} de associação. É esse "
            "contraste que explica por que a Q7 resume o perfil em dois componentes — e por "
            "que a concentração setorial quase não contribui para eles."
        ),
    ),
    Evidencia(
        chave="remuneracao",
        rotulo="Remuneração × qualificação",
        titulo="Remuneração contra qualificação, com as medianas de referência",
        leitura=(
            "Os dois atributos mais acoplados, um contra o outro, com as medianas — "
            "{salario_mediano} salário mínimo e {superior_mediano} de escolaridade — cruzando "
            "o plano em quatro quadrantes. A diagonal é nítida: as nacionalidades de maior "
            "remuneração são as de maior escolaridade, e as duas regiões extremas da Q7 "
            "ocupam quadrantes opostos. O ponto isolado no topo é "
            "{nacionalidade_salario_maximo}, com {salario_maximo} salários mínimos — "
            "{razao_salario_maximo} vezes a mediana."
        ),
    ),
    Evidencia(
        chave="nacionalidades",
        rotulo="Nacionalidades",
        titulo="Perfil das nacionalidades elegíveis",
        leitura=(
            "Os seis atributos de cada uma das {n_elegiveis} nacionalidades, ordenadas por "
            "remuneração. É o material de consulta da aba: as colunas de percentual são "
            "proporções dos vínculos daquele grupo, não da população."
        ),
    ),
)

EVIDENCIA_PADRAO = EVIDENCIAS[0].chave


def rotulo_curto(evidencia: Evidencia) -> str:
    """Rótulo compacto de uma evidência da Q6, para o seletor."""
    return ROTULOS_CURTOS[evidencia.chave]
