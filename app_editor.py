import streamlit as st
import io
import re
import math
import language_tool_python
from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from openai import OpenAI

# Try to import streamlit_quill, show helpful error if not available
try:
    from streamlit_quill import st_quill
    RICH_EDITOR_AVAILABLE = True
except ImportError:
    RICH_EDITOR_AVAILABLE = False
    st.error("""
    ⚠️ **Editor Avançado não disponível!**
    
    O módulo `streamlit-quill` não está instalado. Para usar o Editor Avançado (Word-like), instale executando:
    
    ```bash
    pip install streamlit-quill
    ```
    
    Ou reinstale todas as dependências:
    
    ```bash
    pip install -r requirements.txt
    ```
    
    Depois, reinicie o aplicativo.
    """)

# Import FastFormat for advanced text formatting
from modules.fastformat_utils import apply_fastformat, get_ptbr_options

# --- CONFIGURAÇÃO DA PÁGINA E ESTADO ---
st.set_page_config(page_title="Adapta ONE - Editor Profissional", page_icon="✒️", layout="wide")

def inicializar_estado():
    chaves_estado = {
        "text_content": "", "file_processed": False,
        "book_title": "Sem Título", "author_name": "Autor Desconhecido", "contact_info": "seuemail@exemplo.com",
        "sugestoes_estilo": None, "api_key_valida": False,
        "use_fastformat": True,  # Enable FastFormat by default
        "pending_text_update": None,  # For handling text updates from FastFormat
        "rich_editor_content": None,  # Content from rich text editor
        "use_rich_editor": False  # Toggle for rich editor mode
    }
    for key, value in chaves_estado.items():
        if key not in st.session_state:
            st.session_state[key] = value

inicializar_estado()

# --- FUNÇÕES DE PROCESSAMENTO ---

@st.cache_resource
def carregar_ferramenta_gramatical():
    try:
        return language_tool_python.LanguageTool('pt-BR')
    except Exception as e:
        st.error(f"Falha ao carregar o revisor gramatical: {e}")
        return None

def aplicar_correcoes_automaticas(texto: str, ferramenta) -> str:
    if not ferramenta: return texto
    return ferramenta.correct(texto)

def html_to_plain_text(html_content: str) -> str:
    """Convert HTML from rich editor to plain text for processing."""
    if not html_content:
        return ""
    
    # Remove HTML tags but preserve line breaks
    import html
    
    # Convert <p>, <div>, <br> to newlines
    text = html_content.replace('<p>', '\n').replace('</p>', '\n')
    text = text.replace('<div>', '\n').replace('</div>', '\n')
    text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    
    # Remove all other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Clean up excessive newlines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    return text.strip()

def plain_text_to_html(plain_text: str) -> str:
    """Convert plain text to simple HTML for rich editor."""
    if not plain_text:
        return ""
    
    # Split by paragraphs
    paragraphs = plain_text.split('\n\n')
    
    # Wrap each paragraph in <p> tags
    html_paragraphs = []
    for para in paragraphs:
        if para.strip():
            # Replace single newlines with <br>
            para_html = para.replace('\n', '<br>')
            html_paragraphs.append(f'<p>{para_html}</p>')
    
    return '\n'.join(html_paragraphs)

def gerar_sugestoes_estilo_ia(texto: str, client: OpenAI):
    prompt = f"Analise o texto como um editor sênior. Forneça 3-5 sugestões concisas para melhorar estilo, clareza e impacto. Comece cada uma com 'Sugestão:'."
    try:
        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"{prompt}\n---{texto[:15000]}"}], temperature=0.5)
        sugestoes = response.choices[0].message.content.split('Sugestão:')
        return [s.strip() for s in sugestoes if s.strip()]
    except Exception as e:
        st.error(f"Erro ao chamar a IA para análise de estilo: {e}")
        return ["Não foi possível gerar sugestões."]

