import streamlit as st
import io
import time
import math
from docx import Document # Importa a biblioteca para lidar com arquivos .docx

# --- Configurações da Página Streamlit ---
st.set_page_config(
    page_title="Adapta ONE: Editor Literário IA",
    page_icon="✍️",
    layout="wide"
)

# --- Funções de Lógica ---

# <-- NOVA FUNÇÃO AQUI: Implementa a análise de texto -->
def analisar_texto(texto: str):
    """
    Calcula estatísticas básicas sobre o texto fornecido.
    Retorna um dicionário com as métricas.
    """
    if not texto:
        return None

    palavras = texto.split()
    num_palavras = len(palavras)
    num_caracteres_com_espacos = len(texto)
    num_caracteres_sem_espacos = len(texto.replace(" ", "").replace("\n", ""))
    
    # Média de palavras por minuto para cálculo do tempo de leitura (padrão é ~200-230)
    palavras_por_minuto = 225
    tempo_leitura_minutos = num_palavras / palavras_por_minuto
    
    # Converte o tempo para um formato mais legível (minutos e segundos)
    minutos = int(tempo_leitura_minutos)
    segundos = int((tempo_leitura_minutos * 60) % 60)

    return {
        "Contagem de Palavras": num_palavras,
        "Contagem de Caracteres (com espaços)": num_caracteres_com_espacos,
        "Contagem de Caracteres (sem espaços)": num_caracteres_sem_espacos,
        "Tempo Estimado de Leitura": f"{minutos} min e {segundos} seg"
    }

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
        type=["txt", "docx"],
        accept_multiple_files=False,
        help="Limite de 200MB por arquivo. Formatos: TXT, DOCX."
    )

    if 'text_content' not in st.session_state:
        st.session_state.text_content = ""
    if 'file_processed' not in st.session_state:
        st.session_state.file_processed = False
    if 'last_uploaded_file_id' not in st.session_state:
        st.session_state.last_uploaded_file_id = None

    if uploaded_file is not None:
        current_file_id = f"{uploaded_file.name}-{uploaded_file.size}"
        
        if st.session_state.last_uploaded_file_id != current_file_id:
            st.session_state.last_uploaded_file_id = current_file_id
            st.session_state.text_content = ""
            st.session_state.file_processed = False

            progress_text = "Processando arquivo, por favor aguarde..."
            my_bar = st.progress(0, text=progress_text)

            try:
                file_extension = uploaded_file.name.split('.')[-1].lower()
                text_content = ""

                if file_extension == "txt":
                    my_bar.progress(30, text="Lendo arquivo TXT...")
                    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
                    text_content = stringio.read()
                    my_bar.progress(100, text="Arquivo TXT carregado com sucesso!")
                    
                elif file_extension == "docx":
                    my_bar.progress(20, text="Iniciando leitura de DOCX...")
                    doc = Document(io.BytesIO(uploaded_file.read()))
                    paragraphs = [p.text for p in doc.paragraphs]
                    text_content = "\n".join(paragraphs)
                    my_bar.progress(100, text="Arquivo DOCX carregado com sucesso!")
                
                else:
                    st.error("Formato de arquivo não suportado.")
                    text_content = ""

                st.session_state.text_content = text_content
                st.session_state.file_processed = True
                
                time.sleep(1)
                my_bar.empty()

            except Exception as e:
                st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
                st.session_state.text_content = ""
                st.session_state.file_processed = False
                my_bar.empty()
    
    if st.session_state.get('file_processed', False) and st.session_state.get('text_content'):
        st.write("---")
        st.subheader("Conteúdo do Manuscrito:")
        
        edited_text = st.text_area(
            "Edite seu texto aqui:",
            st.session_state.text_content,
            height=500,
            key="manuscript_editor"
        )

        if edited_text != st.session_state.text_content:
            st.session_state.text_content = edited_text
        
        st.write("---")
        st.subheader("Ferramentas de Edição:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            # <-- LÓGICA DO BOTÃO ATUALIZADA -->
            if st.button("Analisar Texto", help="Analisa a estrutura, gramática e estilo do manuscrito."):
                with st.spinner("Analisando..."):
                    analise = analisar_texto(st.session_state.text_content)
                    if analise:
                        st.success("Análise Concluída!")
                        # Exibe os resultados de forma organizada
                        for metrica, valor in analise.items():
                            st.metric(label=metrica, value=valor)
                    else:
                        st.warning("Não há texto para analisar.")

        with col2:
            if st.button("Gerar Resumo", help="Cria um resumo conciso do conteúdo do livro."):
                st.info("Gerando resumo... (Funcionalidade a ser implementada com IA)")
        with col3:
            if st.button("Formatar Manuscrito", help="Aplica o modelo de estilo selecionado ao texto."):
                st.info("Formatando... (Funcionalidade a ser implementada)")
    
    elif not st.session_state.get('text_content'):
        st.info("Aguardando o carregamento de um arquivo para começar.")


with tab2:
    st.write("Funcionalidade de Exportação aqui.")
    st.write("Você poderá exportar o manuscrito processado em diferentes formatos.")
