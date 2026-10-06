"""Validação do dashboard da Q7.

Dois modos:

* **(padrão)** gera artefatos **sintéticos** em diretório temporário e renderiza todas
  as figuras. Exercita a leitura e os gráficos sem depender dos dados reais.
* **--conferir** compara os artefatos reais de `dados/q7/` com os números congelados na
  validação v5 (101 elegíveis, k = 3, ARI 0,632, regiões 57/20/24).

Os dados do modo padrão são fabricados para exercitar o código e **nunca** são gravados
na pasta do projeto.

Uso:
    .venv/bin/python testes/validar.py
    .venv/bin/python testes/validar.py --conferir
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from nucleo import graficos, textos  # noqa: E402
from nucleo.config import (  # noqa: E402
    ABA_Q7,
    ABAS,
    COLUNAS_ATRIBUTOS,
    CONGELADOS_V5,
    REFERENCIA_INFORMATIVA_V5,
    TOLERANCIA_CONFERENCIA,
    TOLERANCIA_MEDIA,
)
from nucleo.dados import DadosQ7, ArtefatosAusentes, carregar, pasta_dados  # noqa: E402
from paginas.q7_multivariado import FIGURAS  # noqa: E402

SEMENTE_FIXTURE = 42
TAMANHOS_REGIOES = {1: 57, 2: 20, 3: 24}
PERFIS_ESPERADOS = {
    1: {"salario": 1.68, "superior": 0.308, "Q": 0.862},
    2: {"salario": 6.74, "superior": 0.716, "Q": 0.340},
    3: {"salario": 1.59, "superior": 0.201, "Q": 1.237},
}
REPETICOES = 30


def _gerar_perfis(gerador: np.random.Generator) -> pd.DataFrame:
    linhas = []
    for regiao, tamanho in TAMANHOS_REGIOES.items():
        esperado = PERFIS_ESPERADOS[regiao]
        linhas.append(pd.DataFrame({
            "nacionalidade": [f"Nacao {indice:03d}" for indice in range(regiao * 1000, regiao * 1000 + tamanho)],
            "regiao": regiao,
            "salario_medio_sm": gerador.normal(esperado["salario"], 0.28, tamanho).clip(0.5, 12.0),
            "pct_superior": gerador.normal(esperado["superior"], 0.06, tamanho).clip(0.01, 0.98),
            "pct_feminino": gerador.normal(0.38, 0.08, tamanho).clip(0.02, 0.95),
            "pct_faixa_25_39": gerador.normal(0.52, 0.09, tamanho).clip(0.05, 0.95),
            "hhi_setorial": gerador.normal(0.22, 0.07, tamanho).clip(0.03, 0.90),
            "pct_tempo_parcial": gerador.normal(0.11, 0.05, tamanho).clip(0.0, 0.60),
            "V_total": gerador.integers(120, 9000, tamanho).astype(float),
            "Q_medio": gerador.normal(esperado["Q"], 0.16, tamanho).clip(0.02, 3.0),
            "anos_observados": 3,
        }))
    return pd.concat(linhas, ignore_index=True)


def _componentes_principais(perfis: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    brutos = perfis[list(COLUNAS_ATRIBUTOS)].to_numpy(dtype=float)
    padronizado = (brutos - brutos.mean(axis=0)) / brutos.std(axis=0)
    _, singular, transposta = np.linalg.svd(padronizado, full_matrices=False)
    componentes = transposta[:2]
    coordenadas = pd.DataFrame(padronizado @ componentes.T, columns=["PC1", "PC2"])
    coordenadas.insert(0, "regiao", perfis["regiao"].to_numpy())
    coordenadas.insert(0, "nacionalidade", perfis["nacionalidade"].to_numpy())
    coordenadas["V_total"] = perfis["V_total"].to_numpy()
    cargas = pd.DataFrame(componentes.T, index=list(COLUNAS_ATRIBUTOS), columns=["PC1", "PC2"]).reset_index(names="atributo")
    proporcao = singular**2 / (singular**2).sum()
    variancia = pd.DataFrame({
        "componente": ("PC1", "PC2"),
        "variancia_explicada": proporcao[:2],
        "variancia_acumulada": np.cumsum(proporcao[:2]),
    })
    return coordenadas, cargas, variancia


def _gerar_diagnostico(gerador: np.random.Generator) -> pd.DataFrame:
    menores = {2: 20, 3: 20, 4: 8, 5: 1, 6: 1, 7: 1, 8: 1}
    estabilidade = {2: 0.681, 3: 0.742, 4: 0.690, 5: 0.655, 6: 0.721, 7: 0.688, 8: 0.640}
    silhueta = {2: 0.251, 3: 0.268, 4: 0.286, 5: 0.271, 6: 0.259, 7: 0.248, 8: 0.240}
    linhas = []
    for k in range(2, 9):
        valores = gerador.normal(estabilidade[k], 0.18, REPETICOES).clip(0.0, 1.0)
        linhas.append({
            "k": k,
            "inercia": 471.895 - (k - 2) * 58.0,
            "silhueta": silhueta[k],
            "ari_kmeans_ward": 0.632 if k == 3 else float(gerador.uniform(0.35, 0.60)),
            "menor_grupo": menores[k],
            "tamanhos": "|".join(str(valor) for valor in (57, 20, 24)[: min(k, 3)]),
            "ari_estabilidade": float(valores.mean()),
            "ari_desvio": float(valores.std(ddof=1)),
            "ari_minimo": float(valores.min()),
            "ari_valores": "|".join(f"{valor:.6f}" for valor in valores),
            "admissivel": menores[k] >= 4,
        })
    return pd.DataFrame(linhas)


def _gerar_regioes(perfis: pd.DataFrame) -> pd.DataFrame:
    resumo = perfis.groupby("regiao", observed=True).agg(
        n_nacionalidades=("nacionalidade", "size"),
        **{coluna: (coluna, "median") for coluna in COLUNAS_ATRIBUTOS},
        vinculos_na_janela=("V_total", "sum"),
        Q_mediano=("Q_medio", "median"),
    )
    resumo["participacao_vinculos"] = resumo["vinculos_na_janela"] / resumo["vinculos_na_janela"].sum()
    resumo["exemplos"] = "exemplo 1, exemplo 2, exemplo 3"
    return resumo.round(3).reset_index()


def _gerar_arvores() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "arvore": "A_Q_MAIOR_1", "alvo": "sobre_representada",
            "descricao_alvo": "sobre-representada nos vínculos formais (Q > 1)",
            "casos": 101, "positivos": 41, "negativos": 60,
            "acuracia_cv": 0.880, "desvio_cv": 0.055, "baseline": 0.594,
            "folhas": 2, "atributo_mais_importante": "salario_medio_sm",
            "peso_mais_importante": 0.870, "ganho_minimo_impureza": 0.03,
            "max_profundidade": 3, "min_amostras_folha": 5,
            "regra": "|--- salario_medio_sm <= 1.66\n|   |--- class: True\n|--- salario_medio_sm >  1.66\n|   |--- class: False",
        },
        {
            "arvore": "B_SALARIO_TERCIL_SUPERIOR", "alvo": "salario_tercil_superior",
            "descricao_alvo": "remuneração no tercil superior",
            "casos": 66, "positivos": 33, "negativos": 33,
            "acuracia_cv": 0.930, "desvio_cv": 0.042, "baseline": 0.511,
            "folhas": 2, "atributo_mais_importante": "pct_superior",
            "peso_mais_importante": 0.910, "ganho_minimo_impureza": 0.03,
            "max_profundidade": 3, "min_amostras_folha": 5,
            "regra": "|--- pct_superior <= 0.31\n|   |--- class: False\n|--- pct_superior >  0.31\n|   |--- class: True",
        },
    ])


def gerar_fixture(destino: Path) -> Path:
    """Escreve artefatos sintéticos com o mesmo esquema dos reais."""
    gerador = np.random.default_rng(SEMENTE_FIXTURE)
    destino.mkdir(parents=True, exist_ok=True)
    perfis = _gerar_perfis(gerador)
    coordenadas, cargas, variancia = _componentes_principais(perfis)

    perfis.to_csv(destino / "q7_perfis.csv", index=False, encoding="utf-8-sig")
    coordenadas.round(6).to_csv(destino / "q7_pca.csv", index=False, encoding="utf-8-sig")
    cargas.round(6).to_csv(destino / "q7_cargas.csv", index=False, encoding="utf-8-sig")
    variancia.round(6).to_csv(destino / "q7_variancia.csv", index=False, encoding="utf-8-sig")
    _gerar_diagnostico(gerador).to_csv(destino / "q7_diagnostico_k.csv", index=False, encoding="utf-8-sig")
    _gerar_regioes(perfis).to_csv(destino / "q7_regioes.csv", index=False, encoding="utf-8-sig")
    _gerar_arvores().to_csv(destino / "q7_arvores.csv", index=False, encoding="utf-8-sig")

    configuracao = {
        "janela": [2023, 2025],
        "minimo_vinculos_na_janela": 100,
        "regra_elegibilidade": "Q comparável, 6 atributos observados e V_total >= 100",
        "minimo_nacionalidades_por_grupo": 4,
        "acordo_minimo_kmeans_ward": 0.5,
        "repeticoes_reamostragem": REPETICOES,
        "ks_avaliados": list(range(2, 9)),
        "semente": SEMENTE_FIXTURE,
        "k_escolhido": 3,
        "ari_kmeans_ward": 0.632,
        "universo_com_Q_comparavel": 184,
        "com_os_6_atributos": 183,
        "elegiveis": int(len(perfis)),
        "vinculos_das_elegiveis": int(perfis["V_total"].sum()),
        "fixture": True,
    }
    (destino / "q7_config.json").write_text(
        json.dumps(configuracao, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return destino


def _renderizar_tudo(artefatos: DadosQ7) -> list[str]:
    problemas = []
    for chave, construtor in FIGURAS.items():
        try:
            figura = construtor(artefatos)
        except Exception as erro:  # noqa: BLE001 — o objetivo é justamente capturar tudo
            problemas.append(f"{chave}: {type(erro).__name__}: {erro}")
            continue
        if not figure_tem_dados(figura):
            problemas.append(f"{chave}: figura sem traços")
    return problemas


def figure_tem_dados(figura: object) -> bool:
    """Uma figura válida precisa ter ao menos um traço com dados."""
    return bool(getattr(figura, "data", ()))


def _contar_elementos(aplicacao: object, tipo: str) -> int:
    try:
        return len(aplicacao.get(tipo))  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001 — elemento indisponível na versão instalada
        return -1


def _percorrer_evidencias(aplicacao: object) -> tuple[dict[str, str], list[str]]:
    """Troca a evidência da Q7 uma a uma e verifica se todas renderizam."""
    falhas: dict[str, str] = {}
    diagnostico: list[str] = []
    for evidencia in textos.EVIDENCIAS:
        seletores = aplicacao.get("segmented_control")  # type: ignore[attr-defined]
        if not seletores:
            falhas["seletor"] = "seletor de evidência não encontrado"
            return falhas, diagnostico
        seletores[0].set_value(evidencia.rotulo).run()
        if aplicacao.exception:  # type: ignore[attr-defined]
            falhas[evidencia.chave] = aplicacao.exception[0].message
            continue
        diagnostico.append(
            f"{evidencia.chave}: gráficos={_contar_elementos(aplicacao, 'plotly_chart')} · "
            f"tabelas={_contar_elementos(aplicacao, 'dataframe')} · "
            f"expanders={len(aplicacao.expander)}"  # type: ignore[attr-defined]
        )
    return falhas, diagnostico


def validar_aplicacao(pasta: Path) -> tuple[dict[str, str], list[str]]:
    """Sobe o app em memória e percorre todas as abas e todas as evidências da Q7."""
    os.environ["DASHBOARD_DADOS"] = str(pasta)
    from streamlit.testing.v1 import AppTest

    falhas: dict[str, str] = {}
    diagnostico: list[str] = []
    for aba in ABAS:
        aplicacao = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=120)
        aplicacao.run()
        if aplicacao.exception:
            falhas[aba] = aplicacao.exception[0].message
            continue
        aplicacao.sidebar.radio[0].set_value(aba).run()
        if aplicacao.exception:
            falhas[aba] = aplicacao.exception[0].message
        elif aba == ABA_Q7:
            falhas_evidencias, diagnostico = _percorrer_evidencias(aplicacao)
            falhas.update({f"{aba} · {chave}": erro for chave, erro in falhas_evidencias.items()})
    return falhas, diagnostico


def validar_renderizacao() -> int:
    """Exercita leitura, figuras, painéis e as abas do app com dados sintéticos."""
    with tempfile.TemporaryDirectory(prefix="q7_fixture_") as temporario:
        pasta = gerar_fixture(Path(temporario))
        artefatos = carregar(pasta)
        print(f"fixture em {pasta}")
        print(f"  nacionalidades: {len(artefatos.perfis)} | k escolhido: {artefatos.k_escolhido}")
        print(f"  universo: {artefatos.n_universo} | elegíveis: {artefatos.n_elegiveis}")

        problemas = _renderizar_tudo(artefatos)
        for chave, construtor in FIGURAS.items():
            figura = construtor(artefatos)
            print(f"  {chave:12s} traços={len(figura.data)}")

        indicadores = graficos.resumo_numerico(artefatos)
        print(f"  indicadores: {indicadores}")
        if not all(evidencia.leitura for evidencia in textos.EVIDENCIAS):
            problemas.append("evidência sem texto de leitura")
        print(f"  evidências com leitura: {len(textos.EVIDENCIAS)}")
        print(f"  texto da regra (A): {graficos.texto_da_regra(artefatos, 'A_Q_MAIOR_1').splitlines()[0]}")
        print(f"  perfil de uma nacionalidade: {len(graficos.perfil_da_linha(artefatos, 'Nacao 1000'))} linhas")

        print("\npercorrendo as abas do app em memória:")
        falhas_app, diagnostico = validar_aplicacao(pasta)
        for aba in ABAS:
            erro = falhas_app.get(aba)
            print(f"  {'FALHA' if erro else 'ok   '} {aba}{f' — {erro}' if erro else ''}")
        print("\n  evidências da Q7:")
        for linha in diagnostico:
            print(f"    {linha}")
        problemas.extend(f"{aba}: {erro}" for aba, erro in falhas_app.items())

    if problemas:
        print("\nFALHAS:")
        for problema in problemas:
            print(f"  - {problema}")
        return 1
    print("\nrenderização OK")
    return 0


def _marcar(conforme: bool) -> str:
    return "ok" if conforme else ">>"


def _comparar(rotulo: str, obtido: object, esperado: object, tolerancia: float) -> bool:
    conforme = abs(float(obtido) - float(esperado)) <= tolerancia  # type: ignore[arg-type]
    print(f"  {_marcar(conforme)}  {rotulo:<30} {str(obtido):>22}   (guia: {esperado})")
    return conforme


def _comparar_lista(
    rotulo: str, obtidos: list[object], esperados: object, tolerancia: float
) -> bool:
    referencia = list(esperados)  # type: ignore[call-overload]
    conforme = len(obtidos) == len(referencia) and all(
        abs(float(a) - float(b)) <= tolerancia for a, b in zip(obtidos, referencia)
    )
    print(f"  {_marcar(conforme)}  {rotulo:<30} {str(obtidos):>22}   (guia: {referencia})")
    return conforme


def conferir_numeros() -> int:
    """Compara os artefatos reais com os números congelados na v5."""
    try:
        artefatos = carregar()
    except ArtefatosAusentes as erro:
        print("não há artefatos em dados/q7/ para conferir.")
        print(erro)
        return 1

    configuracao = artefatos.configuracao
    regioes = artefatos.regioes.sort_values("regiao")
    print("BLOQUEANTES — a análise depende destes\n")
    conformes = [
        _comparar("elegíveis (V_total >= 100)", configuracao["elegiveis"], CONGELADOS_V5["elegiveis"], TOLERANCIA_CONFERENCIA),
        _comparar("k escolhido", configuracao["k_escolhido"], CONGELADOS_V5["k_escolhido"], TOLERANCIA_CONFERENCIA),
        _comparar("ARI KMeans x Ward", configuracao["ari_kmeans_ward"], CONGELADOS_V5["ari_kmeans_ward"], TOLERANCIA_CONFERENCIA),
        _comparar_lista("tamanhos das regiões", regioes["n_nacionalidades"].tolist(), CONGELADOS_V5["tamanhos_regioes"], TOLERANCIA_CONFERENCIA),
        _comparar_lista("salário médio por região", regioes["salario_medio_sm"].tolist(), CONGELADOS_V5["salario_por_regiao"], TOLERANCIA_MEDIA),
        _comparar_lista("% superior por região", regioes["pct_superior"].tolist(), CONGELADOS_V5["superior_por_regiao"], TOLERANCIA_MEDIA),
    ]

    print("\nINFORMATIVOS — registrados no guia, sem efeito sobre a análise\n")
    for chave, esperado in REFERENCIA_INFORMATIVA_V5.items():
        obtido = configuracao[chave]
        marca = "ok" if str(obtido) == str(esperado) else "~ "
        print(f"  {marca}  {chave.replace('_', ' '):<30} {str(obtido):>22}   (guia: {esperado})")
    print("      ~  a diferença são nacionalidades que aparecem nas duas fontes mas não")
    print("         alcançam o piso de vínculos. Nenhuma delas entra nos elegíveis.")

    print(
        f"\n  vínculos das elegíveis: {configuracao['vinculos_das_elegiveis']:,}"
        f" | janela: {configuracao['janela'][0]}–{configuracao['janela'][1]}"
    )
    if all(conformes):
        print("\ntodos os itens bloqueantes conferem — os artefatos podem alimentar o dashboard")
        return 0
    print("\nATENÇÃO: divergência em item bloqueante. Não use esta execução como saída oficial.")
    return 1


def validar_html() -> int:
    """Regenera o dashboard estático e confere a estrutura do HTML produzido."""
    from gerador.construir import _conteudo_q4, _conteudo_q7, construir, _slug

    destino = construir()
    html = destino.read_text(encoding="utf-8")
    problemas: list[str] = []

    identificadores = [_slug(aba) for aba in ABAS]
    esperados = {
        "seções das abas": [f'id="secao-{slug}"' for slug in identificadores],
        "botões da navegação": [f'data-aba="{slug}"' for slug in identificadores],
        "cartões informativos": ['class="rotulo">Cobertura', 'class="rotulo">Filtros',
                                 'class="rotulo">Nota metodológica'],
        "blocos principais": ['Evidência principal', 'Resposta + limites'],
        "faixa de pisos": ["Pisos fixos"],
        "redimensionamento dos gráficos": ["Plotly.Plots.resize"],
    }
    for rotulo, trechos in esperados.items():
        faltando = [trecho for trecho in trechos if trecho not in html]
        if faltando:
            problemas.append(f"{rotulo}: ausentes {faltando}")

    # O HTML traz `plotly-graph-div`; `js-plotly-plot` só existe depois que o Plotly
    # desenha, no navegador. Contar a primeira é o que verifica o arquivo gerado.
    graficos = html.count('class="plotly-graph-div"')
    tabelas = html.count('<table class="tabela"')
    secoes_ativas = html.count('class="secao ativa"')

    # O que se espera vem das próprias declarações, não de uma constante paralela: uma
    # tabela substitui a figura da sua evidência.
    artefatos = carregar()
    declarados = (_conteudo_q7(artefatos), _conteudo_q4(artefatos))
    esperado_graficos = sum(len(c.evidencias) - (1 if c.tabela else 0) for c in declarados)
    esperado_tabelas = sum(1 for c in declarados if c.tabela)
    esperado_evidencias = sum(len(c.evidencias) for c in declarados)

    # `Plotly.newPlot` resolve o alvo por `getElementById`: um id repetido faz o
    # gráfico ser desenhado no bloco externo e a leitura sair do cartão.
    identificadores_usados = re.findall(r'\sid="([^"]+)"', html)
    repetidos = sorted({valor for valor in identificadores_usados
                        if identificadores_usados.count(valor) > 1})
    if repetidos:
        problemas.append(f"ids repetidos no HTML: {repetidos[:8]}")

    evidencias = html.count('id="ev-')
    if evidencias != esperado_evidencias:
        problemas.append(
            f"blocos de evidência: esperado {esperado_evidencias}, encontrado {evidencias}"
        )

    print(f"gerado: {destino} ({destino.stat().st_size / 1024:,.0f} KB)")
    print(f"  abas: {len(identificadores)} | secções ativas na carga: {secoes_ativas}")
    print(f"  gráficos embutidos: {graficos} | tabelas: {tabelas} | evidências: {evidencias}")
    if graficos != esperado_graficos:
        problemas.append(f"gráficos: esperado {esperado_graficos}, encontrado {graficos}")
    if tabelas != esperado_tabelas:
        problemas.append(f"tabelas: esperado {esperado_tabelas}, encontrado {tabelas}")
    if secoes_ativas != 1:
        problemas.append(f"secções ativas: esperado 1, encontrado {secoes_ativas}")

    if problemas:
        print("\nFALHAS:")
        for problema in problemas:
            print(f"  - {problema}")
        return 1
    print("\ndashboard estático gerado e íntegro")
    return 0


def validar_aplicacao_real() -> int:
    """Percorre todas as abas do app com os artefatos reais de dados/q7/."""
    pasta = pasta_dados()
    try:
        artefatos = carregar(pasta)
    except ArtefatosAusentes as erro:
        print(f"não há artefatos em {pasta} para validar.\n{erro}")
        return 1

    problemas = _renderizar_tudo(artefatos)
    print(f"artefatos reais: {pasta}")
    print(
        f"  nacionalidades: {len(artefatos.perfis)} | k escolhido: {artefatos.k_escolhido} | "
        f"universo: {artefatos.n_universo}"
    )

    falhas, diagnostico = validar_aplicacao(pasta)
    print("\nabas do app:")
    for aba in ABAS:
        erro = falhas.get(aba)
        print(f"  {'FALHA' if erro else 'ok   '} {aba}{f' — {erro}' if erro else ''}")
    print("\nevidências da Q7:")
    for linha in diagnostico:
        print(f"  {linha}")

    problemas.extend(f"{aba}: {erro}" for aba, erro in falhas.items())
    if problemas:
        print("\nFALHAS:")
        for problema in problemas:
            print(f"  - {problema}")
        return 1
    print("\no app renderiza com os dados reais")
    return 0


def main() -> int:
    analisador = argparse.ArgumentParser(description="Validação do dashboard da Q7")
    analisador.add_argument(
        "--conferir", action="store_true", help="confere os artefatos reais contra a v5"
    )
    analisador.add_argument(
        "--app", action="store_true", help="percorre as abas do app com os artefatos reais"
    )
    analisador.add_argument(
        "--html", action="store_true", help="regenera e confere o dashboard estático"
    )
    argumentos = analisador.parse_args()
    if argumentos.conferir:
        return conferir_numeros()
    if argumentos.app:
        return validar_aplicacao_real()
    if argumentos.html:
        return validar_html()
    return validar_renderizacao()


if __name__ == "__main__":
    raise SystemExit(main())
