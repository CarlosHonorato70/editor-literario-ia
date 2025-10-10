import streamlit as st
import io
import time
import math
from docx import Document
from openai import OpenAI

# --- Configurações da Página Streamlit ---
st.set_page_config(
    page_title="Adapta ONE: Editor Literário IA",
    page_icon="✍️",
    layout="wide"
)

# --- Funções de Lógica ---

def analisar_texto(texto: str):
    # (Esta função permanece a mesma)
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

def gerar_resumo_ia(texto: str):
    # (Esta função permanece a mesma)
    if not texto: return "Erro: Não há texto para resumir."
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente de escrita especializado em literatura. Sua tarefa é criar resumos concisos e envolventes de textos."},
                {"role": "user", "content": f"Por favor, gere um resumo de um parágrafo para o seguinte trecho:\n\n---\n\n{texto}"}
            ],
            temperature=0.7, max_tokens=250
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Ocorreu um erro ao conectar com a IA: {e}")
        return "Não foi possível gerar o resumo. Verifique sua chave de API ou tente novamente mais tarde."

# --- Barra Lateral (permanece a mesma) ---
st.sidebar.title("Configuração Inicial")
book_title = st.sidebar.text_input("Título do livro", "Mentes brilhantes, caminhos")
author_name = st.sidebar.text_input("Autor(a)", "Carlos Honorato")
selected_miolo_format = st.sidebar.selectbox("Formato do miolo (KDP/Gráfica)", ["KDP 5,5 x 8,5 pol (140 páginas)"])
selected_style_model = st.sidebar.selectbox("Modelo de Estilo", ["ABNT Acadêmico (Título)"])

# --- Conteúdo Principal ---
st.title("Adapta ONE: Editor Literário IA")

tab1, tab2 = st.tabs(["Manuscrito", "Exportar"])

with tab1:
    st.subheader("Selecione seu arquivo (.txt ou .docx) aqui:")

    uploaded_file = st.file_uploader("Arraste e solte o arquivo", type=["txt", "docx"], help="Formatos: TXT, DOCX.")

    # Inicialização do estado da sessão
    if 'text_content' not in st.session_state: st.session_state.text_content = ""
    if 'file_processed' not in st.session_state: st.session_state.file_processed = False
    if 'last_uploaded_file_id' not in st.session_state: st.session_state.last_uploaded_file_id = None
    if 'resumo_gerado' not in st.session_state: st.session_state.resumo_gerado = ""
    if 'analise_resultados' not in st.session_state: st.session_state.analise_resultados = None

    # Lógica de upload (permanece a mesma)
    if uploaded_file is not None:
        current_file_id = f"{uploaded_file.name}-{uploaded_file.size}"
        if st.session_state.last_uploaded_file_id != current_file_id:
            # ... (código de upload e processamento do arquivo) ...
            st.session_state.last_uploaded_file_id = current_file_id
            st.session_state.text_content = ""
            st.session_state.resumo_gerado = ""
            st.session_state.analise_resultados = None
            st.session_state.file_processed = False
            progress_bar = st.progress(0, "Processando arquivo...")
            try:
                text_content = ""
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
        
        col1, col2 = st.columns(2)
        with col1:
            # Ferramenta de Análise
            if st.button("Analisar Texto", help="Analisa estatísticas do manuscrito."):
                with st.spinner("Analisando..."):
                    analise = analisar_texto(st.session_state.text_content)
                    if analise:
                        st.session_state.analise_resultados = analise
                    else:
                        st.warning("Não há texto para analisar.")
        with col2:
            if st.button("Formatar Manuscrito", help="Aplica o modelo de estilo selecionado."):
                st.info("Formatando... (Funcionalidade a ser implementada)")
        
        # <-- SEÇÃO DE RESUMO ATUALIZADA -->
        st.write("---")
        st.subheader("Resumo com Inteligência Artificial")
        
        # O limite de tokens é ~4 caracteres/token. 16385 tokens * 3.5 ≈ 57000 caracteres.
        # Vamos usar um limite seguro de 15000 caracteres para garantir que não exceda.
        max_chars_para_resumo = 15000
        
        if len(st.session_state.text_content) > max_chars_para_resumo:
            st.warning(f"Seu manuscrito é muito longo para ser resumido de uma só vez. Apenas os primeiros {max_chars_para_resumo} caracteres serão usados.")
            texto_para_resumir = st.session_state.text_content[:max_chars_para_resumo]
        else:
            texto_para_resumir = st.session_state.text_content

        if st.button("Gerar Resumo Agora", help="Cria um resumo conciso com IA usando uma parte do texto.", type="primary"):
            with st.spinner("🤖 A IA está pensando... Isso pode levar um momento."):
                resumo = gerar_resumo_ia(texto_para_resumir)
                st.session_state.resumo_gerado = resumo
        
        # Exibe os resultados
        if st.session_state.analise_resultados:
            st.subheader("Resultados da Análise")
            for metrica, valor in st.session_state.analise_resultados.items():
                st.metric(label=metrica, value=valor)
            if st.button("Limpar Análise"):
                st.session_state.analise_resultados = None

        if st.session_state.resumo_gerado:
            st.subheader("Resumo Gerado pela IA")
            st.success(st.session_state.resumo_gerado)
            if st.button("Limpar Resumo"):
                st.session_state.resumo_gerado = ""

    elif not st.session_state.get('text_content'):
        st.info("Aguardando o carregamento de um arquivo para começar.")

with tab2:
    st.write("Funcionalidade de Exportação aqui.")
