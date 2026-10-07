"""Narrativa da aba Q2 — onde a presença se concentra e quão concentrada ela é.

O achado desta aba não é "São Paulo concentra": é que a UF que mais registra **não é** a
que mais emprega, e que a distância entre as duas é o que dá conteúdo ao índice Q. A
narrativa sustenta isso sem tratar os dois conceitos de UF como um só.
"""

from __future__ import annotations

from nucleo.textos import Evidencia

RESPOSTA_SINTETICA = (
    "A presença está **concentrada e mal distribuída entre os dois lados**. As três UFs com "
    "mais registros respondem por {top3_registros} do país, e {uf_mais_registros} sozinha por "
    "{pct_registros_uf_maior} — mas pesa {pct_vinculos_da_uf_maior} dos vínculos formais. No "
    "outro extremo, {uf_mais_vinculos} concentra {pct_vinculos_uf_maior} dos vínculos com "
    "apenas {pct_registros_da_uf_com_mais_vinculos} dos registros. Essa assimetria tem um "
    "número: a razão do país é de {razao_pais} registros por vínculo, e ela vai de "
    "{razao_menor} em {uf_razao_menor} a {razao_maior} em {uf_razao_maior} — uma diferença de "
    "quase nove vezes entre a UF mais e a menos convertida. **Concentração de presença e "
    "concentração de emprego formal não são a mesma geografia.**"
)

LIMITES: tuple[tuple[str, str], ...] = (
    (
        "Dois conceitos de UF",
        "O SISMIGRA registra a **residência**; a RAIS, o **estabelecimento** onde o vínculo "
        "existe. As duas contagens nunca são somadas nem tratadas como a mesma UF — a divergência "
        "entre elas **é** o achado da aba, e apagá-la apagaria a resposta.",
    ),
    (
        "Piso de {piso_registros} registros",
        "A distribuição de concentração cobre {n_sustentadas} das {n_no_ano} nacionalidades "
        "presentes em {ano_territorio}. As outras {n_removidas} ficam de fora porque uma "
        "nacionalidade com um registro tem HHI igual a 1 por construção — está em uma UF porque "
        "tem uma observação só. Incluí-las produziria a leitura falsa de que quase todas as "
        "origens são territorialmente concentradas.",
    ),
    (
        "O que o HHI mede",
        "Ele mede concentração **entre UFs**, e nada mais. Vai de {hhi_minimo} a {hhi_maximo} na "
        "amostra retida, com mediana de {hhi_mediano}. Não mede volume: uma nacionalidade pequena "
        "e dispersa tem HHI baixo e é irrelevante em tamanho.",
    ),
    (
        "Um único ano",
        "A comparação entre os dois lados existe apenas em {ano_territorio}, o último ano com "
        "estoque e vínculo observados na mesma linha. Nada aqui descreve mudança territorial ao "
        "longo do tempo.",
    ),
    (
        "Participação não é fluxo",
        "As participações são de estoque — vínculos em 31/12, registros em dezembro. Uma UF com "
        "participação alta pode estar recebendo pouca gente nova e apenas acumulando; o fluxo "
        "anual é a matéria da Q3.",
    ),
)

PONTE = (
    "A Q1 mostrou que a conversão de presença em vínculo formal sobe. A Q2 mostra **onde** ela "
    "sobe — e não é onde a presença é maior. São Paulo concentra um terço dos registros e um "
    "quinto dos vínculos; Santa Catarina faz o inverso. É essa distância que a Q4 mede por "
    "nacionalidade, e é por isso que o índice Q não se lê como ranking de tamanho."
)

ROTULOS_CURTOS: dict[str, str] = {
    "ufs": "Participação",
    "razao": "Razão",
    "hhi": "Concentração",
    "tops": "Top por UF",
}

EVIDENCIAS: tuple[Evidencia, ...] = (
    Evidencia(
        chave="ufs",
        rotulo="Participação",
        titulo="Participação de cada UF nos dois lados",
        leitura=(
            "As barras são participações, não contagens: o país tem cerca de {razao_pais} "
            "registros por vínculo, e comparar níveis mostraria apenas isso. A ordenação pelos "
            "registros **não é** a ordenação pelos vínculos, e a inversão acontece já no topo: "
            "{uf_mais_registros} lidera em registros com {pct_registros_uf_maior} e responde por "
            "{pct_vinculos_da_uf_maior} dos vínculos, enquanto {uf_mais_vinculos} sustenta "
            "{pct_vinculos_uf_maior} dos vínculos com {pct_registros_da_uf_com_mais_vinculos} dos "
            "registros. Nas UFs de fronteira e de rota recente o par laranja–azul se abre; nas de "
            "colonização antiga, se fecha."
        ),
    ),
    Evidencia(
        chave="razao",
        rotulo="Razão",
        titulo="Registros ativos por vínculo formal, em cada UF",
        leitura=(
            "A razão do país é uma só, {razao_pais}, e não vale para lugar nenhum em particular: "
            "ela vai de {razao_menor} em {uf_razao_menor} a {razao_maior} em {uf_razao_maior}. "
            "Nas UFs do topo há muito registro para pouco vínculo — **presença que não se "
            "converte em emprego formal**. Nas de baixo, o oposto: o estoque migratório é pequeno "
            "e sustenta uma massa de vínculos desproporcional. É esta figura que dá conteúdo à "
            "pergunta 'proporcional a quê?', que a Q4 responde por nacionalidade."
        ),
    ),
    Evidencia(
        chave="hhi",
        rotulo="Concentração",
        titulo="Concentração territorial por nacionalidade",
        leitura=(
            "A distribuição é larga e assimétrica: mediana de {hhi_mediano}, mínimo de "
            "{hhi_minimo} e máximo de {hhi_maximo}. O limite inferior mostra nacionalidades "
            "espalhadas por muitas UFs; o superior, nacionalidades que praticamente só existem em "
            "uma. A distribuição cobre {n_sustentadas} das {n_no_ano} nacionalidades presentes em "
            "{ano_territorio} — as outras {n_removidas} ficam fora pelo piso de "
            "{piso_registros} registros, e a razão está nos limites desta aba."
        ),
    ),
    Evidencia(
        chave="tops",
        rotulo="Top por UF",
        titulo="Nacionalidades dominantes em cada UF",
        leitura=(
            "As três origens com mais registros em cada UF, com a participação de cada uma no "
            "total local. **A concentração por origem varia muito mais entre UFs do que a média "
            "sugere**: em {uf_primeira_mais_pesada} a primeira colocada responde por "
            "{peso_primeira_maximo} dos registros locais, enquanto em {uf_primeira_mais_diluida} "
            "ela fica em {peso_primeira_minimo}. É o material de consulta da aba."
        ),
    ),
)

EVIDENCIA_PADRAO = EVIDENCIAS[0].chave


def rotulo_curto(evidencia: Evidencia) -> str:
    """Rótulo compacto de uma evidência da Q2, para o seletor."""
    return ROTULOS_CURTOS[evidencia.chave]
