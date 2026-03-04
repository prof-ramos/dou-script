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


from .dou_config import OUTPUT_DIR, PALAVRAS_CHAVE, SECOES_DOU

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
