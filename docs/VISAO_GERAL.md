# Visão Geral do Sistema DOU Download + Filtragem MRE

## O Que É

Sistema automatizado que **baixa o Diário Oficial da União (DOU)** diariamente e **filtra conteúdo relevante** para o Ministério das Relações Exteriores (MRE).

## Para Quem

- Diplomatas e Oficiais de Chancelaria
- Servidores do MRE
- Pesquisadores de relações internacionais
- Concursandos do MRE (IRAD/CEBRAP)

## Como Funciona (Resumo)

```
┌─────────────────────────────────────────────────────────────┐
│                     TODOS OS DIAS ÚTEIS                     │
│                                                              │
│  10h ────────────────────────────────────────────────► Baixa
│           ↓
│     Download XMLs DOU (DO1, DO2, DO3 + extras)
│           ↓
│     Filtra por palavras-chave MRE
│           ↓
│     Salva em output/YYYY-MM-DD-SEÇÃO-MRE.txt
│                                                              │
│  12h ────────────────────────────────────────────────► Verifica
│           ↓
│     Se DOU já existe, remove (evita duplicatas)
│                                                              │
│  23h ────────────────────────────────────────────────► Limpeza
│           ↓
│     Remove duplicatas finais do dia
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## O Que É Monitorado

O sistema busca menções a:
- Ministério das Relações Exteriores
- Oficial de Chancelaria / Chancelaria
- Concursos Públicos (MRE)
- Embaixadas e Consulados
- Diplomacia
- MRE (sigla)

## O Que É Produzido

Arquivos de texto com trechos filtrados:

```
output/
├── 2026-03-02-DO1-MRE.txt  ← Executivo
├── 2026-03-02-DO2-MRE.txt  ← Legislativo ✅ (encontrou 2 trechos)
├── 2026-03-02-DO3-MRE.txt  ← Judiciário
└── 2026-03-03-DO1-MRE.txt  ← Próximo dia
```

**Formato do arquivo**:

```text
=== TRECHOS MRE ENCONTRADOS - 2026-03-02 - DO2 ===

[1] PALAVRA-CHAVE: CHANCELARIA
CONTEXTO:
Art. 1° - Conceder aposentadoria voluntária com proventos integrais
a [NOME REDATIDO], matrícula SIAPE nº [SIAPE REDATIDO],
ocupante do cargo de assistente de chancelaria...
--------------------------------------------------------------------------------
```

## Instalação Rápida

```bash
# 1. Clone o repositório
git clone <repo-url>
cd dou-script

# 2. Configure suas credenciais IN Labs
cp .env.example .env
# Edite .env com suas credenciais

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure o agendamento automático
crontab cron-dou.sh
```

## Uso Manual

```bash
# Baixar e filtrar DOU de hoje
export INLABS_EMAIL="seu_email@example.com"
export INLABS_PASSWORD="sua_senha"
python3 public/python/inlabs-filter-mre.py

# Baixar e filtrar data específica
python3 test-mre.py DATA-ESPECIFICA (ex: 2026-03-02)
```

## Estrutura de Arquivos

```
dou-script/
├── output/                  # ← RESULTADOS FILTRADOS (MRE)
│   └── *-MRE.txt
├── public/python/           # Scripts de processamento
│   └── inlabs-filter-mre.py
├── cron-dou.sh              # Script de agendamento
├── .env                     # Credenciais (NÃO versionar)
└── docs/                    # Documentação
    ├── ARQUITETURA.md       # Documentação técnica detalhada
    └── VISAO_GERAL.md       # Este arquivo
```

## Status Atual

- ✅ **Funcionando**: Download, extração, filtragem, limpeza de texto
- ✅ **Testado**: Dados históricos 2026-03-02, 2026-03-03
- ✅ **Agendado**: Cron configurado (10h, 12h, 23h)
- ✅ **Documentado**: Arquitetura completa em `docs/ARQUITETURA.md`

## Próximos Passos

1. ✅ Implementar limpeza de texto (remover HTML/XML tags)
2. ✅ Salvar em diretório `output/` separado
3. ✅ Documentar arquitetura completa
4. ⏳ Adicionar testes automatizados
5. ⏳ Implementar monitoramento e alertas

## Suporte

Para questões técnicas:
- Ver `docs/ARQUITETURA.md` para documentação detalhada
- Ver `README.md` para instruções de instalação
- Issues: Criar issue no repositório para suporte técnico

---

**Versão**: 1.0
**Última atualização**: 2026-03-04
**Status**: Production ✅
