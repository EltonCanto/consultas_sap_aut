import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from kb_manager import get_business_rules
import re

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
1. PRIORIDADE MÁXIMA: As "REGRAS GLOBAIS DE NEGÓCIO" têm precedência absoluta. Caso haja alguma divergência entre as regras e os modelos fornecidos (como IDs de filiais), siga SEMPRE as regras globais de negócio.
2. Analise o seguinte contexto (modelos fornecidos pelo usuário) e tente basear sua resposta nas estruturas, nomes de tabelas (ex: OINV, INV1, OCRD, etc) e padrões presentes lá:
--- INÍCIO DOS MODELOS ---
{contexto_modelos}
--- FIM DOS MODELOS ---

3. Se a informação não estiver clara nos modelos, você deve usar a ferramenta de Pesquisa no Google para buscar na documentação oficial do SAP B1.
4. Use o padrão exigido: "-- Título: ??? - Consulta - Descrição" no topo do seu código como comentário.
5. REGRAS DE ESTRUTURA DO CÓDIGO (CRÍTICO):
   - Se for gerar uma Consulta SQL, forneça apenas o comando SELECT.
   - Se for gerar uma View, É EXPRESSAMENTE PROIBIDO utilizar o comando `CREATE VIEW ... AS`. A sua resposta DEVE seguir fielmente o padrão dos exemplos: contendo OBRIGATORIAMENTE a tabela Markdown de "Configuração de coluna" dentro de um bloco de comentários `/* ... */`, seguida imediatamente pela instrução SELECT (sem nenhum CREATE VIEW).
6. IMPORTANTE: Você DEVE retornar o código final SEMPRE dentro de um bloco markdown de código (```sql ... ```). Forneça uma breve explicação antes do bloco de código se necessário.
7. Sempre inclua uma sugestão de TÍTULO e DESCRIÇÃO no início do bloco de código como comentários.
8. Ao final da sua resposta, OBRIGATORIAMENTE adicione um bloco listando as tabelas e as regras de negócio utilizadas, envolvido pelas tags <AUDITORIA> e </AUDITORIA>. Para as tabelas, informe um texto curto com a sua função (ex: OPOR_Pedido_Compra). Exemplo:
<AUDITORIA>
**Tabelas Utilizadas:** OINV_Nota_Fiscal_Saida, INV1_Linhas_da_Nota, OCRD_Parceiro_de_Negocios
**Regras Aplicadas:** [SEGURANÇA READ-ONLY], [REGRA_FILIAL_TERESOPOLIS]
</AUDITORIA>
"""

    contents = []
    
    # Adicionar histórico se existir
    if chat_history:
        for msg in chat_history:
            role = 'user' if msg['role'] == 'user' else 'model'
            # Evitar enviar tags de auditoria no histórico se houver
            clean_content = re.sub(r'<AUDITORIA>.*?</AUDITORIA>', '', msg['content'], flags=re.DOTALL | re.IGNORECASE)
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=clean_content)]))
            
    # Adicionar o prompt atual
    contents.append(types.Content(role='user', parts=[types.Part.from_text(text=user_prompt)]))

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )

    import time
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if ("429" in error_msg or "503" in error_msg) and attempt < 2:
                time.sleep(35) # Espera 35 segundos para a cota ser resetada ou aliviar a demanda
            else:
                raise e

def extract_code_and_metadata(response_text: str):
    """
    Tenta extrair o código SQL/View, título, descrição e bloco de auditoria da resposta do Gemini.
    """
    import re
    
    # Extrai auditoria e limpa a resposta
    auditoria = ""
    auditoria_match = re.search(r'<AUDITORIA>(.*?)</AUDITORIA>', response_text, re.DOTALL | re.IGNORECASE)
    if auditoria_match:
        auditoria = auditoria_match.group(1).strip()
    
    resposta_limpa = re.sub(r'<AUDITORIA>.*?</AUDITORIA>', '', response_text, flags=re.DOTALL | re.IGNORECASE).strip()

    # Extrai o código
    code_match = re.search(r'```(?:sql)?\s*\n?(.*?)```', resposta_limpa, re.DOTALL | re.IGNORECASE)
    if code_match:
        codigo = code_match.group(1).strip()
    else:
        codigo = resposta_limpa.replace("```sql", "").replace("```", "").strip()
        # Fallback: garante que a resposta tenha a formatação markdown para exibição correta no Streamlit
        resposta_limpa = f"```sql\n{codigo}\n```"

    titulo = "Consulta Gerada"
    descricao = "Gerada por IA"
    
    # Tenta encontrar o padrão exigido
    padrao = re.search(r'T[ií]tulo:\s*([^\n]+).*?Consulta\s*-\s*([^\n]+)', codigo, re.IGNORECASE | re.DOTALL)
    if padrao:
        titulo = padrao.group(1).strip()
        descricao = padrao.group(2).strip()

    return titulo, descricao, codigo, auditoria, resposta_limpa