def gerar_manuscrito_profissional_docx(titulo: str, autor: str, contato: str, texto_manuscrito: str, use_fastformat: bool = True):
    # Apply FastFormat for professional typography (replaces smartypants)
    if use_fastformat:
        texto_limpo = apply_fastformat(texto_manuscrito, get_ptbr_options())
    else:
        # Basic cleanup
        texto_limpo = re.sub(r'^\s*-\s+', '— ', texto_manuscrito, flags=re.MULTILINE)
        texto_limpo = re.sub(r' +', ' ', texto_limpo)
    
    document = Document()
    for section in document.sections:
        section.top_margin = section.bottom_margin = section.left_margin = section.right_margin = Inches(1)
        header = section.header
        p_header = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        p_header.text = f"{autor.split(' ')[-1]} / {titulo} / "
        p_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p_header.add_run()
        fld_char1 = OxmlElement('w:fldChar'); fld_char1.set(qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText'); instrText.set(qn('xml:space'), 'preserve'); instrText.text = 'PAGE'
        fld_char2 = OxmlElement('w:fldChar'); fld_char2.set(qn('w:fldCharType'), 'end')
        run._r.extend([fld_char1, instrText, fld_char2])
    p_autor_contato = document.add_paragraph(f"{autor}\n{contato}"); p_autor_contato.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    contagem_palavras = len(texto_manuscrito.split())
    p_palavras = document.add_paragraph(f"Aproximadamente {math.ceil(contagem_palavras / 100.0) * 100:,} palavras"); p_palavras.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    p_titulo = document.add_paragraph(f"\n\n\n\n{titulo}"); p_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_titulo.runs[0].font.bold = True; p_titulo.runs[0].font.size = Pt(16)
    document.add_page_break()
    style = document.styles['Normal']; style.font.name = 'Times New Roman'; style.font.size = Pt(12)
    style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    style.paragraph_format.first_line_indent = Cm(1.25)
    for para_texto in texto_limpo.split('\n'):
        para_strip = para_texto.strip()
        if not para_strip: continue
        if para_strip in ['#', '***']:
            p_quebra = document.add_paragraph(para_strip); p_quebra.alignment = WD_ALIGN_PARAGRAPH.CENTER; p_quebra.paragraph_format.first_line_indent = None
        else:
            document.add_paragraph(para_strip)
    buffer = io.BytesIO(); document.save(buffer); buffer.seek(0)
    return buffer

def processar_arquivo_carregado():
    uploaded_file = st.session_state.file_uploader_key
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.txt'):
                text = io.StringIO(uploaded_file.getvalue().decode("utf-8")).read()
            else:
                doc = Document(io.BytesIO(uploaded_file.read()))
                text = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            st.session_state.text_content = text
            st.session_state.file_processed = True
            st.session_state.sugestoes_estilo = None
        except Exception as e:
            st.error(f"Ocorreu um erro ao ler o arquivo: {e}")
            st.session_state.text_content = ""
            st.session_state.file_processed = False

# --- INTERFACE DO USUÁRIO ---
st.title("Adapta ONE - Editor Profissional ✒️")
st.markdown("**A evolução da preparação de manuscritos.** Carregue seu texto, faça ajustes e, com um clique, obtenha um manuscrito profissional e revisado.")

with st.sidebar:
    st.header("Informações do Manuscrito")
    st.session_state.book_title = st.text_input("Título do Livro", st.session_state.book_title)
    st.session_state.author_name = st.text_input("Nome do Autor(a)", st.session_state.author_name)
    st.session_state.contact_info = st.text_input("Email ou Contato", st.session_state.contact_info)
    
    st.divider()
    st.header("Opções de Formatação")
    st.session_state.use_fastformat = st.checkbox(
        "Usar FastFormat (Tipografia Avançada)", 
        value=st.session_state.use_fastformat,
        help="Aplica formatação tipográfica profissional: aspas curvas, travessões em diálogos, reticências padronizadas, etc."
    )
    
    st.divider()
    st.header("Chave da OpenAI")
    api_key = st.text_input("Sua API Key (Opcional)", type="password", help="Necessária apenas para as sugestões de estilo.")
    if api_key:
        try:
            client = OpenAI(api_key=api_key); client.models.list()
            st.session_state.api_key_valida = True; st.session_state.openai_client = client
            st.success("API Key válida!")
        except Exception:
            st.error("API Key inválida."); st.session_state.api_key_valida = False

# --- ABAS DE FLUXO DE TRABALHO ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Escrever & Editar", 
    "✍️ Editor Avançado (Word-like)",
    "2. FastFormat (Formatação)", 
    "3. Sugestões de Estilo (IA)", 
    "4. Finalizar & Baixar"
])

