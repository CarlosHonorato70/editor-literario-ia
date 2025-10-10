import streamlit as st
import io
import time
from docx import Document # Importa a biblioteca para lidar com arquivos .docx

# --- Configurações da Página Streamlit ---
st.set_page_config(
    page_title="Adapta ONE: Editor Literário IA",
    page_icon="✍️",
    layout="wide"
)

# --- Barra Lateral: Configuração Inicial ---
st.sidebar.title("Configuração Inicial")
st.sidebar.write("Defina informações do livro e preferências do miolo.")

# Campos de entrada na barra lateral
book_title = st.sidebar.text_input("Título do livro", "Mentes brilhantes, caminhos")
author_name = st.sidebar.text_input("Autor(a)", "Carlos Honorato")

miolo_format_options = [
    "KDP 5,5 x 8,5 pol (140 páginas)",
    "A5 (148 x 210 mm)",
    "Personalizado..."
]
selected_miolo_format = st.sidebar.selectbox("Formato do miolo (KDP/Gráfica)", miolo_format_options)

style_model_options = [
    "ABNT Acadêmico (Título)",
    "MLA",
    "APA",
    "Chicago"
]
selected_style_model = st.sidebar.selectbox("Modelo de Estilo", style_model_options)

# --- Conteúdo Principal ---
st.title("Adapta ONE: Editor Literário IA")

# Abas para "Manuscrito" e "Exportar"
tab1, tab2 = st.tabs(["Manuscrito", "Exportar"])

with tab1:
    st.subheader("Selecione seu arquivo (.txt ou .docx) aqui:")

    uploaded_file = st.file_uploader(
        "Arraste e solte o arquivo aqui (ou clique para selecionar)",
        type=["txt", "docx"], # Permite arquivos .txt e .docx
        accept_multiple_files=False,
        help="Limite de 200MB por arquivo. Formatos: TXT, DOCX."
    )

    # Inicializa o estado da sessão para o conteúdo do texto e status de processamento
    if 'text_content' not in st.session_state:
        st.session_state.text_content = ""
    if 'file_processed' not in st.session_state:
        st.session_state.file_processed = False
    if 'last_uploaded_file_id' not in st.session_state:
        st.session_state.last_uploaded_file_id = None

    if uploaded_file is not None:
        # Verifica se um novo arquivo foi carregado ou se é uma re-execução com o mesmo arquivo.
        # Isso evita reprocessar o mesmo arquivo desnecessariamente a cada interação.
        current_file_id = f"{uploaded_file.name}-{uploaded_file.size}"
        
        if st.session_state.last_uploaded_file_id != current_file_id:
            st.session_state.last_uploaded_file_id = current_file_id
            st.session_state.text_content = "" # Limpa o conteúdo anterior
            st.session_state.file_processed = False

            # Exibe a barra de progresso
            progress_text = "Processando arquivo, por favor aguarde..."
            my_bar = st.progress(0, text=progress_text)

            try:
                file_extension = uploaded_file.name.split('.')[-1].lower()
                text_content = ""

                if file_extension == "txt":
                    my_bar.progress(30, text="Lendo arquivo TXT...")
                    # Leitura de arquivo TXT
                    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
                    text_content = stringio.read()
                    my_bar.progress(100, text="Arquivo TXT carregado com sucesso!")
                    
                elif file_extension == "docx":
                    my_bar.progress(20, text="Iniciando leitura de DOCX...")
                    # Leitura de arquivo DOCX
                    doc = Document(io.BytesIO(uploaded_file.read()))
                    paragraphs = [p.text for p in doc.paragraphs]
                    text_content = "\n".join(paragraphs)
                    my_bar.progress(100, text="Arquivo DOCX carregado com sucesso!")
                
                else:
                    st.error("Formato de arquivo não suportado. Por favor, envie .txt ou .docx.")
                    text_content = ""

                # Armazena o conteúdo e o status no st.session_state
                st.session_state.text_content = text_content
                st.session_state.file_processed = True
                
                # Simula um pequeno atraso para a barra de progresso ser visível
                time.sleep(1)
                my_bar.empty() # Remove a barra de progresso após a conclusão

            except Exception as e:
                st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
                st.session_state.text_content = ""
                st.session_state.file_processed = False
                my_bar.empty() # Remove a barra de progresso em caso de erro
    
    # Esta seção agora é executada independentemente do bloco de upload acima
    # Exibe o conteúdo e os botões adicionais SE o arquivo já foi processado e está no session_state
    if st.session_state.get('file_processed', False) and st.session_state.get('text_content'):
        st.write("---") # Separador
        st.subheader("Conteúdo do Manuscrito:")
        
        # st.text_area para exibir e permitir edição do texto
        # O valor vem DIRETAMENTE do session_state, garantindo persistência
        edited_text = st.text_area(
            "Edite seu texto aqui:",
            st.session_state.text_content,
            height=500,
            key="manuscript_editor"
        )

        # Atualiza o session_state se o usuário editar o texto diretamente
        if edited_text != st.session_state.text_content:
            st.session_state.text_content = edited_text
        
        st.write("---") # Separador
        st.subheader("Ferramentas de Edição:")
        
        # Adiciona os botões de comando que "sumiram"
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Analisar Texto", help="Analisa a estrutura, gramática e estilo do manuscrito."):
                st.success("Análise de texto iniciada! (Funcionalidade a ser implementada)")
        with col2:
            if st.button("Gerar Resumo", help="Cria um resumo conciso do conteúdo do livro."):
                st.success("Geração de resumo iniciada! (Funcionalidade a ser implementada)")
        with col3:
            if st.button("Formatar Manuscrito", help="Aplica o modelo de estilo selecionado ao texto."):
                st.success("Formatação iniciada! (Funcionalidade a ser implementada)")
    
    # Mensagem inicial quando nada foi carregado ainda
    elif not st.session_state.get('text_content'):
        st.info("Aguardando o carregamento de um arquivo para começar.")


with tab2:
    st.write("Funcionalidade de Exportação aqui.")
    st.write("Você poderá exportar o manuscrito processado em diferentes formatos.")
    # if st.button("Exportar para PDF"):
    #     st.write("Gerando PDF...")
