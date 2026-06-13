import os
from pathlib import Path

KB_DIR = Path("knowledge_base")
MODELO_SQL_PATH = KB_DIR / "modelo_sql.txt"
MODELO_VIEW_PATH = KB_DIR / "modelo_view.txt"

def init_kb():
    os.makedirs(KB_DIR, exist_ok=True)
    if not MODELO_SQL_PATH.exists():
        MODELO_SQL_PATH.write_text("-- Colecione suas consultas SQL aqui.\n-- Formato:\n-- - Título: Exemplo\n-- - Consulta - Descrição detalhada\n\n", encoding="utf-8")
    if not MODELO_VIEW_PATH.exists():
        MODELO_VIEW_PATH.write_text("-- Colecione suas Views aqui.\n-- Formato:\n-- - Título: Exemplo\n-- - Consulta - Descrição detalhada\n\n", encoding="utf-8")

def get_model_content(tipo: str) -> str:
    path = MODELO_SQL_PATH if tipo == "SQL" else MODELO_VIEW_PATH
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

def append_to_model(tipo: str, titulo: str, descricao: str, codigo: str):
    path = MODELO_SQL_PATH if tipo == "SQL" else MODELO_VIEW_PATH
    
    nova_entrada = f"\n\n-- - Título: {titulo}\n-- - Consulta - {descricao}\n{codigo}\n"
    
    with open(path, "a", encoding="utf-8") as f:
        f.write(nova_entrada)