with tab1:
    # Handle pending text update from FastFormat
    if st.session_state.get('pending_text_update'):
        st.session_state.text_content = st.session_state['pending_text_update']
        st.session_state['pending_text_update'] = None
    
    st.subheader("Cole ou Faça o Upload do seu Manuscrito")
    st.file_uploader(
        "Formatos: .txt, .docx",
        type=["txt", "docx"],
        key="file_uploader_key",
        on_change=processar_arquivo_carregado
    )

    st.subheader("Editor Principal")
    st.text_area(
        "Seu texto aparecerá aqui após o upload. Você também pode colar diretamente.",
        height=600,
        key="text_content"
    )
    
    # Sync button to rich editor
    if RICH_EDITOR_AVAILABLE:
        if st.button("📤 Enviar para Editor Avançado", help="Carrega o texto no Editor Avançado (Word-like) para edição com formatação rica"):
            if st.session_state.text_content:
                st.session_state.rich_editor_content = plain_text_to_html(st.session_state.text_content)
                st.session_state.use_rich_editor = True
                st.success("✅ Texto carregado no Editor Avançado! Vá para a aba 'Editor Avançado (Word-like)' para editar.")
            else:
                st.warning("⚠️ Adicione texto antes de enviar para o Editor Avançado.")
    else:
        st.warning("⚠️ Editor Avançado não disponível. Instale `streamlit-quill` para usar: `pip install streamlit-quill`")

with tab2:
    st.header("✍️ Editor Avançado - Interface estilo Word")
    
    # Check if rich editor is available
    if not RICH_EDITOR_AVAILABLE:
        st.error("""
        ### ⚠️ Editor Avançado não disponível
        
        O módulo `streamlit-quill` não está instalado. 
        
        **Para ativar o Editor Avançado:**
        
        1. Pare o aplicativo (Ctrl+C no terminal)
        2. Execute: `pip install streamlit-quill`
        3. Reinicie o aplicativo: `streamlit run app_editor.py`
        
        Ou reinstale todas as dependências:
        ```bash
        pip install -r requirements.txt
        ```
        """)
        st.info("💡 Enquanto isso, você pode usar o Editor Principal (Aba 1) para editar seu texto.", icon="ℹ️")
    
    else:
        st.markdown("""
        ### 📝 Editor de Texto Rico com Barra de Ferramentas
        
        Este editor oferece uma experiência similar ao Microsoft Word com:
        
        - **Formatação de texto:** Negrito, itálico, sublinhado, tachado
        - **Títulos:** H1, H2, H3 (títulos de diferentes níveis)
        - **Listas:** Com marcadores ou numeradas
        - **Alinhamento:** Esquerda, centro, direita, justificado
        - **Links e imagens:** Adicione links e imagens ao texto
        - **Cores:** Personalize cores de texto e fundo
        - **Desfazer/Refazer:** Histórico completo de edição
        
        **💡 Dica:** Use o editor para intervir manualmente no processo de edição quando necessário!
        """)
        
        st.divider()
        
        # Check if content exists
        if not st.session_state.get('rich_editor_content') and not st.session_state.text_content:
            st.info("📝 Escreva ou carregue um texto na primeira aba, depois use o botão '📤 Enviar para Editor Avançado'.", icon="ℹ️")
            
            # Option to start fresh
            if st.button("✨ Começar novo documento no Editor"):
                st.session_state.rich_editor_content = "<p>Comece a escrever seu texto aqui...</p>"
                st.session_state.use_rich_editor = True
                st.rerun()
        
        else:
            # Initialize rich editor content if not exists
            if not st.session_state.get('rich_editor_content'):
                st.session_state.rich_editor_content = plain_text_to_html(st.session_state.text_content)
            
            st.subheader("🖊️ Área de Edição")
            
            # Rich text editor with full toolbar
            content = st_quill(
                value=st.session_state.rich_editor_content,
                html=True,
                readonly=False,
                key='quill_editor',
                toolbar=[
                    ['bold', 'italic', 'underline', 'strike'],
                    ['blockquote', 'code-block'],
                    [{'header': 1}, {'header': 2}],
                    [{'list': 'ordered'}, {'list': 'bullet'}],
                    [{'script': 'sub'}, {'script': 'super'}],
                    [{'indent': '-1'}, {'indent': '+1'}],
                    [{'direction': 'rtl'}],
                    [{'size': ['small', False, 'large', 'huge']}],
                    [{'header': [1, 2, 3, 4, 5, 6, False]}],
                    [{'color': []}, {'background': []}],
                    [{'font': []}],
                    [{'align': []}],
                    ['clean'],
                    ['link', 'image']
                ]
            )
            
            # Update session state with editor content
            if content:
                st.session_state.rich_editor_content = content
            
            st.divider()
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Salvar para Texto Principal", type="primary", use_container_width=True):
                if st.session_state.rich_editor_content:
                    # Convert HTML to plain text and save to main text content
                    plain_text = html_to_plain_text(st.session_state.rich_editor_content)
                    st.session_state.text_content = plain_text
                    st.success("✅ Texto salvo no Editor Principal!")
                else:
                    st.warning("⚠️ O editor está vazio.")
        
        with col2:
            if st.button("🔄 Recarregar do Texto Principal", use_container_width=True):
                st.session_state.rich_editor_content = plain_text_to_html(st.session_state.text_content)
                st.success("✅ Texto recarregado do Editor Principal!")
                st.rerun()
        
        with col3:
            if st.button("🗑️ Limpar Editor", use_container_width=True):
                st.session_state.rich_editor_content = "<p></p>"
                st.rerun()
        
        # Show word count
        if st.session_state.rich_editor_content:
            plain_for_count = html_to_plain_text(st.session_state.rich_editor_content)
            word_count = len(plain_for_count.split())
            st.info(f"📊 **Contagem de palavras:** {word_count:,} palavras")

