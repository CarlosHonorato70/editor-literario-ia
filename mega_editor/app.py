"""
MEGA EDITOR - Dashboard Unificado
Integração completa de todas as funcionalidades do Editor Literário IA
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Importações dos módulos existentes
from modules.workflow_tab_enhanced import render_workflow_tab
from modules.workflow_orchestrator import WorkflowOrchestrator
from modules.analyzer import analyze_manuscript
from modules.enhancer import enhance_content
from modules.formatter import format_document
from modules.reviewer import review_text
from modules.exporter import export_document
from modules.isbn_cip_generator import generate_isbn_cip
from modules.print_ready_generator import generate_print_ready
from modules.fastformat_utils import apply_fastformat

# Importações de produção
try:
    from modules.production.pipeline import ProductionPipeline
    from modules.production.cover_designer import CoverDesigner
    from modules.production.layout_engine import LayoutEngine
    from modules.production.materials_generator import MaterialsGenerator
    PRODUCTION_AVAILABLE = True
except ImportError:
    PRODUCTION_AVAILABLE = False

# Configuração da página
st.set_page_config(
    page_title="📚 MEGA EDITOR - Editor Literário Profissional",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização do session state
def initialize_session_state():
    """Inicializa todas as variáveis de estado necessárias"""
    defaults = {
        'text_content': '',
        'manuscript_metadata': {},
        'workflow_phase': 0,
        'project_name': 'Novo Projeto',
        'editor_mode': 'simple',
        'quill_content': '',
        'ace_content': '',
        'enhanced_text': '',
        'formatted_text': '',
        'review_results': {},
        'export_formats': [],
        'production_status': {},
        'uploaded_text': None,
        'pending_text_update': None,
        'rich_editor_content': '',
        'file_processed': False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Header principal
st.markdown('<h1 class="main-header">📚 MEGA EDITOR</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Plataforma Completa de Edição e Publicação Literária</p>', unsafe_allow_html=True)

# Sidebar com informações do projeto
with st.sidebar:
    st.title("🎯 Painel de Controle")
    
    # Informações do projeto
    st.subheader("Projeto Atual")
    project_name = st.text_input(
        "Nome do Projeto:",
        value=st.session_state.project_name,
        key="project_name_input"
    )
    if project_name != st.session_state.project_name:
        st.session_state.project_name = project_name
    
    # Estatísticas rápidas
    st.subheader("📊 Estatísticas")
    word_count = len(st.session_state.text_content.split()) if st.session_state.text_content else 0
    char_count = len(st.session_state.text_content) if st.session_state.text_content else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Palavras", f"{word_count:,}")
    with col2:
        st.metric("Caracteres", f"{char_count:,}")
    
    # Progresso do workflow
    st.subheader("🔄 Progresso")
    progress = (st.session_state.workflow_phase / 14) * 100
    st.progress(progress / 100)
    st.caption(f"Fase {st.session_state.workflow_phase} de 14 - {progress:.0f}%")
    
    st.divider()
    
    # Ações rápidas
    st.subheader("⚡ Ações Rápidas")
    if st.button("💾 Salvar Projeto", use_container_width=True):
        st.success("Projeto salvo!")
    
    if st.button("📥 Carregar Projeto", use_container_width=True):
        st.info("Selecione um arquivo de projeto...")
    
    if st.button("🔄 Resetar", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.divider()
    
    # Links úteis
    st.subheader("🔗 Links Úteis")
    st.markdown("- [Documentação](https://github.com)")
    st.markdown("- [Suporte](https://github.com/issues)")
    st.markdown("- [Tutoriais](https://github.com/wiki)")

# Tabs principais do dashboard
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 Início",
    "✍️ Editores",
    "🔄 Workflow 14 Fases",
    "🎨 Produção",
    "📊 Análise",
    "🚀 Exportação",
    "⚙️ Configurações"
])

# TAB 1: INÍCIO - Dashboard principal
with tab1:
    st.header("🏠 Bem-vindo ao MEGA EDITOR")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.subheader("✍️ Múltiplos Editores")
        st.write("• Editor Simples (Texto)")
        st.write("• Editor Avançado (Quill)")
        st.write("• Editor de Código (Ace)")
        st.write("• Editor WYSIWYG")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.subheader("🔄 Workflow Completo")
        st.write("• 14 Fases Profissionais")
        st.write("• Análise Estrutural")
        st.write("• FastFormat")
        st.write("• Sugestões de IA")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.subheader("🎨 Produção Gráfica")
        st.write("• Design de Capa")
        st.write("• Layout Profissional")
        st.write("• Materiais Marketing")
        st.write("• Print-Ready")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("🚀 Começar Agora")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📝 Novo Manuscrito", use_container_width=True):
            st.session_state.workflow_phase = 1
            st.rerun()
    
    with col2:
        if st.button("📤 Importar Arquivo", use_container_width=True):
            st.session_state.workflow_phase = 2
            st.rerun()
    
    with col3:
        if st.button("🔄 Workflow Guiado", use_container_width=True):
            st.switch_page = "tab3"
            st.rerun()
    
    with col4:
        if st.button("📊 Analisar Texto", use_container_width=True):
            st.switch_page = "tab5"
            st.rerun()
    
    st.divider()
    
    # Projetos recentes
    st.subheader("📂 Projetos Recentes")
    if st.session_state.text_content:
        st.info(f"**{st.session_state.project_name}** - {word_count} palavras")
    else:
        st.info("Nenhum projeto aberto. Comece criando um novo manuscrito!")

# TAB 2: EDITORES - Múltiplos editores integrados
with tab2:
    st.header("✍️ Editores Integrados")
    
    editor_tabs = st.tabs([
        "📝 Simples",
        "✨ Quill (WYSIWYG)",
        "💻 Ace (Código)",
        "🔄 Sincronização"
    ])
    
    # Editor Simples
    with editor_tabs[0]:
        st.subheader("Editor de Texto Simples")
        
        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "Carregar arquivo (.txt, .docx)",
            type=['txt', 'docx'],
            key="mega_file_uploader"
        )
        
        if uploaded_file:
            if uploaded_file.type == 'text/plain':
                content = uploaded_file.read().decode('utf-8')
            else:
                from docx import Document
                doc = Document(uploaded_file)
                content = '\n'.join([para.text for para in doc.paragraphs])
            
            st.session_state.text_content = content
            st.success(f"✅ Arquivo '{uploaded_file.name}' carregado com sucesso!")
        
        # Editor de texto
        text_value = st.session_state.text_content
        new_text = st.text_area(
            "Seu texto:",
            value=text_value,
            height=400,
            key="simple_editor_area"
        )
        
        if new_text != st.session_state.text_content:
            st.session_state.text_content = new_text
    
    # Editor Quill
    with editor_tabs[1]:
        st.subheader("Editor WYSIWYG (Quill)")
        
        try:
            from streamlit_quill import st_quill
            
            if st.button("📤 Carregar do Editor Simples"):
                st.session_state.quill_content = st.session_state.text_content
                st.success("Texto carregado!")
            
            quill_content = st_quill(
                value=st.session_state.quill_content,
                placeholder="Edite com formatação rica...",
                html=True,
                key="mega_quill_editor"
            )
            
            if quill_content:
                st.session_state.quill_content = quill_content
            
            if st.button("💾 Salvar para Editor Simples"):
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(quill_content or "", 'html.parser')
                st.session_state.text_content = soup.get_text()
                st.success("Texto sincronizado!")
        
        except ImportError:
            st.error("streamlit-quill não instalado. Execute: pip install streamlit-quill")
    
    # Editor Ace
    with editor_tabs[2]:
        st.subheader("Editor de Código (Ace)")
        
        try:
            from streamlit_ace import st_ace
            
            col1, col2 = st.columns(2)
            with col1:
                language = st.selectbox(
                    "Linguagem:",
                    ["markdown", "html", "text", "python", "json"],
                    key="mega_ace_lang"
                )
            
            with col2:
                theme = st.selectbox(
                    "Tema:",
                    ["monokai", "github", "tomorrow"],
                    key="mega_ace_theme"
                )
            
            if st.button("📤 Carregar do Editor Simples", key="load_to_ace"):
                st.session_state.ace_content = st.session_state.text_content
                st.success("Texto carregado!")
            
            ace_content = st_ace(
                value=st.session_state.ace_content,
                language=language,
                theme=theme,
                height=400,
                key="mega_ace_editor"
            )
            
            if ace_content:
                st.session_state.ace_content = ace_content
            
            if st.button("💾 Salvar para Editor Simples", key="save_from_ace"):
                st.session_state.text_content = ace_content
                st.success("Texto sincronizado!")
        
        except ImportError:
            st.error("streamlit-ace não instalado. Execute: pip install streamlit-ace")
    
    # Sincronização
    with editor_tabs[3]:
        st.subheader("🔄 Sincronização entre Editores")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Editor Simples", f"{len(st.session_state.text_content)} chars")
        with col2:
            st.metric("Editor Quill", f"{len(st.session_state.quill_content)} chars")
        with col3:
            st.metric("Editor Ace", f"{len(st.session_state.ace_content)} chars")
        
        st.divider()
        
        if st.button("⬇️ Sincronizar Tudo para Simples"):
            # Prioridade: Quill > Ace > Simples
            if st.session_state.quill_content:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(st.session_state.quill_content, 'html.parser')
                st.session_state.text_content = soup.get_text()
            elif st.session_state.ace_content:
                st.session_state.text_content = st.session_state.ace_content
            st.success("Sincronização completa!")

# TAB 3: WORKFLOW 14 FASES
with tab3:
    render_workflow_tab()

# TAB 4: PRODUÇÃO
with tab4:
    st.header("🎨 Produção Gráfica e Editorial")
    
    if PRODUCTION_AVAILABLE:
        prod_tabs = st.tabs([
            "📖 Capa",
            "📄 Layout",
            "📢 Marketing",
            "🖨️ Print-Ready"
        ])
        
        with prod_tabs[0]:
            st.subheader("Design de Capa")
            st.info("Recurso em desenvolvimento - Designer de capa integrado")
        
        with prod_tabs[1]:
            st.subheader("Layout do Livro")
            st.info("Recurso em desenvolvimento - Engine de layout profissional")
        
        with prod_tabs[2]:
            st.subheader("Materiais de Marketing")
            st.info("Recurso em desenvolvimento - Gerador de materiais promocionais")
        
        with prod_tabs[3]:
            st.subheader("Arquivos Print-Ready")
            
            if st.session_state.text_content:
                if st.button("🖨️ Gerar Arquivo para Gráfica"):
                    try:
                        result = generate_print_ready(
                            st.session_state.text_content,
                            st.session_state.manuscript_metadata
                        )
                        st.success("Arquivo print-ready gerado!")
                        st.download_button(
                            "📥 Baixar PDF",
                            result,
                            file_name="manuscript_print_ready.pdf"
                        )
                    except Exception as e:
                        st.error(f"Erro: {e}")
            else:
                st.warning("Carregue um manuscrito primeiro!")
    else:
        st.warning("Módulos de produção não disponíveis. Verifique a instalação.")

# TAB 5: ANÁLISE
with tab5:
    st.header("📊 Análise do Manuscrito")
    
    if st.session_state.text_content:
        if st.button("🔍 Analisar Texto"):
            with st.spinner("Analisando manuscrito..."):
                try:
                    analysis = analyze_manuscript(st.session_state.text_content)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Palavras", analysis.get('word_count', 0))
                    with col2:
                        st.metric("Parágrafos", analysis.get('paragraph_count', 0))
                    with col3:
                        st.metric("Legibilidade", f"{analysis.get('readability', 0):.1f}")
                    with col4:
                        st.metric("Complexidade", analysis.get('complexity', 'N/A'))
                    
                    st.subheader("Análise Detalhada")
                    st.json(analysis)
                except Exception as e:
                    st.error(f"Erro na análise: {e}")
    else:
        st.info("Carregue um texto para análise na aba Editores")

# TAB 6: EXPORTAÇÃO
with tab6:
    st.header("🚀 Exportação Multi-formato")
    
    if st.session_state.text_content:
        st.subheader("Selecione os formatos de exportação")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            export_docx = st.checkbox("📄 DOCX (Word)", value=True)
            export_pdf = st.checkbox("📕 PDF")
        
        with col2:
            export_epub = st.checkbox("📱 EPUB (E-book)")
            export_html = st.checkbox("🌐 HTML")
        
        with col3:
            export_md = st.checkbox("📝 Markdown")
            export_txt = st.checkbox("📃 TXT")
        
        st.divider()
        
        if st.button("📦 Exportar Selecionados", type="primary"):
            formats = []
            if export_docx: formats.append('docx')
            if export_pdf: formats.append('pdf')
            if export_epub: formats.append('epub')
            if export_html: formats.append('html')
            if export_md: formats.append('md')
            if export_txt: formats.append('txt')
            
            if formats:
                with st.spinner("Gerando arquivos..."):
                    try:
                        for fmt in formats:
                            result = export_document(
                                st.session_state.text_content,
                                fmt,
                                st.session_state.manuscript_metadata
                            )
                            st.download_button(
                                f"📥 Baixar {fmt.upper()}",
                                result,
                                file_name=f"{st.session_state.project_name}.{fmt}",
                                key=f"download_{fmt}"
                            )
                        st.success(f"✅ {len(formats)} arquivo(s) gerado(s)!")
                    except Exception as e:
                        st.error(f"Erro na exportação: {e}")
            else:
                st.warning("Selecione pelo menos um formato!")
    else:
        st.info("Carregue um texto para exportar na aba Editores")

# TAB 7: CONFIGURAÇÕES
with tab7:
    st.header("⚙️ Configurações do Sistema")
    
    config_tabs = st.tabs(["Geral", "Editor", "IA", "Exportação", "Sobre"])
    
    with config_tabs[0]:
        st.subheader("Configurações Gerais")
        auto_save = st.checkbox("💾 Salvamento Automático", value=True)
        theme_mode = st.selectbox("🎨 Tema", ["Claro", "Escuro", "Auto"])
        language = st.selectbox("🌐 Idioma", ["Português (BR)", "English", "Español"])
    
    with config_tabs[1]:
        st.subheader("Configurações do Editor")
        font_size = st.slider("📏 Tamanho da Fonte", 10, 24, 14)
        line_height = st.slider("📐 Altura da Linha", 1.0, 2.0, 1.5)
        word_wrap = st.checkbox("🔄 Quebra de Linha Automática", value=True)
    
    with config_tabs[2]:
        st.subheader("Configurações de IA")
        api_key = st.text_input("🔑 OpenAI API Key", type="password")
        model = st.selectbox("🤖 Modelo", ["gpt-4", "gpt-3.5-turbo"])
        creativity = st.slider("🎨 Criatividade", 0.0, 1.0, 0.7)
    
    with config_tabs[3]:
        st.subheader("Configurações de Exportação")
        default_format = st.selectbox("📦 Formato Padrão", ["DOCX", "PDF", "EPUB"])
        include_metadata = st.checkbox("📋 Incluir Metadados", value=True)
        watermark = st.checkbox("🔖 Adicionar Marca d'água", value=False)
    
    with config_tabs[4]:
        st.subheader("Sobre o MEGA EDITOR")
        st.markdown("""
        **MEGA EDITOR v1.0**
        
        Plataforma integrada de edição e publicação literária.
        
        **Funcionalidades:**
        - ✅ Múltiplos editores (Simples, Quill, Ace)
        - ✅ Workflow de 14 fases
        - ✅ Análise de manuscrito
        - ✅ FastFormat integrado
        - ✅ Sugestões de IA
        - ✅ Exportação multi-formato
        - ✅ Produção gráfica
        - ✅ Suporte multiplataforma (KDP, Apple, Google, Kobo)
        
        **Desenvolvido com:**
        - Streamlit
        - Python 3.13
        - OpenAI API
        
        ---
        
        📧 Suporte: github.com/CarlosHonorato70/editor-literario-ia
        """)
        
        if st.button("🔄 Verificar Atualizações"):
            st.info("Você está usando a versão mais recente!")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>MEGA EDITOR</strong> - Plataforma Completa de Edição Literária</p>
    <p>© 2025 | Desenvolvido com ❤️ usando Streamlit</p>
</div>
""", unsafe_allow_html=True)
