"""
INLABS Client - Download automatizado do Diário Oficial da União

Repositório: https://github.com/Imprensa-Nacional/inlabs
API: https://inlabs.in.gov.br

Uso:
    from inlabs_client import INLABSClient
    
    client = INLABSClient(email="seu@email.com", password="sua_senha")
    client.download_today(secoes=["DO1", "DO2"])
"""

import os
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict
import requests


class INLABSClient:
    """
    Cliente para download automatizado do Diário Oficial da União.
    
    Requer cadastro prévio em: https://inlabs.in.gov.br
    
    Seções disponíveis:
        - DO1: Seção 1 (Atos Normativos)
        - DO2: Seção 2 (Atos de Interesse de Servidores)
        - DO3: Seção 3 (Contratos, Editais e Atos Oficiais)
        - DO1E: Seção 1 Extra
        - DO2E: Seção 2 Extra
        - DO3E: Seção 3 Extra
    """
    
    URL_LOGIN = "https://inlabs.in.gov.br/logar.php"
    URL_DOWNLOAD = "https://inlabs.in.gov.br/index.php?p="
    
    SECOES = ["DO1", "DO2", "DO3", "DO1E", "DO2E", "DO3E"]
    
    def __init__(
        self,
        email: str,
        password: str,
        output_dir: str = "./dou",
        timeout: int = 30
    ):
        """
        Inicializa cliente INLABS.
        
        Args:
            email: Email cadastrado no INLABS
            password: Senha da conta
            output_dir: Diretório para salvar arquivos
            timeout: Timeout em segundos
        """
        self.email = email
        self.password = password
        self.output_dir = output_dir
        self.timeout = timeout
        
        self.session = requests.Session()
        self.cookie: Optional[str] = None
        
        # Criar diretório de saída
        os.makedirs(output_dir, exist_ok=True)
    
    def login(self) -> bool:
        """
        Realiza login e obtém cookie de sessão.
        
        Returns:
            True se login bem-sucedido
        """
        payload = {
            "email": self.email,
            "password": self.password
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        try:
            response = self.session.post(
                self.URL_LOGIN,
                data=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            # Verificar se obteve cookie
            self.cookie = self.session.cookies.get('inlabs_session_cookie')
            
            if not self.cookie:
                print("❌ Falha ao obter cookie. Verifique suas credenciais.")
                return False
            
            print(f"✅ Login realizado com sucesso")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def download(
        self,
        data: Optional[date] = None,
        secoes: Optional[List[str]] = None,
        formato: str = "xml"
    ) -> Dict[str, str]:
        """
        Download das edições do DOU para uma data específica.
        
        Args:
            data: Data das edições (padrão: hoje)
            secoes: Lista de seções (padrão: todas)
            formato: "xml" ou "pdf"
            
        Returns:
            Dict com arquivos baixados {secao: caminho}
        """
        if not self.cookie and not self.login():
            return {}
        
        if data is None:
            data = date.today()
        
        if secoes is None:
            secoes = self.SECOES
        
        # Validar seções
        secoes = [s.upper() for s in secoes if s.upper() in self.SECOES]
        
        if not secoes:
            print("❌ Nenhuma seção válida especificada")
            return {}
        
        data_str = data.strftime("%Y-%m-%d")
        arquivos_baixados = {}
        
        for secao in secoes:
            arquivo = self._download_secao(data_str, secao, formato)
            if arquivo:
                arquivos_baixados[secao] = arquivo
        
        return arquivos_baixados
    
    def download_today(
        self,
        secoes: Optional[List[str]] = None,
        formato: str = "xml"
    ) -> Dict[str, str]:
        """Download da edição de hoje."""
        return self.download(date.today(), secoes, formato)
    
    def download_range(
        self,
        data_inicial: date,
        data_final: date,
        secoes: Optional[List[str]] = None,
        formato: str = "xml"
    ) -> Dict[str, List[str]]:
        """
        Download de um range de datas.
        
        Args:
            data_inicial: Data inicial
            data_final: Data final
            secoes: Lista de seções
            formato: "xml" ou "pdf"
            
        Returns:
            Dict {data: {secao: caminho}}
        """
        if not self.cookie and not self.login():
            return {}
        
        resultados = {}
        delta = timedelta(days=1)
        current = data_inicial
        
        while current <= data_final:
            data_str = current.strftime("%Y-%m-%d")
            print(f"\n📅 Baixando {data_str}...")
            
            arquivos = self.download(current, secoes, formato)
            
            if arquivos:
                resultados[data_str] = arquivos
            
            current += delta
        
        return resultados
    
    def _download_secao(
        self,
        data_str: str,
        secao: str,
        formato: str
    ) -> Optional[str]:
        """
        Download de uma seção específica.
        
        Args:
            data_str: Data no formato YYYY-MM-DD
            secao: Seção (DO1, DO2, etc)
            formato: "xml" ou "pdf"
            
        Returns:
            Caminho do arquivo ou None
        """
        # Montar URL
        url = f"{self.URL_DOWNLOAD}{data_str}&dl={data_str}-{secao}.zip"
        
        headers = {
            'Cookie': f'inlabs_session_cookie={self.cookie}',
            'origem': '736372697074'
        }
        
        try:
            print(f"  📥 Baixando {secao}...", end=" ")
            
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                # Salvar arquivo
                filename = f"{data_str}-{secao}.zip"
                filepath = os.path.join(self.output_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                print(f"✅ {filename}")
                return filepath
            
            elif response.status_code == 404:
                print(f"❌ Não encontrado")
                return None
            
            else:
                print(f"❌ Erro {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro: {e}")
            return None
    
    def list_available_dates(self, days: int = 7) -> List[date]:
        """
        Lista datas provavelmente disponíveis (úteis nos últimos N dias).
        
        Args:
            days: Número de dias para verificar
            
        Returns:
            Lista de datas
        """
        datas = []
        hoje = date.today()
        delta = timedelta(days=1)
        
        for i in range(days):
            d = hoje - (delta * i)
            # Pular finais de semana (DOU não publica)
            if d.weekday() < 5:  # Seg-Sex
                datas.append(d)
        
        return datas


# Exemplo de uso
if __name__ == "__main__":
    import os
    
    # Configurações (usar variáveis de ambiente)
    email = os.getenv("INLABS_EMAIL", "seu@email.com")
    password = os.getenv("INLABS_PASSWORD", "sua_senha")
    
    # Criar cliente
    client = INLABSClient(
        email=email,
        password=password,
        output_dir="./dou"
    )
    
    # Download de hoje
    arquivos = client.download_today(secoes=["DO1", "DO2"])
    
    print(f"\n✅ {len(arquivos)} arquivos baixados:")
    for secao, path in arquivos.items():
        print(f"  {secao}: {path}")
