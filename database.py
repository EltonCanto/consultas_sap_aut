import sqlite3
import datetime
from pathlib import Path

DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)
DB_FILE = str(DB_DIR / "consultas.db")

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela para consultas/views salvas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL, -- 'SQL' ou 'View'
            codigo TEXT NOT NULL,
            descricao TEXT,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_query(nome: str, tipo: str, codigo: str, descricao: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO saved_queries (nome, tipo, codigo, descricao, data_criacao) VALUES (?, ?, ?, ?, ?)",
        (nome, tipo, codigo, descricao, datetime.datetime.now())
    )
    conn.commit()
    conn.close()

def search_queries(search_term: str = "", start_date=None, end_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, nome, tipo, codigo, descricao, data_criacao FROM saved_queries WHERE 1=1"
    params = []
    
    if search_term:
        query += " AND nome LIKE ?"
        params.append(f"%{search_term}%")
        
    if start_date:
        query += " AND date(data_criacao) >= date(?)"
        params.append(start_date)
        
    if end_date:
        query += " AND date(data_criacao) <= date(?)"
        params.append(end_date)
        
    query += " ORDER BY data_criacao DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": r[0],
            "nome": r[1],
            "tipo": r[2],
            "codigo": r[3],
            "descricao": r[4],
            "data_criacao": r[5]
        }
        for r in rows
    ]

# Garante que o banco seja inicializado ao importar o módulo
init_db()
