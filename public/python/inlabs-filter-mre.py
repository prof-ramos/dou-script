#!/usr/bin/env python3
"""
DOU Download + Filtragem MRE
Baixa XMLs do DOU e filtra por palavras-chave do Ministério das Relações Exteriores
"""

from datetime import date
import requests
import os
import time
import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO
import re
import html

# Configurações
OUTPUT_DIR = "output"
login = os.getenv("INLABS_EMAIL")
senha = os.getenv("INLABS_PASSWORD")

# Palavras-chave para filtrar (MRE - Ministério das Relações Exteriores)
PALAVRAS_CHAVE = [
    "ministério das relações exteriores",
    "ministério relações exteriores",
    "oficial de chancelaria",
    "chancelaria",
    "concursos públicos",
    "concursos",
    "mre",
    "embaixada",
    "consulado",
    "diplomacia"
]

# Seções DOU para XML (inclui edições extras)
tipo_dou = "DO1 DO2 DO3 DO1E DO2E DO3E"

url_login = "https://inlabs.in.gov.br/logar.php"
url_download = "https://inlabs.in.gov.br/index.php?p="

payload = {"email": login, "password": senha}
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

s = requests.Session()

def extrair_texto_xml(conteudo_zip):
    """Extrai texto de arquivo XML dentro do ZIP"""
    try:
        with zipfile.ZipFile(BytesIO(conteudo_zip)) as zip_ref:
            for arquivo in zip_ref.namelist():
                if arquivo.endswith('.xml'):
                    xml_content = zip_ref.read(arquivo)
                    return xml_content.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Erro ao extrair XML: {e}")
    return ""

def limpar_texto_xml(texto):
    """Limpa e padroniza texto XML extraído do DOU"""
    # Decodificar entidades HTML
    texto = html.unescape(texto)

    # Remover tags HTML comuns
    texto = re.sub(r'</?p>', '', texto)
    texto = re.sub(r'<br\s*/?>', '\n', texto)
    texto = re.sub(r'</?[a-z]+[^>]*>', '', texto)

    # Remover atributos XML
    texto = re.sub(r'\s*[a-zA-Z]+="[^"]*"', '', texto)

    # Limpar espaços excessivos (apenas tabs e espaços, preservando newlines)
    texto = re.sub(r'[ \t]+', ' ', texto)
    texto = re.sub(r'\n\s*\n\s*\n+', '\n\n', texto)

    return texto.strip()

def filtrar_conteudo(texto_xml, palavras_chave):
    """Filtra conteúdo pelas palavras-chave"""
    trechos_encontrados = []

    # Limpar o texto XML antes de filtrar
    texto_limpo = limpar_texto_xml(texto_xml)
    texto_lower = texto_limpo.lower()

    for palavra in palavras_chave:
        palavra_lower = palavra.lower()

        # Buscar TODAS as ocorrências da palavra-chave
        for match in re.finditer(re.escape(palavra_lower), texto_lower):
            idx = match.start()
            inicio = max(0, idx - 200)
            fim = min(len(texto_limpo), idx + 500)
            contexto = texto_limpo[inicio:fim].strip()

            # Limitar tamanho
            if len(contexto) > 300:
                contexto = contexto[:300] + "..."

            trechos_encontrados.append({
                'palavra': palavra,
                'contexto': contexto
            })

    return trechos_encontrados

def salvar_resultados(data_hoje, trechos, secao):
    """Salva os trechos filtrados em arquivo"""
    if not trechos:
        return

    # Criar diretório de output se não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    nome_arquivo = os.path.join(OUTPUT_DIR, f"{data_hoje}-{secao}-MRE.txt")
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(f"=== TRECHOS MRE ENCONTRADOS - {data_hoje} - {secao} ===\n\n")

        for i, trecho in enumerate(trechos, 1):
            f.write(f"[{i}] PALAVRA-CHAVE: {trecho['palavra'].upper()}\n")
            f.write(f"CONTEXTO:\n{trecho['contexto']}\n")
            f.write("-" * 80 + "\n\n")

    print(f"  ✓✓ {len(trechos)} trechos salvos: {nome_arquivo}")

def download_xml_filtrado():
    """Baixa XMLs e filtra por palavras-chave MRE"""
    # Realizar login com retry loop e exponential backoff
    max_attempts = 3
    response = None

    for attempt in range(max_attempts):
        try:
            response = s.request("POST", url_login, data=payload, headers=headers)
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            if attempt < max_attempts - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"Erro de conexão, tentando novamente em {wait_time}s...")
                time.sleep(wait_time)
            else:
                print("❌ Erro de conexão após múltiplas tentativas")
                return False

    # Verificar cookie
    if not s.cookies.get('inlabs_session_cookie'):
        print("❌ Falha ao obter cookie. Verifique suas credenciais")
        return False

    cookie = s.cookies.get('inlabs_session_cookie')
    print(f"✓ Login realizado com sucesso")

    # Data atual
    ano = date.today().strftime("%Y")
    mes = date.today().strftime("%m")
    dia = date.today().strftime("%d")
    data_completa = f"{ano}-{mes}-{dia}"

    # Download e filtragem de cada seção
    for dou_secao in tipo_dou.split():
        print(f"\n📥 Processando {dou_secao}...")

        # Construir URL de download
        url_arquivo = f"{url_download}{data_completa}&dl={data_completa}-{dou_secao}.zip"
        cabecalho_arquivo = {
            'Cookie': f'inlabs_session_cookie={cookie}',
            # '736372697074' é 'script' em hexadecimal (valor exigido pelo INLABS)
            'origem': '736372697074'
        }

        # Download do arquivo
        response_arquivo = s.request("GET", url_arquivo, headers=cabecalho_arquivo)

        if response_arquivo.status_code == 200:
            # Salvar ZIP
            nome_zip = f"{data_completa}-{dou_secao}.zip"
            with open(nome_zip, 'wb') as f:
                f.write(response_arquivo.content)

            # Extrair e filtrar conteúdo
            print(f"  ✓ Baixado: {nome_zip}")

            texto_xml = extrair_texto_xml(response_arquivo.content)
            trechos_encontrados = filtrar_conteudo(texto_xml, PALAVRAS_CHAVE)

            if trechos_encontrados:
                salvar_resultados(data_completa, trechos_encontrados, dou_secao)
            else:
                print(f"  - Nenhum trecho MRE encontrado")

            # Remover ZIP (não é mais necessário)
            try:
                os.remove(nome_zip)
            except OSError as e:
                print(f"  ⚠️  Aviso: não foi possível remover {nome_zip}: {e}")

        elif response_arquivo.status_code == 404:
            nome_zip = f"{data_completa}-{dou_secao}.zip"
            print(f"  - Arquivo não encontrado: {nome_zip}")
        else:
            print(f"  ❌ Erro no download: HTTP {response_arquivo.status_code}")

    print(f"\n✅ Processamento concluído")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("📰 DOU Download + Filtragem MRE")
    print("=" * 60)
    print(f"📅 Data: {date.today().strftime('%d/%m/%Y')}")
    print(f"🔍 Palavras-chave: {', '.join(PALAVRAS_CHAVE[:5])}...")
    print("=" * 60)

    download_xml_filtrado()
