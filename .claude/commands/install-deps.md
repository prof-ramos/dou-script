# Install Dependencies

Gerencia dependências Python do projeto.

## Usage

```
/install-deps
```

## Dependências do Projeto

### Produção
```bash
pip install requests
```

### Desenvolvimento (opcional)
```bash
# Formatação de código
pip install black

# Linting
pip install flake8

# Type hints
pip install mypy

# Testes
pip install pytest pytest-cov
```

## requirements.txt

Criar arquivo de dependências:

```text
requests>=2.31.0
```

### requirements-dev.txt (opcional)

```text
black>=24.0.0
flake8>=7.0.0
mypy>=1.8.0
pytest>=8.0.0
pytest-cov>=4.1.0
```

## Ambiente Virtual

### Criar ambiente virtual

```bash
# Criar venv
python -m venv .venv

# Ativar (Linux/Mac)
source .venv/bin/activate

# Ativar (Windows)
.venv\Scripts\activate
```

### Instalar dependências

```bash
# Produção
pip install -r requirements.txt

# Com dependências de dev
pip install -r requirements.txt -r requirements-dev.txt
```

### Salvar dependências

⚠️ **Aviso:** `pip freeze > requirements.txt` sobrescreve o arquivo organizado.
```bash
# Para lockfile separado (recomendado):
pip freeze > requirements-lock.txt

# Para atualizar requirements.txt intencionalmente:
pip freeze > requirements.txt
```

## Verificar Instalação

```bash
# Listar pacotes instalados
pip list

# Verificar versão específica
python -c "import requests; print(requests.__version__)"
```

## Desinstalar

```bash
# Desativar ambiente virtual
deactivate

# Remover ambiente virtual
rm -rf .venv
```

## Atualizar Dependências

```bash
# Atualizar pip
python -m pip install --upgrade pip

# Atualizar pacote específico
pip install --upgrade requests

# Verificar pacotes desatualizados
pip list --outdated
```
