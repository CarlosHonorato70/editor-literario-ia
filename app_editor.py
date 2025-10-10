import streamlit as st
import io
import time
import re
import math
import smartypants
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from openai import OpenAI

# --- Configurações da Página Streamlit ---
st.set_page_config(page_title="Adapta ONE: Editor Literário IA", page_icon="✍️", layout="wide")

# --- FUNÇÕES DE LÓGICA ---

def analisar_texto(texto: str):
    """Calcula estatísticas básicas sobre o texto."""
    if not texto: return None
    palavras = texto.split()
    num_palavras = len(palavras)
    return {
        "Contagem de Palavras": num_palavras,
        "Contagem de Caracteres": len(texto),
        "Tempo Estimado de Leitura": f"{math.ceil(num_palavras / 225)} min"
    }

def gerar_resumo_ia(texto: str):
    """Usa a API da OpenAI para gerar um resumo do texto."""
    if not texto: return "Erro: Não há texto para resumir."
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente de escrita especializado em literatura. Crie resumos concisos e envolventes."},
                {"role": "user", "content": f"Por favor, gere um resumo de um parágrafo para o seguinte trecho:\n\n{texto}"}
            ],
            temperature=0.7, max_tokens=250
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Ocorreu um erro ao conectar com a IA: {e}")
        return "Não foi possível gerar o resumo."

def limpar_e_otimizar_texto(texto: str) -> str:
    """Aplica regras de micro-tipografia e limpeza ao texto."""
    if not texto: return ""
    texto = texto.replace('\r\n', '\n').replace('\r', '\n')
    linhas = [linha.strip() for linha in texto.split('\n')]
    texto = '\n'.join(linhas)
    texto = re.sub(r' +', ' ', texto)
    texto = smartypants.smartypants(texto)
    texto = re.sub(r'^\s*-\s+', '— ', texto, flags=re.MULTILINE)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto.strip()

# --- NOVA FUNÇÃO: Geração do Documento .DOCX Formatado ---
def gerar_docx_formatado(texto: str):
    """Cria um documento .docx com formatação ABNT/Editorial a partir do texto."""
    texto_limpo = limpar_e_otimizar_texto(texto)
    
    document = Document()
    
    # Configura o estilo padrão do documento
    style = document.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    # Configura o parágrafo padrão
    paragraph_format = style.paragraph_format
    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph_format.space_after = Pt(0)
    paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    paragraph_format.first_line_indent = Cm(1.25)
    
    # Adiciona os parágrafos do texto ao documento
    paragrafos = texto_limpo.split('\n\n') # Divide por parágrafos (linhas em branco duplas)
    for para_texto in paragrafos:
        if para_texto.strip(): # Evita adicionar parágrafos vazios
            document.add_paragraph(para_texto.strip())

    # Salva o documento em um buffer de memória para download
    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer

# --- Barra Lateral (permanece a mesma) ---
st.sidebar.title("Configuração Inicial")
# ...

# --- Conteúdo Principal ---
st.title("Adapta ONE: Editor Literário IA")

tab1, tab2 = st.tabs(["Manuscrito", "Exportar"])

with tab1:
    st.subheader("Selecione seu arquivo (.txt ou .docx)")
    uploaded_file = st.file_uploader("Arraste e solte o arquivo", type=["txt", "docx"])

    # --- Gerenciamento de Estado COMPLETO e PERSISTENTE ---
    if 'text_content' not in st.session_state: st.session_state.text_content = ""
    if 'file_processed' not in st.session_state: st.session_state.file_processed = False
    if 'last_uploaded_file_id' not in st.session_state: st.session_state.last_uploaded_file_id = None
    if 'resumo_gerado' not in st.session_state: st.session_state.resumo_gerado = None
    if 'analise_resultados' not in st.session_state: st.session_state.analise_resultados = None

    # Lógica de upload
    if uploaded_file is not None:
        current_file_id = f"{uploaded_file.name}-{uploaded_file.size}"
        if st.session_state.last_uploaded_file_id != current_file_id:
            st.session_state.last_uploaded_file_id = current_file_id
            st.session_state.resumo_gerado = None # Limpa resultados antigos
            st.session_state.analise_resultados = None # Limpa resultados antigos
            # ... (código de upload e processamento do arquivo) ...
            progress_bar = st.progress(0, "Processando arquivo...")
            # ...
            st.session_state.file_processed = True
            progress_bar.empty()

    # Seção de exibição do conteúdo e ferramentas
    if st.session_state.get('file_processed'):
        st.write("---")
        st.subheader("Conteúdo do Manuscrito")
        edited_text = st.text_area("Edite seu texto aqui:", st.session_state.text_content, height=500, key="editor")
        if edited_text != st.session_state.text_content:
            st.session_state.text_content = edited_text
        
        st.write("---")
        st.subheader("Ferramentas de Edição e Produção")
        
        cols = st.columns([1, 1, 1, 2]) # Colunas para botões
        with cols[0]:
            if st.button("Analisar Texto"):
                with st.spinner("Analisando..."):
                    st.session_state.analise_resultados = analisar_texto(st.session_state.text_content)
        with cols[1]:
            if st.button("Limpar Texto"):
                with st.spinner("Otimizando texto..."):
                    st.session_state.text_content = limpar_e_otimizar_texto(st.session_state.text_content)
                    st.experimental_rerun()
        with cols[2]:
            if st.button("Gerar Resumo IA"):
                with st.spinner("🤖 A IA está pensando..."):
                    texto_para_resumir = st.session_state.text_content[:15000]
                    st.session_state.resumo_gerado = gerar_resumo_ia(texto_para_resumir)
        with cols[3]:
            # Botão de Download do DOCX
            docx_buffer = gerar_docx_formatado(st.session_state.text_content)
            st.download_button(
                label="Baixar Manuscrito Formatado (.docx)",
                data=docx_buffer,
                file_name="manuscrito_formatado.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary", # Destaca o botão principal
                help="Gera e baixa um arquivo .docx com formatação profissional ABNT/Editorial."
            )

        # --- Seção de Resultados PERSISTENTES ---
        st.write("---")
        if st.session_state.analise_resultados or st.session_state.resumo_gerado:
            st.subheader("Resultados")
            
            # Exibe a análise se ela existir
            if st.session_state.analise_resultados:
                st.write("##### Análise do Texto")
                for metrica, valor in st.session_state.analise_resultados.items():
                    st.metric(label=metrica, value=valor)
            
            # Exibe o resumo se ele existir
            if st.session_state.resumo_gerado:
                st.write("##### Resumo Gerado pela IA")
                st.success(st.session_state.resumo_gerado)
        
            # Botão para limpar todos os resultados
            if st.button("Limpar Resultados"):
                st.session_state.analise_resultados = None
                st.session_state.resumo_gerado = None
                st.experimental_rerun()

    else:
        st.info("Aguardando o carregamento de um arquivo para começar.")

with tab2:
    st.header("Exportar")
    st.info("A principal função de exportação agora é o botão 'Baixar Manuscrito Formatado (.docx)' na aba Manuscrito.")
