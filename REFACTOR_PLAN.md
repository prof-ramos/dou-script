# 🎯 Plano de Refatoração - DOU Script

## Visão Geral

Este plano endereça os 9 findings identificados em REFACTOR_FINDINGS.md, organizados em 3 fases de acordo com risco e dependências.

**Estratégia:** Aplicações incrementais e testáveis, com rollback safety.

---

## FASE 1 - Refatoração Segura/Mecânica

**Risco:** BAIXO | **Impacto:** Melhorias incrementais | **Rollback:** Git revert

### 1.1 Remover Código Morto (Finding #8)

**Arquivo:** `public/python/inlabs-filter-mre.py`

**Mudança:**
```python
# REMOVER:
import xml.etree.ElementTree as ET  # Linha 12
```

**Justificativa:** Import nunca referenciado no código.

**Validação:**
```bash
python3 -m py_compile public/python/inlabs-filter-mre.py
python3 test-mre.py 2026-03-02
```

---

### 1.2 Substituir print() por logging (Finding #1)

**Arquivos:** `inlabs-filter-mre.py`, `test-mre.py`

**Mudança:**
```python
# ADICIONAR no topo:
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# SUBSTITUIR:
print(f"Baixando {tipo_dou} - {data_hoje}")
# POR:
logger.info(f"Baixando {tipo_dou} - {data_hoje}")
```

**Mapeamento:**
- `print("ERRO: ...")` → `logger.error(...)`
- `print("AVISO: ...")` → `logger.warning(...)`
- `print("Sucesso!")` → `logger.info(...)`

**Validação:**
```bash
# Verificar se logs aparecem
python3 test-mre.py 2026-03-02 2>&1 | grep -E "(INFO|ERROR|WARNING)"
```

---

### 1.3 Adicionar Type Hints Básicos (Finding #4)

**Arquivos:** `inlabs-filter-mre.py`, `test-mre.py`

**Mudança:**
```python
from typing import Optional, List, Dict
from io import BytesIO
from zipfile import ZipFile

def extrair_texto_xml(conteudo_zip: bytes) -> Optional[str]:
    """Extrai texto de arquivo XML dentro do ZIP."""
    try:
        with ZipFile(BytesIO(conteudo_zip)) as zip_ref:
            ...
    except Exception as e:
        logger.error(f"Erro ao extrair XML: {e}")
        return None

def limpar_texto_xml(texto: str) -> str:
    """Limpa e padroniza texto XML extraído do DOU."""
    return re.sub(r'</?p>', '', texto)

def filtrar_conteudo(texto_xml: str, palavras_chave: List[str]) -> List[Dict[str, str]]:
    """Filtra conteúdo baseado em palavras-chave."""
    trechos = []
    for palavra in palavras_chave:
        ...
    return trechos
```

**Validação:**
```bash
python3 -m mypy public/python/inlabs-filter-mre.py --ignore-missing-imports
```

---

### 1.4 Usar Exceções Específicas (Finding #6)

**Arquivos:** `public/python/inlabs-auto-download-xml.py`, `inlabs-filter-mre.py`

**Mudança:**
```python
from zipfile import BadZipFile
from requests.exceptions import RequestException

# ANTES:
except Exception as e:
    print(f"Erro ao extrair XML: {e}")

# DEPOIS:
except BadZipFile as e:
    logger.error(f"ZIP corrompido: {e}")
except (IOError, OSError) as e:
    logger.error(f"Erro de I/O: {e}")
except RequestException as e:
    logger.error(f"Erro de requisição: {e}")
except Exception as e:
    logger.error(f"Erro inesperado: {e}")
```

**Validação:**
```bash
python3 test-mre.py 2026-03-02
```

---

## FASE 2 - Refatoração Moderada

**Risco:** MÉDIO | **Impacto:** Melhorias estruturais | **Rollback:** Git revert

### 2.1 Criar Módulo Compartilhado (Finding #2 - ALTA PRIORIDADE)

**Novo Arquivo:** `public/python/dou_utils.py`

