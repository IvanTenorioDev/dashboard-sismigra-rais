# Dashboard analítico — SISMIGRA × RAIS-CTPS

Painel do Projeto Integrador I. A navegação é organizada **pelas perguntas**, não pelas
técnicas: cada aba entrega uma resposta analítica verificável e explicita seus limites.

Implementadas: **Q7 Análise multivariada** (completa) e as demais abas com o esqueleto do
contrato de layout, prontas para receber conteúdo.

---

## 0. Duas formas de ver o mesmo painel

| | Gerador estático (recomendado) | App Streamlit |
|---|---|---|
| O que é | `gerador/` produz `docs/index.html` | `app.py` renderiza em servidor |
| Fidelidade ao desenho | **total** — o CSS descreve exatamente o alvo | aproximada; exige CSS sobre a estrutura interna do Streamlit |
| Publicação | **GitHub Pages**, arquivos estáticos | Streamlit Community Cloud |
| Interatividade | hover, zoom, legenda (Plotly) + troca de aba e de evidência por JS | qualquer widget do Streamlit |
| Filtros | precisam ser escritos em JS | nativos |
| Dependências em execução | nenhuma | Python + Streamlit |

Os dois leem os **mesmos** artefatos e reaproveitam a mesma camada analítica
(`nucleo/dados.py`, `nucleo/graficos.py`, `nucleo/textos.py`, `nucleo/formatos.py`).
A diferença está só em quem desenha.

O gerador estático existe porque o alvo é uma **composição de tela única,
pixel-específica**: painel branco com sombra, cabeçalho cruzando a largura inteira,
cartões de altura igual e faixa de pisos dentro do painel. O Streamlit impõe sidebar de
altura total e não entrega esse desenho sem gambiarra — e o CSS para chegar perto ataca
`data-testid` e classes internas, que quebram a cada atualização da biblioteca.

---

## 1. Como o dashboard se relaciona com o notebook

O app **não recalcula nada**. A FASE 9 de `Integrador_Base_Unificada_REV1.ipynb` exporta
os agregados da Q7, e o app apenas lê o que foi exportado. Isso garante três coisas:

- **rastreabilidade** — todo número na tela vem de uma execução identificável do notebook;
- **determinismo** — a interface não depende de a reamostragem cair no mesmo lugar a cada abertura;
- **peso** — o app publicado não precisa dos ZIPs de entrada (centenas de MB), só dos agregados (poucos KB).

O contrato dos arquivos está em `dados/q7/LEIA-ME.txt` e é validado na leitura: se um
arquivo faltar ou vier com coluna inesperada, o app falha com mensagem explícita em vez
de exibir número errado em silêncio.

## 2. Gerar os dados

1. Abra o notebook no Colab e rode inteiro (ele pede os 4 ZIPs no início).
2. Rode a FASE 9 — a última célula imprime a conferência contra os números congelados na v5.
3. Se os números conferirem, copie o conteúdo de `integrador_base_unificada/dashboard/`
   para `dados/q7/`.
4. Confira o que chegou:

```bash
.venv/bin/python testes/validar.py --conferir
```

## 3. Rodar

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**Gerador estático** — cria `docs/index.html` (interativo, sem servidor):

```bash
.venv/bin/python gerador/construir.py
.venv/bin/python -m http.server 8600 --directory docs   # abrir http://localhost:8600
```

Cada aba tem link direto: `#q7-multivariado`, `#q4-representacao`, etc.

**App Streamlit** — alternativa com filtros nativos:

```bash
.venv/bin/streamlit run app.py
```

Sem os dados reais, o app abre numa tela explicando o que falta. Como todo módulo de
`nucleo/` fica em cache no servidor, **alterar qualquer arquivo de lá exige reiniciar o
processo** — `ferramentas/reiniciar_e_capturar.sh` faz isso e ainda tira a captura de
tela de uma aba.

## 3.1 Testar

