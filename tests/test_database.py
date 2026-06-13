import pytest
import sqlite3
import os
import database

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_consultas.db"
    monkeypatch.setattr(database, "DB_FILE", str(db_path))
    database.init_db()
    yield
    # Cleanup if needed

def test_init_db(temp_db):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saved_queries'")
    assert cursor.fetchone() is not None
    conn.close()

def test_save_and_search_query(temp_db):
    database.save_query("Teste", "SQL", "SELECT * FROM OINV", "Teste desc")
    
    # Search all
    results = database.search_queries()
    assert len(results) == 1
    assert results[0]["nome"] == "Teste"
    assert results[0]["tipo"] == "SQL"
    assert results[0]["codigo"] == "SELECT * FROM OINV"
    assert results[0]["descricao"] == "Teste desc"

    # Search by term
    results_term = database.search_queries("Teste")
    assert len(results_term) == 1
    
    results_term_not_found = database.search_queries("NaoExiste")
    assert len(results_term_not_found) == 0
