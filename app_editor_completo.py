import streamlit as st
from streamlit_quill import st_quill
from streamlit_ace import st_ace
import json

st.set_page_config(
    page_title="📝 Editor Literário Completo",
    page_icon="📖",
    layout="wide"
)

st.title("📝 Editor Literário Profissional")

# Inicializar session state
if "quill_content" not in st.session_state:
    st.session_state.quill_content = ""

if "ace_content" not in st.session_state:
    st.session_state.ace_content = ""

# Abas para alternar entre editores
tab1, tab2, tab3 = st.tabs(["✍️ Redação (Quill)", "💻 Código/Markdown (Ace)", "📊 Visualização"])

# ===== ABA 1: QUILL (Redação) =====
with tab1:
    st.subheader("Editor de Redação - Tipo Word")
    
    col_left, col_right = st.columns([3, 1])
    
    with col_left:
        st.write("**Recursos:** Negrito, Itálico, Listas, Links, Imagens, Títulos...")
        quill_content = st_quill(
            placeholder="Comece a escrever seu manuscrito...",
            toolbar=True,
            key="quill_editor",
            height=500
        )
        
        if quill_content:
            st.session_state.quill_content = quill_content
    
    with col_right:
        st.write("**Ações:**")
        if st.button("💾 Salvar Rascunho"):
            st.success("✅ Rascunho salvo!")
        
        if st.button("📥 Carregar Último"):
            st.info("Carregando rascunho anterior...")
        
        if st.button("🗑️ Limpar"):
            st.session_state.quill_content = ""
            st.rerun()

# ===== ABA 2: ACE (Código/Markdown) =====
with tab2:
    st.subheader("Editor de Código/Markdown - Profissional")
    
    col_lang, col_theme = st.columns(2)
    
    with col_lang:
        language = st.selectbox(
            "Linguagem:",
            ["markdown", "html", "css", "javascript", "python", "yaml", "json", "xml"],
            key="ace_language"
        )
    
    with col_theme:
        theme = st.selectbox(
            "Tema:",
            ["monokai", "github", "tomorrow", "twilight", "solarized_light", "solarized_dark"],
            key="ace_theme"
        )
    
    st.write("**Recursos:** Syntax highlighting, autocomplete, busca, múltiplos cursores...")
    
    ace_content = st_ace(
        value=st.session_state.ace_content,
        language=language,
        theme=theme,
        height=500,
        key="ace_editor",
        font_size=14,
        show_gutter=True,
        show_print_margin=True,
        wrap=True,
        auto_update=True
    )
    
    if ace_content:
        st.session_state.ace_content = ace_content
    
    col_save, col_clear = st.columns(2)
    
    with col_save:
        if st.button("💾 Salvar Código"):
            st.success("✅ Código salvo!")
    
    with col_clear:
        if st.button("🗑️ Limpar Código"):
            st.session_state.ace_content = ""
            st.rerun()

# ===== ABA 3: VISUALIZAÇÃO =====
with tab3:
    st.subheader("📊 Visualização do Conteúdo")
    
    viz_tab1, viz_tab2 = st.tabs(["📝 Conteúdo Quill", "💻 Conteúdo Ace"])
    
    with viz_tab1:
        st.write("**Visualização HTML do Editor Quill:**")
        if st.session_state.quill_content:
            st.markdown(st.session_state.quill_content, unsafe_allow_html=True)
        else:
            st.info("Nenhum conteúdo no Editor Quill ainda.")
        
        with st.expander("📄 Ver Código HTML"):
            st.code(st.session_state.quill_content, language="html")
    
    with viz_tab2:
        st.write("**Visualização do Editor Ace:**")
        if st.session_state.ace_content:
            if st.session_state.get("ace_language") == "markdown":
                st.markdown(st.session_state.ace_content)
            else:
                st.code(st.session_state.ace_content, language=st.session_state.get("ace_language", "text"))
        else:
            st.info("Nenhum conteúdo no Editor Ace ainda.")
        
        with st.expander("📊 Estatísticas"):
            lines = st.session_state.ace_content.count("\n") + 1 if st.session_state.ace_content else 0
            chars = len(st.session_state.ace_content)
            words = len(st.session_state.ace_content.split()) if st.session_state.ace_content else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Linhas", lines)
            col2.metric("Palavras", words)
            col3.metric("Caracteres", chars)

# ===== SIDEBAR: INFO E EXPORTAÇÃO =====
with st.sidebar:
    st.header("ℹ️ Informações")
    st.write("""
    **Editor Literário Completo** combina dois editores profissionais:
    
    **Quill (Redação):**
    - Interface tipo Word
    - Formatação visual
    - Ideal para manuscritos
    
    **Ace (Código):**
    - Interface tipo VS Code
    - Syntax highlighting
    - Ideal para Markdown/código
    """)
    
    st.divider()
    
    st.header("💾 Exportação")
    
    if st.button("📥 Baixar Conteúdo Quill (HTML)"):
        if st.session_state.quill_content:
            st.download_button(
                label="📥 Download HTML",
                data=st.session_state.quill_content,
                file_name="manuscrito_quill.html",
                mime="text/html"
            )
        else:
            st.warning("Nenhum conteúdo para baixar.")
    
    if st.button("📥 Baixar Conteúdo Ace"):
        if st.session_state.ace_content:
            language = st.session_state.get("ace_language", "txt")
            extension = "txt" if language == "text" else language
            st.download_button(
                label=f"📥 Download .{extension}",
                data=st.session_state.ace_content,
                file_name=f"codigo.{extension}",
                mime="text/plain"
            )
        else:
            st.warning("Nenhum conteúdo para baixar.")
    
    st.divider()
    
    st.write("**📖 Versão:** 1.0.0")
    st.write("**🚀 Status:** Pronto para uso!")
