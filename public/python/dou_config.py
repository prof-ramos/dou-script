#!/usr/bin/env python3
"""
DOU Configuration Module
Centralized configuration for DOU download and filtering
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
