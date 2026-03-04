"""
Fixtures compartilhadas para testes.
"""

import pytest
import zipfile
from io import BytesIO

from dou.config import PALAVRAS_CHAVE, SECOES_DOU


@pytest.fixture
def sample_zip_bytes():
    """ZIP de exemplo para testes."""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr('test.xml', '<?xml version="1.0"?><artigo>Teste MRE conteúdo</artigo>')

    return zip_buffer.getvalue()


@pytest.fixture
def sample_zip_with_multiple_files():
    """ZIP com múltiplos arquivos para testes."""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr('meta.xml', '<?xml version="1.0"?><meta>Info</meta>')
        zf.writestr('content.xml', '<?xml version="1.0"?><artigo>Conteúdo principal MRE aqui</artigo>')
        zf.writestr('readme.txt', 'Este é um arquivo texto')

    return zip_buffer.getvalue()


@pytest.fixture
def sample_xml_content():
    """Conteúdo XML de exemplo para testes."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<artigo>
    <p>O <b>Ministério das Relações Exteriores</b> publicou hoje.</p>
    <br/>
    <p>Seção&nbsp;1 - Conteúdo de teste.</p>
</artigo>"""


@pytest.fixture
def palavras_chave():
    """Palavras-chave MRE para testes."""
    return PALAVRAS_CHAVE


@pytest.fixture
def temp_output_dir(tmp_path):
    """Diretório temporário para output de testes."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return str(output_dir)


@pytest.fixture
def sample_trechos():
    """Trechos de exemplo para testes de salvamento."""
    return [
        {'palavra': 'mre', 'contexto': 'O Ministério das Relações Exteriores publicou...'},
        {'palavra': 'embaixada', 'contexto': 'A embaixada informou que...'}
    ]
