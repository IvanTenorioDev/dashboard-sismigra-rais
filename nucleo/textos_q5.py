"""Narrativa da aba Q5 — a persistência dos registros ao longo do tempo.

A resposta é contraintuitiva em relação ao que a pergunta sugere: a presença **se
sustenta**, e a cauda de presença curta é um artefato de volume. Demonstrar isso exige
separar observação única de interrupção real, e é o que as duas figuras fazem.
"""

from __future__ import annotations

from nucleo.textos import Evidencia

RESPOSTA_SINTETICA = (
    "**Sustentam — e a maioria sustenta por inteiro.** Das {n_total} nacionalidades com vínculo "
    "formal na série, {n_completas} aparecem nos {maximo_anos} anos ({pct_completas}), e a "
    "mediana é de {mediana_anos} anos de presença. A cauda curta existe, mas quase não resiste a "
    "exame: as {n_curtas} nacionalidades com três anos ou menos têm no máximo "
    "{maior_volume_curtas} registros ativos no último ano, e **nenhuma passa do piso de "
    "{piso_registros}**. Não são casos de presença interrompida — são observações únicas, "
    "mantidas na base mas sem massa para descrever trajetória. Entre as {n_sustentadas} que "
    "passam do piso, aparece outro fenômeno: {n_com_lacuna} têm buraco no meio da série "
    "({pct_com_lacuna}), ou seja, aparecem, somem e voltam."
)

LIMITES: tuple[tuple[str, str], ...] = (
    (
        "O piso de {piso_registros} registros",
        "Das {n_total} nacionalidades, {n_sustentadas} passam do piso e {n_removidas} não. Sem "
        "ele, a cauda curta — {n_curtas} nacionalidades com três anos ou menos e no máximo "
        "{maior_volume_curtas} registros ativos — seria lida como falta de persistência, quando é "
        "falta de massa para observar.",
    ),
    (
        "Anos distintos, não anos corridos",
        "A contagem é de anos **distintos** com vínculo, não de um intervalo contínuo. É por isso "
        "que a segunda figura existe: ela separa quem aparece em todos os anos desde a estreia de "
        "quem tem buracos no meio — duas situações que a contagem sozinha confunde.",
    ),
    (
        "Cobertura da RAIS",
        "A série de vínculos vai de {primeiro_ano} a {ultimo_ano}. Uma nacionalidade com "
        "{maximo_anos} anos estreou no primeiro ano da série: não se pode afirmar que chegou ali, "
        "apenas que já estava.",
    ),
    (
        "Presença não é permanência",
        "O que se mede é a existência de vínculo formal em cada ano, por nacionalidade. Isso não "
        "significa que as mesmas pessoas ficaram — a unidade é o agregado, e a base não tem "
        "identificador de indivíduo.",
    ),
    (
        "Lacuna tem muitas causas",
        "Um ano sem vínculo naquela nacionalidade pode ser ausência de trabalhadores, saída do "
        "país, mudança de nacionalidade declarada ou volume abaixo do que a agregação capta. Esta "
        "aba identifica a lacuna; não a explica.",
    ),
)

PONTE = (
    "A Q1 mediu o crescimento do estoque; a Q5 mede do que ele é feito. A resposta é que a maior "
    "parte da presença se sustenta ano a ano, e que a cauda curta é um artefato de volume, não um "
    "fenômeno de rotatividade. É isso que autoriza tratar a janela fixa das abas Q6 e Q7 como "
    "estável, e é por isso que o piso de vínculos da elegibilidade não descarta nenhuma "
    "nacionalidade de presença longa."
)

ROTULOS_CURTOS: dict[str, str] = {
    "distribuicao": "Anos de presença",
    "lacunas": "Presença contínua",
    "anos": "Nacionalidades",
}

EVIDENCIAS: tuple[Evidencia, ...] = (
    Evidencia(
        chave="distribuicao",
        rotulo="Anos de presença",
        titulo="Anos de presença por nacionalidade, com e sem o piso",
        leitura=(
            "A barra alta em {maximo_anos} anos é a moda, e não um artefato de borda: "
            "{n_completas} das {n_total} nacionalidades aparecem em todos os anos da série. A "
            "camada azul são as que passam do piso; a cinza, o conjunto inteiro. A diferença "
            "entre as duas é o que o piso retira, e **ela se concentra à esquerda**: as "
            "{n_curtas} nacionalidades com três anos ou menos caem todas abaixo de "
            "{piso_registros} registros, e o maior volume entre elas é de {maior_volume_curtas}. "
            "Sem essa marca, a distribuição sugeriria presença curta generalizada."
        ),
    ),
    Evidencia(
        chave="lacunas",
        rotulo="Presença contínua",
        titulo="Presença contínua ou interrompida",
        leitura=(
            "A diagonal marca a presença contínua: quem está sobre ela aparece em **todos** os "
            "anos desde a estreia. Os pontos abaixo têm buracos no meio — apareceu, sumiu e "
            "voltou. São {n_com_lacuna} casos entre as nacionalidades da amostra "
            "({pct_com_lacuna}), a maioria deles com volume baixo, marcados com losango vazado. É "
            "esta figura que separa 'presença curta' de 'presença interrompida', que a contagem de "
            "anos confunde."
        ),
    ),
    Evidencia(
        chave="anos",
        rotulo="Nacionalidades",
        titulo="Persistência por nacionalidade",
        leitura=(
            "O material de consulta da aba: anos com vínculo, primeiro e último ano, volume no "
            "último ano e o mesmo para o lado dos registros. Ordenado pelos anos de presença, o "
            "corte entre a cauda curta e o corpo da distribuição fica visível na própria lista."
        ),
    ),
)

EVIDENCIA_PADRAO = EVIDENCIAS[0].chave


def rotulo_curto(evidencia: Evidencia) -> str:
    """Rótulo compacto de uma evidência da Q5, para o seletor."""
    return ROTULOS_CURTOS[evidencia.chave]
