import os
import sys

# Adiciona o diretório pai ao path para importar llm_service
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm_service import generate_sap_code

def main():
    print("Testando OpenRouter API...")
    
    # Prompt simples para teste
    prompt = "Crie uma consulta simples para trazer as notas fiscais de saída (tabela OINV)."
    tipo = "SQL"
    contexto = ""
    
    try:
        resultado = generate_sap_code(
            user_prompt=prompt,
            tipo=tipo,
            contexto_modelos=contexto,
            provider="OpenRouter"
        )
        print("\n--- Resultado com Sucesso ---\n")
        print(resultado)
    except Exception as e:
        print(f"\n[ERRO] Falha ao testar OpenRouter: {e}")

if __name__ == "__main__":
    main()
