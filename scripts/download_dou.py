#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOU Download + Filtragem MRE
Baixa XMLs do DOU e filtra por palavras-chave do Ministério das Relações Exteriores
"""

import os
import sys
import time
import logging
import requests
from datetime import date
from requests.exceptions import RequestException

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dou.config import INLABS_LOGIN_URL, INLABS_BASE_URL, PALAVRAS_CHAVE, SECOES_DOU, DOWNLOAD_TIMEOUT, OUTPUT_DIR
from dou.utils import extrair_texto_xml, limpar_texto_xml, filtrar_conteudo, salvar_resultados

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Credenciais
login = os.getenv("INLABS_EMAIL")
senha = os.getenv("INLABS_PASSWORD")

# Payload e headers
payload = {"email": login, "password": senha}
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def download_xml_filtrado() -> bool:
    """Baixa XMLs e filtra por palavras-chave MRE"""
    # Criar sessão localmente
    s = requests.Session()

    # Realizar login com retry loop e exponential backoff
    max_attempts = 3
    response = None

    for attempt in range(max_attempts):
        try:
            response = s.request("POST", INLABS_LOGIN_URL, data=payload, headers=headers)
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
    for dou_secao in SECOES_DOU.split():
        logger.info(f"Processando {dou_secao}...")

        # Construir URL de download
        url_arquivo = f"{INLABS_BASE_URL}{data_completa}&dl={data_completa}-{dou_secao}.zip"
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
    logger.info("DOU Download + Filtragem MRE")
    logger.info("=" * 60)
    logger.info(f"Data: {date.today().strftime('%d/%m/%Y')}")
    logger.info(f"Palavras-chave: {', '.join(PALAVRAS_CHAVE[:5])}...")
    logger.info("=" * 60)

    download_xml_filtrado()
