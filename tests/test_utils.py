"""
Testes para dou_utils.
"""

import os
import pytest
import zipfile
from io import BytesIO

from dou.utils import extrair_texto_xml, limpar_texto_xml, filtrar_conteudo, salvar_resultados


class TestExtrairTextoXML:
    """Testes para extração de texto XML."""

    def test_extrair_xml_valido(self, sample_zip_bytes):
        """Deve extrair XML de ZIP válido."""
        resultado = extrair_texto_xml(sample_zip_bytes)
        assert resultado is not None
        assert len(resultado) > 0
        assert "<?xml" in resultado or "artigo" in resultado

    def test_extrair_xml_primeiro_arquivo(self, sample_zip_with_multiple_files):
        """Deve extrair o primeiro arquivo XML encontrado."""
        resultado = extrair_texto_xml(sample_zip_with_multiple_files)
        assert resultado is not None
        # Deve retornar o primeiro XML (meta.xml ou content.xml)
        assert "<?xml" in resultado

    def test_extrair_xml_zip_corrompido(self):
        """Deve retornar string vazia para ZIP corrompido."""
        zip_corrompido = b"Este nao e um ZIP valido"
        resultado = extrair_texto_xml(zip_corrompido)
        assert resultado == ""

    def test_extrair_xml_zip_vazio(self):
        """Deve retornar string vazia para ZIP sem XML."""
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr('readme.txt', 'Apenas texto')

        resultado = extrair_texto_xml(zip_buffer.getvalue())
        assert resultado == ""


class TestLimparTextoXML:
    """Testes para limpeza de texto XML."""

    def test_limpar_texto_remove_html_tags(self):
        """Deve remover tags <p> e </p>."""
        texto = "<p>Art. 1°</p> O MINISTÉRIO"
        resultado = limpar_texto_xml(texto)
        assert "<p>" not in resultado
        assert "</p>" not in resultado
        assert "Art. 1°" in resultado

    def test_limpar_texto_remove_bold_tags(self):
        """Deve remover tags <b> e </b>."""
        texto = "Texto <b>importante</b> aqui"
        resultado = limpar_texto_xml(texto)
        assert "<b>" not in resultado
        assert "</b>" not in resultado
        assert "Texto importante aqui" == resultado

    def test_limpar_texto_convert_br_to_newline(self):
        """Deve converter <br> para quebra de linha."""
        texto = "Linha 1<br>Linha 2"
        resultado = limpar_texto_xml(texto)
        assert "<br" not in resultado
        assert "\n" in resultado

    def test_limpar_texto_decode_entities(self):
        """Deve decodificar entidades HTML."""
        texto = "Seção&nbsp;1"
        resultado = limpar_texto_xml(texto)
        assert "&nbsp;" not in resultado
        # &nbsp; é decodificado para non-breaking space (\xa0), não espaço regular
        assert "Seção\xa01" == resultado

    def test_limpar_texto_remove_xml_attributes(self):
        """Deve remover atributos XML."""
        texto = 'texto id="123" classe="abc"'
        resultado = limpar_texto_xml(texto)
        assert 'id="123"' not in resultado
        assert 'classe="abc"' not in resultado

    def test_limpar_texto_normalize_spaces(self):
        """Deve normalizar espaços excessivos."""
        texto = "Texto    com    espaços    múltiplos"
        resultado = limpar_texto_xml(texto)
        assert "Texto com espaços múltiplos" == resultado

    def test_limpar_texto_preserve_newlines(self):
        """Deve preservar quebras de linha significativas."""
        texto = "Linha 1\n\n\nLinha 2"
        resultado = limpar_texto_xml(texto)
        assert "\n\n" in resultado  # Dupla newline preservada

    def test_limpar_texto_strip(self):
        """Deve remover espaços no início e fim."""
        texto = "   \n  Texto central  \n   "
        resultado = limpar_texto_xml(texto)
        assert resultado == resultado.strip()


