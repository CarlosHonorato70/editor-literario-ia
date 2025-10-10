import streamlit as st
import io
import time
import math
from docx import Document
from openai import OpenAI # <-- NOVA IMPORTAÇÃO AQUI

# --- Configurações da Página Streamlit ---
st.set_page_config(
    page_title="Adapta ONE: Editor Literário IA",
    page_icon="✍️",
    layout="wide"
)

# --- Funções de Lógica ---

def analisar_texto(texto: str):
    """Calcula estatísticas básicas sobre o texto."""
    if not texto: return None
    palavras = texto.split()
    num_palavras = len(palavras)
    num_caracteres_com_espacos = len(texto)
    num_caracteres_sem_espacos = len(texto.replace(" ", "").replace("\n", ""))
    palavras_por_minuto = 225
    tempo_leitura_minutos = num_palavras / palavras_por_minuto
    minutos = int(tempo_leitura_minutos)
    segundos = int((tempo_leitura_minutos * 60) % 60)
    return {
        "Contagem de Palavras": num_palavras,
        "Contagem de Caracteres (com espaços)": num_caracteres_com_espacos,
        "Contagem de Caracteres (sem espaços)": num_caracteres_sem_espacos,
        "Tempo Estimado de Leitura": f"{minutos} min e {segundos} seg"
    }

# <-- NOVA FUNÇÃO AQUI: Implementa a geração de resumo com IA -->
def gerar_resumo_ia(texto: str):
    """
    Usa a API da OpenAI para gerar um resumo do texto fornecido.
    Retorna o resumo como uma string ou uma mensagem de erro.
    """
    if not texto:
        return "Erro: Não há texto para resumir."
    
    try:
        # Inicializa o cliente da OpenAI usando a chave dos Secrets
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        # Monta a instrução para a IA
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Modelo rápido e eficiente para resumos
            messages=[
                {
                    "role": "system", 
                    "content": "Você é um assistente de escrita especializado em literatura. Sua tarefa é criar resumos concisos e envolventes de textos."
                },
                {
                    "role": "user", 
                    "content": f"Por favor, gere um resumo de um parágrafo para o seguinte texto:\n\n---\n\n{texto}"
                }
            ],
            temperature=0.7, # Um pouco de criatividade, mas ainda focado no conteúdo
            max_tokens=250   # Limita o tamanho do resumo
        )
        # Extrai e retorna o conteúdo do resumo
        return response.choices[0].message.content

    except Exception as e:
        # Retorna uma mensagem de erro amigável se algo der errado (ex: chave de API inválida)
        st.error(f"Ocorreu um erro ao conectar com a IA: {e}")
        return "Não foi possível gerar o resumo. Verifique sua chave de API ou tente novamente mais tarde."


# --- Barra Lateral: Configuração Inicial ---
st.sidebar.title("Configuração Inicial")
# (O resto da barra lateral permanece o mesmo)
book_title = st.sidebar.text_input("Título do livro", "Mentes brilhantes, caminhos")
author_name = st.sidebar.text_input("Autor(a)", "Carlos Honorato")
selected_miolo_format = st.sidebar.selectbox("Formato do miolo (KDP/Gráfica)", ["KDP 5,5 x 8,5 pol (140 páginas)"])
selected_style_model = st.sidebar.selectbox("Modelo de Estilo", ["ABNT Acadêmico (Título)"])

# --- Conteúdo Principal ---
st.title("Adapta ONE: Editor Literário IA")

tab1, tab2 = st.tabs(["Manuscrito", "Exportar"])

