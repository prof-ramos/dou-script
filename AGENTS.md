<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-03-04 | Updated: 2026-03-04 -->

# dou-script

## Purpose
Automação de download e processamento do Diário Oficial da União (DOU) para a ASOF. Monitora publicações relevantes, faz download de XMLs e PDFs, e entrega via WhatsApp/relatório.

## Key Files

| Arquivo | Descrição |
|---------|-----------|
| `cron-dou.sh` | Script principal de execução cron |
| `auto_download_xml.py` | Download automático de XMLs do DOU |
| `download_dou.py` | Download de edições específicas |
| `test_mre.py` | Testes do módulo MRE |
| `pyproject.toml` | Dependências Python |
| `ARCHITECTURE.md` | Arquitetura do sistema |
| `VISAO_GERAL.md` | Visão geral do projeto |
| `TAILSCALE_SETUP.md` | Configuração de rede via Tailscale |

## Subdirectories

| Diretório | Propósito |
|-----------|-----------|
| `dou/` | Pacote Python principal (config, utils) |
| `tests/` | Testes (conftest, config, utils) |

## For AI Agents

### Working In This Directory
- Setup: `pip install -e .` ou verificar `pyproject.toml`
- Rodar download manual: `python download_dou.py`
- Cron configurado via `cron-dou.sh` — verificar crontab do sistema
- Rede: usa Tailscale para acesso a recursos internos (ver `TAILSCALE_SETUP.md`)

### Testing Requirements
```bash
pytest tests/test_config.py
pytest tests/test_utils.py
```

### Entrega de Resultados
- Arquivos gerados ficam em `../dou/YYYY-MM-DD/`
- Envio WhatsApp via `openclaw message send` para o grupo da ASOF

## Dependencies

### Internal
- Integra com grupo WhatsApp `120363401210534264@g.us` (agente Abduh)

### External
- `inlabs` API — download oficial do DOU
- Tailscale — rede privada para recursos internos