with tab3:
    st.header("✨ FastFormat - Formatação Tipográfica Profissional")
    
    if not st.session_state.text_content:
        st.info("📝 Escreva ou carregue um texto na primeira aba para usar o FastFormat.", icon="ℹ️")
    else:
        st.markdown("""
        ### O que o FastFormat faz?
        
        O FastFormat aplica formatação tipográfica profissional ao seu texto:
        
        - **Aspas Curvas:** `"texto"` → `"texto"`
        - **Travessões em Diálogos:** `- Olá` → `— Olá`
        - **Travessões em Intervalos:** `10-20` → `10–20`
        - **Reticências:** `...` → `…`
        - **Espaçamento:** Remove espaços extras
        - **Pontuação PT-BR:** Ajusta automaticamente
        """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("⚙️ Opções de Formatação")
            
            preset = st.radio(
                "Escolha o preset:",
                ["PT-BR (Ficção)", "Acadêmico/Técnico", "Personalizado"],
                help="PT-BR usa travessões em diálogos. Acadêmico preserva formatação original."
            )
            
            if preset == "Personalizado":
                st.markdown("**Configurações Personalizadas:**")
                custom_quotes = st.checkbox("Aspas curvas", value=True)
                custom_dialogue = st.selectbox("Diálogos:", ["Travessão (—)", "Hífen (-)"], index=0)
                custom_ellipsis = st.checkbox("Normalizar reticências (...→…)", value=True)
                custom_bullets = st.checkbox("Normalizar marcadores (•)", value=True)
        
        with col2:
            st.subheader("👁️ Visualizar Resultado")
            
            if st.button("🔍 Prévia da Formatação", type="primary", use_container_width=True):
                with st.spinner("Aplicando FastFormat..."):
                    from modules.fastformat_utils import apply_fastformat, get_ptbr_options, get_academic_options
                    from fastformat import FastFormatOptions
                    
                    # Determine options based on preset
                    if preset == "PT-BR (Ficção)":
                        options = get_ptbr_options()
                    elif preset == "Acadêmico/Técnico":
                        options = get_academic_options()
                    else:  # Personalizado
                        options = FastFormatOptions(
                            normalize_whitespace=True,
                            quotes_style="curly" if custom_quotes else "straight",
                            dialogue_dash="emdash" if custom_dialogue == "Travessão (—)" else "hyphen",
                            normalize_ellipsis=custom_ellipsis,
                            normalize_bullets=custom_bullets,
                            smart_ptbr_punctuation=True
                        )
                    
                    texto_formatado = apply_fastformat(st.session_state.text_content, options)
                    st.session_state['fastformat_preview'] = texto_formatado
            
            if 'fastformat_preview' in st.session_state:
                st.success("✅ Prévia gerada! Role para baixo para ver o resultado.")
        
        # Show preview if available
        if 'fastformat_preview' in st.session_state:
            st.divider()
            st.subheader("📄 Prévia do Texto Formatado")
            
            # Show before/after comparison
            col_before, col_after = st.columns(2)
            
            with col_before:
                st.markdown("**Antes (original):**")
                st.text_area(
                    "Texto original",
                    value=st.session_state.text_content[:1000] + ("..." if len(st.session_state.text_content) > 1000 else ""),
                    height=300,
                    disabled=True,
                    label_visibility="collapsed"
                )
            
            with col_after:
                st.markdown("**Depois (FastFormat):**")
                st.text_area(
                    "Texto formatado",
                    value=st.session_state['fastformat_preview'][:1000] + ("..." if len(st.session_state['fastformat_preview']) > 1000 else ""),
                    height=300,
                    disabled=True,
                    label_visibility="collapsed"
                )
            
            # Action buttons
            col_action1, col_action2 = st.columns(2)
            with col_action1:
                if st.button("✅ Aplicar ao Texto", type="primary", use_container_width=True):
                    st.session_state['pending_text_update'] = st.session_state['fastformat_preview']
                    del st.session_state['fastformat_preview']
                    st.success("✅ Formatação aplicada ao texto principal!")
                    st.rerun()
            
            with col_action2:
                if st.button("❌ Descartar", use_container_width=True):
                    del st.session_state['fastformat_preview']
                    st.rerun()

with tab4:
    st.header("Assistente de Escrita com IA (Opcional)")
    if not st.session_state.text_content:
        st.info("Escreva ou carregue um texto na primeira aba para começar.")
    elif not st.session_state.api_key_valida:
        st.warning("Insira uma chave de API válida da OpenAI na barra lateral para usar esta função.")
    else:
        if st.button("Analisar Estilo e Coerência (IA)", use_container_width=True):
            with st.spinner("IA está lendo seu texto..."):
                st.session_state.sugestoes_estilo = gerar_sugestoes_estilo_ia(st.session_state.text_content, st.session_state.openai_client)
        
        if st.session_state.sugestoes_estilo:
            st.subheader("Sugestões da IA")
            for sugestao in st.session_state.sugestoes_estilo:
                # ★★★ A CORREÇÃO FINAL ESTÁ AQUI ★★★
                st.info(sugestao, icon="💡")

with tab5:
    st.header("Finalize e Exporte seu Manuscrito Profissional")
    if not st.session_state.text_content:
        st.warning("Não há texto para finalizar. Escreva ou carregue seu manuscrito na primeira aba.")
    else:
        st.markdown("**O que este botão faz?**\n1. **Revisão Automática:** Aplica correções ortográficas e gramaticais.\n2. **Formatação Profissional:** Gera um arquivo `.docx` com todos os padrões da indústria.")
        
        if st.session_state.use_fastformat:
            st.info("✨ **FastFormat ativado:** Seu manuscrito terá formatação tipográfica profissional com aspas curvas, travessões, reticências e pontuação padronizada.", icon="✅")
        
        if st.button("Revisão Automática & Download Profissional (.DOCX)", type="primary", use_container_width=True):
            with st.spinner("Automatizando revisões e montando seu manuscrito profissional..."):
                tool = carregar_ferramenta_gramatical()
                texto_corrigido = aplicar_correcoes_automaticas(st.session_state.text_content, tool)
                docx_buffer = gerar_manuscrito_profissional_docx(
                    st.session_state.book_title, 
                    st.session_state.author_name, 
                    st.session_state.contact_info, 
                    texto_corrigido,
                    use_fastformat=st.session_state.use_fastformat
                )
            st.success("Manuscrito finalizado!")
            st.download_button(
                label="BAIXAR MANUSCRITO.DOCX",
                data=docx_buffer,
                file_name=f"{st.session_state.book_title}_ManuscritoProfissional.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
