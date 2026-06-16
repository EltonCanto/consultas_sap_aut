import os
import re
from pathlib import Path

KB_DIR = Path("knowledge_base")
MODELO_SQL_PATH = KB_DIR / "modelo_sql.txt"
MODELO_VIEW_PATH = KB_DIR / "modelo_view.txt"
REGRAS_NEGOCIO_PATH = KB_DIR / "regras_negocio.txt"

def get_business_rules() -> str:
    if REGRAS_NEGOCIO_PATH.exists():
        return REGRAS_NEGOCIO_PATH.read_text(encoding="utf-8")
    return ""

def init_kb():
    os.makedirs(KB_DIR, exist_ok=True)
    if not MODELO_SQL_PATH.exists():
        MODELO_SQL_PATH.write_text("-- Colecione suas consultas SQL aqui.\n-- Formato:\n-- - Título: Exemplo\n-- - Consulta - Descrição detalhada\n\n", encoding="utf-8")
    if not MODELO_VIEW_PATH.exists():
        MODELO_VIEW_PATH.write_text("-- Colecione suas Views aqui.\n-- Formato:\n-- - Título: Exemplo\n-- - Consulta - Descrição detalhada\n\n", encoding="utf-8")

def get_model_content(tipo: str, user_prompt: str = "") -> str:
    path = MODELO_SQL_PATH if tipo == "SQL" else MODELO_VIEW_PATH
    if not path.exists():
        return ""
        
    content = path.read_text(encoding="utf-8")
    if not user_prompt:
        return content

    # Separar os modelos (assumindo formato padrão iniciado por "-- - Título:")
    parts = re.split(r'(?=\n-- - Título:)', '\n' + content)
    
    header = parts[0].strip() if parts and not '-- - Título:' in parts[0] else ""
    models = [p.strip() for p in parts if '-- - Título:' in p]
    
    if not models:
        return content

    if len(models) <= 2:
        return content

    # Mini-RAG: similaridade simples baseada em intersecção de palavras (removendo stop words muito comuns ajudaria, mas simples interseção funciona para jargões)
    prompt_words = set(re.findall(r'\w+', user_prompt.lower()))
    # Remover palavras muito comuns que causam falso positivo (opcional, básico)
    stop_words = {'de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua'}
    prompt_words = prompt_words - stop_words
    
    scored_models = []
    for m in models:
        # Extrair título e descrição para focar a busca neles
        title_desc_match = re.search(r'-- - Título:\s*(.*?)\n-- - Consulta -\s*(.*?)\n', m, re.IGNORECASE)
        m_text = m
        if title_desc_match:
            m_text = title_desc_match.group(1) + " " + title_desc_match.group(2)
            
        m_words = set(re.findall(r'\w+', m_text.lower()))
        score = len(prompt_words.intersection(m_words))
        scored_models.append((score, m))
    
    # Ordenar por score decrescente
    scored_models.sort(key=lambda x: x[0], reverse=True)
    
    # Se os maiores scores forem 0 (nenhuma similaridade), pegamos os 2 últimos adicionados
    if scored_models[0][0] == 0:
        top_2 = models[-2:]
    else:
        # Pegar os 2 primeiros
        top_2 = [sm[1] for sm in scored_models[:2]]
        
    final_content = header + "\n\n" + "\n\n".join(top_2)
    return final_content.strip()

def append_to_model(tipo: str, titulo: str, descricao: str, codigo: str):
    path = MODELO_SQL_PATH if tipo == "SQL" else MODELO_VIEW_PATH
    
    nova_entrada = f"\n\n-- - Título: {titulo}\n-- - Consulta - {descricao}\n{codigo}\n"
    
    with open(path, "a", encoding="utf-8") as f:
        f.write(nova_entrada)
