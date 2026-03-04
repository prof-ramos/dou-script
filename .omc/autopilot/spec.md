# Especificação: dou-script Melhorias

## Resumo Executivo

Melhorar os scripts de download DOU com: CLI argparse, logging estruturado, testes automatizados e cleanup MCP.

## 1. CLI Arguments (argparse)

### Argumentos Necessários
- `--data` (DATE): Data específica no formato YYYY-MM-DD (default: hoje)
- `--secoes` (LIST): Seções DOU: DO1, DO2, DO3, DO1E, DO2E, DO3E
- `--formato` (CHOICE): pdf ou xml (default: pdf)
- `--output` (PATH): Diretório de saída (default: ./)
- `--verbose` (FLAG): Aumenta verbosidade (-v INFO, -vv DEBUG)
- `--email` (STR): Email INlabs (sobrescreve env var)
- `--password` (STR): Senha INlabs (sobrescreve env var)

### Validações
- Rejeitar datas futuras
- Rejeitar datas antes de 2000-01-01
- Validar formato ISO 8601
- Validar códigos de seção (whitelist)

### Credenciais
- Preferência: Environment variables (`INLABS_EMAIL`, `INLABS_PASSWORD`)
- Fallback: Argumentos CLI
- Suporte: `.env` file via python-dotenv

## 2. Logging Module

### Configuração
- Module: `logging` (stdlib)
- Formato: `%(asctime)s | %(levelname)-8s | %(name)s | %(message)s`
- Timestamp: ISO 8601
- Níveis: INFO (default), DEBUG (--verbose), ERROR
- Saída: stdout + arquivo (opcional)

### Arquivo de Log
- Local: `./logs/dou-script.log`
- Rotação: RotatingFileHandler (10MB, 5 backups)
- Encoding: UTF-8
- Criar diretório se não existir

### Mensagens
- Manter português para consistência
- Redatar credenciais em logs
- Todas as mensagens com timestamp

## 3. Test Framework (pytest)

### Estrutura
```
tests/
├── conftest.py              # Fixtures pytest
├── test_cli.py              # Testes CLI
├── test_auth.py             # Testes autenticação
├── test_downloader.py       # Testes download
└── fixtures/
    └── mock_responses.py    # HTTP responses mockadas
```

### Fixtures
- `mock_session`: Session requests mockada
- `auth_env_vars`: Variáveis de ambiente
- `temp_output_dir`: Diretório temporário
- `mock_200_response`: Response sucesso
- `mock_404_response`: Response not found

### Coverage Target
- Mínimo: 80%
- Report: terminal + HTML
- Comando: `pytest --cov=dou_script --cov-report=term-missing --cov-report=html`

### HTTP Mocking
- Usar: `responses` library
- TODAS as requisições mockadas
- Zero chamadas reais em testes

## 4. MCP.json Cleanup

### Servidores a Remover
- `docker` (não usado)
- `jupyter` (não usado)
- `postgresql` (não usado)
- `opik` (não usado)
- `memory-bank` (não usado)
- `sequential-thinking` (opcional)
- `brave-search` (manter para docs)
- `google-maps` (não usado)
- `deep-graph` (não usado)

### Servidores a Manter
- `filesystem` - Para operações com arquivos
- `context7` - Para documentação (adicionar se necessário)

### Config Final
```json
{
  "mcpServers": {
    "filesystem": {...},
    "context7": {...}
  }
}
```

## Dependências Adicionais

### requirements.txt (Produção)
```
requests>=2.31.0
python-dotenv>=1.0.0
```

### requirements-dev.txt (Desenvolvimento)
```
pytest>=8.0.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
responses>=0.25.0
black>=24.0.0
flake8>=7.0.0
```

## Decisões Técnicas

| Item | Decisão | Justificativa |
|------|---------|---------------|
| CLI Library | argparse | Stdlib, sem dependências extras |
| Logging | logging stdlib | Suficiente, padronizado |
| Test Framework | pytest | Padrão Python, ecossistema rico |
| HTTP Mocking | responses | Determinístico, simples |
| Type Hints | Sim (opcional) | Melhora IDE, mypy |
| Code Formatting | black (100 chars) | Padrão projeto |

## Estrutura de Código Proposta

```
dou-script/
├── src/
│   └── dou_script/
│       ├── __init__.py
│       ├── cli.py                 # argparse entry point
│       ├── core/
│       │   ├── auth.py            # SessionManager
│       │   ├── downloader.py      # DownloadManager
│       │   └── exceptions.py      # Exceções customizadas
│       └── utils/
│           └── logging.py         # logging setup
├── tests/
│   ├── conftest.py
│   ├── test_cli.py
│   ├── test_auth.py
│   └── test_downloader.py
├── public/python/                 # scripts legados (deprecation warning)
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── .mcp.json                      # cleaned up
```

## Critérios de Aceite

### CLI
- [ ] `--help` mostra usage completo
- [ ] `--data 2024-01-15` funciona
- [ ] `--secoes DO1 DO2` funciona
- [ ] Data futura rejeitada
- [ ] Credenciais de env vars funcionam

### Logging
- [ ] Zero `print()` em código de produção
- [ ] Logs em arquivo com rotação
- [ ] Timestamps ISO 8601
- [ ] Credenciais redatadas

### Testes
- [ ] `pytest` executa sem erros
- [ ] Coverage >= 80%
- [ ] Todas as requisições mockadas
- [ ] Tests < 5 segundos

### MCP
- [ ] Apenas 2 servidores
- [ ] JSON válido
- [ ] Documentação atualizada
