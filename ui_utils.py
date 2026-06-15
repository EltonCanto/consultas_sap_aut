import streamlit.components.v1 as components
import html

def add_custom_copy_button(text_to_copy: str, button_text: str = "Copiar Código"):
    """
    Renderiza um botão de cópia customizado que funciona mesmo sem HTTPS (rede local).
    O botão nativo do Streamlit falha quando não está em localhost ou HTTPS.
    """
    escaped_text = html.escape(text_to_copy).replace("\n", "&#10;")
    
    custom_css = """
    <style>
        .copy-btn {
            background-color: transparent;
            color: inherit;
            border: 1px solid #4b4b57;
            padding: 0.4rem 0.8rem;
            border-radius: 0.4rem;
            cursor: pointer;
            font-family: inherit;
            font-size: 14px;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
        }
        .copy-btn:hover {
            border-color: #ff4b4b;
            color: #ff4b4b;
        }
    </style>
    """
    
    js_code = """
    <script>
    function fallbackCopyTextToClipboard(text) {
      var textArea = document.createElement("textarea");
      textArea.value = text;
      
      // Prevent scrolling
      textArea.style.top = "0";
      textArea.style.left = "0";
      textArea.style.position = "fixed";
      
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      try {
        var successful = document.execCommand('copy');
        if(successful) {
            updateButtonState();
        }
      } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
      }
      document.body.removeChild(textArea);
    }

    function updateButtonState() {
        const btn = document.getElementById('copy-btn-id');
        const originalText = btn.innerHTML;
        btn.innerHTML = '✅ Copiado!';
        btn.style.borderColor = '#00cc66';
        btn.style.color = '#00cc66';
        setTimeout(() => { 
            btn.innerHTML = originalText;
            btn.style.borderColor = '#4b4b57';
            btn.style.color = 'inherit';
        }, 2000);
    }

    function copyText() {
        const textArea = document.getElementById('text-to-copy');
        // Decode HTML entities backwards
        const text = textArea.value;
        
        if (!navigator.clipboard) {
            fallbackCopyTextToClipboard(text);
            return;
        }
        navigator.clipboard.writeText(text).then(function() {
            updateButtonState();
        }, function(err) {
            console.error('Async: Could not copy text: ', err);
            fallbackCopyTextToClipboard(text);
        });
    }
    </script>
    """
    
    html_code = f"""
    {custom_css}
    <textarea id="text-to-copy" style="display:none;">{escaped_text}</textarea>
    <button id="copy-btn-id" class="copy-btn" onclick="copyText()">📋 {button_text}</button>
    {js_code}
    """
    
    components.html(html_code, height=45)

def render_sidebar_docs():
    import streamlit as st
    import os
    
    st.sidebar.divider()
    st.sidebar.markdown("### 📄 Documentação")
    
    docs_dir = "Docs" if os.path.exists("Docs") else "docs"
    
    if os.path.exists(docs_dir):
        files = [f for f in os.listdir(docs_dir) if f.endswith('.pdf')]
        if not files:
            st.sidebar.info("Nenhum documento PDF encontrado na pasta 'docs'.")
        else:
            for file in files:
                file_path = os.path.join(docs_dir, file)
                with open(file_path, "rb") as f:
                    pdf_bytes = f.read()
                st.sidebar.download_button(
                    label=f"Baixar {file}",
                    data=pdf_bytes,
                    file_name=file,
                    mime="application/pdf"
                )
    else:
        st.sidebar.info("Pasta 'docs' não encontrada. Adicione seus PDFs nesta pasta na raiz do projeto.")
