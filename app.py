import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from database import init_db
from kb_manager import init_kb
from ui_utils import render_sidebar_docs
import os

# Configuração da página principal
st.set_page_config(
    page_title="Consulta SAP AI",
    page_icon="icon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Banco de Dados e Base de Conhecimento
init_db()
init_kb()

# Autenticação
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Tela de Login
try:
    authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state["authentication_status"]:
    # Sidebar
    with st.sidebar:
        st.write(f'Bem-vindo *{st.session_state["name"]}*')
        authenticator.logout('Sair', 'sidebar')
        st.divider()
        st.markdown("### Navegação")
        st.page_link("app.py", label="Início", icon="🏠")
        st.page_link("pages/1_Gerador.py", label="Gerador IA", icon="✨")
        st.page_link("pages/2_Historico.py", label="Histórico", icon="📚")
        
        render_sidebar_docs()
        
    # Conteúdo Principal (Home)
    st.title("🤖 Consulta SAP B1 com Inteligência Artificial")
    st.markdown("""
    Bem-vindo ao gerador de Consultas SQL e Views para SAP Business One.
    
    Esta ferramenta utiliza o Google Gemini com acesso à internet para ler documentações oficiais do SAP e sua Base de Conhecimento pessoal para criar códigos precisos.
    
    👈 **Use o menu lateral para acessar o Gerador ou o Histórico.**
    """)
    
elif st.session_state["authentication_status"] is False:
    st.error('Usuário/senha is incorreto')
elif st.session_state["authentication_status"] is None:
    st.warning('Por favor, insira seu usuário e senha')

