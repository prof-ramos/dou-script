# 📰 DOU Script - Download Automatizado do Diário Oficial da União

Scripts Python para download automatizado do Diário Oficial da União (DOU) através do serviço [IN Labs](https://inlabs.in.gov.br).

## 🎯 Funcionalidades

- **Download automático** de PDFs e XMLs das seções do DOU
- **Agendamento automático** via cron (10h, 12h, 23h)
- **Detecção de duplicatas** - Evita baixar o mesmo DOU múltiplas vezes
- **Suporte a múltiplas seções** - DO1 (Executivo), DO2 (Legislativo), DO3 (Judiciário)

## 📋 Pré-requisitos

- Python 3.8+
- Conta ativa no [IN Labs](https://inlabs.in.gov.br)
- Biblioteca `requests`

## 🚀 Instalação Rápida

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
# Substitua <url-do-repositorio> pela URL do seu repositório (ex: https://github.com/usuario/dou-script.git)
cd dou-script

# 2. Configure suas credenciais
cp .env.example .env
# Edite .env com suas credenciais IN Labs

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure o agendamento automático (opcional)
# O arquivo cron-dou.sh está no diretório do projeto
crontab cron-dou.sh
```

## 📖 Uso

### Download Manual

```bash
# Baixar DOU de hoje (XML com filtragem MRE)
python3 scripts/download_dou.py

# Baixar DOU de data específica
python3 scripts/test_mre.py 2026-03-02

# Baixar XMLs brutos (sem filtragem)
python3 scripts/auto_download_xml.py
```

**Nota:** As credenciais devem ser configuradas no arquivo `.env` (veja seção de Instalação Rápida).

**Importante:** Evite usar `export` para definir credenciais diretamente no terminal, pois isso pode deixar suas credenciais no histórico do shell. Use sempre o arquivo `.env`. Se você usou `export` anteriormente, limpe o histórico do shell com `history -c`.

### Agendamento Automático

O script está configurado para rodar automaticamente via cron:

- **10h** - Download DOU da manhã
- **12h** - Verifica se é o mesmo DOU (apaga se for duplicata)
- **23h** - Verifica duplicata final (mantém última versão)

**Dias de execução:** Segunda a Sexta

```bash
# Verificar cron instalado
crontab -l

# Editar cron
crontab -e
```

## 📂 Estrutura do Projeto

```
dou-script/
├── dou/                    # Pacote Python principal
│   ├── __init__.py         # exports do pacote
│   ├── config.py           # configurações (URLs, palavras-chave)
│   └── utils.py            # funções compartilhadas (XML, filtragem)
├── scripts/                # Scripts executáveis
│   ├── download_dou.py     # script principal de download
│   ├── test_mre.py         # teste com data específica
│   └── auto_download_xml.py # download de XMLs brutos
├── tests/                  # Testes unitários
│   ├── test_config.py      # testes de configuração
│   ├── test_utils.py       # testes de utilitários
│   └── conftest.py         # fixtures pytest
├── output/                 # Resultados filtrados
├── cron-dou.sh             # Wrapper para agendamento cron
├── requirements.txt        # Dependências
├── requirements-dev.txt    # Dependências de desenvolvimento
└── README.md
```

## 🧪 Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Rodar com coverage
pytest tests/ --cov=dou --cov-report=term-missing

# Rodar teste específico
pytest tests/test_utils.py::TestLimparTextoXML -v
```

**Coverage atual:** 94% (37 testes)

## 🔐 Segurança

- **NUNCA** faça commit do arquivo `.env` (já está no `.gitignore`)
- Mantenha suas credenciais IN Labs seguras
- O script usa variáveis de ambiente para evitar credenciais hardcoded

## 🛠️ Desenvolvimento

### Dependências

```bash
# Produção
pip install -r requirements.txt

# Desenvolvimento
pip install -r requirements-dev.txt
```

### Formatação de Código

```bash
# Formatar com Black
black dou/ scripts/ tests/ --line-length 100

# Verificar formatação
black --check dou/ scripts/ tests/

# Lint com Flake8
flake8 dou/ scripts/ tests/ --max-line-length=100

# Type check com mypy
mypy dou/ --ignore-missing-imports
```

## 📝 Arquivos de Saída

Os arquivos baixados seguem o padrão: `YYYY-MM-DD-SEÇÃO.ext`

**Exemplos:**
- `2024-01-15-do1.pdf` - DO1 Executivo em PDF
- `2024-01-15-do2.pdf` - DO2 Legislativo em PDF
- `2024-01-15-do3.pdf` - DO3 Judiciário em PDF
- `2024-01-15-DO1.zip` - DO1 Executivo em XML
- `2024-01-15-DO2.zip` - DO2 Legislativo em XML
- `2024-01-15-DO3.zip` - DO3 Judiciário em XML

## 🔧 Solução de Problemas

### "Falha ao obter cookie"
- Verifique suas credenciais no arquivo `.env`
- Confirme que sua conta IN Labs está ativa
- Verifique se o site IN Labs está acessível

### "Arquivo não encontrado" (404)
- O DOU pode não ter sido publicado no dia
- Finais de semana e feriados podem não ter DOU
- Edições extras (DO1E, DO2E, DO3E) nem sempre existem

### Erro de conexão
- Verifique sua conexão com a internet
- O script tenta novamente automaticamente em caso de falha

## 📄 Licença

Este projeto é fornecido "como está", sem garantias.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Enviar pull requests

## 📞 Suporte

Para questões sobre o DOU ou o serviço IN Labs, consulte:
- [IN Labs](https://inlabs.in.gov.br) - Serviço oficial de downloads
- [Imprensa Nacional](http://www.in.gov.br/) - Portal oficial do DOU

---

**Desenvolvido para automatizar downloads do Diário Oficial da União**
