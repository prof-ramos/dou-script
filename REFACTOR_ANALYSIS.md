# 📊 Repository Map - DOU Script

## Estrutura Atual
```
dou-script/
├── public/
│   ├── python/
│   │   ├── inlabs-auto-download-pdf.py    (60 linhas)
│   │   ├── inlabs-auto-download-xml.py    (60 linhas)
│   │   └── inlabs-filter-mre.py           (218 linhas) ⭐ PRINCIPAL
│   └── bash/
│       ├── inlabs-auto-download-pdf.sh
│       └── inlabs-auto-download-xml.sh
├── test-mre.py                                (240 linhas) ⭐ PRINCIPAL
├── cron-dou.sh                               (60 linhas)
├── docs/
│   ├── ARQUITETURA.md
│   ├── DIAGRAMA.md
│   └── VISAO_GERAL.md
├── output/                                    # Resultados MRE
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── .env.example
```

## Convenções Detectadas

**Ferramentas:**
- Python: 3.14.3
- Linting: ruff (disponível)
- Type checking: mypy (configurado mas não usado)
- Formatação: Black (line-length=100)

**Estilo de Código:**
- Scripts standalone (sem estrutura de package)
- Uso de print() para logging (módulo logging disponível mas não usado)
- CamelCase para funções (PEP 8)
- Constantes em UPPER_CASE

## Stack Primário

**PRIMARY_STACK:** Python 3.8+ (scripts standalone, não framework web)

**DOMAIN_AREAS:**
- `download/` - Autenticação e download de DOUs
- `filtro/` - Extração e filtragem de conteúdo MRE
- `agendamento/` - Cron e shell scripts

**CRITICAL_MODULES:**
- `public/python/inlabs-filter-mre.py` (218 linhas) - Script principal de produção
- `test-mre.py` (240 linhas) - Script de teste com data específica
- `cron-dou.sh` (60 linhas) - Wrapper de agendamento

## Configurações Detectadas

**pyproject.toml:**
- ✅ Black: line-length=100, target-version=[py38, py39, py310, py311]
- ✅ isort: profile="black", line-length=100
- ✅ flake8: max-line-length=100
- ✅ mypy: python_version=3.8 (mas type checking não é usado)

**Obs:** Projeto não usa ruff (apenas Black/flake8/isort separados)
