#!/bin/bash
# Script para download do DOU usando credenciais do IN Labs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Carregar variáveis de ambiente
source .env

# Verificar se as credenciais foram configuradas
if [ -z "$INLABS_EMAIL" ] || [ -z "$INLABS_PASSWORD" ]; then
    echo "❌ Credenciais não configuradas!"
    echo "Configure em .env:"
    echo "INLABS_EMAIL=seu@email.com"
    echo "INLABS_PASSWORD=sua_senha"
    exit 1
fi

# Executar download
python3 -c "
from inlabs_client import INLABSClient
import sys

try:
    client = INLABSClient(
        email='$INLABS_EMAIL',
        password='$INLABS_PASSWORD',
        output_dir='./dou'
    )

    # Download da edição de hoje
    arquivos = client.download_today(secoes=['DO1', 'DO2'])

    print(f'\n✅ {len(arquivos)} arquivos baixados:')
    for secao, path in arquivos.items():
        print(f'  {secao}: {path}')

except Exception as e:
    print(f'❌ Erro: {e}', file=sys.stderr)
    sys.exit(1)
"
