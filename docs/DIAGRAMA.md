# Diagramas do Sistema DOU Download + Filtragem MRE

## Diagrama de Alto Nível

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SISTEMA DOU + MRE                                │
│                                                                             │
│  ┌───────────────┐      ┌─────────────────┐      ┌─────────────────────┐  │
│  │   CRON 10h    │      │   CRON 12h/23h  │      │   USUÁRIO MANUAL    │  │
│  │  (Seg-Sex)    │      │   (Seg-Sex)     │      │                     │  │
│  └───────┬───────┘      └────────┬────────┘      └──────────┬──────────┘  │
│          │                       │                           │              │
│          ▼                       ▼                           ▼              │
│  ┌───────────────┐      ┌─────────────────┐      ┌─────────────────────┐  │
│  │  cron-dou.sh  │      │  cron-dou.sh    │      │   test-mre.py       │  │
│  │   (download)  │      │ (check-dup)     │      │   (data específica)  │  │
│  └───────┬───────┘      └────────┬────────┘      └──────────┬──────────┘  │
│          │                       │                           │              │
│          └───────────────────────┼───────────────────────────┘              │
│                                  ▼                                          │
│                  ┌─────────────────────────────┐                             │
│                  │  inlabs-filter-mre.py      │                             │
│                  │  (Python + requests)        │                             │
│                  └──────────────┬──────────────┘                             │
│                                 │                                            │
│           ┌─────────────────────┼─────────────────────┐                     │
│           ▼                     ▼                     ▼                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐               │
│  │ AUTENTICAÇÃO │     │   DOWNLOAD   │     │   FILTRAGEM  │               │
│  │   IN Labs    │     │   XML/ZIP    │     │     MRE      │               │
│  └──────────────┘     └──────┬───────┘     └──────┬───────┘               │
│                              │                     │                        │
│                              ▼                     ▼                        │
│                    ┌──────────────┐     ┌──────────────┐                  │
│                    │ ZIPs temp    │     │    output/   │                  │
│                    │ (removidos)  │     │  *-MRE.txt   │                  │
│                    └──────────────┘     └──────────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Fluxo de Dados Detalhado

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          FLUXO DE PROCESSAMENTO                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INÍCIO (10h ou manual)                                                     │
│    │                                                                         │
│    ▼                                                                         │
│  ┌─────────────────────────────────────────┐                                │
│  │ 1. AUTENTICAÇÃO                         │                                │
│  │    POST https://inlabs.in.gov.br/login │                                │
│  │    ↓                                    │                                │
│  │    Recebe cookie: inlabs_session_cookie │                                │
│  └──────────────┬──────────────────────────┘                                │
│                 │                                                           │
│                 ▼                                                           │
│  ┌─────────────────────────────────────────┐                                │
│  │ 2. DOWNLOAD (loop 6 seções)            │                                │
│  │    DO1, DO2, DO3, DO1E, DO2E, DO3E     │                                │
│  │    ↓                                    │                                │
│  │    GET /index.php?p=YYYY-MM-DD&dl=    │                                │
│  └──────────────┬──────────────────────────┘                                │
│                 │                                                           │
│                 ├──── 200 ──► ZIP baixado                                   │
│                 ├──── 404 ──► Pular (não existe)                            │
│                 ├──── XXX ──► Erro (logar)                                  │
│                 │                                                           │
│                 ▼                                                           │
│  ┌─────────────────────────────────────────┐                                │
│  │ 3. EXTRAÇÃO XML                         │                                │
│  │    Abrir ZIP na memória (BytesIO)       │                                │
│  │    ↓                                    │                                │
│  │    Buscar primeiro arquivo .xml         │                                │
│  │    ↓                                    │                                │
│  │    Decode UTF-8 (errors=ignore)         │                                │
│  └──────────────┬──────────────────────────┘                                │
│                 │                                                           │
│                 ▼                                                           │
│  ┌─────────────────────────────────────────┐                                │
│  │ 4. LIMPEZA DE TEXTO                     │                                │
│  │    ↓                                    │                                │
│  │    Remover tags HTML: <p>, </p>, <br>  │                                │
│  │    Remover atributos XML: artType="..." │                                │
│  │    Decodificar entidades: &nbsp;        │                                │
│  │    Normalizar espaços                   │                                │
│  └──────────────┬──────────────────────────┘                                │
│                 │                                                           │
│                 ▼                                                           │
│  ┌─────────────────────────────────────────┐                                │
│  │ 5. FILTRAGEM MRE                        │                                │
│  │    ↓                                    │                                │
│  │    Para cada palavra-chave:            │                                │
│  │    • ministério das relações exteriores │                                │
│  │    • chancelaria                        │                                │
│  │    • concursos públicos                 │                                │
│  │    • mre, embaixada, consulado         │                                │
│  │    ↓                                    │                                │
│  │    Extrair contexto (-200, +500 chars)  │                                │
│  │    ↓                                    │                                │
│  │    Limitar a 300 caracteres            │                                │
│  └──────────────┬──────────────────────────┘                                │
│                 │                                                           │
│                 ├──── ENCONTROU ──► Salvar output/                          │
│                 │                   YYYY-MM-DD-SEÇÃO-MRE.txt                │
│                 │                                                           │
│                 ├──── NÃO ENCONTROU ──► Pular                              │
│                 │                                                           │
│                 ▼                                                           │
│  ┌─────────────────────────────────────────┐                                │
│  │ 6. LIMPEZA                              │                                │
│  │    Remover ZIP temporário              │                                │
│  └──────────────┬──────────────────────────┘                                │
│                 │                                                           │
│                 ▼                                                           │
│  FIM (próxima seção ou fim)                                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Estrutura de Arquivos

