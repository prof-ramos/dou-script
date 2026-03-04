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
