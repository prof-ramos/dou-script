#!/usr/bin/env python3
"""
DOU Download + Filtragem MRE
Baixa XMLs do DOU e filtra por palavras-chave do Ministério das Relações Exteriores
"""

from datetime import date
from typing import Optional, List, Dict
from io import BytesIO
from zipfile import ZipFile, BadZipFile
import requests
import os
import time
import zipfile
import re
import html
import logging
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def extrair_texto_xml(conteudo_zip: bytes) -> Optional[str]:
    """Extrai texto de arquivo XML dentro do ZIP"""
    try:
        with zipfile.ZipFile(BytesIO(conteudo_zip)) as zip_ref:
            for arquivo in zip_ref.namelist():
                if arquivo.endswith('.xml'):
                    xml_content = zip_ref.read(arquivo)
                    return xml_content.decode('utf-8', errors='ignore')
    except BadZipFile as e:
        logger.error(f"ZIP corrompido: {e}")
    except (IOError, OSError) as e:
        logger.error(f"Erro de I/O: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao extrair XML: {e}")
    return ""

def limpar_texto_xml(texto: str) -> str:
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

def filtrar_conteudo(texto_xml: str, palavras_chave: List[str]) -> List[Dict[str, str]]:
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

def salvar_resultados(data_hoje: str, trechos: List[Dict[str, str]], secao: str) -> bool:
    """Salva os trechos filtrados em arquivo"""
    if not trechos:
        return False

    # Criar diretório de output se não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    nome_arquivo = os.path.join(OUTPUT_DIR, f"{data_hoje}-{secao}-MRE.txt")
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(f"=== TRECHOS MRE ENCONTRADOS - {data_hoje} - {secao} ===\n\n")

        for i, trecho in enumerate(trechos, 1):
            f.write(f"[{i}] PALAVRA-CHAVE: {trecho['palavra'].upper()}\n")
            f.write(f"CONTEXTO:\n{trecho['contexto']}\n")
            f.write("-" * 80 + "\n\n")

    logger.info(f"  ✓✓ {len(trechos)} trechos salvos: {nome_arquivo}")
    return True

def download_xml_filtrado() -> bool:
    """Baixa XMLs e filtra por palavras-chave MRE"""
    # Realizar login com retry loop e exponential backoff
    max_attempts = 3
    response = None

    for attempt in range(max_attempts):
        try:
            response = s.request("POST", url_login, data=payload, headers=headers)
            if response.status_code == 200:
                break
        except RequestException as e:
            if attempt < max_attempts - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                logger.warning(f"Erro de conexão, tentando novamente em {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Erro de conexão após múltiplas tentativas: {e}")
                return False

    # Verificar cookie
    if not s.cookies.get('inlabs_session_cookie'):
        logger.error("Falha ao obter cookie. Verifique suas credenciais")
        return False

    cookie = s.cookies.get('inlabs_session_cookie')
    logger.info("Login realizado com sucesso")

    # Data atual
    ano = date.today().strftime("%Y")
    mes = date.today().strftime("%m")
    dia = date.today().strftime("%d")
    data_completa = f"{ano}-{mes}-{dia}"

    # Download e filtragem de cada seção
    for dou_secao in tipo_dou.split():
        logger.info(f"Processando {dou_secao}...")

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
            try:
                with open(nome_zip, 'wb') as f:
                    f.write(response_arquivo.content)

                # Extrair e filtrar conteúdo
                logger.info(f"Baixado: {nome_zip}")

                texto_xml = extrair_texto_xml(response_arquivo.content)
                if texto_xml is None:
                    logger.warning(f"Não foi possível extrair XML de {nome_zip}")
                    continue
                trechos_encontrados = filtrar_conteudo(texto_xml, PALAVRAS_CHAVE)

                if trechos_encontrados:
                    salvar_resultados(data_completa, trechos_encontrados, dou_secao)
                else:
                    logger.info(f"Nenhum trecho MRE encontrado em {dou_secao}")

                # Remover ZIP (não é mais necessário)
                try:
                    os.remove(nome_zip)
                except OSError as e:
                    logger.warning(f"Não foi possível remover {nome_zip}: {e}")
            except (IOError, OSError) as e:
                logger.error(f"Erro de I/O ao processar {nome_zip}: {e}")

        elif response_arquivo.status_code == 404:
            nome_zip = f"{data_completa}-{dou_secao}.zip"
            logger.info(f"Arquivo não encontrado: {nome_zip}")
        else:
            logger.error(f"Erro no download: HTTP {response_arquivo.status_code}")

    logger.info("Processamento concluído")
    return True

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("📰 DOU Download + Filtragem MRE")
    logger.info("=" * 60)
    logger.info(f"📅 Data: {date.today().strftime('%d/%m/%Y')}")
    logger.info(f"🔍 Palavras-chave: {', '.join(PALAVRAS_CHAVE[:5])}...")
    logger.info("=" * 60)

    download_xml_filtrado()
