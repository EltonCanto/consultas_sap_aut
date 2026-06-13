import pytest
from pathlib import Path
import kb_manager

@pytest.fixture
def temp_kb(tmp_path, monkeypatch):
    kb_dir = tmp_path / "test_knowledge_base"
    monkeypatch.setattr(kb_manager, "KB_DIR", kb_dir)
    monkeypatch.setattr(kb_manager, "MODELO_SQL_PATH", kb_dir / "modelo_sql.txt")
    monkeypatch.setattr(kb_manager, "MODELO_VIEW_PATH", kb_dir / "modelo_view.txt")
    kb_manager.init_kb()
    yield kb_dir

def test_init_kb(temp_kb):
    assert (temp_kb / "modelo_sql.txt").exists()
    assert (temp_kb / "modelo_view.txt").exists()
    content = kb_manager.get_model_content("SQL")
    assert "-- Colecione suas consultas SQL aqui" in content

def test_append_to_model(temp_kb):
    kb_manager.append_to_model("SQL", "Teste SQL", "Desc Teste", "SELECT * FROM INV1")
    content = kb_manager.get_model_content("SQL")
    assert "Título: Teste SQL" in content
    assert "SELECT * FROM INV1" in content