```python
"""
Módulo compartilhado para processamento de DOU.

Comum a inlabs-filter-mre.py e test-mre.py.
"""

import logging
import re
import html
from typing import Optional, List, Dict
from io import BytesIO
from zipfile import ZipFile

logger = logging.getLogger(__name__)

# Constantes compartilhadas
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
    "diplomacia",
]

SECOES_DOU = ["DO1", "DO2", "DO3", "DO1E", "DO2E", "DO3E"]


def extrair_texto_xml(conteudo_zip: bytes) -> Optional[str]:
    """
    Extrai texto de arquivo XML dentro do ZIP.

    Args:
        conteudo_zip: Bytes do arquivo ZIP

    Returns:
        Texto XML decodificado ou None em caso de erro
    """
    try:
        with ZipFile(BytesIO(conteudo_zip)) as zip_ref:
            for arq in zip_ref.namelist():
                if arq.endswith('.xml'):
                    with zip_ref.open(arq) as f:
                        return f.read().decode('utf-8', errors='ignore')
        return None
    except Exception as e:
        logger.error(f"Erro ao extrair XML: {e}")
        return None


def limpar_texto_xml(texto: str) -> str:
    """
    Limpa e padroniza texto XML extraído do DOU.

    Args:
        texto: Texto XML bruto

    Returns:
        Texto limpo sem tags HTML/XML
    """
    texto = html.unescape(texto)
    texto = re.sub(r'</?p>', '', texto)
    texto = re.sub(r'<br\s*/?>', '\n', texto)
    texto = re.sub(r'artType="[^"]*"', '', texto)
    texto = re.sub(r'[ \t]+', ' ', texto)
    texto = re.sub(r'\n+', '\n', texto)
    return texto.strip()


def filtrar_conteudo(texto_xml: str, palavras_chave: List[str]) -> List[Dict[str, str]]:
    """
    Filtra conteúdo baseado em palavras-chave.

    Args:
        texto_xml: Texto XML limpo
        palavras_chave: Lista de palavras para buscar

    Returns:
        Lista de trechos encontrados com contexto
    """
    trechos = []
    texto_lower = texto_xml.lower()

    for palavra in palavras_chave:
        if palavra.lower() in texto_lower:
            idx = texto_lower.find(palavra.lower())
            inicio = max(0, idx - 200)
            fim = min(len(texto_xml), idx + len(palavra) + 500)
            contexto = texto_xml[inicio:fim].strip()

            trechos.append({
                'palavra_chave': palavra.upper(),
                'contexto': contexto[:300]
            })

    return trechos


def salvar_resultados(data: str, trechos: List[Dict], secao: str, output_dir: str = "output") -> bool:
    """
    Salva trechos filtrados em arquivo.

    Args:
        data: Data no formato YYYY-MM-DD
        trechos: Lista de trechos encontrados
        secao: Seção do DOU (DO1, DO2, etc.)
        output_dir: Diretório de saída

    Returns:
        True se salvou com sucesso, False caso contrário
    """
    if not trechos:
        return False

    import os
    os.makedirs(output_dir, exist_ok=True)

    arquivo = f"{output_dir}/{data}-{secao}-MRE.txt"

    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(f"=== TRECHOS MRE ENCONTRADOS - {data} - {secao} ===\n\n")

            for i, trecho in enumerate(trechos, 1):
                f.write(f"[{i}] PALAVRA-CHAVE: {trecho['palavra_chave']}\n")
                f.write(f"CONTEXTO:\n{trecho['contexto']}\n")
                f.write("-" * 80 + "\n\n")

        logger.info(f"Salvo: {arquivo}")
        return True
    except IOError as e:
        logger.error(f"Erro ao salvar {arquivo}: {e}")
        return False
```

**Atualizar `inlabs-filter-mre.py`:**
```python
# REMOVER funções duplicadas
# ADICIONAR:
from dou_utils import (
    PALAVRAS_CHAVE,
    SECOES_DOU,
    extrair_texto_xml,
    limpar_texto_xml,
    filtrar_conteudo,
    salvar_resultados
)
```

**Atualizar `test-mre.py`:**
```python
# REMOVER funções duplicadas
# ADICIONAR:
import sys
sys.path.insert(0, 'public/python')
from dou_utils import (
    PALAVRAS_CHAVE,
    SECOES_DOU,
    extrair_texto_xml,
    limpar_texto_xml,
    filtrar_conteudo,
    salvar_resultados
)
```

**Validação:**
```bash
# Testar ambos os scripts
python3 test-mre.py 2026-03-02
python3 public/python/inlabs-filter-mre.py

# Verificar outputs
ls -lh output/
```

---

