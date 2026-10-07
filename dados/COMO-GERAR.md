# Como gerar os artefatos

Os arquivos em `dados/q7/` **são versionados no Git** — são poucos KB e o dashboard
precisa deles para funcionar no GitHub Pages, que é estático. Eles vêm do notebook, na
pasta de trabalho, e não são editados à mão.

## Passo a passo

1. **Reenvie** `Integrador_Base_Unificada_REV1.ipynb` para o Colab, substituindo a cópia
   antiga.
2. Rode o notebook inteiro. As 4 entradas em ZIP são pedidas no início; marcar
   `USAR_DRIVE = True` evita subir de novo a cada sessão.
3. A **FASE 9** e a **FASE 9b** escrevem os artefatos e imprimem a conferência contra os
   números congelados na v5 (101 elegíveis, k = 3, ARI 0,632, regiões 57/20/24).
   **Se houver divergência, não use a execução.**
4. A **FASE 10** baixa automaticamente o `dashboard_q7.zip`. Copie o conteúdo dele para
   `dados/q7/`.
5. Confira: `.venv/bin/python testes/validar.py --conferir`

> **Reenviar o notebook não é opcional.** O Colab congela a cópia do arquivo no momento
> do upload: reexecutar a mesma sessão repete a **versão antiga** do código. Foi assim
> que um pacote de 05/10 chegou sem os campos que já existiam no notebook em disco. O
> pacote agora carrega um `LEIA-ME.txt` com o carimbo `VERSAO_NOTEBOOK` — confira se
> bate antes de copiar.

## Arquivos esperados

**Q4, Q6 e Q7** (FASE 9)

| Arquivo | Grão |
|---|---|
| `q7_config.json` | parâmetros, funil e contagens de conferência |
| `q7_perfis.csv` | nacionalidade — 6 atributos, Q, região |
| `q7_pca.csv` | nacionalidade — PC1 × PC2 |
| `q7_cargas.csv` | atributo — cargas nos componentes |
| `q7_variancia.csv` | componente — variância explicada e acumulada |
| `q7_diagnostico_k.csv` | k — inércia, silhueta, ARI e estabilidade |
| `q7_regioes.csv` | região — perfil mediano |
| `q7_arvores.csv` | árvore — alvos, acurácias e regras |

**Q1, Q2, Q3 e Q5** (FASE 9b)

| Arquivo | Grão |
|---|---|
| `q1_serie_anual.csv` | nacionalidade × ano |
| `q1_resumo_por_ano.csv` | ano |
| `q2_uf_ano.csv` | UF × ano |
| `q2_concentracao.csv` | nacionalidade × ano |
| `q2_uf_top_nacionalidades.csv` | UF × posição |
| `q3_fluxo_ano.csv` | ano |
| `q5_persistencia.csv` | nacionalidade |

Mais o `LEIA-ME.txt` que o notebook escreve dentro do pacote: ele descreve o contrato,
alerta sobre os **dois conceitos de UF** e sobre a diferença entre **fluxo** e
**estoque**, e traz o carimbo de versão.

## Sem os dados reais

`.venv/bin/python testes/validar.py` gera artefatos sintéticos em diretório temporário e
verifica o layout. O painel exibe um aviso em vermelho quando está nesse modo.
