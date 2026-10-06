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

ARQUIVOS_Q7: dict[str, str] = {
    "configuracao": "q7_config.json",
    "perfis": "q7_perfis.csv",
    "pca": "q7_pca.csv",
    "cargas": "q7_cargas.csv",
    "variancia": "q7_variancia.csv",
    "diagnostico": "q7_diagnostico_k.csv",
    "regioes": "q7_regioes.csv",
    "arvores": "q7_arvores.csv",
}

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

CORES_REGIAO: dict[int, str] = {1: "#4C78A8", 2: "#F58518", 3: "#54A24B", 4: "#B279A2"}
AZUL = "#1F3A5F"
LARANJA = "#D97A2B"
CINZA = "#6B7785"

PISO_HHI = 500
PISO_PERSISTENCIA = 500
PISO_PERFIL = 100

# Quantas nacionalidades a tabela de rastreabilidade exibe por padrão.
NACIONALIDADES_NA_TABELA = 60

# A navegação do slide 11: abas por pergunta, não por técnica.
ABA_Q4 = "Q4 Representação"
ABA_Q7 = "Q7 Multivariado"
ABAS: tuple[str, ...] = (
    "Q1 Presença",
    "Q2 Território",
    "Q3 Registros",
    ABA_Q4,
    "Q5 Persistência",
    "Q6 Atributos",
    ABA_Q7,
    "Método & limites",
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
