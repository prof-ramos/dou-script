# dou-script

Scripts para download automático do **Diário Oficial da União (DOU)** via plataforma [INLABS](https://inlabs.in.gov.br).

## Estrutura

```
public/
├── bash/
│   ├── inlabs-auto-download-pdf.sh   # Download de PDFs (bash)
│   └── inlabs-auto-download-xml.sh   # Download de XMLs (bash)
└── python/
    ├── inlabs-auto-download-pdf.py   # Download de PDFs (Python)
    └── inlabs-auto-download-xml.py   # Download de XMLs (Python)
```

## Pré-requisitos

- Conta ativa no [INLABS](https://inlabs.in.gov.br)
- **Bash:** `curl`
- **Python:** `pip install requests` (+ `pip install requests[socks]` para proxy SOCKS5)

## Configuração

Edite as credenciais no início do script:

```python
login = "seu@email.com"
senha = "sua_senha"
```

## Uso

### Python

```bash
# Download de PDFs (do1, do2, do3 + edições extras)
python3 public/python/inlabs-auto-download-pdf.py

# Download de XMLs (DO1, DO2, DO3, DO1E, DO2E, DO3E)
python3 public/python/inlabs-auto-download-xml.py
```

### Bash

```bash
bash public/bash/inlabs-auto-download-pdf.sh
bash public/bash/inlabs-auto-download-xml.sh
```

### Com proxy SOCKS5

Se o IP do servidor for bloqueado pelo WAF do INLABS, use um proxy SOCKS5:

```bash
export SOCKS5_PROXY=socks5://127.0.0.1:1080
python3 public/python/inlabs-auto-download-pdf.py
```

## Automação diária (Linux)

```bash
# Adicionar ao crontab — roda às 09:00 de segunda a sexta
crontab -e
# 0 9 * * 1-5 python3 /caminho/inlabs-auto-download-pdf.py >> /var/log/dou.log 2>&1
```

## Nomenclatura dos arquivos gerados

| Tipo | Formato |
|------|---------|
| PDF principal | `YYYY_MM_DD_ASSINADO_do1.pdf` |
| PDF edição extra | `YYYY_MM_DD_ASSINADO_do1_extra_A.pdf` |
| XML (zip) | `YYYY-MM-DD-DO1.zip` |

## Seções disponíveis

| Código | Descrição |
|--------|-----------|
| `do1` / `DO1` | Diário Oficial — Seção 1 |
| `do2` / `DO2` | Diário Oficial — Seção 2 |
| `do3` / `DO3` | Diário Oficial — Seção 3 |
| `DO1E` | Seção 1 Extra (somente XML) |
| `DO2E` | Seção 2 Extra (somente XML) |
| `DO3E` | Seção 3 Extra (somente XML) |

## Licença

MIT
