"""Folha de estilo do dashboard estático.

Transcrição direta do desenho aprovado (slide 11): um painel branco com sombra sobre
fundo cinza, cabeçalho azul cruzando a largura inteira do painel, navegação em botões,
cartões com sombra e a faixa de pisos dentro do painel.

Aqui não há luta contra framework: o CSS descreve exatamente o que se quer ver.
"""

from __future__ import annotations

AZUL = "#1F3A5F"
LARANJA = "#D97A2B"
VERDE = "#54A24B"
AZUL_GRAFICO = "#4C78A8"
LARANJA_GRAFICO = "#F58518"

FUNDO_PAGINA = "#E9ECF0"
FUNDO_CONTEUDO = "#F7F8FA"
BORDA = "#E3E7EB"
TEXTO = "#1A1A1A"
CINZA = "#6B7785"
CINZA_CLARO = "#8B96A3"

SOMBRA_CARTAO = "0 1px 5px rgba(20, 32, 48, 0.10)"
SOMBRA_NAVEGACAO = "0 1px 3px rgba(20, 32, 48, 0.10)"
SOMBRA_PAINEL = "0 2px 14px rgba(20, 32, 48, 0.14)"

CORES_REGIAO = {1: AZUL_GRAFICO, 2: LARANJA_GRAFICO, 3: VERDE, 4: "#B279A2"}

CSS = f"""
* {{ box-sizing: border-box; }}

body {{
  margin: 0;
  background: {FUNDO_PAGINA};
  color: {TEXTO};
  font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 15px;
}}

.painel {{
  max-width: 1500px;
  margin: 24px auto;
  height: calc(100vh - 48px);
  min-height: 620px;
  display: flex;
  flex-direction: column;
  background: #FFFFFF;
  border-radius: 14px;
  box-shadow: {SOMBRA_PAINEL};
  overflow: hidden;
}}

.cabecalho {{
  flex: 0 0 auto;
  background: {AZUL};
  color: #FFFFFF;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.01em;
  padding: 16px 26px;
}}

/* O painel ocupa a janela e é o CONTEÚDO que rola. Assim a faixa de pisos fica
   sempre à vista, na base do painel — como no desenho aprovado. */
.corpo {{ flex: 1 1 auto; display: flex; align-items: stretch; min-height: 0; }}

.navegacao {{
  width: 272px;
  flex: 0 0 272px;
  background: #FFFFFF;
  border-right: 1px solid {BORDA};
  padding: 18px 16px;
  overflow-y: auto;
}}

.aba-nav {{
  display: block;
  width: 100%;
  text-align: left;
  background: #FFFFFF;
  border: 1px solid {BORDA};
  border-radius: 9px;
  box-shadow: {SOMBRA_NAVEGACAO};
  padding: 11px 15px;
  margin-bottom: 11px;
  font: inherit;
  font-size: 14px;
  color: {TEXTO};
  cursor: pointer;
}}
.aba-nav:hover {{ border-color: {LARANJA}; }}
.aba-nav.ativa {{
  background: {LARANJA};
  border-color: {LARANJA};
  color: #FFFFFF;
  font-weight: 600;
}}

.coluna {{
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: {FUNDO_CONTEUDO};
}}

.conteudo {{ flex: 1 1 auto; min-height: 0; overflow-y: auto; padding: 20px; }}
.secao {{ display: none; }}
.secao.ativa {{ display: block; }}

.linha-cartoes {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}}
.linha-principal {{
  display: grid;
  grid-template-columns: 1.55fr 1fr;
  gap: 20px;
  margin-top: 20px;
  align-items: stretch;
}}
/* Aba sem figura: não há evidência a alternar, e a resposta ocupa a linha toda. */
.linha-unica {{ grid-template-columns: 1fr; }}
/* Bloco de largura total abaixo da linha principal, na mesma malha de cartões. */
.bloco-extra {{ margin-top: 20px; }}

.cartao {{
  background: #FFFFFF;
  border-radius: 12px;
  box-shadow: {SOMBRA_CARTAO};
  padding: 16px 20px;
}}
.cartao-alto {{ border-radius: 16px; padding: 20px 24px; }}

.rotulo {{ color: {LARANJA}; font-size: 16px; font-weight: 700; margin-bottom: 7px; }}
.linha {{ color: {CINZA}; font-size: 13px; line-height: 1.45; }}

.titulo-bloco {{
  color: {AZUL};
  font-size: 19px;
  font-weight: 700;
  margin-bottom: 14px;
}}

.indicadores {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px 18px;
  margin-bottom: 12px;
  font-size: 13px;
  color: {CINZA};
}}
.indicadores b {{ color: {TEXTO}; font-weight: 600; }}

.limites {{ margin: 0; padding-left: 18px; font-size: 14px; line-height: 1.65; }}
.limites li {{ margin-bottom: 2px; }}

.detalhe {{ margin-top: 14px; font-size: 13px; color: {CINZA}; }}
.detalhe summary {{ cursor: pointer; color: {AZUL}; font-weight: 600; }}
.detalhe p {{ margin: 8px 0 0 0; line-height: 1.5; }}
.detalhe b {{ color: {TEXTO}; }}

.ponte {{
  margin-top: 20px;
  border-left: 4px solid {LARANJA};
  background: #FDF7F1;
  border-radius: 0 10px 10px 0;
  padding: 14px 18px;
  box-shadow: {SOMBRA_CARTAO};
}}
.ponte-rotulo {{
  color: #8A5A1F;
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 6px;
}}
.ponte-texto {{ font-size: 14px; line-height: 1.5; }}

.seletor {{ display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 14px; }}
.opcao {{
  background: #FFFFFF;
  border: 1px solid {BORDA};
  border-radius: 999px;
  padding: 5px 12px;
  font: inherit;
  font-size: 12px;
  color: {CINZA};
  cursor: pointer;
  white-space: nowrap;
}}
.opcao:hover {{ border-color: {LARANJA}; color: {TEXTO}; }}
.opcao.ativa {{
  background: {AZUL};
  border-color: {AZUL};
  color: #FFFFFF;
  font-weight: 600;
}}

.evidencia {{ display: none; }}
.evidencia.ativa {{ display: block; }}
.leitura {{ color: {CINZA}; font-size: 13px; line-height: 1.5; margin-top: 10px; }}

.aviso {{
  background: #EAF1F8;
  border-radius: 10px;
  padding: 14px 18px;
  font-size: 14px;
  margin-bottom: 20px;
}}

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

.pisos {{
  flex: 0 0 auto;
  padding: 14px 20px 18px 20px;
  border-top: 1px solid {BORDA};
  background: #FFFFFF;
  font-size: 13px;
  line-height: 1.5;
  color: {TEXTO};
}}
.pisos b {{ color: {LARANJA}; }}

code {{
  background: #F2F4F7;
  border-radius: 4px;
  padding: 1px 5px;
  font-size: 12px;
}}

@media (max-width: 1100px) {{
  .linha-principal {{ grid-template-columns: 1fr; }}
  .navegacao {{ width: 220px; flex-basis: 220px; }}
}}
"""
