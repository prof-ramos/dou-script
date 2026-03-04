"""
Testes para dou_config.
"""

import pytest

from dou.config import (
    INLABS_LOGIN_URL,
    INLABS_BASE_URL,
    PALAVRAS_CHAVE,
    SECOES_DOU,
    DOWNLOAD_TIMEOUT,
    OUTPUT_DIR
)


class TestConfigURLs:
    """Testes para URLs de configuração."""

    def test_login_url_format(self):
        """URL de login deve ser HTTPS válida."""
        assert INLABS_LOGIN_URL.startswith("https://")
        assert "inlabs.in.gov.br" in INLABS_LOGIN_URL

    def test_base_url_format(self):
        """URL base deve ser HTTPS válida."""
        assert INLABS_BASE_URL.startswith("https://")
        assert "inlabs.in.gov.br" in INLABS_BASE_URL

    def test_base_url_contains_param(self):
        """URL base deve conter parâmetro p=."""
        assert "p=" in INLABS_BASE_URL


class TestConfigTimeout:
    """Testes para configuração de timeout."""

    def test_download_timeout_positive(self):
        """Timeout de download deve ser positivo."""
        assert DOWNLOAD_TIMEOUT > 0
        assert isinstance(DOWNLOAD_TIMEOUT, int)

    def test_download_timeout_reasonable(self):
        """Timeout de download deve ser razoável (pelo menos 10 segundos)."""
        assert DOWNLOAD_TIMEOUT >= 10


class TestConfigPalavrasChave:
    """Testes para palavras-chave de configuração."""

    def test_palavras_chave_not_empty(self):
        """Palavras-chave não devem estar vazias."""
        assert len(PALAVRAS_CHAVE) > 0

    def test_palavras_chave_contains_mre(self):
        """Palavras-chave devem conter 'mre'."""
        assert "mre" in PALAVRAS_CHAVE

    def test_palavras_chave_contains_variations(self):
        """Palavras-chave devem conter variações do Ministério."""
        assert "ministério das relações exteriores" in PALAVRAS_CHAVE
        assert "embaixada" in PALAVRAS_CHAVE
        assert "consulado" in PALAVRAS_CHAVE

    def test_palavras_chave_all_lowercase(self):
        """Todas as palavras-chave devem ser minúsculas."""
        assert all(p.islower() for p in PALAVRAS_CHAVE)


class TestConfigSecoes:
    """Testes para seções do DOU."""

    def test_secoes_dou_not_empty(self):
        """Seções não devem estar vazias."""
        assert len(SECOES_DOU) > 0

    def test_secoes_dou_contains_expected(self):
        """Seções devem conter DO1, DO2, DO3."""
        assert "DO1" in SECOES_DOU
        assert "DO2" in SECOES_DOU
        assert "DO3" in SECOES_DOU

    def test_secoes_dou_contains_extras(self):
        """Seções devem conter edições extras."""
        assert "DO1E" in SECOES_DOU
        assert "DO2E" in SECOES_DOU
        assert "DO3E" in SECOES_DOU


class TestConfigOutput:
    """Testes para configuração de output."""

    def test_output_dir_is_string(self):
        """Diretório de output deve ser string."""
        assert isinstance(OUTPUT_DIR, str)

    def test_output_dir_not_empty(self):
        """Diretório de output não deve estar vazio."""
        assert len(OUTPUT_DIR) > 0
