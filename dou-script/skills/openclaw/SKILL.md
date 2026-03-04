---
name: openclaw
description: Desenvolvimento, instalação, configuração e uso do OpenClaw — assistente pessoal de IA local que integra com WhatsApp, Telegram, Discord, Slack, Signal e iMessage. Use esta skill sempre que o usuário mencionar OpenClaw, openclaw.ai, instalação de assistente de IA local com integração a apps de chat, ou qualquer referência a comandos CLI do openclaw. Inclui instaladores multiplataforma (macOS/Linux/Windows), variáveis de ambiente, comandos pós-instalação e desenvolvimento do site Astro.
---

# OpenClaw

**OpenClaw** é um assistente pessoal de IA que roda localmente e integra com apps de chat (WhatsApp, Telegram, Discord, Slack, Signal, iMessage). O site `openclaw.ai` (repo Astro no GitHub Pages) é o hub de instalação com one-liners para macOS, Linux e Windows.

---

## Instalação

### macOS/Linux

```bash
# Padrão (com onboarding)
curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash

# Beta
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta

# Via git (developers)
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git

# Sem onboarding
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard

# Dry-run (preview sem executar)
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --dry-run

# Versão específica
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --version 1.2.3
```

### CLI-Only / Non-Interactive (CI/CD)

```bash
curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install-cli.sh | bash

# JSON output para scripting
curl -fsSL https://openclaw.ai/install-cli.sh | bash -s -- --json

# Prefix customizado
curl -fsSL https://openclaw.ai/install-cli.sh | bash -s -- --prefix /opt/openclaw

# Node.js específico
curl -fsSL https://openclaw.ai/install-cli.sh | bash -s -- --node-version 22.22.0
```

### Windows PowerShell

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex

# Beta
& ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -Tag beta

# Sem onboarding
& ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard

# Dry run
& ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -DryRun
```

### Windows CMD

```cmd
curl -fsSL https://openclaw.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

---

## Opções do install.sh

| Opção | Descrição |
|---|---|
| `--install-method npm\|git` | Método de instalação (padrão: npm) |
| `--beta` | Canal beta |
| `--version <ver>` | Versão específica |
| `--git-dir <path>` | Diretório do checkout git (padrão: ~/openclaw) |
| `--no-git-update` | Pula git pull em checkout existente |
| `--no-onboard` | Pula wizard de onboarding |
| `--no-prompt` | Sem prompts interativos (CI) |
| `--dry-run` | Preview sem mudanças |
| `--verbose` | Debug output |

## Opções do install-cli.sh

| Opção | Descrição |
|---|---|
| `--json` | NDJSON events (machine-readable) |
| `--prefix <path>` | Prefix de instalação (padrão: ~/.openclaw) |
| `--node-version <ver>` | Versão do Node.js (padrão: 22.22.0) |
| `--onboard` | Executa onboarding pós-install |

---

## Variáveis de Ambiente

```bash
export OPENCLAW_INSTALL_METHOD=npm      # npm ou git
export OPENCLAW_VERSION=latest
export OPENCLAW_BETA=1
export OPENCLAW_GIT_DIR=~/openclaw
export OPENCLAW_GIT_UPDATE=0           # Pula git pull
export OPENCLAW_NO_ONBOARD=1
export OPENCLAW_NO_PROMPT=1            # CI/CD
export OPENCLAW_DRY_RUN=1
export OPENCLAW_VERBOSE=1
export OPENCLAW_NPM_LOGLEVEL=error     # error|warn|notice
export SHARP_IGNORE_GLOBAL_LIBVIPS=1
export OPENCLAW_PREFIX=~/.openclaw     # CLI installer
export OPENCLAW_NODE_VERSION=22.22.0   # CLI installer
export OPENCLAW_CONFIG_PATH=~/.openclaw/openclaw.json
export OPENCLAW_PROFILE=default        # Multi-workspace
```

---

## Comandos CLI Pós-Instalação

```bash
# Onboarding
openclaw onboard

# Health check e migrações
openclaw doctor
openclaw doctor --non-interactive

# Plugins
openclaw plugins update --all

# Daemon do gateway
openclaw daemon status
openclaw daemon status --json
openclaw gateway install --force
openclaw gateway restart
openclaw gateway status --probe --deep

# Update (installs via git)
openclaw update --restart

# Versão
openclaw --version
```

---

## Desenvolvimento do Site (Astro)

```bash
# Requer Bun
bun install
bun run dev      # http://localhost:4321
bun run build
bun run preview
```

### Estrutura do Repositório

```
openclaw.ai/
├── public/
│   ├── install.sh           # Installer macOS/Linux
│   ├── install-cli.sh       # CLI non-interactive
│   ├── install.ps1          # PowerShell
│   ├── install.cmd          # Windows CMD
│   └── sponsors/            # Logos SVG
├── src/
│   ├── pages/
│   │   ├── index.astro
│   │   ├── integrations.astro
│   │   ├── showcase.astro
│   │   └── trust/
│   ├── content/blog/        # Posts Markdown
│   ├── data/
│   │   ├── testimonials.json
│   │   └── showcase.json
│   └── layouts/Layout.astro
├── astro.config.mjs
├── package.json
└── vercel.json
```

### astro.config.mjs

```javascript
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://openclaw.ai',
  build: { assets: '_assets' }
});
```

### Dependências principais

```json
{
  "dependencies": {
    "@astrojs/rss": "^4.0.15",
    "@lucide/astro": "^0.563.0",
    "@vercel/analytics": "^1.6.1",
    "astro": "^5.17.2",
    "js-yaml": "^4.1.1",
    "simple-icons": "^16.8.0"
  }
}
```

---

## Referência

- Repo: https://github.com/openclaw/openclaw.ai
- Site: https://openclaw.ai
- Docs Context7: https://context7.com/openclaw/openclaw.ai
- Node.js mínimo: 22+
- Gerenciador de pacotes do site: Bun
- Deploy: GitHub Pages + Vercel
