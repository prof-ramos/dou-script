# Files

## File: __init__.py
```python
"""
DOU Script - Módulo de processamento do Diário Oficial da União.

Este pacote fornece funcionalidades para download, filtragem e processamento
de dados do Diário Oficial da União (DOU) através da API INLABS.
"""

from dou.config import (
    INLABS_LOGIN_URL,
    INLABS_BASE_URL,
    PALAVRAS_CHAVE,
    SECOES_DOU,
    DOWNLOAD_TIMEOUT,
    OUTPUT_DIR
)

from dou.utils import (
    extrair_texto_xml,
    limpar_texto_xml,
    filtrar_conteudo,
    salvar_resultados
)

__all__ = [
    "INLABS_LOGIN_URL",
    "INLABS_BASE_URL",
    "PALAVRAS_CHAVE",
    "SECOES_DOU",
    "DOWNLOAD_TIMEOUT",
    "OUTPUT_DIR",
    "extrair_texto_xml",
    "limpar_texto_xml",
    "filtrar_conteudo",
    "salvar_resultados"
]
```

## File: __init__.py
```python
"""
DOU Script - Módulo de processamento do Diário Oficial da União.

Este pacote fornece funcionalidades para download, filtragem e processamento
de dados do Diário Oficial da União (DOU) através da API INLABS.
"""

from dou.config import (
    INLABS_LOGIN_URL,
    INLABS_BASE_URL,
    PALAVRAS_CHAVE,
    SECOES_DOU,
    DOWNLOAD_TIMEOUT,
    OUTPUT_DIR
)

from dou.utils import (
    extrair_texto_xml,
    limpar_texto_xml,
    filtrar_conteudo,
    salvar_resultados
)

__all__ = [
    "INLABS_LOGIN_URL",
    "INLABS_BASE_URL",
    "PALAVRAS_CHAVE",
    "SECOES_DOU",
    "DOWNLOAD_TIMEOUT",
    "OUTPUT_DIR",
    "extrair_texto_xml",
    "limpar_texto_xml",
    "filtrar_conteudo",
    "salvar_resultados"
]
```

## File: config.py
```python
#!/usr/bin/env python3
"""
DOU Configuration Module

Centralized configuration for DOU download and filtering.
"""

# INLABS API URLs
INLABS_LOGIN_URL = "https://inlabs.in.gov.br/logar.php"
INLABS_BASE_URL = "https://inlabs.in.gov.br/index.php?p="

# Download timeout in seconds
DOWNLOAD_TIMEOUT = 30

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
SECOES_DOU = "DO1 DO2 DO3 DO1E DO2E DO3E"

# Output directory
OUTPUT_DIR = "output"
```

