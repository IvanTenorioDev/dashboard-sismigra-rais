#!/usr/bin/env bash
# Reinicia o dashboard e captura a tela de uma aba.
#
# Necessário porque o Streamlit mantém em cache os módulos de `nucleo/`: alterar
# qualquer arquivo de lá só tem efeito depois de reiniciar o processo.
#
#   ./ferramentas/reiniciar_e_capturar.sh "Q7 Multivariado" /tmp/tela.png
set -euo pipefail

ABA="${1:-Q7 Multivariado}"
DESTINO="${2:-/tmp/tela.png}"
PORTA="${PORTA:-8501}"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

pkill -f "streamlit run app.py" 2>/dev/null || true
sleep 1
find "$RAIZ" -name "__pycache__" -not -path "*/.venv/*" -exec rm -rf {} + 2>/dev/null || true

cd "$RAIZ"
nohup .venv/bin/streamlit run app.py --server.port "$PORTA" --server.headless true \
    --browser.gatherUsageStats false >/tmp/streamlit.log 2>&1 &

# Espera o servidor responder de fato: capturar antes disso grava a tela de
# carregamento do Streamlit, que parece um app vazio e engana a inspeção.
for _ in $(seq 1 40); do
    if curl -sf "http://localhost:$PORTA/_stcore/health" >/dev/null 2>&1; then
        break
    fi
    sleep 0.5
done
sleep 2

CODIFICADA="$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$ABA")"
rm -rf "/tmp/chrome-captura" "$DESTINO"
google-chrome --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
    --user-data-dir=/tmp/chrome-captura --window-size=1600,1080 \
    --virtual-time-budget=25000 --screenshot="$DESTINO" \
    "http://localhost:$PORTA/?aba=$CODIFICADA" >/dev/null 2>&1

TAMANHO="$(stat -c%s "$DESTINO")"
echo "captura: $DESTINO ($TAMANHO bytes)"
if [ "$TAMANHO" -lt 40000 ]; then
    echo "AVISO: imagem pequena demais — provavelmente a tela de carregamento"
fi
grep -i "traceback" /tmp/streamlit.log | head -3 || true
