#!/usr/bin/env python3
"""
DOU Download + Filtragem MRE - Versão de Teste com Data Específica
Uso: python3 test-mre.py 2026-03-03
"""

import sys
sys.path.insert(0, 'public/python')
from dou_config import INLABS_LOGIN_URL, INLABS_BASE_URL, PALAVRAS_CHAVE, SECOES_DOU, DOWNLOAD_TIMEOUT, OUTPUT_DIR
from dou_utils import extrair_texto_xml, limpar_texto_xml, filtrar_conteudo, salvar_resultados

from datetime import date, datetime
import requests
import os
import time

# Data específica ou hoje
if len(sys.argv) > 1:
    data_especifica = sys.argv[1]
    try:
        data_alvo = datetime.strptime(data_especifica, "%Y-%m-%d").date()
    except ValueError:
        print(f"❌ Data inválida: {data_especifica}. Use formato YYYY-MM-DD")
        sys.exit(1)
else:
    data_alvo = date.today()

# Configurações
login = os.getenv("INLABS_EMAIL")
senha = os.getenv("INLABS_PASSWORD")

# Validar credenciais
if login is None or senha is None:
    print("❌ Erro: As variáveis de ambiente INLABS_EMAIL e INLABS_PASSWORD devem ser definidas")
    sys.exit(1)

payload = {"email": login, "password": senha}
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def download_xml_filtrado():
    """Baixa XMLs e filtra por palavras-chave MRE"""
    s = requests.Session()
    print(f"📅 Data alvo: {data_alvo.strftime('%d/%m/%Y')} ({data_alvo.strftime('%A')})")

    # Realizar login com retry loop e exponential backoff
    max_attempts = 3
    response = None

    for attempt in range(max_attempts):
        try:
            response = s.request("POST", INLABS_LOGIN_URL, data=payload, headers=headers)
            if response.status_code == 200:
                print(f"✓ Status login: HTTP {response.status_code}")
                break
        except requests.exceptions.ConnectionError:
            if attempt < max_attempts - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"❌ Erro de conexão, tentando novamente em {wait_time}s...")
                time.sleep(wait_time)
            else:
                print("❌ Erro de conexão após múltiplas tentativas")
                return False

    # Verificar cookie
    if not s.cookies.get('inlabs_session_cookie'):
        print("❌ Falha ao obter cookie. Verifique suas credenciais")
        return False

    cookie = s.cookies.get('inlabs_session_cookie')
    print(f"✓ Cookie obtido: {cookie[:10]}...")

    # Data atual formatação
    ano = data_alvo.strftime("%Y")
    mes = data_alvo.strftime("%m")
    dia = data_alvo.strftime("%d")
    data_completa = f"{ano}-{mes}-{dia}"

    total_trechos = 0

    # Download e filtragem de cada seção
    for dou_secao in SECOES_DOU.split():
        print(f"\n📥 Processando {dou_secao}...")

        # Construir URL de download
        url_arquivo = f"{INLABS_BASE_URL}{data_completa}&dl={data_completa}-{dou_secao}.zip"
        cabecalho_arquivo = {
            'Cookie': f'inlabs_session_cookie={cookie}',
            'origem': '736372697074'
        }

        # Download do arquivo
        response_arquivo = s.request("GET", url_arquivo, headers=cabecalho_arquivo)

        if response_arquivo.status_code == 200:
            # Salvar ZIP no diretório output/
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            nome_zip = os.path.join(OUTPUT_DIR, f"{data_completa}-{dou_secao}.zip")
            with open(nome_zip, 'wb') as f:
                f.write(response_arquivo.content)

            print(f"  ✓ Baixado: {nome_zip} ({len(response_arquivo.content)} bytes)")

            # Extrair e filtrar conteúdo
            texto_xml = extrair_texto_xml(response_arquivo.content)
            trechos_encontrados = filtrar_conteudo(texto_xml, PALAVRAS_CHAVE)

            if trechos_encontrados:
                salvar_resultados(data_completa, trechos_encontrados, dou_secao)
                total_trechos += len(trechos_encontrados)
            else:
                print(f"  - Nenhum trecho MRE encontrado")

            # Manter ZIP para referência
            # os.remove(nome_zip)

        elif response_arquivo.status_code == 404:
            nome_zip = os.path.join(OUTPUT_DIR, f"{data_completa}-{dou_secao}.zip")
            print(f"  - Arquivo não encontrado: {nome_zip}")
        else:
            nome_zip = os.path.join(OUTPUT_DIR, f"{data_completa}-{dou_secao}.zip")
            print(f"  ❌ Erro no download: HTTP {response_arquivo.status_code} - {nome_zip}")

    print(f"\n{'='*60}")
    print(f"✅ Processamento concluído")
    print(f"📊 Total de trechos MRE encontrados: {total_trechos}")
    print(f"{'='*60}")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("📰 DOU Download + Filtragem MRE - Teste com Data Específica")
    print("=" * 60)

    resultado = download_xml_filtrado()
    sys.exit(0 if resultado else 1)
