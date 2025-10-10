import streamlit as st
import io
from docx import Document  # Para lidar com arquivos .docx (instale com pip install python-docx)

# --- Configuração Inicial da Página Streamlit ---
st.set_page_config(
    page_title="Editor Literário IA - Adapta ONE",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Inicialização do Session State ---
# Isso é crucial para manter o estado da aplicação entre os reruns. Corrigi para incluir o texto editável.
if 'book_title' not in st.session_state:
    st.session_state.book_title = "Mentes brilhantes, caminhos"  # Valor inicial
if 'author' not in st.session_state:
    st.session_state.author = "Carlos Honorato"  # Valor inicial
if 'format' not in st.session_state:
    st.session_state.format = "KDP 5,5 x 8,5 pol (140..."  # Valor inicial
if 'style_model' not in st.session_state:
    st.session_state.style_model = "ABNT Acadêmico (Título..."  # Valor inicial
if 'uploaded_file_content' not in st.session_state:
    st.session_state.uploaded_file_content = ""  # Texto inicial vazio para o editor
if 'file_name' not in st.session_state:
    st.session_state.file_name = None
if 'file_size' not in st.session_state:
    st.session_state.file_size = 0
if 'last_uploaded_file_id' not in st.session_state:  # Para detectar novos uploads
    st.session_state.last_uploaded_file_id = None
if 'arquivo_carregado' not in st.session_state:  # Flag para saber se upload foi feito (nova adição para correção)
    st.session_state.arquivo_carregado = False

# --- Funções Auxiliares ---
def clear_editor_content():
    """Função para limpar o conteúdo do editor e redefinir o estado do arquivo."""
    st.session_state.uploaded_file_content = ""
    st.session_state.file_name = None
    st.session_state.file_size = 0
    st.session_state.last_uploaded_file_id = None
    st.session_state.arquivo_carregado = False  # Reset da flag

def read_docx(file):
    """Lê o conteúdo de um arquivo .docx e retorna o texto."""
    try:
        doc = Document(io.BytesIO(file.read()))
        full_text = [para.text for para in doc.paragraphs]
        return "\n".join(full_text)
    except Exception as e:
        st.error(f"Erro ao ler arquivo .docx: {e}")
        return ""

# --- Barra Lateral (Configuração Inicial) ---
with st.sidebar:
    st.header("Configuração Inicial")
    st.markdown("Defina informações do livro e preferências do miolo.")

    # Título do livro
    st.session_state.book_title = st.text_input(
        "Título do livro",
        value=st.session_state.book_title,
        placeholder="Mentes brilhantes, caminhos",
        key="book_title_input"
    )

    # Autor(a)
    st.session_state.author = st.text_input(
        "Autor(a)",
        value=st.session_state.author,
        placeholder="Carlos Honorato",
        key="author_input"
    )

    # Formato do miolo (KDP/Gráfica)
    format_options = ["KDP 5,5 x 8,5 pol (140...", "A4 (210x297mm)", "A5 (148x210mm)", "US Letter (8.5x11in)"]
    try:
        default_format_index = format_options.index(st.session_state.format)
    except ValueError:
        default_format_index = 0
    st.session_state.format = st.selectbox(
        "Formato do miolo (KDP/Gráfica)",
        options=format_options,
        index=default_format_index,
        key="format_select"
    )

    # Modelo de Estilo
    style_options = ["ABNT Acadêmico (Título...", "MLA (Modern Language Association)", "APA (American Psychological Association)", "Chicago (CMS)"]
    try:
        default_style_index = style_options.index(st.session_state.style_model)
    except ValueError:
        default_style_index = 0
    st.session_state.style_model = st.selectbox(
        "Modelo de Estilo",
        options=style_options,
        index=default_style_index,
        key="style_model_select"
    )

# --- Área Principal com Abas (Integração para melhor organização) ---
st.title("Adapta ONE: Editor Literário IA")
st.markdown("---")  # Divisor para melhor visualização

# Exemplo de estrutura de abas (baseado nas suas mensagens anteriores). Você pode adicionar mais.
tab1, tab2 = st.tabs(["Manuscrito", "Exportar"])  # Abas simples para organização

with tab1:
    st.subheader("Selecione seu arquivo (.txt ou .docx) aqui:")

    # Componente File Uploader
    uploaded_file = st.file_uploader(
        "Arraste e solte o arquivo aqui",
        type=["txt", "docx"],
        help="Limite de 200 MB por arquivo TXT, DOCX",
        label_visibility="collapsed"  # Esconde o rótulo padrão
    )

    # Processa o arquivo carregado - Correção principal: Verifica se não é None e atualiza session_state
    if uploaded_file is not None:
        # Verifica se é um novo upload para evitar reprocessamento desnecessário
        if st.session_state.last_uploaded_file_id != uploaded_file.file_id:  # Correção: Use 'file_id' em vez de 'id' para evitar AttributeError
            st.session_state.last_uploaded_file_id = uploaded_file.file_id
            st.session_state.file_name = uploaded_file.name
            st.session_state.file_size = uploaded_file.size

            if uploaded_file.type == "text/plain":
                st.session_state.uploaded_file_content = uploaded_file.read().decode("utf-8")
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                st.session_state.uploaded_file_content = read_docx(uploaded_file)
            else:
                st.error("Formato de arquivo não suportado. Por favor, use .txt ou .docx.")
                st.session_state.uploaded_file_content = ""

            st.session_state.arquivo_carregado = True  # Ativa a flag

    # Exibe mensagem de sucesso se o conteúdo estiver disponível
    if st.session_state.arquivo_carregado and st.session_state.uploaded_file_content:
        st.success("✔ Arquivo carregado com sucesso! O texto está no editor abaixo.")
        st.markdown(f"**{st.session_state.file_name}** {round(st.session_state.file_size / 1024, 1)}KB")
    elif st.session_state.arquivo_carregado:
        st.warning("O arquivo foi carregado, mas não foi possível extrair o texto. Verifique o formato.")
    else:
        st.info("Nenhum arquivo carregado ainda. Arraste um arquivo para começar.")

    st.markdown("---")  # Divisor

    # Botão para limpar o texto
    st.button("Limpar todo o texto do editor", on_click=clear_editor_content)

    # Editor de texto - Sempre visível, com valor do session_state (correção para aparecer e ser editável)
    st.markdown("Editor de texto (editar ou visualizar o texto carregado)")
    edited_content = st.text_area(
        "Conteúdo do texto",
        value=st.session_state.uploaded_file_content,
        height=400,
        placeholder="O conteúdo do seu arquivo aparecerá aqui...",
        key="text_editor",
        label_visibility="collapsed"
    )

    # Atualiza o session_state com as edições do usuário em tempo real
    if edited_content != st.session_state.uploaded_file_content:
        st.session_state.uploaded_file_content = edited_content
        st.success("Edições detectadas e salvas temporariamente!")

with tab2:
    st.subheader("Exportar Manuscrito")
    if st.button("Exportar como TXT"):
        if st.session_state.uploaded_file_content:
            st.download_button(
                label="Baixar TXT",
                data=st.session_state.uploaded_file_content,
                file_name="manuscrito_editado.txt",
                mime="text/plain"
            )
        else:
            st.warning("Nada para exportar. Carregue ou edite texto primeiro.")

st.markdown("---")  # Divisor final
st.caption("Adapta ONE © 2023. Todos os direitos reservados.")

# --- Depuração Opcional (Comente ou remova após testes) ---
# st.write(f"Debug: Conteúdo no session_state: {st.session_state.uploaded_file_content[:100]}...")  # Mostra os primeiros 100 chars para depuração