## File: utils.py
```python
"""
Utilitários compartilhados para processamento de DOU.

Este módulo fornece funções auxiliares para extração, limpeza,
filtragem e salvamento de dados do Diário Oficial da União (DOU).
"""

import html
import logging
import os
import re
import zipfile
from io import BytesIO
from typing import Dict, List, Optional

from dou.config import OUTPUT_DIR, PALAVRAS_CHAVE, SECOES_DOU

# Configurar logger
logger = logging.getLogger(__name__)


def extrair_texto_xml(conteudo_zip: bytes) -> Optional[str]:
    """
    Extrai texto de arquivo XML dentro do ZIP.

    Percorre os arquivos dentro do ZIP e retorna o conteúdo do primeiro
    arquivo XML encontrado. Retorna string vazia em caso de erro.

    Args:
        conteudo_zip: Bytes do conteúdo do arquivo ZIP.

    Returns:
        String com o conteúdo XML decodificado em UTF-8, ou string vazia
        se houver erro ou se nenhum XML for encontrado.

    Raises:
        zipfile.BadZipFile: Se o arquivo ZIP estiver corrompido.
        IOError: Se houver erro de leitura do arquivo.
        OSError: Se houver erro no sistema operacional durante leitura.

    Example:
        >>> with open('arquivo.zip', 'rb') as f:
        ...     conteudo = f.read()
        ...     xml = extrair_texto_xml(conteudo)
        >>> print(xml[:100])
        '<?xml version="1.0" encoding="UTF-8"?>...'
    """
    try:
        with zipfile.ZipFile(BytesIO(conteudo_zip)) as zip_ref:
            logger.debug(f"Arquivos no ZIP: {zip_ref.namelist()}")
            for arquivo in zip_ref.namelist():
                if arquivo.endswith('.xml'):
                    xml_content = zip_ref.read(arquivo)
                    return xml_content.decode('utf-8', errors='ignore')
    except zipfile.BadZipFile as e:
        logger.error(f"ZIP corrompido: {e}")
    except (IOError, OSError) as e:
        logger.error(f"Erro de I/O: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao extrair XML: {e}")
    return ""


def limpar_texto_xml(texto: str) -> str:
    """
    Limpa e padroniza texto XML extraído do DOU.

    Remove tags HTML/XML, decodifica entidades HTML e normaliza espaços.
    Preserva quebras de linha significativas.

    Args:
        texto: String com conteúdo XML/HTML bruto.

    Returns:
        String limpa sem tags HTML/XML, com espaços normalizados.

    Example:
        >>> texto = "<p>Texto&lt;br&gt;com <b>tags</b></p>"
        >>> limpar_texto_xml(texto)
        'Texto\\ncom tags'
    """
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
    """
    Filtra conteúdo XML pelas palavras-chave e extrai contexto.

    Para cada ocorrência de cada palavra-chave, extrai um trecho de
    contexto com 200 caracteres antes e 500 depois da ocorrência.

    Args:
        texto_xml: String com conteúdo XML bruto.
        palavras_chave: Lista de palavras-chave para buscar no texto.

    Returns:
        Lista de dicionários contendo:
            - 'palavra': A palavra-chave encontrada.
            - 'contexto': Trecho de texto ao redor da ocorrência (máx 300 chars).
        Retorna lista vazia se nenhuma ocorrência for encontrada.

    Example:
        >>> texto = "O Ministério das Relações Exteriores publicou..."
        >>> palavras = ["ministério das relações exteriores"]
        >>> resultados = filtrar_conteudo(texto, palavras)
        >>> len(resultados)
        1
        >>> resultados[0]['palavra']
        'ministério das relações exteriores'
    """
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


def salvar_resultados(
    data_hoje: str,
    trechos: List[Dict[str, str]],
    secao: str
) -> bool:
    """
    Salva os trechos filtrados em arquivo de texto.

    Cria o diretório de output se não existir e escreve os trechos
    em formato legível com numeração e separadores.

    Args:
        data_hoje: Data no formato YYYY-MM-DD para o nome do arquivo.
        trechos: Lista de dicionários com 'palavra' e 'contexto'.
        secao: Seção do DOU (ex: 'DO1', 'DO2').

    Returns:
        True se salvou com sucesso, False se a lista de trechos está vazia.

    Raises:
        OSError: Se não tiver permissão para criar diretório ou arquivo.
        UnicodeEncodeError: Se não conseguir codificar texto como UTF-8.

    Example:
        >>> trechos = [{'palavra': 'mre', 'contexto': 'Texto do contexto...'}]
        >>> salvar_resultados('2026-03-04', trechos, 'DO1')
        True
        >>> salvar_resultados('2026-03-04', [], 'DO1')
        False
    """
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

    logger.info(f"  {len(trechos)} trechos salvos: {nome_arquivo}")
    return True
```

