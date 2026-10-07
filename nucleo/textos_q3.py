"""Narrativa da aba Q3 — o fluxo de registros ano a ano.

Duas armadilhas de leitura dominam esta aba e as duas estão declaradas nos limites: 2017
não existe na fonte (ausência, não zero) e {ano_em_curso} é um ano civil incompleto na
data da extração. Sem isso, o gráfico conta uma história que os dados não contam.
"""

from __future__ import annotations

from nucleo.textos import Evidencia

RESPOSTA_SINTETICA = (
    "O fluxo cresce de {registros_primeiro} registros em {primeiro_ano_fluxo} para "
    "{registros_ultimo_fechado} em {maior_ano} — {crescimento_fluxo} em quinze anos, com "
    "formato irregular: sobe até {queda_ano_anterior}, cai {queda_percentual} em {queda_ano} — "
    "a maior queda da série — e retoma acima do patamar anterior. **Mas a composição muda mais "
    "que o volume.** Desde {primeiro_ano_amparo}, quando a tipologia de amparos passou a ser "
    "publicada, a acolhida recua de {pct_acolhida_primeiro} para {pct_acolhida_ultimo} do fluxo "
    "e o amparo por trabalho sobe de {pct_trabalho_primeiro} para {pct_trabalho_ultimo}. No "
    "mesmo período a participação de mulheres no fluxo vai de {pct_feminino_primeiro} a "
    "{pct_feminino_ultimo}. O fluxo que entra **não é o mesmo** que entrava há cinco anos."
)

LIMITES: tuple[tuple[str, str], ...] = (
    (
        "{lacunas} não existe",
        "Não há registro com data de registro em {lacunas} no recorte, e isso **não é zero**: é "
        "ausência da fonte. A malha do eixo é construída sobre o intervalo completo dos anos "
        "justamente para que a lacuna apareça como lacuna, em vez de ligar "
        "{queda_ano_anterior} a 2018 numa continuidade que não existiu.",
    ),
    (
        "{ano_em_curso} está em curso",
        "A extração foi feita antes do fim do ano civil, então {ano_em_curso} tem menos meses "
        "que os outros. Ele sai marcado e fora do traçado principal: o valor de "
        "{ultimo_ano_fluxo} não se compara ao de {maior_ano}. A regra é declarada no config do "
        "notebook — a tela não a infere.",
    ),
    (
        "Tipologia só a partir de {primeiro_ano_amparo}",
        "O campo de tipo de amparo não existe nos arquivos anteriores a {primeiro_ano_amparo}. "
        "Os anos anteriores ficam **vazios** no gráfico de composição, e não em zero — zero "
        "afirmaria que nenhum registro foi por acolhida, quando o que falta é o campo.",
    ),
    (
        "Amparo não é motivo",
        "A tipologia classifica o amparo legal do registro, não a intenção de quem migra. Uma "
        "pessoa com amparo por trabalho pode ter vindo por outros motivos; uma com acolhida pode "
        "estar empregada. O estoque de vínculos é outra medida, e está na Q1.",
    ),
    (
        "Fluxo não é estoque",
        "Os registros contados aqui têm data de registro no ano. Eles não se somam ao estoque de "
        "dezembro — e é a diferença entre os dois que a razão da Q1 mede.",
    ),
)

PONTE = (
    "A Q1 e a Q2 mediram o resultado: quanto da presença vira vínculo, e onde. A Q3 mostra a "
    "entrada — um fluxo que quadruplica e **muda de composição antes de mudar de tamanho**, com "
    "a acolhida perdendo peso para o amparo por trabalho e a participação feminina subindo. É "
    "essa mudança de perfil do que entra que a Q6 descreve já no lado dos vínculos, e que a Q5 "
    "testa quanto tempo se sustenta."
)

ROTULOS_CURTOS: dict[str, str] = {
    "fluxo": "Fluxo anual",
    "amparo": "Composição",
    "anos": "Série anual",
}

EVIDENCIAS: tuple[Evidencia, ...] = (
    Evidencia(
        chave="fluxo",
        rotulo="Fluxo anual",
        titulo="Registros por ano, com a lacuna e o ano em curso marcados",
        leitura=(
            "O vazio entre 2016 e 2018 é a lacuna de {lacunas} — o eixo é fixado no intervalo "
            "completo dos anos justamente para deixá-la visível. A faixa sombreada marca "
            "{ano_em_curso}, que a extração pegou em curso. O formato da série importa: o pico de "
            "{maior_registros} registros é {maior_ano}, e a maior queda é {queda_percentual} em "
            "{queda_ano}, sobre {queda_ano_anterior}."
        ),
    ),
    Evidencia(
        chave="amparo",
        rotulo="Composição",
        titulo="Composição do fluxo por tipo de amparo",
        leitura=(
            "Só há cinco anos fechados, porque a tipologia nasce em {primeiro_ano_amparo} — antes "
            "disso o campo não existe e o gráfico fica vazio, não zero. A acolhida sai de "
            "{pct_acolhida_primeiro} e chega a {pct_acolhida_ultimo}, com pico de "
            "{pico_acolhida} em {pico_acolhida_ano}. O amparo por trabalho faz o caminho inverso "
            "em nível — de {pct_trabalho_primeiro} para {pct_trabalho_ultimo} — e continua sendo "
            "uma fração pequena do fluxo. O marcador vazado é {ano_em_curso}: a proporção de um "
            "ano parcial é observável, mas não é comparável à de um ano fechado."
        ),
    ),
    Evidencia(
        chave="anos",
        rotulo="Série anual",
        titulo="Fluxo anual consolidado",
        leitura=(
            "O material de consulta da aba: registros, origens presentes, registros com tipologia "
            "e a composição do amparo, ano a ano. As colunas de percentual ficam vazias nos anos "
            "sem tipologia publicada — ausência, de novo, não zero. A participação de mulheres "
            "cresce ao longo de toda a série, de {pct_feminino_primeiro} em {primeiro_ano_fluxo} "
            "a {pct_feminino_ultimo} em {maior_ano}, e é a única coluna de composição disponível "
            "em todos os anos."
        ),
    ),
)

EVIDENCIA_PADRAO = EVIDENCIAS[0].chave


def rotulo_curto(evidencia: Evidencia) -> str:
    """Rótulo compacto de uma evidência da Q3, para o seletor."""
    return ROTULOS_CURTOS[evidencia.chave]
