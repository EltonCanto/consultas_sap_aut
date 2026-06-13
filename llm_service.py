import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from kb_manager import get_business_rules

load_dotenv()

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "sua_chave_api_aqui":
        raise ValueError("Chave API do Gemini não configurada.")
    return genai.Client(api_key=api_key)

def generate_sap_code(user_prompt: str, tipo: str, contexto_modelos: str, chat_history: list = None) -> str:
    """
    Gera código SQL ou View para SAP B1 usando Gemini com Google Search Grounding.
    """
    client = get_client()
    model_name = 'gemini-2.5-flash' # atualizado para modelo disponível no plano gratuito
    regras_negocio = get_business_rules()
    
    system_instruction = f"""Você é um especialista em SAP Business One (SAP B1).
Sua tarefa é gerar ou melhorar um código de {tipo} baseado no pedido do usuário.

REGRAS GLOBAIS DE NEGÓCIO:
{regras_negocio}

REGRAS DE CONTEXTO E GERAÇÃO:
1. Analise o seguinte contexto (modelos fornecidos pelo usuário) e tente basear sua resposta nas estruturas, nomes de tabelas (ex: OINV, INV1, OCRD, etc) e padrões presentes lá:
--- INÍCIO DOS MODELOS ---
{contexto_modelos}
--- FIM DOS MODELOS ---

2. Se a informação não estiver clara nos modelos, você deve usar a ferramenta de Pesquisa no Google para buscar na documentação oficial do SAP B1.
3. Use o padrão exigido: "- Título: ??? - Consulta - Descrição" no topo do seu código como comentário (ex: -- - Título: ...).
4. Retorne APENAS o código SQL ou a View (sem marcações markdown como ```sql fora do padrão, se possível, ou retorne apenas o bloco markdown). Mas como o Streamlit lida bem com markdown, você deve explicar brevemente e fornecer o código em um bloco ```sql ... ```.
5. Sempre inclua uma sugestão de TÍTULO e DESCRIÇÃO no início do bloco de código como comentários.
"""

    contents = []
    
    # Adicionar histórico se existir
    if chat_history:
        for msg in chat_history:
            role = 'user' if msg['role'] == 'user' else 'model'
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg['content'])]))
            
    # Adicionar o prompt atual
    contents.append(types.Content(role='user', parts=[types.Part.from_text(text=user_prompt)]))

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )

    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=config
    )
    
    return response.text

def extract_code_and_metadata(response_text: str):
    """
    Tenta extrair o código SQL/View, título e descrição da resposta do Gemini.
    """
    # Lógica simplificada: extrair o que está dentro do bloco ```sql ... ```
    import re
    code_match = re.search(r'```sql\n(.*?)\n```', response_text, re.DOTALL)
    
    if code_match:
        codigo = code_match.group(1).strip()
    else:
        # Se não usar markdown, pegar o texto todo (limpando o possível começo)
        codigo = response_text.replace("```sql", "").replace("```", "").strip()

    titulo = "Consulta Gerada"
    descricao = "Gerada por IA"
    
    # Tenta encontrar o padrão exigido
    padrao = re.search(r'T[ií]tulo:\s*([^\n]+).*?Consulta\s*-\s*([^\n]+)', codigo, re.IGNORECASE | re.DOTALL)
    if padrao:
        titulo = padrao.group(1).strip()
        descricao = padrao.group(2).strip()

    return titulo, descricao, codigo