class TestFiltrarConteudo:
    """Testes para filtragem de conteúdo."""

    def test_filtrar_conteudo_case_insensitive(self):
        """Busca deve ser case-insensitive."""
        texto = "O Ministério das Relações Exteriores publicou."
        palavras = ["mre"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado) == 0  # "mre" não está no texto

    def test_filtrar_conteudo_encontra_palavra(self):
        """Deve encontrar palavra-chave no texto."""
        texto = "O Ministério das Relações Exteriores publicou."
        palavras = ["ministério das relações exteriores"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado) == 1
        assert resultado[0]['palavra'] == "ministério das relações exteriores"

    def test_filtrar_conteudo_multiple_ocorrencias(self):
        """Deve encontrar múltiplas ocorrências da mesma palavra."""
        texto = "O MRE informou. O MRE publicou. O MRE decidiu."
        palavras = ["mre"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado) == 3

    def test_filtrar_conteudo_multiple_palavras(self):
        """Deve encontrar múltiplas palavras-chave."""
        texto = "O MRE e a embaixada informaram."
        palavras = ["mre", "embaixada"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado) == 2

    def test_filtrar_conteudo_contexto_limitado(self):
        """Contexto deve ser limitado a 300 caracteres."""
        texto = "MRE" + "X" * 1000
        palavras = ["mre"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado) == 1
        assert len(resultado[0]['contexto']) <= 303  # 300 + "..."

    def test_filtrar_conteudo_retorna_lista_vazia(self):
        """Deve retornar lista vazia se não encontrar nada."""
        texto = "Texto sem palavras-chave relevantes."
        palavras = ["inexistente"]
        resultado = filtrar_conteudo(texto, palavras)
        assert len(resultado) == 0

    def test_filtrar_conteudo_com_tags_html(self, sample_xml_content):
        """Deve funcionar com XML contendo tags HTML."""
        palavras = ["ministério das relações exteriores"]
        resultado = filtrar_conteudo(sample_xml_content, palavras)
        assert len(resultado) == 1
        assert "<b>" not in resultado[0]['contexto']


class TestSalvarResultados:
    """Testes para salvamento de resultados."""

    def test_salvar_resultados_sucesso(self, tmp_path, sample_trechos, monkeypatch):
        """Deve salvar arquivo com sucesso."""
        # Patch OUTPUT_DIR para usar tmp_path
        monkeypatch.setattr("dou.utils.OUTPUT_DIR", str(tmp_path))

        resultado = salvar_resultados("2026-03-04", sample_trechos, "DO1")
        assert resultado is True

        # Verificar que arquivo foi criado
        arquivo = tmp_path / "2026-03-04-DO1-MRE.txt"
        assert arquivo.exists()

        # Verificar conteúdo
        conteudo = arquivo.read_text(encoding='utf-8')
        assert "TRECHOS MRE ENCONTRADOS" in conteudo
        assert "PALAVRA-CHAVE: MRE" in conteudo
        assert "PALAVRA-CHAVE: EMBAIXADA" in conteudo

    def test_salvar_resultados_lista_vazia(self, tmp_path, monkeypatch):
        """Deve retornar False para lista vazia."""
        monkeypatch.setattr("dou.utils.OUTPUT_DIR", str(tmp_path))

        resultado = salvar_resultados("2026-03-04", [], "DO1")
        assert resultado is False

    def test_salvar_resultados_cria_diretorio(self, tmp_path, sample_trechos, monkeypatch):
        """Deve criar diretório de output se não existir."""
        output_dir = tmp_path / "novo_output"
        monkeypatch.setattr("dou.utils.OUTPUT_DIR", str(output_dir))

        salvar_resultados("2026-03-04", sample_trechos, "DO1")

        assert output_dir.exists()
        assert (output_dir / "2026-03-04-DO1-MRE.txt").exists()

    def test_salvar_resultados_unicode(self, tmp_path, monkeypatch):
        """Deve salvar caracteres Unicode corretamente."""
        monkeypatch.setattr("dou.utils.OUTPUT_DIR", str(tmp_path))

        trechos = [
            {'palavra': 'mre', 'contexto': 'Ministério das Relações Exteriores - Seção 1'}
        ]

        salvar_resultados("2026-03-04", trechos, "DO1")

        arquivo = tmp_path / "2026-03-04-DO1-MRE.txt"
        conteudo = arquivo.read_text(encoding='utf-8')
        assert "Ministério" in conteudo
        assert "Seção" in conteudo
