# Scripts de Teste Python

Testa os scripts de download DOU com validação de funcionalidade.

## Usage

```
/test-script
```

## Testes Disponíveis

### Teste de Importação
```bash
python -c "import requests; print('✓ requests OK')"
```

### Teste de Sintaxe
```bash
python -m py_compile public/python/inlabs-auto-download-pdf.py
python -m py_compile public/python/inlabs-auto-download-xml.py
```

### Teste de Credenciais
```python
import requests
import os

# NÃO use valores padrão para credenciais
login = os.getenv("INLABS_EMAIL")
senha = os.getenv("INLABS_PASSWORD")

# ⚠️ AVISO: NUNCA commite credenciais reais no código
if not login or not senha:
    raise ValueError("INLABS_EMAIL e INLABS_PASSWORD devem ser definidos")

url = "https://inlabs.in.gov.br/logar.php"
payload = {"email": login, "password": senha}
```

### Teste de Conexão IN Labs
```python
import requests

response = requests.get("https://inlabs.in.gov.br")
print(f"✓ Site IN Labs acessível: {response.status_code}")
```


### Dry Run (sem download real)
```python
# Definir variável para controle
DRY_RUN = False

# No arquivo do script, comente ou condicione:
if not DRY_RUN:
    response_arquivo = s.request("GET", url_arquivo, headers=cabecalho_arquivo)
```
Ou adicione uma variável de ambiente:
```bash
DRY_RUN=1 python script.py  # Modo teste (pula downloads)
```

## Teste de Integração Simples

```bash
# Testar script com verbose
python -v public/python/inlabs-auto-download-pdf.py

# Verificar arquivos baixados
ls -lh *.pdf *.zip 2>/dev/null | head -10
```

## Validação de Arquivos

```bash
# Verificar integridade dos PDFs
file *.pdf | grep -v "PDF document"

# Verificar tamanho dos arquivos (vazios = problema)
find . -name "*.pdf" -size 0

# Verificar arquivos recentes
find . -name "*.pdf" -mtime -1 -ls
```

## Cobertura de Testes

Atualmente o projeto não possui testes automatizados. Recomendado adicionar:

```python
# tests/test_dou_download.py
import pytest
from unittest.mock import patch, Mock
import requests

def test_authentication_success():
    """Testa autenticação bem-sucedida."""
    # TODO: Implementar teste
    pass

def test_url_construction():
    """Testa construção da URL de download."""
    # TODO: Implementar teste
    pass

def test_file_not_found_handling():
    """Testa tratamento de 404."""
    # TODO: Implementar teste
    pass
```

## Próximos Passos

- [ ] Adicionar pytest como dependência de desenvolvimento
- [ ] Criar testes unitários para cada função
- [ ] Criar testes de integração com mock do IN Labs
- [ ] Adicionar CI/CD para testes automáticos