## File: auto_download_xml.py
```python
#!/usr/bin/env python3
"""
Auto Download DOU XMLs from INLABS
Downloads DOU sections for current date
"""

from datetime import date
import requests
import logging
from zipfile import BadZipFile
from requests.exceptions import RequestException
import os
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration from environment
login = os.getenv("INLABS_EMAIL", "email@dominio.com")
senha = os.getenv("INLABS_PASSWORD", "minha_senha")

tipo_dou = os.getenv("DOU_SECOES", "DO1 DO2 DO3 DO1E DO2E DO3E")  # Seções separadas por espaço
# Opções DO1 DO2 DO3 DO1E DO2E DO3E

url_login = "https://inlabs.in.gov.br/logar.php"
url_download = "https://inlabs.in.gov.br/index.php?p="

payload = {"email": login, "password": senha}
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}
s = requests.Session()

def download() -> None:
    """Download DOU XML files"""
    try:
        if s.cookies.get('inlabs_session_cookie'):
            cookie = s.cookies.get('inlabs_session_cookie')
        else:
            logger.error("Falha ao obter cookie. Verifique suas credenciais")
            exit(37)

        # Montagem da URL:
        ano = date.today().strftime("%Y")
        mes = date.today().strftime("%m")
        dia = date.today().strftime("%d")
        data_completa = ano + "-" + mes + "-" + dia

        # Create output directory
        output_dir = os.getenv("OUTPUT_DIR", "output")
        os.makedirs(output_dir, exist_ok=True)

        for dou_secao in tipo_dou.split(' '):
            logger.info("Aguarde Download...")
            url_arquivo = url_download + data_completa + "&dl=" + data_completa + "-" + dou_secao + ".zip"
            cabecalho_arquivo = {
                'Cookie': 'inlabs_session_cookie=' + cookie,
                'origem': '736372697074'
            }
            response_arquivo = s.request("GET", url_arquivo, headers=cabecalho_arquivo)

            if response_arquivo.status_code == 200:
                filename = os.path.join(output_dir, data_completa + "-" + dou_secao + ".zip")
                with open(filename, "wb") as f:
                    f.write(response_arquivo.content)
                    logger.info(f"Arquivo {filename} salvo.")
                del response_arquivo
                del f
            elif response_arquivo.status_code == 404:
                logger.warning(f"Arquivo não encontrado: {data_completa + '-' + dou_secao + '.zip'}")

        logger.info("Aplicação encerrada")
        exit(0)
    except (IOError, OSError) as e:
        logger.error(f"Erro de I/O: {e}")
        exit(1)
    except RequestException as e:
        logger.error(f"Erro de requisição: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        exit(1)

def login_inlabs() -> None:
    """Perform login to INLABS"""
    try:
        response = s.request("POST", url_login, data=payload, headers=headers)
        download()
    except RequestException as e:
        logger.error(f"Erro de requisição no login: {e}")
        login_inlabs()
    except Exception as e:
        logger.error(f"Erro inesperado no login: {e}")
        exit(1)

if __name__ == "__main__":
    login_inlabs()
```

## File: download_dou.py
```python
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
```

## File: test_mre.py
```python
#!/usr/bin/env python3
"""
DOU Download + Filtragem MRE - Versão de Teste com Data Específica
Uso: python3 scripts/test_mre.py 2026-03-03
"""

from datetime import date, datetime
import requests
import os
import sys
import time

from dou.config import INLABS_LOGIN_URL, INLABS_BASE_URL, PALAVRAS_CHAVE, SECOES_DOU, DOWNLOAD_TIMEOUT, OUTPUT_DIR
from dou.utils import extrair_texto_xml, limpar_texto_xml, filtrar_conteudo, salvar_resultados

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
```

## File: __init__.py
```python
"""
Testes unitários para o pacote dou.
"""
```

## File: __init__.py
```python
"""
Testes unitários para o pacote dou.
"""
```

## File: conftest.py
```python
"""
Fixtures compartilhadas para testes.
"""

import pytest
import zipfile
from io import BytesIO

from dou.config import PALAVRAS_CHAVE, SECOES_DOU


@pytest.fixture
def sample_zip_bytes():
    """ZIP de exemplo para testes."""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr('test.xml', '<?xml version="1.0"?><artigo>Teste MRE conteúdo</artigo>')

    return zip_buffer.getvalue()


@pytest.fixture
def sample_zip_with_multiple_files():
    """ZIP com múltiplos arquivos para testes."""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr('meta.xml', '<?xml version="1.0"?><meta>Info</meta>')
        zf.writestr('content.xml', '<?xml version="1.0"?><artigo>Conteúdo principal MRE aqui</artigo>')
        zf.writestr('readme.txt', 'Este é um arquivo texto')

    return zip_buffer.getvalue()


@pytest.fixture
def sample_xml_content():
    """Conteúdo XML de exemplo para testes."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<artigo>
    <p>O <b>Ministério das Relações Exteriores</b> publicou hoje.</p>
    <br/>
    <p>Seção&nbsp;1 - Conteúdo de teste.</p>
</artigo>"""


@pytest.fixture
def palavras_chave():
    """Palavras-chave MRE para testes."""
    return PALAVRAS_CHAVE


@pytest.fixture
def temp_output_dir(tmp_path):
    """Diretório temporário para output de testes."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return str(output_dir)


@pytest.fixture
def sample_trechos():
    """Trechos de exemplo para testes de salvamento."""
    return [
        {'palavra': 'mre', 'contexto': 'O Ministério das Relações Exteriores publicou...'},
        {'palavra': 'embaixada', 'contexto': 'A embaixada informou que...'}
    ]
```