```
dou-script/
│
├── 📁 output/                          ← RESULTADOS FILTRADOS
│   ├── 2026-03-02-DO1-MRE.txt
│   ├── 2026-03-02-DO2-MRE.txt         ← EXEMPLO: 2 trechos MRE
│   ├── 2026-03-02-DO3-MRE.txt
│   └── ...
│
├── 📁 public/
│   └── 📁 python/
│       ├── inlabs-filter-mre.py       ← SCRIPT PRINCIPAL (cron)
│       └── inlabs-auto-download-*.py
│
├── 📁 docs/                            ← DOCUMENTAÇÃO
│   ├── ARQUITETURA.md                  ← Documentação técnica detalhada
│   ├── VISAO_GERAL.md                  ← Visão geral executiva
│   └── DIAGRAMA.md                     ← Este arquivo (diagramas ASCII)
│
├── cron-dou.sh                         ← WRAPPER CRON
├── test-mre.py                         ← TESTE MANUAL COM DATA
├── .env                                ← CREDENCIAIS (não versionado)
├── .env.example                        ← TEMPLATE DE CREDENCIAIS
├── requirements.txt                    ← DEPENDÊNCIAS
├── README.md                           ← DOCUMENTAÇÃO USUÁRIO
└── CLAUDE.md                           ← INSTRUÇÕES CLAUDE CODE
```

## Mapeamento de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPONENTE → ARQUIVO                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  AGENDAMENTO           → cron-dou.sh                             │
│  (10h, 12h, 23h)       → /tmp/crontab-dou                        │
│                                                                  │
│  AUTENTICAÇÃO         → inlabs-filter-mre.py:login_inlabs()      │
│  (IN Labs login)      → test-mre.py:test_login()                 │
│                                                                  │
│  DOWNLOAD             → inlabs-filter-mre.py:download_file()     │
│  (XML/ZIP fetch)      → test-mre.py:test_download()              │
│                                                                  │
│  EXTRAÇÃO XML         → inlabs-filter-mre.py:extract_xml()       │
│  (ZIP → texto)        → test-mre.py:test_extract_xml()           │
│                                                                  │
│  LIMPEZA TEXTO        → inlabs-filter-mre.py:limpar_texto_xml()  │
│  (HTML/XML strip)     → test-mre.py:test_clean_xml()             │
│                                                                  │
│  FILTRAGEM MRE        → inlabs-filter-mre.py:filtrar_conteudo()  │
│  (palavras-chave)     → test-mre.py:test_filter_mre()            │
│                                                                  │
│  SALVAR RESULTADOS    → inlabs-filter-mre.py:save_result()       │
│  (output/)            → test-mre.py:test_save()                 │
│                                                                  │
│  DETECÇÃO DUPLICATA   → cron-dou.sh:check_duplicate()            │
│  (12h/23h check)      → cron-dou.sh:remove_duplicate()          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Timeline de Execução

