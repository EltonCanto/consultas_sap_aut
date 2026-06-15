import streamlit as st
import pandas as pd
from database import search_queries
from ui_utils import add_custom_copy_button, render_sidebar_docs

# Verifica autenticação antes de mostrar conteúdo
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("Por favor, faça login na página inicial.")
    st.stop()

st.title("📚 Histórico de Consultas e Views Salvas")

# Exibe documentação na sidebar
render_sidebar_docs()

# Filtros de Busca
st.subheader("Filtros")
col1, col2, col3 = st.columns(3)
with col1:
    search_term = st.text_input("Buscar por nome (ou parte):")
with col2:
    start_date = st.date_input("Data inicial:", value=None)
with col3:
    end_date = st.date_input("Data final:", value=None)

# Botão de busca
if st.button("Buscar"):
    # Executar busca no banco
    resultados = search_queries(search_term, start_date, end_date)
    
    if not resultados:
        st.info("Nenhuma consulta ou view encontrada com os filtros informados.")
    else:
        st.success(f"{len(resultados)} registro(s) encontrado(s)!")
        
        # Exibir resultados de forma organizada
        for res in resultados:
            with st.expander(f"{res['tipo']} - {res['nome']} ({res['data_criacao']})"):
                if res['descricao']:
                    st.write(f"**Descrição:** {res['descricao']}")
                st.code(res['codigo'], language="sql")
                add_custom_copy_button(res['codigo'], "Copiar Código")
