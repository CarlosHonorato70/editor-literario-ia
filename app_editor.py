import streamlit as st
import io
import time
import re
import math
import smartypants
import language_tool_python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from openai import OpenAI

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Adapta ONE - Editor Editorial Completo", page_icon="📚", layout="wide")

# --- FUNÇÕES DE LÓGICA ---

@st.cache_resource
def carregar_ferramenta_gramatical():
    """Carrega o modelo de linguagem (pesado) apenas uma vez."""
    return language_tool_python.LanguageTool('pt-BR')

def analisar_texto(texto: str):
    if not texto: return None
    palavras = texto.split()
    return {"Contagem de Palavras": len(palavras), "Contagem de Caracteres": len(texto), "Tempo de Leitura (aprox.)": f"{math.ceil(len(palavras) / 225)} min"}

def gerar_resumo_ia(texto: str):
    if not texto: return "Erro: Não há texto para resumir."
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente editorial. Crie resumos concisos e impactantes."},
                {"role": "user", "content": f"Resuma o seguinte trecho em um único parágrafo:\n\n{texto}"}
            ],
            temperature=0.7, max_tokens=250
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ocorreu um erro ao conectar com a IA: {e}"

def revisar_gramatica_estilo(texto: str, ferramenta):
    if not texto: return None
    return ferramenta.check(texto)

def limpar_e_otimizar_texto(texto: str) -> str:
    texto = texto.replace('\r\n', '\n').replace('\r', '\n')
    texto = re.sub(r' +', ' ', texto)
    texto = smartypants.smartypants(texto, 2) # Attr 2 para aspas e travessões
    texto = re.sub(r'^\s*-\s+', '— ', texto, flags=re.MULTILINE)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto.strip()

def gerar_manuscrito_final_docx(titulo: str, autor: str, texto_manuscrito: str):
    texto_limpo = limpar_e_otimizar_texto(texto_manuscrito)
    document = Document()

    # --- Página de Rosto ---
    p_titulo = document.add_paragraph()
    p_titulo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runner = p_titulo.add_run(titulo.upper())
    runner.font.name = 'Times New Roman'
    runner.font.size = Pt(16)
    runner.bold = True
    
    document.add_paragraph() # Espaçamento
    
    p_autor = document.add_paragraph()
    p_autor.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runner_autor = p_autor.add_run(autor)
    runner_autor.font.name = 'Times New Roman'
    runner_autor.font.size = Pt(12)

    document.add_page_break()

    # --- Corpo do Texto ---
    style = document.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    style.paragraph_format.first_line_indent = Cm(1.25)
    style.paragraph_format.space_after = Pt(0)
    
    paragrafos = texto_limpo.split('\n\n')
    for para_texto in paragrafos:
        if para_texto.strip():
            document.add_paragraph(para_texto.strip())

    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFACE DO USUÁRIO ---

st.title("Adapta ONE - Editor Editorial Completo 📚")
st.markdown("Carregue seu manuscrito, utilize as ferramentas de IA e revisão, e baixe a versão final pronta para publicação.")

# --- Barra Lateral para Informações do Livro ---
with st.sidebar:
    st.header("Informações do Manuscrito")
    st.session_state.book_title = st.text_input("Título do Livro", st.session_state.get("book_title", "Sem Título"))
    st.session_state.author_name = st.text_input("Nome do Autor(a)", st.session_state.get("author_name", "Autor Desconhecido"))
    st.divider()
    st.info("O título e o autor serão usados na página de rosto do documento final.")

# --- Inicialização do Estado da Sessão ---
if 'text_content' not in st.session_state: st.session_state.text_content = ""
if 'file_processed' not in st.session_state: st.session_state.file_processed = False
if 'last_uploaded_file_id' not in st.session_state: st.session_state.last_uploaded_file_id = None
if 'resumo_gerado' not in st.session_state: st.session_state.resumo_gerado = None
if 'analise_resultados' not in st.session_state: st.session_state.analise_resultados = None
if 'correcoes_gramaticais' not in st.session_state: st.session_state.correcoes_gramaticais = None

