######################################################################
## INLABS                                                           ##
## Script desenvolvido em Python para download automático de PDFs   ##
## Autor: https://github.com/Iakim                                  ##
## A simplicidade é o último grau de sofisticação                   ##
######################################################################

import os
import sys
import requests
from datetime import date

login    = "email@dominio.com"
senha    = "sua_senha"

## Seções do DOU: do1 do2 do3 (inclui edições extras automaticamente)
tipo_dou = "do1 do2 do3"

## Configuração de proxy opcional (via variável de ambiente)
## Exemplo: export SOCKS5_PROXY=socks5://127.0.0.1:1080
PROXY = os.environ.get("SOCKS5_PROXY") or os.environ.get("HTTPS_PROXY")

URL_LOGIN    = "https://inlabs.in.gov.br/logar.php"
URL_DOWNLOAD = "https://inlabs.in.gov.br/index.php"
HEADERS_BASE = {"origem": "736372697074"}

s = requests.Session()
if PROXY:
    s.proxies.update({"http": PROXY, "https": PROXY})


def fazer_login():
    headers = {
        **HEADERS_BASE,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    for tentativa in range(1, 4):
        try:
            s.post(URL_LOGIN, data={"email": login, "password": senha},
                   headers=headers, timeout=30)
            if s.cookies.get("inlabs_session_cookie"):
                print("Login realizado com sucesso.")
                return True
        except requests.exceptions.ConnectionError:
            print(f"Tentativa {tentativa}/3: erro de conexão.")
    print("Falha de autenticação. Verifique suas credenciais.")
    return False


def baixar_secao(cookie, data_str, secao):
    """Baixa a edição principal e as extras (para no primeiro 404)."""
    ano, mes, dia = data_str.split("-")
    headers = {"Cookie": f"inlabs_session_cookie={cookie}", **HEADERS_BASE}
    baixados = []

    # Edição principal
    nome = f"{ano}_{mes}_{dia}_ASSINADO_{secao}.pdf"
    url  = f"{URL_DOWNLOAD}?p={data_str}&dl={nome}"
    r = s.get(url, headers=headers, timeout=60)
    if r.status_code == 200 and len(r.content) > 1_000:
        with open(nome, "wb") as f:
            f.write(r.content)
        baixados.append(nome)
        print(f"Arquivo {nome} salvo.")
    else:
        print(f"Arquivo não encontrado: {nome}")

    # Edições extras — para no primeiro 404
    for letra in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        nome_extra = f"{ano}_{mes}_{dia}_ASSINADO_{secao}_extra_{letra}.pdf"
        url_extra  = f"{URL_DOWNLOAD}?p={data_str}&dl={nome_extra}"
        r2 = s.get(url_extra, headers=headers, timeout=30)
        if r2.status_code == 200 and len(r2.content) > 1_000:
            with open(nome_extra, "wb") as f:
                f.write(r2.content)
            baixados.append(nome_extra)
            print(f"Arquivo {nome_extra} salvo.")
        else:
            break  # sem mais edições extras nesta seção

    return baixados


def main():
    if not fazer_login():
        sys.exit(1)

    cookie       = s.cookies.get("inlabs_session_cookie")
    hoje         = date.today()
    data_str     = hoje.strftime("%Y-%m-%d")
    todos        = []

    for secao in tipo_dou.split():
        todos.extend(baixar_secao(cookie, data_str, secao))

    if not todos:
        print("Nenhum arquivo disponível para hoje.")
        sys.exit(0)

    print(f"\n{len(todos)} arquivo(s) baixado(s).")


if __name__ == "__main__":
    main()
