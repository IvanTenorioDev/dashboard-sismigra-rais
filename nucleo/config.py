"""Configuração central do dashboard.

Nenhum valor metodológico fica solto dentro das páginas: pisos, rótulos e cores
mudam aqui e se propagam para todo o app.
"""

from __future__ import annotations

import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def pasta_dados() -> Path:
    """Pasta dos artefatos da Q7.

    Resolvida em tempo de chamada, não na importação: assim a variável de ambiente
    `DASHBOARD_DADOS` pode ser definida depois, o que os testes precisam para apontar
    para dados sintéticos sem tocar na pasta real.
    """
    return Path(os.environ.get("DASHBOARD_DADOS", RAIZ / "dados" / "q7"))

ARQUIVOS_PERFIL: dict[str, str] = {
    "configuracao": "q7_config.json",
    "perfis": "q7_perfis.csv",
    "pca": "q7_pca.csv",
    "cargas": "q7_cargas.csv",
    "variancia": "q7_variancia.csv",
    "diagnostico": "q7_diagnostico_k.csv",
    "regioes": "q7_regioes.csv",
    "arvores": "q7_arvores.csv",
}

# Artefatos com grão temporal ou territorial, escritos pela FASE 9b. A chave é o nome
# curto usado no código; o arquivo é o que o notebook escreve. Os prefixos q1/q2/q3/q5
# são da pergunta que cada um atende, não do formato.
ARQUIVOS_TEMPORAIS: dict[str, str] = {
    "serie_anual": "q1_serie_anual.csv",
    "resumo_anual": "q1_resumo_por_ano.csv",
    "uf_ano": "q2_uf_ano.csv",
    "concentracao_territorial": "q2_concentracao.csv",
    "uf_top": "q2_uf_top_nacionalidades.csv",
    "fluxo": "q3_fluxo_ano.csv",
    "persistencia": "q5_persistencia.csv",
}

ARQUIVOS: dict[str, str] = {**ARQUIVOS_PERFIL, **ARQUIVOS_TEMPORAIS}

COLUNAS_ATRIBUTOS: tuple[str, ...] = (
    "salario_medio_sm",
    "pct_superior",
    "pct_feminino",
    "pct_faixa_25_39",
    "hhi_setorial",
    "pct_tempo_parcial",
)

ROTULOS_ATRIBUTOS: dict[str, str] = {
    "salario_medio_sm": "Salário médio",
    "pct_superior": "Superior completo",
    "pct_feminino": "Mulheres",
    "pct_faixa_25_39": "Faixa 25–39 anos",
    "hhi_setorial": "Concentração setorial",
    "pct_tempo_parcial": "Tempo parcial",
}

UNIDADES_ATRIBUTOS: dict[str, str] = {
    "salario_medio_sm": "SM",
    "pct_superior": "%",
    "pct_feminino": "%",
    "pct_faixa_25_39": "%",
    "hhi_setorial": "índice",
    "pct_tempo_parcial": "%",
}

ATRIBUTOS_PERCENTUAIS: tuple[str, ...] = (
    "pct_superior",
    "pct_feminino",
    "pct_faixa_25_39",
    "pct_tempo_parcial",
)

AZUL_GRAFICO = "#4C78A8"
LARANJA_GRAFICO = "#F58518"
VERDE_GRAFICO = "#54A24B"
ROXO_GRAFICO = "#B279A2"

# Paleta das regiões da Q7, na ordem em que os grupos são numerados.
CORES_REGIAO: dict[int, str] = {
    1: AZUL_GRAFICO,
    2: LARANJA_GRAFICO,
    3: VERDE_GRAFICO,
    4: ROXO_GRAFICO,
}
AZUL = "#1F3A5F"
LARANJA = "#D97A2B"
CINZA = "#6B7785"
BORDA = "#E3E7EB"
FUNDO_PONTE = "#FDF7F1"
ROTULO_PONTE = "#8A5A1F"

# Estilo da tabela de conteúdo, compartilhado pelas duas telas. Fica aqui, e não num dos
# renderizadores, porque os dois montam a mesma tabela: o painel estático em
# `gerador/componentes.py` e a aplicação, que exibe o mesmo HTML.
CSS_TABELA = f"""
table.tabela {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
table.tabela th {{
  text-align: left;
  color: {CINZA};
  font-size: 11px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border-bottom: 1px solid {BORDA};
  padding: 8px 10px;
}}
table.tabela td {{ padding: 7px 10px; border-bottom: 1px solid #F0F2F5; }}
"""

# Quantas nacionalidades a tabela de rastreabilidade exibe por padrão.
NACIONALIDADES_NA_TABELA = 60

# Pisos de massa declarados. Não são filtros de tela: são o mínimo para que uma razão ou
# um índice de concentração signifiquem alguma coisa. Abaixo deles a estatística existe e
# é vazia de conteúdo — uma nacionalidade com um único registro tem HHI igual a 1 porque
# está numa UF só, e essa é uma afirmação sobre a amostra, não sobre o território.
PISO_REGISTROS = 500
PISO_VINCULOS = 100

# A navegação do slide 11: abas por pergunta, não por técnica.
ABA_Q1 = "Q1 Presença"
ABA_Q2 = "Q2 Território"
ABA_Q3 = "Q3 Registros"
ABA_Q4 = "Q4 Representação"
ABA_Q5 = "Q5 Persistência"
ABA_Q6 = "Q6 Atributos"
ABA_Q7 = "Q7 Multivariado"
ABA_METODO = "Método & limites"
ABAS: tuple[str, ...] = (
    ABA_Q1,
    ABA_Q2,
    ABA_Q3,
    ABA_Q4,
    ABA_Q5,
    ABA_Q6,
    ABA_Q7,
    ABA_METODO,
)

# Números congelados na validação v5. Servem para CONFERIR a execução do notebook,
# nunca para desenhar gráficos — o app exibe o que veio do arquivo, não estes valores.
#
# BLOQUEANTES: a análise depende diretamente destes. Divergir aqui invalida a execução,
# porque significa que a base ou a clusterização são outras.
CONGELADOS_V5: dict[str, object] = {
    "elegiveis": 101,
    "k_escolhido": 3,
    "ari_kmeans_ward": 0.632,
    "tamanhos_regioes": [57, 20, 24],
    "salario_por_regiao": [1.680, 6.738, 1.592],
    "superior_por_regiao": [0.308, 0.716, 0.201],
}

# INFORMATIVOS: registrados no guia, sem efeito sobre a análise.
# O funil deste notebook chega a 185/185 onde o guia registra 184/183. A diferença são
# nacionalidades presentes nas duas fontes que não alcançam o piso de vínculos —
# nenhuma delas entra nos 101 elegíveis. Conferido em 05/10/2026: com 102 linhas o
# resultado era outro (k=2, regiões 42/60); com 101 tudo o que importa bate.
REFERENCIA_INFORMATIVA_V5: dict[str, object] = {
    "universo_com_Q_comparavel": 184,
    "com_os_6_atributos": 183,
}

TOLERANCIA_CONFERENCIA = 0.005
TOLERANCIA_MEDIA = 0.01
