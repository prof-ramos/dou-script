from datetime import date
import requests
import logging
from zipfile import BadZipFile
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

login = "email@dominio.com"
senha = "minha_senha"

tipo_dou="DO1 DO2 DO3 DO1E DO2E DO3E" # Seções separadas por espaço
# Opções DO1 DO2 DO3 DO1E DO2E DO3E

url_login = "https://inlabs.in.gov.br/logar.php"
url_download = "https://inlabs.in.gov.br/index.php?p="

payload = {"email" : login, "password" : senha}
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
s = requests.Session()

def download():
    try:
        if s.cookies.get('inlabs_session_cookie'):
            cookie = s.cookies.get('inlabs_session_cookie')
        else:
            logger.error("Falha ao obter cookie. Verifique suas credenciais")
            exit(37)

        # Montagem da URL:
        ano = date.today().strftime("%Y")
        mes = date.today().strftime("%m")
        dia = date.today().strftime("%d")
        data_completa = ano + "-" + mes + "-" + dia

        for dou_secao in tipo_dou.split(' '):
            logger.info("Aguarde Download...")
            url_arquivo = url_download + data_completa + "&dl=" + data_completa + "-" + dou_secao + ".zip"
            cabecalho_arquivo = {'Cookie': 'inlabs_session_cookie=' + cookie, 'origem': '736372697074'}
            response_arquivo = s.request("GET", url_arquivo, headers = cabecalho_arquivo)
            if response_arquivo.status_code == 200:
                with open(data_completa + "-" + dou_secao + ".zip", "wb") as f:
                    f.write(response_arquivo.content)
                    logger.info(f"Arquivo {data_completa + '-' + dou_secao + '.zip'} salvo.")
                del response_arquivo
                del f
            elif response_arquivo.status_code == 404:
                logger.warning(f"Arquivo não encontrado: {data_completa + '-' + dou_secao + '.zip'}")

        logger.info("Aplicação encerrada")
        exit(0)
    except (IOError, OSError) as e:
        logger.error(f"Erro de I/O: {e}")
        exit(1)
    except RequestException as e:
        logger.error(f"Erro de requisição: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        exit(1)

def login():
    try:
        response = s.request("POST", url_login, data=payload, headers=headers)
        download()
    except RequestException as e:
        logger.error(f"Erro de requisição no login: {e}")
        login()
    except Exception as e:
        logger.error(f"Erro inesperado no login: {e}")
        exit(1)
login()

