# CLAUDE.md

Este arquivo fornece orientação para Claude Code trabalhar com este projeto.

## Visão Geral do Projeto

Este é um projeto de **scripts Python** para download automatizado do Diário Oficial da União (DOU) através do serviço IN Labs. Não é uma aplicação web, API ou framework.

## Estrutura do Projeto

```
public/
├── python/
│   ├── inlabs-auto-download-pdf.py    # Download de PDFs DOU
│   ├── inlabs-auto-download-xml.py    # Download de XMLs DOU
│   └── README.md
└── bash/
    ├── inlabs-auto-download-pdf.sh    # Wrapper shell para PDF
    ├── inlabs-auto-download-xml.sh    # Wrapper shell para XML
    └── README.md
```

## Scripts Disponíveis

### inlabs-auto-download-pdf.py
Download de PDFs das seções do DOU (DO1, DO2, DO3).

**Dependências:**
```bash
pip install requests
```

**Uso:**
```bash
python public/python/inlabs-auto-download-pdf.py
```

### inlabs-auto-download-xml.py
Download de XMLs das seções do DOU (DO1, DO2, DO3, DO1E, DO2E, DO3E).

**Dependências:**
```bash
pip install requests
```

**Uso:**
```bash
python public/python/inlabs-auto-download-xml.py
```

## Configuração

Ambos os scripts requerem credenciais do IN Labs:

**Configuração segura:**
1. Copie `.env.example` para `.env`: `cp .env.example .env`
2. Edite `.env` com suas credenciais reais
3. As credenciais serão carregadas automaticamente a partir das variáveis de ambiente

**Importante:** Nunca commit credenciais reais. Use o arquivo `.env` para configurações sensíveis.

## Tipos de DOU

- **DO1**: Diário Oficial 1 (Executivo)
- **DO2**: Diário Oficial 2 (Legislativo)
- **DO3**: Diário Oficial 3 (Judiciário)
- **DO1E, DO2E, DO3E**: Edições extras

## Comportamento dos Scripts

1. **Autenticação**: Faz login no IN Labs
2. **Data**: Usa a data atual automaticamente
3. **Download**: Baixa os arquivos para o diretório atual
4. **Nomenclatura**: `YYYY-MM-DD-TIPO.pdf` ou `YYYY-MM-DD-TIPO.zip`
5. **Retry**: Tenta novamente em caso de erro de conexão

## Execução via Bash

Scripts shell estão disponíveis para facilitar execução:

```bash
# Download PDF
bash public/bash/inlabs-auto-download-pdf.sh

# Download XML
bash public/bash/inlabs-auto-download-xml.sh
```

## Boas Práticas para este Projeto

### Desenvolvimento
- Manter credenciais fora do versionamento (usar .env ou variáveis de ambiente)
- Testar com dados limitados antes de executar downloads completos
- Verificar espaço em disco antes de downloads massivos

### Código
- Usar `logging` em vez de `print()` para melhor debug
- Adicionar type hints para melhor manutenibilidade
- Documentar funções com docstrings
- Tratar exceções adequadamente (ConnectionError, HTTPError)

### Segurança
- Nunca commitar credenciais reais (arquivo `.env` já está no `.gitignore`)
- Usar `.env` para todas configurações sensíveis
- Validar respostas HTTP antes de processar
- Manter `.env.example` com valores de exemplo apenas

## Possíveis Melhorias Futuras

- [ ] Adicionar argumentos CLI (data, seções, output dir)
- [ ] Implementar sistema de logging configurável
- [ ] Adicionar testes unitários
- [ ] Suporte a download de períodos (range de datas)
- [ ] Verificação de integridade dos arquivos (checksum)
- [ ] Parallel downloads para múltiplas seções
- [ ] Sistema de retry com backoff exponencial

## Resolução de Problemas

### Erro de Autenticação
- Verificar credenciais
- Confirmar que a conta IN Labs está ativa
- Verificar se o site IN Labs está operacional

### Arquivo Não Encontrado (404)
- O DOU pode não ter sido publicado no dia
- Verificar se a seção especificada existe para aquela data

### Erro de Conexão
- Verificar conexão com a internet
- O script já tenta novamente automaticamente
- Aumentar timeout se necessário

## Scripts Relacionados

Projetos similares que podem complementar este:
- Script de extração de conteúdo dos PDFs
- Script de parsing de XML para metadados
- Script de indexação/busca de DOUs baixados
- Script de organização de arquivos por data/seção
