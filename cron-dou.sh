#!/bin/bash
set -euo pipefail
# Script para agendamento do DOU download + Filtragem MRE
# Horários: 10h, 12h (se não o DOU for o mesmo, apagará), 23h (se for o mesmo, apagará)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Exportar variáveis de ambiente
set -a; source .env; set +a

# Função para verificar se o DOU já existe
check_duplicate() {
    local data_hoje=$(date +%Y-%m-%d)
    local OUTPUT_DIR="output"
    for secao in DO1 DO2 DO3 DO1E DO2E DO3E; do
        if [ -f "${OUTPUT_DIR}/${data_hoje}-${secao}.zip" ] || [ -f "${OUTPUT_DIR}/${data_hoje}-${secao}-MRE.txt" ]; then
            return 0  # Duplicata encontrada
        fi
    done
    return 1  # Sem duplicata
}

# Função para remover DOU duplicado
remove_duplicate() {
    local data_hoje=$(date +%Y-%m-%d)
    local OUTPUT_DIR="output"
    echo "[$(date)] Removendo DOU duplicado..."
    for secao in DO1 DO2 DO3 DO1E DO2E DO3E; do
        if [ -f "${OUTPUT_DIR}/${data_hoje}-${secao}.zip" ]; then
            rm -f "${OUTPUT_DIR}/${data_hoje}-${secao}.zip"
            echo "[$(date)] Removido: ${OUTPUT_DIR}/${data_hoje}-${secao}.zip"
        fi
        if [ -f "${OUTPUT_DIR}/${data_hoje}-${secao}-MRE.txt" ]; then
            rm -f "${OUTPUT_DIR}/${data_hoje}-${secao}-MRE.txt"
            echo "[$(date)] Removido: ${OUTPUT_DIR}/${data_hoje}-${secao}-MRE.txt"
        fi
    done
}

# Horário 10h e 23h: Download + Filtragem MRE
if [ "$1" = "download" ]; then
    echo "[$(date)] Iniciando download DOU + Filtragem MRE..."
    python3 public/python/inlabs-filter-mre.py
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "[$(date)] Erro no script Python (exit code: $exit_code)"
        exit $exit_code
    fi
    echo "[$(date)] Processamento concluído"
fi

# Horário 12h e 23h: Verificar e remover duplicata
if [ "$1" = "check-duplicate" ]; then
    if check_duplicate; then
        remove_duplicate
    else
        echo "[$(date)] Sem duplicata para remover"
    fi
fi
