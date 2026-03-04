# 📰 DOU Script - Download Automatizado + Filtragem MRE

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Coverage](https://img.shields.io/badge/Coverage-94%25-brightgreen)](tests/)
[![Tests](https://img.shields.io/badge/Tests-37%20passing-success)](tests/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> Sistema automatizado para download e filtragem inteligente do Diário Oficial da União (DOU) com foco em publicações do **Ministério das Relações Exteriores (MRE)**.

Sistema Python profissional com **94% de cobertura de testes**, arquitetura modular e agendamento automático via cron.

---

## ✨ Funcionalidades

### 🎯 Principais Recursos

| Funcionalidade | Descrição |
|---------------|-----------|
| **Download Automatizado** | Baixa XMLs do DOU via [IN Labs](https://inlabs.in.gov.br) |
| **Filtragem MRE** | Busca inteligente por palavras-chave do Ministério das Relações Exteriores |
| **Extração de Contexto** | Extrai ±200 caracteres antes e +500 depois da palavra-chave |
| **Agendamento Cron** | Execução automática em horários estratégicos (10h, 12h, 23h) |
| **Detecção de Duplicatas** | Evita downloads redundantes do mesmo DOU |
| **Multi-Seção** | Suporta DO1, DO2, DO3 e edições extras (DO1E, DO2E, DO3E) |
| **Logging Estruturado** | Logs com timestamps para facilitar debugging |
| **Testes Automatizados** | 37 testes pytest com 94% de coverage |

### 🔍 Palavras-Chave Monitoradas

O sistema busca automaticamente por:
- Ministério das Relações Exteriores
- Ministério Relações Exteriores
- Oficial de Chancelaria
- Chancelaria
- Concursos Públicos
- MRE
- Embaixada
- Consulado
- Diplomacia

---

## 🚀 Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/prof-ramos/dou-script.git
cd dou-script

# 2. Configure suas credenciais
cp .env.example .env
# Edite .env com suas credenciais IN Labs

# 3. Crie ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 4. Instale dependências
pip install -r requirements.txt

# 5. (Opcional) Instale dependências de desenvolvimento
pip install -r requirements-dev.txt
```

---

## 📖 Como Funciona

### Fluxo de Processamento

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  1. LOGIN   │───▶│  2. DOWNLOAD │───▶│ 3. EXTRAI   │───▶│ 4. FILTRA   │
│  IN Labs    │    │  XMLs ZIP   │    │  Texto XML  │    │  Conteúdo   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                           │
                                                           ▼
                                                 ┌─────────────────────┐
                                                 │ 5. SALVA RESULTADOS  │
                                                 │ output/*-MRE.txt     │
                                                 └─────────────────────┘
```

### Detalhamento do Pipeline

1. **Autenticação**: Login via POST com cookie session
2. **Download**: Baixa ZIPs de todas as seções (DO1-DO3 + extras)
3. **Extração**: Lê XML do ZIP na memória (BytesIO)
4. **Limpeza**: Remove tags HTML/XML e decodifica entidades
5. **Filtragem**: Busca palavras-chave MRE com contexto
6. **Salvamento**: Gera arquivo `*MRE.txt` com trechos encontrados

---

## 💻 Uso

### Download Manual

```bash
# Download de hoje com filtragem MRE
python3 scripts/download_dou.py

# Download de data específica
python3 scripts/test_mre.py 2026-03-02

# Download de XMLs brutos (sem filtragem)
python3 scripts/auto_download_xml.py
```

### Agendamento Automático

O sistema já vem configurado com `cron-dou.sh` para execução automática:

```bash
# 10h (Seg-Sex)   - Download + Filtragem MRE
# 12h (Seg-Sex)   - Verifica duplicatas e remove
# 23h (Seg-Sex)   - Verifica duplicatas final
```

**Configurar crontab:**

```bash
# Adicionar ao crontab
crontab -e

# Adicionar linha:
0 10 * * 1-5 /path/to/dou-script/cron-dou.sh download
0 12 * * 1-5 /path/to/dou-script/cron-dou.sh check-duplicate
0 23 * * 1-5 /path/to/dou-script/cron-dou.sh check-duplicate
```

---

## 📂 Estrutura do Projeto

```
dou-script/
├── dou/                    # 📦 Pacote Python principal
│   ├── __init__.py         # exports do pacote
│   ├── config.py           # configurações (URLs, keywords)
│   └── utils.py            # funções (XML, limpeza, filtragem)
│
├── scripts/                # 🚀 Scripts executáveis
│   ├── download_dou.py     # principal (download + filtragem)
│   ├── test_mre.py         # teste com data específica
│   └── auto_download_xml.py # download XMLs brutos
│
├── tests/                  # 🧪 Testes unitários (94% coverage)
│   ├── test_config.py      # testes de configuração
│   ├── test_utils.py       # testes de utilitários
│   └── conftest.py         # fixtures pytest
│
├── docs/                   # 📚 Documentação detalhada
│   ├── ARQUITETURA.md      # arquitetura técnica
│   ├── DIAGRAMA.md         # diagramas do sistema
│   └── VISAO_GERAL.md      # visão executiva
│
├── output/                 # 📄 Resultados filtrados
├── cron-dou.sh             # ⏰ Agendamento cron
├── ARCHITECTURE.md         # 🏗️ Visão geral da arquitetura
├── requirements.txt        # Dependências produção
├── requirements-dev.txt    # Dependências dev
└── pyproject.toml         # Config Python (Black, pytest, etc.)
```

---

## 🧪 Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Rodar com coverage
pytest tests/ --cov=dou --cov-report=term-missing

# Rodar teste específico
pytest tests/test_utils.py::TestLimparTextoXML -v

# Gerar relatório HTML
pytest tests/ --cov=dou --cov-report=html
# Abra htmlcov/index.html no navegador
```

**Coverage:** 94% (37 testes pytest)

---

## 🛠️ Desenvolvimento

### Dependências

```bash
# Produção
pip install -r requirements.txt

# Desenvolvimento
pip install -r requirements-dev.txt
```

### Ferramentas

```bash
# Formatar código (Black)
black dou/ scripts/ tests/ --line-length 100

# Verificar formatação
black --check dou/ scripts/ tests/

# Lint (Flake8)
flake8 dou/ scripts/ tests/ --max-line-length=100

# Type check (mypy)
mypy dou/ --ignore-missing-imports
```

---

## 📊 Arquivos de Saída

### Formato dos Arquivos

Os arquivos filtrados seguem o padrão: `YYYY-MM-DD-SEÇÃO-MRE.txt`

**Exemplo de conteúdo:**

```text
=== TRECHOS MRE ENCONTRADOS - 2026-03-02 - DO2 ===

[1] PALAVRA-CHAVE: MINISTÉRIO DAS RELAÇÕES EXTERIORES
CONTEXTO:
Art. 1° Conceder aposentadoria com proventos integrais a [NOME],
matrícula SIAPE nº [SIAPE], ocupante do cargo de assistente de
chancelaria do Ministério das Relações Exteriores...
--------------------------------------------------------------------------------

[2] PALAVRA-CHAVE: CHANCELARIA
CONTEXTO:
O MINISTÉRIO DAS RELAÇÕES EXTERIORES publica hoje...
--------------------------------------------------------------------------------
```

---

## 🔧 Solução de Problemas

### Erro: "Falha ao obter cookie"

**Causa:** Credenciais inválidas ou conta inativa

**Solução:**
```bash
# Verifique suas credenciais no .env
cat .env | grep INLABS

# Teste login manual
curl -X POST https://inlabs.in.gov.br/logar.php \
  -d "email=SEU_EMAIL&password=SUA_SENHA"
```

### Erro: "Arquivo não encontrado" (HTTP 404)

**Causa:** DOU não publicado no dia

**Solução:**
- Finais de semana e feriados podem não ter DOU
- Edições extras (DO1E, DO2E, DO3E) nem sempre existem
- Verifique no [site oficial](https://inlabs.in.gov.br)

### Erro: "WAF bloqueando IP de datacenter"

**Causa:** WAF do IN Labs bloqueia IPs de VPS/datacenter

**Solução:** Consulte [TAILSCALE_SETUP.md](TAILSCALE_SETUP.md) para configurar VPN

### Erro: "ModuleNotFoundError: No module named 'dou'"

**Causa:** Python não encontra o pacote

**Solução:**
```bash
# Verifique que está na raiz do projeto
pwd

# Instale o pacote em modo development
pip install -e .
```

---

## 🔐 Segurança

- ✅ Credenciais armazenadas em `.env` (não versionado)
- ✅ `.env.example` fornecido com valores fake
- ✅ Cookies de sessão em memória (não persistidos)
- ✅ HTTPS obrigatório para IN Labs API
- ✅ Timeout de 30s para evitar hangs

**⚠️ IMPORTANTE:**
- NUNCA faita commit do arquivo `.env`
- Não use `export` para definir credenciais (fica no histórico do shell)
- Use sempre o arquivo `.env` para segredos

---

## 📚 Documentação Adicional

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Visão geral da arquitetura
- **[docs/ARQUITETURA.md](docs/ARQUITETURA.md)** - Documentação técnica detalhada
- **[docs/DIAGRAMA.md](docs/DIAGRAMA.md)** - Diagramas do sistema
- **[docs/VISAO_GERAL.md](docs/VISAO_GERAL.md)** - Visão executiva
- **[TAILSCALE_SETUP.md](TAILSCALE_SETUP.md)** - Configuração de VPN para WAF

---

## 🚀 Deploy

### Requisitos de Produção

- **Python:** 3.8+
- **SO:** Linux (testado no Ubuntu 20.04+)
- **Memória:** Mínimo 512MB
- **Disk:** 1GB+ (para ZIPs e outputs)

### Configuração Cron em Produção

```bash
# No servidor VPS
cd /path/to/dou-script

# Configurar .env
cp .env.example .env
vim .env  # Adicione INLABS_EMAIL e INLABS_PASSWORD

# Testar manual
python3 scripts/test_mre.py $(date +%Y-%m-%d)

# Configurar crontab
crontab -e

# Adicionar:
0 10 * * 1-5 cd /path/to/dou-script && ./cron-dou.sh download
0 12 * * 1-5 cd /path/to/dou-script && ./cron-dou.sh check-duplicate
0 23 * * 1-5 cd /path/to/dou-script && ./cron-dou.sh check-duplicate
```

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:

1. **Reportar bugs** - Abra uma issue com detalhes
2. **Sugerir funcionalidades** - Abra uma issue com tag `enhancement`
3. **Enviar pull requests** - Fork, branch, commit, PR

### Padrões de Código

- Seguir [PEP 8](https://peps.python.org/pep-0008/)
- Type hints em todas as funções
- Docstrings Google Style
- Testes para novas funcionalidades

---

## 📄 Licença

Este projeto é fornecido "como está", sem garantias.

MIT License - use livremente para fins pessoais ou comerciais.

---

## 📞 Suporte

### Links Úteis

- **[IN Labs](https://inlabs.in.gov.br)** - Serviço oficial de downloads
- **[Imprensa Nacional](http://www.in.gov.br/)** - Portal oficial do DOU
- **[DOU Search](http://www.in.gov.br/leiturajornal)** - Busca oficial no DOU

### Issues

Para problemas específicos do script:
1. Verifique a seção [Solução de Problemas](#-solução-de-problemas)
2. Consulte [docs/](docs/)
3. Abra uma issue no GitHub

---

## 🎯 Roadmap

- [ ] Adicionar suporte a download em PDF
- [ ] Implementar modo verboso (--verbose)
- [ ] Adicionar métricas de execução
- [ ] Suporte a notificações (email, Telegram)
- [ ] Interface web (FastAPI + React)
- [ ] Docker para deploy simplificado

---

<div align="center">

**Desenvolvido com ❤️ para automação inteligente do DOU**

[⬆ Voltar ao topo](#-dou-script---download-automatizado--filtragem-mre)

</div>
