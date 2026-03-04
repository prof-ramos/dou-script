# Configuração Tailscale para DOU Script

## Problema
O WAF do INLABS bloqueia IPs de datacenter (VPS proframos.com).

## Solução: Tailscale Exit Node

### Passo 1: Instalar Tailscale no VPS

```bash
# Ubuntu/Debian
curl -fsSL https://tailscale.com/install.sh | sh

# Iniciar Tailscale
sudo tailscale up
```

### Passo 2: Instalar Tailscale no PC de Casa

```bash
# Windows/Mac/Linux
# Download em: https://tailscale.com/download/
# Instalar e fazer login
```

### Passo 3: Configurar Exit Node no PC de Casa

No Tailscale do PC de casa:
1. Abrir settings
2. Ir em "Preferences"
3. Ativar "Use as an exit node"
4. Selecionar "Allow LAN access"

### Passo 4: Conectar VPS à rede Tailscale

No VPS:
```bash
# Verificar status do Tailscale
sudo tailscale status

# Conectar à sua rede
sudo tailscale up
```

### Passo 5: Modificar script para usar Exit Node

```bash
# Criar wrapper script
cat > /usr/local/bin/dou-wrapper.sh << 'EOF'
#!/bin/bash
# Forçar uso do exit node Tailscale para INLABS

export TS_EXIT_NODE="${TS_EXIT_NODE:-$(tailscale status | grep 'Exit node' | awk '{print $3}')}"
export INLABS_EMAIL="$(grep INLABS_EMAIL .env | cut -d'=' -f2)"
export INLABS_PASSWORD="$(grep INLABS_PASSWORD .env | cut -d'=' -f2)"

cd /Users/gabrielramos/dou-script
python3 test-mre.py "$(date +%Y-%m-%d)"
EOF

chmod +x /usr/local/bin/dou-wrapper.sh
```

### Passo 6: Testar conexão via Tailscale

```bash
# Testar se está usando o exit node
curl -s https://ifconfig.me

# Deve mostrar o IP residencial, não o IP do VPS
```

### Passo 7: Atualizar crontab

```bash
# Substituir
0 10 * * 1-5 /Users/gabrielramos/dou-script/cron-dou.sh download

# Por
0 10 * * 1-5 /usr/local/bin/dou-wrapper.sh
```

## Validação

Antes de agendar:
```bash
# 1. Verificar Tailscale ativo
sudo tailscale status

# 2. Verificar Exit node
sudo tailscale status | grep "Exit node"

# 3. Testar IP
curl -s https://ifconfig.me

# 4. Testar script
/usr/local/bin/dou-wrapper.sh
```

## Troubleshooting

**Exit node não aparece:**
```bash
# No PC de casa, verificar se "Use as an exit node" está ativado
# Verificar se VPS está na mesma rede Tailscale
```

**Ainda bloqueado:**
```bash
# Verificar se tráfego está saindo pelo exit node
curl -s https://ifconfig.me
# Se mostrar IP do VPS, Tailscale não está sendo usado
```

## Alternativa: tinyproxy (se não quiser Tailscale)

Se preferir proxy HTTP tradicional:

**No PC de casa:**
```bash
# Instalar tinyproxy
sudo apt install tinyproxy

# Configurar para aceitar conexões do Tailscale
# Porta: 8888
```

**No script Python:**
```python
import requests

proxies = {
    'http': 'http://IP_TAILSCALE_PC:8888',
    'https': 'http://IP_TAILSCALE_PC:8888'
}

response = requests.post(url_login, data=payload, proxies=proxies)
```

## Recomendação Final

**Opção 1 (Tailscale Exit Node)** - Recomendada
- Mais simples e segura
- Criptografia automática
- Sem configuração de proxy manual

**Opção 4 (Cron em casa)** - Mais simples
- Se tiver PC ligado em casa
- Executar script localmente
- Upload via rsync/scp para VPS