with tab1:
    st.subheader("Selecione seu arquivo (.txt ou .docx) aqui:")

    uploaded_file = st.file_uploader(
        "Arraste e solte o arquivo aqui", type=["txt", "docx"], help="Formatos: TXT, DOCX."
    )

    # Gerenciamento do estado da sessão
    if 'text_content' not in st.session_state:
        st.session_state.text_content = ""
    if 'file_processed' not in st.session_state:
        st.session_state.file_processed = False
    if 'last_uploaded_file_id' not in st.session_state:
        st.session_state.last_uploaded_file_id = None
    if 'resumo_gerado' not in st.session_state: # <-- Novo estado para guardar o resumo
        st.session_state.resumo_gerado = ""

    # Lógica de upload (permanece a mesma)
    if uploaded_file is not None:
        current_file_id = f"{uploaded_file.name}-{uploaded_file.size}"
        if st.session_state.last_uploaded_file_id != current_file_id:
            st.session_state.last_uploaded_file_id = current_file_id
            st.session_state.text_content = ""
            st.session_state.resumo_gerado = "" # Limpa resumo antigo ao carregar novo arquivo
            st.session_state.file_processed = False
            progress_bar = st.progress(0, "Processando arquivo...")
            try:
                # ... (Lógica de leitura de TXT e DOCX) ...
                if uploaded_file.name.endswith('.txt'):
                    text_content = io.StringIO(uploaded_file.getvalue().decode("utf-8")).read()
                elif uploaded_file.name.endswith('.docx'):
                    doc = Document(io.BytesIO(uploaded_file.read()))
                    text_content = "\n".join([p.text for p in doc.paragraphs])
                st.session_state.text_content = text_content
                st.session_state.file_processed = True
                progress_bar.progress(100, "Arquivo carregado!")
                time.sleep(1)
                progress_bar.empty()
            except Exception as e:
                st.error(f"Erro ao processar: {e}")
                progress_bar.empty()

    # Seção de exibição do conteúdo e ferramentas
    if st.session_state.get('file_processed') and st.session_state.get('text_content'):
        st.write("---")
        st.subheader("Conteúdo do Manuscrito:")
        edited_text = st.text_area("Edite seu texto aqui:", st.session_state.text_content, height=500, key="editor")
        if edited_text != st.session_state.text_content:
            st.session_state.text_content = edited_text
        
        st.write("---")
        st.subheader("Ferramentas de Edição:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Analisar Texto", help="Analisa estatísticas do manuscrito."):
                # (Lógica de análise permanece a mesma)
                with st.spinner("Analisando..."):
                    analise = analisar_texto(st.session_state.text_content)
                    if analise:
                        st.session_state.analise_resultados = analise # Salva no estado
                    else:
                        st.warning("Não há texto para analisar.")
        with col2:
            # <-- LÓGICA DO BOTÃO "GERAR RESUMO" ATUALIZADA -->
            if st.button("Gerar Resumo", help="Cria um resumo conciso com IA."):
                with st.spinner("�� A IA está pensando... Isso pode levar um momento."):
                    resumo = gerar_resumo_ia(st.session_state.text_content)
                    st.session_state.resumo_gerado = resumo # Salva o resumo no estado
        with col3:
            if st.button("Formatar Manuscrito", help="Aplica o modelo de estilo selecionado."):
                st.info("Formatando... (Funcionalidade a ser implementada)")

        # Exibe os resultados da análise, se existirem
        if 'analise_resultados' in st.session_state and st.session_state.analise_resultados:
            st.subheader("Resultados da Análise")
            for metrica, valor in st.session_state.analise_resultados.items():
                st.metric(label=metrica, value=valor)
            if st.button("Limpar Análise"):
                del st.session_state.analise_resultados

        # Exibe o resumo gerado, se existir
        if st.session_state.resumo_gerado:
            st.subheader("Resumo Gerado pela IA")
            st.success(st.session_state.resumo_gerado)
            if st.button("Limpar Resumo"):
                st.session_state.resumo_gerado = ""

    elif not st.session_state.get('text_content'):
        st.info("Aguardando o carregamento de um arquivo para começar.")


with tab2:
    st.write("Funcionalidade de Exportação aqui.")
