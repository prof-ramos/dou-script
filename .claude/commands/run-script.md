# Run Python Script

Execute os scripts de download DOU com tratamento de erros e logging.

## Usage

```
/run-script
```

## Scripts Disponíveis

### Download PDF
```bash
python public/python/inlabs-auto-download-pdf.py
```

Baixa arquivos PDF do DOU (DO1, DO2, DO3).

### Download XML
```bash
python public/python/inlabs-auto-download-xml.py
```

Baixa arquivos XML do DOU (DO1, DO2, DO3, DO1E, DO2E, DO3E).

## Pré-requisitos

Ambiente Python:
```bash
# Python 3.8+ necessário
python --version

# Criar e ativar ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

Instalar dependências:
```bash
pip install requests
```

## Configuração

**Método Recomendado: Variáveis de Ambiente**
```bash
export INLABS_EMAIL="email@dominio.com"
export INLABS_PASSWORD="sua_senha"
python public/python/inlabs-auto-download-pdf.py
```

**Método Alternativo: Edição Direta (⚠️ Risco de Segurança)**
```python
# ⚠️ NUNCA commite credenciais no código; usar só localmente
login = "email@dominio.com"
senha = "sua_senha"
```


## Execução com Logs

```bash
# Verbose output
python -u public/python/inlabs-auto-download-pdf.py 2>&1 | tee download.log

# Background com nohup
nohup python public/python/inlabs-auto-download-pdf.py > download.log 2>&1 &

# Com data específica (requer modificação do script)
# TODO: Adicionar suporte a argumentos CLI
```

## Troubleshooting

### Erro de autenticação
- Verificar credenciais
- Confirmar conta ativa no IN Labs

### Arquivo não encontrado (404)
- DOU pode não ter sido publicado no dia
- Verificar se a seção existe para a data

### Erro de conexão
- Script já tenta novamente automaticamente
- Verificar conexão com internet

### Rate Limiting
- Se receber erros 429, aguarde 30 segundos antes de tentar novamente
- Considere executar em horários de menor tráfego

### Problemas de Permissão
- Verificar permissões de escrita no diretório atual
- Executar com `chmod +x` se necessário

### Espaço em Disco
- Arquivos ZIP podem ser grandes (50-100MB)
- Verificar espaço livre disponível com `df -h`

### Timeouts
- Se o script travar, verificar se ocorreram timeouts
- Pode ser necessário ajustar tempos de espera manualmente

## Saída dos Scripts

Arquivos são salvos no diretório atual:
- PDF: `YYYY-MM-DD-DO1.pdf`, `YYYY-MM-DD-DO2.pdf`, `YYYY-MM-DD-DO3.pdf` (5-20MB cada)
- XML: `YYYY-MM-DD-DO1.zip`, `YYYY-MM-DD-DO2.zip`, etc. (50-100MB cada)
- Logs: `download.log` (detalhes da execução, útil para debugging)
