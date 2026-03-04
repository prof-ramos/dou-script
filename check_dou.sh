#!/bin/bash
# Script para check se o DOU saiu e envio de notificação

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Carregar credenciais
source .env

# Criar diretório de logs
mkdir -p ./logs

# Data de hoje
DATA=$(date +%Y-%m-%d)
DATA_FORMATADA=$(date +%d/%m/%Y)

# Verificar se já existe log de hoje
LOG_FILE="./logs/${DATA}.log"

# Verificar se o log já foi processado hoje
if [ -f "$LOG_FILE" ]; then
    ULTIMO_CHECK=$(tail -1 "$LOG_FILE" | grep -oP '\d{2}:\d{2}:\d{2}' || echo "00:00:00")
    HORA_ATUAL=$(date +%H:%M:%S)
    echo "🔄 Último check: $ULTIMO_CHECK | Agora: $HORA_ATUAL"
    echo "Processed today"
    exit 0
fi

# Criar log file
echo "=== Check DOU - $DATA_FORMATADA ===" > "$LOG_FILE"

# Executar download
RESULT=$(python3 -c "
from inlabs_client import INLABSClient
import os
import json

try:
    client = INLABSClient(
        email='$INLABS_EMAIL',
        password='$INLABS_PASSWORD',
        output_dir='./dou'
    )

    arquivos = client.download_today(secoes=['DO1', 'DO2'])

    if arquivos:
        print(json.dumps({'status': 'success', 'files': list(arquivos.keys())}))
    else:
        print(json.dumps({'status': 'no_files'}))

except Exception as e:
    print(json.dumps({'status': 'error', 'message': str(e)}))
" 2>&1)

# Salvar resultado no log
echo "$RESULT" >> "$LOG_FILE"

# Parsear resultado
echo "$RESULT" > /tmp/dou_result.json

# Verificar se há arquivos novos
if command -v jq &> /dev/null; then
    FILES=$(jq -r '.files[]' /tmp/dou_result.json 2>/dev/null || echo "")

    if [ -n "$FILES" ]; then
        # Construir mensagem de notificação
        MENSAGEM="📄 **DOU SAIU!**\n\n📅 Data: $DATA_FORMATADA\n\n✅ Arquivos baixados:"
        for arquivo in $FILES; do
            MENSAGEM+="\n- $arquivo.zip"
        done

        MENSAGEM+="\n\n📂 Salvo em: $SCRIPT_DIR/dou/"

        # Enviar para WhatsApp (via cron - sem session context)
        # Enviar para URL webhook se configurada, ou manter local
        echo "📧 $MENSAGEM" >> "$LOG_FILE"

        # Salvar mensagem para notificação futura
        echo "$MENSAGEM" > "$LOG_FILE".notify
    fi
fi

# Limpar
rm -f /tmp/dou_result.json

echo "✅ Check completo: $DATA_FORMATADA"