```
HORÁRIO     AÇÃO                           ARQUIVOS ENVOLVIDOS
─────────────────────────────────────────────────────────────────
10:00       Inicia download                cron-dou.sh ↓
10:01       Autentica IN Labs              inlabs-filter-mre.py ↓
10:02       Baixa DO1.zip                  DO1.zip (temp)
10:03       Extrai XML, limpa, filtra       (memória)
10:04       Se MRE encontrado              → output/DO1-MRE.txt
            Senão                          → (pula)
10:05       Remove DO1.zip                  (limpeza)
10:06       [Repete para DO2, DO3, extras]
10:15       Fim download                   ───────────────────
─────────────────────────────────────────────────────────────────
12:00       Verifica duplicatas            cron-dou.sh ↓
12:01       Se arquivos existem            → Remove ZIPs + MREs
            Senão                          → (nada)
12:02       Fim verificação                ───────────────────
─────────────────────────────────────────────────────────────────
23:00       Verifica duplicatas (final)    cron-dou.sh ↓
23:01       Se arquivos existem            → Remove ZIPs + MREs
            Senão                          → (nada)
23:02       Fim verificação                ───────────────────
```

## Fluxo de Dados (Texto)

```
CREDENCIAIS (.env)
    ↓
INLABS_EMAIL + INLABS_PASSWORD
    ↓
POST https://inlabs.in.gov.br/logar.php
    ↓
inlabs_session_cookie
    ↓
GET https://inlabs.in.gov.br/... (DO1 - 2026-03-02)
    ↓
2026-03-02-DO1.zip (BYTES BINÁRIOS)
    ↓
zipfile.ZipFile(BytesIO)
    ↓
515_20260302_23475975.xml (UTF-8 DECODE)
    ↓
<artigo><p>Art. 1° O MINISTÉRIO DAS RELAÇÕES EXTERIORES...</p></artigo>
    ↓
limpar_texto_xml()
    ↓
Art. 1° O MINISTÉRIO DAS RELAÇÕES EXTERIORES...
    ↓
filtrar_conteudo(PALAVRAS_CHAVE)
    ↓
MATCH: "ministério das relações exteriores"
    ↓
CONTEXTO: "Art. 1° O MINISTÉRIO DAS RELAÇÕES EXTERIORES..."
    ↓
output/2026-03-02-DO1-MRE.txt
```

## Estados do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    ESTADOS POSSÍVEIS                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  IDLE          → Esperando próximo horário (10h/12h/23h)   │
│  AUTHENTICATING→ Conectando ao IN Labs                     │
│  DOWNLOADING   → Baixando ZIPs (seção por seção)           │
│  EXTRACTING    → Extraindo XML do ZIP                      │
│  FILTERING     → Buscando palavras-chave MRE               │
│  SAVING        → Escrevendo output/*-MRE.txt               │
│  CLEANING      → Removendo ZIPs temporários                │
│  CHECKING      → Verificando duplicatas (12h/23h)          │
│  ERROR         → Falha (requisição, parse, disco cheio...)  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Palavras-Chave Monitoradas

```
┌─────────────────────────────────────────────────────────────┐
│              PALAVRAS-CHAVE MRE (BUSCA CASE-INSENSITIVE)    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. "ministério das relações exteriores"   ← Mais específico│
│  2. "ministério relações exteriores"       ← Variação      │
│  3. "oficial de chancelaria"               ← Cargo         │
│  4. "chancelaria"                          ← Termo genérico│
│  5. "concursos públicos"                   ← Processos     │
│  6. "concursos"                            ← Variação      │
│  7. "mre"                                  ← Sigla         │
│  8. "embaixada"                            ← Instituição   │
│  9. "consulado"                            ← Instituição   │
│  10. "diplomacia"                          ← Área          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**Documentação de Diagramas v1.0**
**Data**: 2026-03-04
**Formato**: ASCII Art (compatível com todos os terminais)