### 2.2 Mover Sessão para Escopo Local (Finding #3)

**Arquivo:** `public/python/inlabs-filter-mre.py`

**Mudança:**
```python
# ANTES (linha 48):
s = requests.Session()  # Global

def download_xml_filtrado(data, tipo_dou):
    ...
    response = s.get(url_download, ...)  # Usa global

# DEPOIS:
def download_xml_filtrado(data: str, tipo_dou: str, session: requests.Session) -> Optional[bytes]:
    """Baixa XML filtrado usando sessão existente."""
    ...
    response = session.get(url_download, ...)
    ...

# NOVO main():
def main():
    s = requests.Session()
    s.raise_for_status = True

    # Login
    payload = {"email": email, "password": password}
    r = s.post(url_login, data=payload, timeout=30)
    r.raise_for_status()

    # Downloads passam a sessão
    for tipo_dou in SECOES_DOU:
        download_xml_filtrado(data_hoje, tipo_dou, s)
```

**Validação:**
```bash
python3 test-mre.py 2026-03-02
```

---

### 2.3 Mover Constantes para Configuração (Finding #5)

**Novo Arquivo:** `public/python/dou_config.py`

```python
"""
Configurações para processamento de DOU.
"""

from typing import List

# URLs IN Labs
INLABS_LOGIN_URL = "https://inlabs.in.gov.br/logar.php"
INLABS_BASE_URL = "https://inlabs.inlabs.in.gov.br/index.php?p="

# Palavras-chave MRE
PALAVRAS_CHAVE: List[str] = [
    "ministério das relações exteriores",
    "ministério relações exteriores",
    "oficial de chancelaria",
    "chancelaria",
    "concursos públicos",
    "concursos",
    "mre",
    "embaixada",
    "consulado",
    "diplomacia",
]

# Seções DOU
SECOES_DOU: List[str] = ["DO1", "DO2", "DO3", "DO1E", "DO2E", "DO3E"]

# Configurações de download
DOWNLOAD_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]
```

**Atualizar imports:**
```python
from dou_config import INLABS_LOGIN_URL, INLABS_BASE_URL, PALAVRAS_CHAVE, SECOES_DOU
```

**Validação:**
```bash
python3 test-mre.py 2026-03-02
```

---

### 2.4 Melhorar Docstrings (Finding #7)

**Padrão Google Style:**
```python
def filtrar_conteudo(texto_xml: str, palavras_chave: List[str]) -> List[Dict[str, str]]:
    """
    Filtra conteúdo XML baseado em palavras-chave do MRE.

    Busca cada palavra-chave no texto e extrai contexto ao redor
    (-200 caracteres antes, +500 depois).

    Args:
        texto_xml: Texto XML limpo sem tags
        palavras_chave: Lista de palavras para busca case-insensitive

    Returns:
        Lista de dicionários com:
            - palavra_chave: str - Palavra encontrada (uppercase)
            - contexto: str - Contexto de até 300 caracteres

    Example:
        >>> palavras = ["mre", "embaixada"]
        >>> filtrar_conteudo("O MRE publicou...", palavras)
        [{'palavra_chave': 'MRE', 'contexto': 'O MRE publicou...'}]
    """
    ...
```

**Validação:**
```bash
python3 -c "from dou_utils import filtrar_conteudo; help(filtrar_conteudo)"
```

---

## FASE 3 - Refatoração Avançada (Opcional)

**Risco:** MÉDIO-ALTO | **Impacto:** Reorganização estrutural | **Rollback:** Git revert

### 3.1 Reorganizar Estrutura de Diretórios

**Estrutura Atual:**
```
dou-script/
├── public/python/
│   ├── inlabs-filter-mre.py
│   ├── inlabs-auto-download-pdf.py
│   └── inlabs-auto-download-xml.py
├── test-mre.py
└── cron-dou.sh
```

**Estrutura Proposta:**
```
dou-script/
├── dou/
│   ├── __init__.py
│   ├── config.py          # Configurações
│   ├── utils.py           # Funções compartilhadas
│   ├── api.py             # Cliente IN Labs
│   └── filter.py          # Lógica de filtragem MRE
├── scripts/
│   ├── download_dou.py    # Script principal
│   └── test_mre.py        # Script de teste
├── tests/
│   ├── __init__.py
│   ├── test_utils.py
│   └── test_filter.py
├── cron-dou.sh
└── requirements.txt
```

