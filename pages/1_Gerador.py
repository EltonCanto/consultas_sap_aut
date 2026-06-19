import streamlit as st
from llm_service import generate_sap_code, extract_code_and_metadata
from kb_manager import get_model_content, append_to_model
from database import save_query
from ui_utils import add_custom_copy_button, render_sidebar_docs

# Verifica autenticação antes de mostrar conteúdo
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("Por favor, faça login na página inicial.")
    st.stop()

st.title("✨ Gerador de Consultas e Views")

# Exibe documentação na sidebar
render_sidebar_docs()

def clear_state():
    if "messages" in st.session_state:
        st.session_state.messages = []
    for key in ['last_code', 'last_title', 'last_desc', 'last_type', 'last_auditoria']:
        if key in st.session_state:
            del st.session_state[key]
    if "show_save_form" in st.session_state:
        st.session_state["show_save_form"] = False

# Configurações de Geração
col_cfg1, col_cfg2 = st.columns(2)
with col_cfg1:
    tipo = st.radio("O que você deseja gerar?", ["SQL", "View"], horizontal=True, on_change=clear_state)
with col_cfg2:
    provider = st.radio("Escolha a Inteligência Artificial:", ["Gemini (Padrão)", "OpenRouter"], horizontal=True)
st.divider()

# Histórico da conversa
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens anteriores
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input do usuário
if prompt := st.chat_input("Descreva a consulta ou view que você precisa..."):
    # Adiciona mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Obter contexto com Mini-RAG (filtragem por similaridade do prompt)
    contexto = get_model_content(tipo, prompt)

    # Processamento
    with st.chat_message("model"):
        with st.spinner("Analisando pedido e buscando contexto (isso pode levar alguns segundos)..."):
            try:
                resposta = generate_sap_code(prompt, tipo, contexto, st.session_state.messages[:-1], provider)
                
                # Extrair código e metadados para facilitar cópia/salvamento
                titulo, descricao, codigo, auditoria, resposta_limpa = extract_code_and_metadata(resposta)
                
                st.markdown(resposta_limpa)
                st.session_state.messages.append({"role": "model", "content": resposta_limpa})
                
                # Armazenar no session_state temporário para os botões funcionarem
                st.session_state['last_code'] = codigo
                st.session_state['last_title'] = titulo
                st.session_state['last_desc'] = descricao
                st.session_state['last_type'] = tipo
                st.session_state['last_auditoria'] = auditoria
                
            except Exception as e:
                st.error(f"Erro ao gerar código: {e}")

# Opções para a última resposta gerada
if 'last_code' in st.session_state and st.session_state['last_code']:
    st.divider()
    
    if st.session_state.get('last_auditoria'):
        with st.expander("🔍 Auditoria: Tabelas e Regras de Negócio", expanded=False):
            st.info(st.session_state['last_auditoria'])
            
    st.subheader("Ações")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("💾 Salvar Consulta/View"):
            # Mostra form para confirmar/editar o salvamento
            st.session_state['show_save_form'] = True
            
    with col2:
        add_custom_copy_button(st.session_state['last_code'], "Copiar Código")

    with col3:
        st.info("Para pedir melhorias ou informar erros, basta digitar no chat acima!")

# Formulário de Salvamento
if st.session_state.get('show_save_form', False):
    with st.form("save_form"):
        st.write("Confirmar dados para salvar:")
        nome_save = st.text_input("Título", value=st.session_state['last_title'])
        desc_save = st.text_input("Descrição", value=st.session_state['last_desc'])
        add_to_kb = st.checkbox("Salvar como Modelo (Base de Conhecimento da IA)", value=False, help="Marque esta opção apenas para consultas/views relevantes que a IA deva usar como exemplo no futuro.")
        
        submitted = st.form_submit_button("Confirmar")
        if submitted:
            try:
                # Salva no DB
                save_query(nome_save, st.session_state['last_type'], st.session_state['last_code'], desc_save)
                # Salva no arquivo KB se selecionado
                if add_to_kb:
                    append_to_model(st.session_state['last_type'], nome_save, desc_save, st.session_state['last_code'])
                
                st.success(f"{st.session_state['last_type']} salva com sucesso!")
                st.session_state['show_save_form'] = False # Esconde após salvar
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