```bash
.venv/bin/python testes/validar.py              # figuras + abas + evidências (fixture)
.venv/bin/python testes/validar.py --conferir   # artefatos reais x números congelados na v5
.venv/bin/python testes/validar.py --app        # abas do app com os artefatos reais
.venv/bin/python testes/validar.py --html       # regenera e confere o HTML estático
```

## 4. Testar

```bash
.venv/bin/python testes/validar.py              # leitura, 7 figuras, 8 abas, 8 evidências
.venv/bin/python testes/validar.py --conferir   # artefatos reais x números congelados na v5
```

O validador sobe o app em memória, percorre todas as abas e todas as evidências da Q7 e
falha se qualquer uma levantar exceção. Foi ele que pegou a colisão de colunas `V_total`
entre `q7_pca.csv` e `q7_perfis.csv`.

## 5. Publicar

```bash
git init && git add . && git commit -m "dashboard Q7"
git remote add origin <url-do-repositorio>
git push -u origin main
```

**GitHub Pages** (gerador estático) — no repositório: *Settings* → *Pages* →
*Source: Deploy from a branch* → branch `main`, pasta **`/docs`**. O painel fica em
`https://<usuario>.github.io/<repositorio>/`.

Vantagens em relação ao Streamlit Cloud: não precisa de servidor Python, **não hiberna**,
carrega instantaneamente e não tem limite de recursos. O `index.html` gerado é
autossuficiente — carrega o Plotly de CDN e traz os dados embutidos.

**Streamlit Community Cloud** (app alternativo) — em <https://share.streamlit.io> →
*New app* → escolha o repositório, `main` e `app.py`.

Em qualquer das duas rotas os arquivos de `dados/q7/` **precisam estar no commit**.

## 6. Estrutura

```
app.py                      navegação e tratamento de ausência de dados
nucleo/
  config.py                 pisos, rótulos, cores, lista de abas, caminho dos dados
  dados.py                  leitura e validação do esquema dos artefatos
  graficos.py               as 7 figuras — nenhuma página monta gráfico sozinha
  textos.py                 a narrativa: pergunta, resposta, limites, leitura de cada evidência
  layout.py                 os três cartões, o painel de resposta, o rodapé de pisos
  formatos.py               formatação numérica em padrão brasileiro
paginas/
  q7_multivariado.py        a aba Q7
  em_construcao.py          esqueleto do contrato para as demais abas
dados/q7/                   artefatos congelados (versionados)
testes/validar.py           validação em dois modos
```

## 7. Decisões de desenho da aba Q7

### 7.1 Convenções visuais (slide 11)

O desenho aprovado tem identidade própria que o tema do Streamlit não cobre. Ela vive
em `nucleo/estilo.py`, num único lugar — nenhuma página injeta CSS por conta própria.

| Elemento | Como está implementado |
|---|---|
| Barra superior azul, colada nas bordas | `.dash-cabecalho`, com o cabeçalho fixo do Streamlit oculto |
| Itens de navegação como botões, ativo em laranja | CSS sobre o `radio` da sidebar, escondendo o círculo |
| Cartões com rótulo laranja em caixa alta e baixa | `.dash-rotulo` |
| Seletor de evidência em uma linha | rótulos curtos, em `ROTULOS_CURTOS` |
| Sem barra de ferramentas no gráfico | `config={"displayModeBar": False}` |

**Duas diferenças conhecidas em relação ao desenho**, ambas por limite da plataforma:

1. A barra azul **não passa por cima da sidebar**. A sidebar do Streamlit é sempre de
   altura total; o desenho mostra a barra cruzando a largura inteira do painel.
2. A faixa de pisos **não fica presa na base da janela** (é o último elemento da página).
   A mesma informação aparece permanentemente na sidebar, que não rola — então o
   requisito de estar sempre visível é atendido por outro caminho.

### 7.2 Registro da narrativa