## File: test_config.py
```python
"""
Testes para dou_config.
"""

import pytest

from dou.config import (
    INLABS_LOGIN_URL,
    INLABS_BASE_URL,
    PALAVRAS_CHAVE,
    SECOES_DOU,
    DOWNLOAD_TIMEOUT,
    OUTPUT_DIR
)


class TestConfigURLs:
    """Testes para URLs de configuração."""

    def test_login_url_format(self):
        """URL de login deve ser HTTPS válida."""
        assert INLABS_LOGIN_URL.startswith("https://")
        assert "inlabs.in.gov.br" in INLABS_LOGIN_URL

    def test_base_url_format(self):
        """URL base deve ser HTTPS válida."""
        assert INLABS_BASE_URL.startswith("https://")
        assert "inlabs.in.gov.br" in INLABS_BASE_URL

    def test_base_url_contains_param(self):
        """URL base deve conter parâmetro p=."""
        assert "p=" in INLABS_BASE_URL


class TestConfigTimeout:
    """Testes para configuração de timeout."""

    def test_download_timeout_positive(self):
        """Timeout de download deve ser positivo."""
        assert DOWNLOAD_TIMEOUT > 0
        assert isinstance(DOWNLOAD_TIMEOUT, int)

    def test_download_timeout_reasonable(self):
        """Timeout de download deve ser razoável (pelo menos 10 segundos)."""
        assert DOWNLOAD_TIMEOUT >= 10


class TestConfigPalavrasChave:
    """Testes para palavras-chave de configuração."""

    def test_palavras_chave_not_empty(self):
        """Palavras-chave não devem estar vazias."""
        assert len(PALAVRAS_CHAVE) > 0

    def test_palavras_chave_contains_mre(self):
        """Palavras-chave devem conter 'mre'."""
        assert "mre" in PALAVRAS_CHAVE

    def test_palavras_chave_contains_variations(self):
        """Palavras-chave devem conter variações do Ministério."""
        assert "ministério das relações exteriores" in PALAVRAS_CHAVE
        assert "embaixada" in PALAVRAS_CHAVE
        assert "consulado" in PALAVRAS_CHAVE

    def test_palavras_chave_all_lowercase(self):
        """Todas as palavras-chave devem ser minúsculas."""
        assert all(p.islower() for p in PALAVRAS_CHAVE)


class TestConfigSecoes:
    """Testes para seções do DOU."""

    def test_secoes_dou_not_empty(self):
        """Seções não devem estar vazias."""
        assert len(SECOES_DOU) > 0

    def test_secoes_dou_contains_expected(self):
        """Seções devem conter DO1, DO2, DO3."""
        assert "DO1" in SECOES_DOU
        assert "DO2" in SECOES_DOU
        assert "DO3" in SECOES_DOU

    def test_secoes_dou_contains_extras(self):
        """Seções devem conter edições extras."""
        assert "DO1E" in SECOES_DOU
        assert "DO2E" in SECOES_DOU
        assert "DO3E" in SECOES_DOU


class TestConfigOutput:
    """Testes para configuração de output."""

    def test_output_dir_is_string(self):
        """Diretório de output deve ser string."""
        assert isinstance(OUTPUT_DIR, str)

    def test_output_dir_not_empty(self):
        """Diretório de output não deve estar vazio."""
        assert len(OUTPUT_DIR) > 0
```

