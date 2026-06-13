import pytest
from unittest.mock import patch, MagicMock
import llm_service

def test_get_client_missing_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    # mock getenv
    with patch("os.getenv", return_value="sua_chave_api_aqui"):
        with pytest.raises(ValueError, match="Chave API do Gemini não configurada."):
            llm_service.get_client()

@patch("llm_service.get_client")
def test_generate_sap_code(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_response = MagicMock()
    mock_response.text = "```sql\nSELECT * FROM OINV\n```"
    mock_client.models.generate_content.return_value = mock_response

    result = llm_service.generate_sap_code("Me de as notas", "SQL", "context")
    assert result == "```sql\nSELECT * FROM OINV\n```"
    mock_client.models.generate_content.assert_called_once()

def test_extract_code_and_metadata():
    response = "Aqui esta:\n```sql\n-- - Titulo: Notas Fiscais\n-- - Consulta - Notas\nSELECT * FROM OINV\n```"
    titulo, desc, codigo = llm_service.extract_code_and_metadata(response)
    
    assert titulo == "Notas Fiscais"
    assert desc == "Notas"
    assert "SELECT * FROM OINV" in codigo