**Migração:**
```bash
# Criar estrutura
mkdir -p dou scripts tests

# Mover código
mv public/python/dou_config.py dou/config.py
mv public/python/dou_utils.py dou/utils.py
mv public/python/inlabs-filter-mre.py scripts/download_dou.py
mv test-mre.py scripts/test_mre.py

# Limpar
rm -rf public/
```

**Validação:**
```bash
# Testar imports
python3 -c "from dou.config import PALAVRAS_CHAVE; print(PALAVRAS_CHAVE)"

# Testar scripts
python3 scripts/test_mre.py 2026-03-02

# Testar cron
./cron-dou.sh download
```

---

### 3.2 Adicionar Testes Unitários

**Novo Arquivo:** `tests/test_utils.py`

```python
"""
Testes unitários para dou_utils.
"""

import pytest
from dou.utils import limpar_texto_xml, filtrar_conteudo


class TestLimparTextoXml:
    """Testes para limpar_texto_xml."""

    def test_remove_html_tags(self):
        """Deve remover tags <p> e </p>."""
        texto = "<p>Art. 1°</p> O MINISTÉRIO"
        resultado = limpar_texto_xml(texto)
        assert "<p>" not in resultado
        assert "Art. 1° O MINISTÉRIO" == resultado

    def test_decode_html_entities(self):
        """Deve decodificar entidades HTML."""
        texto = "Seção&nbsp;1&ccedil;&atilde;o"
        resultado = limpar_texto_xml(texto)
        assert "Seção 1ção" == resultado

    def test_remove_xml_attributes(self):
        """Deve remover atributos XML."""
        texto = 'artType="Origem">Texto</artigo>'
        resultado = limpar_texto_xml(texto)
        assert 'artType=' not in resultado


class TestFiltrarConteudo:
    """Testes para filtrar_conteudo."""

    def test_busca_case_insensitive(self):
        """Deve encontrar palavras ignorando maiúsculas/minúsculas."""
        texto = "O Ministério das Relações Exteriores publicou."
        palavras = ["mre"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado) == 1
        assert resultado[0]['palavra_chave'] == 'MRE'

    def test_extrai_contexto(self):
        """Deve extrair contexto ao redor da palavra-chave."""
        texto = "0" * 200 + "MRE" + "0" * 500
        palavras = ["MRE"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado[0]['contexto']) <= 300
```

**Validação:**
```bash
pytest tests/ -v
pytest tests/ --cov=dou --cov-report=html
```

---

## Timeline de Execução

### FASE 1 (1-2 horas)
1. ✅ Remover import morto
2. ✅ Implementar logging
3. ✅ Adicionar type hints
4. ✅ Melhorar exceções

### FASE 2 (2-3 horas)
1. ✅ Criar dou_utils.py
2. ✅ Refatorar scripts para usar módulo
3. ✅ Mover sessão para local
4. ✅ Criar dou_config.py
5. ✅ Melhorar docstrings

### FASE 3 (3-4 horas, OPCIONAL)
1. ⏸️ Reorganizar diretórios
2. ⏸️ Adicionar testes unitários
3. ⏸️ Configurar pytest

---

## Critérios de Sucesso

**Fase 1:**
- [ ] Zero imports não utilizados
- [ ] Zero print() em código (apenas logger)
- [ ] mypy sem erros
- [ ] Exceções específicas em except

**Fase 2:**
- [ ] Duplicação de código < 10%
- [ ] Zero estado global (sessões, variáveis)
- [ ] Constantes em módulo de config
- [ ] Docstrings completas (args, returns, examples)

**Fase 3 (Opcional):**
- [ ] Estrutura de pacote Python
- [ ] Coverage de testes > 70%
- [ ] Zero warnings do pytest

---

## Rollback Plan

Cada fase pode ser revertida independentemente:

```bash
# Verificar mudanças
git diff

# Reverter fase específica
git revert HEAD

# Reverter tudo
git reset --hard origin/main
```

---

## Próximos Passos

1. ✅ Análise completa (REFACTOR_ANALYSIS.md)
2. ✅ Findings documentados (REFACTOR_FINDINGS.md)
3. ✅ Plano criado (REFACTOR_PLAN.md)
4. ⏸️ **AGUARDANDO APROVAÇÃO** para executar FASE 1