## File: test_utils.py
```python
"""
Testes para dou_utils.
"""

import os
import pytest
import zipfile
from io import BytesIO

from dou.utils import extrair_texto_xml, limpar_texto_xml, filtrar_conteudo, salvar_resultados


class TestExtrairTextoXML:
    """Testes para extração de texto XML."""

    def test_extrair_xml_valido(self, sample_zip_bytes):
        """Deve extrair XML de ZIP válido."""
        resultado = extrair_texto_xml(sample_zip_bytes)
        assert resultado is not None
        assert len(resultado) > 0
        assert "<?xml" in resultado or "artigo" in resultado

    def test_extrair_xml_primeiro_arquivo(self, sample_zip_with_multiple_files):
        """Deve extrair o primeiro arquivo XML encontrado."""
        resultado = extrair_texto_xml(sample_zip_with_multiple_files)
        assert resultado is not None
        # Deve retornar o primeiro XML (meta.xml ou content.xml)
        assert "<?xml" in resultado

    def test_extrair_xml_zip_corrompido(self):
        """Deve retornar string vazia para ZIP corrompido."""
        zip_corrompido = b"Este nao e um ZIP valido"
        resultado = extrair_texto_xml(zip_corrompido)
        assert resultado == ""

    def test_extrair_xml_zip_vazio(self):
        """Deve retornar string vazia para ZIP sem XML."""
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr('readme.txt', 'Apenas texto')

        resultado = extrair_texto_xml(zip_buffer.getvalue())
        assert resultado == ""


class TestLimparTextoXML:
    """Testes para limpeza de texto XML."""

    def test_limpar_texto_remove_html_tags(self):
        """Deve remover tags <p> e </p>."""
        texto = "<p>Art. 1°</p> O MINISTÉRIO"
        resultado = limpar_texto_xml(texto)
        assert "<p>" not in resultado
        assert "</p>" not in resultado
        assert "Art. 1°" in resultado

    def test_limpar_texto_remove_bold_tags(self):
        """Deve remover tags <b> e </b>."""
        texto = "Texto <b>importante</b> aqui"
        resultado = limpar_texto_xml(texto)
        assert "<b>" not in resultado
        assert "</b>" not in resultado
        assert "Texto importante aqui" == resultado

    def test_limpar_texto_convert_br_to_newline(self):
        """Deve converter <br> para quebra de linha."""
        texto = "Linha 1<br>Linha 2"
        resultado = limpar_texto_xml(texto)
        assert "<br" not in resultado
        assert "\n" in resultado

    def test_limpar_texto_decode_entities(self):
        """Deve decodificar entidades HTML."""
        texto = "Seção&nbsp;1"
        resultado = limpar_texto_xml(texto)
        assert "&nbsp;" not in resultado
        # &nbsp; é decodificado para non-breaking space (\xa0), não espaço regular
        assert "Seção\xa01" == resultado

    def test_limpar_texto_remove_xml_attributes(self):
        """Deve remover atributos XML."""
        texto = 'texto id="123" classe="abc"'
        resultado = limpar_texto_xml(texto)
        assert 'id="123"' not in resultado
        assert 'classe="abc"' not in resultado

    def test_limpar_texto_normalize_spaces(self):
        """Deve normalizar espaços excessivos."""
        texto = "Texto    com    espaços    múltiplos"
        resultado = limpar_texto_xml(texto)
        assert "Texto com espaços múltiplos" == resultado

    def test_limpar_texto_preserve_newlines(self):
        """Deve preservar quebras de linha significativas."""
        texto = "Linha 1\n\n\nLinha 2"
        resultado = limpar_texto_xml(texto)
        assert "\n\n" in resultado  # Dupla newline preservada

    def test_limpar_texto_strip(self):
        """Deve remover espaços no início e fim."""
        texto = "   \n  Texto central  \n   "
        resultado = limpar_texto_xml(texto)
        assert resultado == resultado.strip()


class TestFiltrarConteudo:
    """Testes para filtragem de conteúdo."""

    def test_filtrar_conteudo_case_insensitive(self):
        """Busca deve ser case-insensitive."""
        texto = "O Ministério das Relações Exteriores publicou."
        palavras = ["mre"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado) == 0  # "mre" não está no texto

    def test_filtrar_conteudo_encontra_palavra(self):
        """Deve encontrar palavra-chave no texto."""
        texto = "O Ministério das Relações Exteriores publicou."
        palavras = ["ministério das relações exteriores"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado) == 1
        assert resultado[0]['palavra'] == "ministério das relações exteriores"

    def test_filtrar_conteudo_multiple_ocorrencias(self):
        """Deve encontrar múltiplas ocorrências da mesma palavra."""
        texto = "O MRE informou. O MRE publicou. O MRE decidiu."
        palavras = ["mre"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado) == 3

    def test_filtrar_conteudo_multiple_palavras(self):
        """Deve encontrar múltiplas palavras-chave."""
        texto = "O MRE e a embaixada informaram."
        palavras = ["mre", "embaixada"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado) == 2

    def test_filtrar_conteudo_contexto_limitado(self):
        """Contexto deve ser limitado a 300 caracteres."""
        texto = "MRE" + "X" * 1000
        palavras = ["mre"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado) == 1
        assert len(resultado[0]['contexto']) <= 303  # 300 + "..."

    def test_filtrar_conteudo_retorna_lista_vazia(self):
        """Deve retornar lista vazia se não encontrar nada."""
        texto = "Texto sem palavras-chave relevantes."
        palavras = ["inexistente"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado) == 0

    def test_filtrar_conteudo_com_tags_html(self, sample_xml_content):
        """Deve funcionar com XML contendo tags HTML."""
        palavras = ["ministério das relações exteriores"]
        resultado = filtrar_conteudo(sample_xml_content, palavras)
        assert len(resultado) == 1
        assert "<b>" not in resultado[0]['contexto']


class TestSalvarResultados:
    """Testes para salvamento de resultados."""

    def test_salvar_resultados_sucesso(self, tmp_path, sample_trechos, monkeypatch):
        """Deve salvar arquivo com sucesso."""
        # Patch OUTPUT_DIR para usar tmp_path
        monkeypatch.setattr("dou.utils.OUTPUT_DIR", str(tmp_path))

        resultado = salvar_resultados("2026-03-04", sample_trechos, "DO1")
        assert resultado is True

        # Verificar que arquivo foi criado
        arquivo = tmp_path / "2026-03-04-DO1-MRE.txt"
        assert arquivo.exists()

        # Verificar conteúdo
        conteudo = arquivo.read_text(encoding='utf-8')
        assert "TRECHOS MRE ENCONTRADOS" in conteudo
        assert "PALAVRA-CHAVE: MRE" in conteudo
        assert "PALAVRA-CHAVE: EMBAIXADA" in conteudo

    def test_salvar_resultados_lista_vazia(self, tmp_path, monkeypatch):
        """Deve retornar False para lista vazia."""
        monkeypatch.setattr("dou.utils.OUTPUT_DIR", str(tmp_path))

        resultado = salvar_resultados("2026-03-04", [], "DO1")
        assert resultado is False

    def test_salvar_resultados_cria_diretorio(self, tmp_path, sample_trechos, monkeypatch):
        """Deve criar diretório de output se não existir."""
        output_dir = tmp_path / "novo_output"
        monkeypatch.setattr("dou.utils.OUTPUT_DIR", str(output_dir))

        salvar_resultados("2026-03-04", sample_trechos, "DO1")

        assert output_dir.exists()
        assert (output_dir / "2026-03-04-DO1-MRE.txt").exists()

    def test_salvar_resultados_unicode(self, tmp_path, monkeypatch):
        """Deve salvar caracteres Unicode corretamente."""
        monkeypatch.setattr("dou.utils.OUTPUT_DIR", str(tmp_path))

        trechos = [
            {'palavra': 'mre', 'contexto': 'Ministério das Relações Exteriores - Seção 1'}
        ]

        salvar_resultados("2026-03-04", trechos, "DO1")

        arquivo = tmp_path / "2026-03-04-DO1-MRE.txt"
        conteudo = arquivo.read_text(encoding='utf-8')
        assert "Ministério" in conteudo
        assert "Seção" in conteudo
```