# --- Upload e Área de Edição ---
uploaded_file = st.file_uploader("1. Carregue seu arquivo (.txt ou .docx)", type=["txt", "docx"])

if uploaded_file is not None:
    current_file_id = f"{uploaded_file.name}-{uploaded_file.size}"
    if st.session_state.last_uploaded_file_id != current_file_id:
        st.session_state.last_uploaded_file_id = current_file_id
        # Limpa todos os resultados antigos ao carregar um novo arquivo
        st.session_state.resumo_gerado = None
        st.session_state.analise_resultados = None
        st.session_state.correcoes_gramaticais = None
        with st.spinner("Processando arquivo..."):
            if uploaded_file.name.endswith('.txt'):
                st.session_state.text_content = io.StringIO(uploaded_file.getvalue().decode("utf-8")).read()
            elif uploaded_file.name.endswith('.docx'):
                doc = Document(io.BytesIO(uploaded_file.read()))
                st.session_state.text_content = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            st.session_state.file_processed = True

if st.session_state.file_processed:
    st.text_area("Seu Manuscrito (editável):", value=st.session_state.text_content, height=500, key="editor_texto")
    st.session_state.text_content = st.session_state.editor_texto # Atualiza o estado com as edições

    st.divider()
    st.header("2. Ferramentas de Análise e Revisão")

    cols_botoes = st.columns(3)
    with cols_botoes[0]:
        if st.button("Analisar Texto"):
            with st.spinner("Analisando métricas..."):
                st.session_state.analise_resultados = analisar_texto(st.session_state.text_content)
    with cols_botoes[1]:
        if st.button("Revisar Gramática e Estilo"):
            with st.spinner("Buscando por erros e sugestões..."):
                tool = carregar_ferramenta_gramatical()
                st.session_state.correcoes_gramaticais = revisar_gramatica_estilo(st.session_state.text_content, tool)
    with cols_botoes[2]:
        if st.button("Gerar Resumo (IA)"):
            with st.spinner("🤖 A IA está lendo seu texto para criar um resumo..."):
                st.session_state.resumo_gerado = gerar_resumo_ia(st.session_state.text_content[:15000])

    # --- Área de Resultados Persistentes com Expanders ---
    if st.session_state.analise_resultados or st.session_state.correcoes_gramaticais or st.session_state.resumo_gerado:
        st.subheader("Resultados")
        
        if st.session_state.analise_resultados:
            with st.expander("Análise do Texto", expanded=True):
                for metrica, valor in st.session_state.analise_resultados.items():
                    st.metric(label=metrica, value=valor)
        
        if st.session_state.correcoes_gramaticais:
            with st.expander(f"Revisão Gramatical ({len(st.session_state.correcoes_gramaticais)} problemas encontrados)", expanded=True):
                for erro in st.session_state.correcoes_gramaticais:
                    st.markdown(f"- **Problema:** {erro.message} (Regra: `{erro.ruleId}`)")
                    st.markdown(f"  - **No trecho:** `...{erro.context}...`")
                    if erro.replacements:
                        st.markdown(f"  - **Sugestões:** {', '.join(erro.replacements)}")
                    st.divider()

        if st.session_state.resumo_gerado:
            with st.expander("Resumo Gerado pela IA", expanded=True):
                st.success(st.session_state.resumo_gerado)
    
    st.divider()
    st.header("3. Baixar o Manuscrito Final")
    
    # --- Botão de Download Final ---
    if st.session_state.text_content:
        docx_buffer = gerar_manuscrito_final_docx(st.session_state.book_title, st.session_state.author_name, st.session_state.text_content)
        st.download_button(
            label="BAIXAR MANUSCRITO FINAL (.DOCX)",
            data=docx_buffer,
            file_name=f"{st.session_state.book_title}_formatado.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
            use_container_width=True
        )
else:
    st.info("Aguardando o carregamento de um arquivo para começar a mágica.")