O produto é avaliado em banca de MBA. O texto assume leitor com formação quantitativa:
não explica o que é um coeficiente de silhueta, um baseline ou uma validação cruzada, e
não usa metáfora onde cabe o termo técnico. Os textos vêm de uma revisão que removeu
didatismo ("sem isso, uma acurácia de 0,84 pareceria excelente...") e coloquialismo
("chute informado", "k sortudo", "duas pontas e um meio").

**Nenhum número da narrativa é escrito à mão.** Eles são campos preenchidos em tempo de
geração a partir de `DadosQ7.valores_para_texto()`:

```python
RESPOSTA_SINTETICA = "... a partição em {k} regiões ... silhueta de {silhueta} ..."
```

A razão é concreta: a leitura da regra de k afirmava, fixado no texto, que a concordância
KMeans × Ward em k=2 era **0,007**. Com a elegibilidade corrigida ela passou a **0,432** —
o texto continuou dizendo 0,007 e ninguém notaria. Agora `{acordo_k2}` acompanha a
execução, e o modo `--html` falha se algum campo ficar sem valor.

### 7.3 Decisões analíticas

**O painel "Resposta + limites" é fixo.** Trocar a evidência não troca a conclusão. Isso é
deliberado: a mensagem da Q7 é que a leitura vem do **conjunto** das evidências, e um
painel que mudasse junto sugeriria o contrário.

**Um seletor de evidência, não oito abas.** O layout aprovado reserva uma caixa para a
"Evidência principal". A Q7 tem oito provas e uma caixa — por isso o seletor segmentado,
que é a única liberdade que esta aba toma em relação ao desenho original.

**Filtros desligados nesta aba.** As outras abas filtram por ano, nacionalidade e Top N.
Aqui o ano é fixo na janela 2023–2025 e a estrutura de grupos depende das 101
nacionalidades elegíveis: filtrar mudaria o resultado, não a visão dele. O único controle
é o tamanho da tabela.

**Mostramos os k descartados.** A tabela de diagnóstico exibe k = 2 a 8, inclusive os
recusados. Esconder o que foi rejeitado faria a escolha de k parecer arbitrária.

**k é escolhido em duas peneiras, não por um número só.** Primeiro exige-se que todo
grupo tenha pelo menos 4 nacionalidades (elimina k = 5..8, que produzem grupos de uma
nacionalidade). Depois exige-se que KMeans e Ward **concordem** (elimina k = 2, onde o ARI
entre os dois é ≈ 0,007). Só então a estabilidade sob reamostragem desempata.

Por que a segunda peneira é indispensável: estabilidade por reamostragem mede se **um**
algoritmo concorda consigo mesmo, não se a estrutura existe no dado. Em k = 2 a
estabilidade é alta (0,76) — mas os dois algoritmos acham partições diferentes. Um
critério aparentemente objetivo escolheria k = 2 e o resultado seria um artefato do
método.

**A estabilidade aparece como faixa.** A reamostragem é reprodutível com semente fixa
neste ambiente, mas não entre versões de biblioteca — verificamos divergência de 0,742
para 0,769 no k = 3 entre execuções. Por isso o painel exibe média **e** pior caso, e
`q7_diagnostico_k.csv` guarda os valores individuais.

## 8. Pontos em aberto

- **Escala de escolaridade** — os dados usam 7 níveis e o dicionário do projeto traz 11.
  A escala adotada foi inferida por três testes independentes e ainda aguarda confirmação
  do layout oficial da Base Harmonizada. Ver `06_achados_qualidade_dados.md`.
- **Uma nacionalidade do funil** — a primeira execução real classificou 102 nacionalidades
  porque incluía quem tem vínculos no RAIS e nenhum registro no SISMIGRA (a NAURU), para
  quem Q é indefinido. A exigência de Q comparável levou a 101 e aos grupos 57/20/24.
  A diferença de uma linha mudava o tamanho de um grupo.
- **Data de entrega** — 09/10 ou 16/10 conforme o alinhamento; não resolvido.
