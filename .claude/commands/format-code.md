# Format Python Code

Formata e aplica lint nos scripts Python do projeto.

## Usage

```
/format-code
```

## Black (Formatador)

```bash
# Formatar todos os arquivos Python
black public/python/

# Verificar sem alterar
black --check public/python/

# Formatar arquivo específico
black public/python/inlabs-auto-download-pdf.py

# Com linha de 100 caracteres
black --line-length 100 public/python/
```

## Flake8 (Linter)

```bash
# Verificar todos os arquivos
flake8 public/python/ --max-line-length=100

# Verificar arquivo específico
flake8 public/python/inlabs-auto-download-pdf.py --max-line-length=100

# Com configuração personalizada
flake8 public/python/ --max-line-length=100 --ignore=E203,W503
```

## isort (Organizar Imports)

```bash
# Organizar imports
isort public/python/

# Verificar sem alterar
isort --check-only public/python/

# Compatível com Black
isort --profile black public/python/
```

## MyPy (Type Hints)

```bash
# Verificar tipos
mypy public/python/

# Arquivo específico
mypy public/python/inlabs-auto-download-pdf.py

# Modo mais flexível
mypy public/python/ --no-strict-optional
```

## Configuração

### pyproject.toml

```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true

[tool.flake8]
max-line-length = 100
extend-ignore = ["E203", "W503"]
```

### .flake8

```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,.venv
ignore = E203,W503
```

## Executar Tudo

```bash
# Format completo
black public/python/ && isort public/python/

# Check completo
black --check public/python/ && isort --check-only public/python/ && flake8 public/python/ --max-line-length=100
```

## Pré-commit

Adicionar hook para formatar automaticamente:

```bash
# Install pre-commit
pip install pre-commit

# Criar .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        args: [--line-length=100]

  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort
        args: [--profile=black]

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]
EOF

# Install hooks
pre-commit install
```
