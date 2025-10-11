import streamlit as st
import io
import re
import math
import smartypants
import language_tool_python
from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from openai import OpenAI

# --- CONFIGURAÇÃO DA PÁGINA E ESTADO ---
st.set_page_config(page_title="Adapta ONE - MODO DEBUG", page_icon="🐞", layout="wide")

def inicializar_estado():
    chaves_estado = {
        "text_content": "", "file_processed": False,
        "book_title": "Sem Título", "author_name": "Autor Desconhecido", "contact_info": "seuemail@exemplo.com",
        "sugestoes_estilo": None, "api_key_valida": False
    }
    for key, value in chaves_estado.items():
        if key not in st.session_state:
            st.session_state[key] = value

inicializar_estado()

# --- FUNÇÕES DE PROCESSAMENTO ---
@st.cache_resource
def carregar_ferramenta_gramatical():
    try: return language_tool_python.LanguageTool('pt-BR')
    except: return None

def aplicar_correcoes_automaticas(texto: str, ferramenta) -> str:
    if not ferramenta: return texto
    return ferramenta.correct(texto)

def gerar_sugestoes_estilo_ia(texto: str, client: OpenAI):
    prompt = f"Analise o texto como um editor sênior. Forneça 3-5 sugestões concisas para melhorar estilo, clareza e impacto. Comece cada uma com 'Sugestão:'."
    try:
        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"{prompt}\n---{texto[:15000]}"}], temperature=0.5)
        sugestoes = response.choices[0].message.content.split('Sugestão:')
        return [s.strip() for s in sugestoes if s.strip()]
    except Exception as e:
        return [f"Erro na chamada à IA: {e}"]

def gerar_manuscrito_profissional_docx(titulo: str, autor: str, contato: str, texto_manuscrito: str):
    texto_limpo = smartypants.smartypants(texto_manuscrito, 2)
    document = Document()
    buffer = io.BytesIO()
    # Código da função omitido para focar no debug, mas ele existe
    document.save(buffer)
    buffer.seek(0)
    return buffer

# --- FUNÇÃO DE CALLBACK PARA DEBUG ---
def processar_arquivo_carregado_DEBUG():
    st.warning("DEBUG: 1. Função 'processar_arquivo_carregado_DEBUG' foi chamada.")
    
    uploaded_file = st.session_state.get('file_uploader_key')
    if not uploaded_file:
        st.error("DEBUG: 1.1. A função foi chamada, mas 'st.session_state.file_uploader_key' está VAZIO. Isso não deveria acontecer.")
        return

    st.warning(f"DEBUG: 2. Arquivo detectado: {uploaded_file.name}, Tamanho: {uploaded_file.size} bytes.")
    
    try:
        text = ""
        if uploaded_file.name.endswith('.txt'):
            st.warning("DEBUG: 3. Detectado arquivo .txt. Tentando decodificar...")
            text = io.StringIO(uploaded_file.getvalue().decode("utf-8")).read()
        
        elif uploaded_file.name.endswith('.docx'):
            st.warning("DEBUG: 3. Detectado arquivo .docx. Tentando ler com python-docx...")
            doc = Document(io.BytesIO(uploaded_file.read()))
            
            # Ponto de investigação crucial
            paragrafos = [p.text for p in doc.paragraphs]
            st.warning(f"DEBUG: 3.1. Extração de parágrafos concluída. Total de parágrafos encontrados: {len(paragrafos)}")
            st.info("DEBUG: Conteúdo bruto dos parágrafos extraídos (em formato JSON):")
            st.json(paragrafos) # Exibe a lista de parágrafos

            text = "\n\n".join([p for p in paragrafos if p.strip()])
        
        st.warning(f"DEBUG: 4. Processamento finalizado. O texto extraído tem {len(text)} caracteres.")
        if not text:
            st.error("DEBUG: 4.1. ALERTA! O texto final está VAZIO após a leitura do arquivo.")
        
        st.session_state.text_content = text
        st.session_state.file_processed = True
        st.session_state.sugestoes_estilo = None
        st.success("DEBUG: 5. 'st.session_state.text_content' foi atualizado com sucesso.")

    except Exception as e:
        st.error(f"DEBUG: X. OCORREU UM ERRO GRAVE DURANTE O PROCESSAMENTO: {e}")
        import traceback
        st.code(traceback.format_exc())
        st.session_state.text_content = "Falha ao ler o arquivo."
        st.session_state.file_processed = False


# --- INTERFACE DO USUÁRIO ---
st.title("Adapta ONE - MODO DEBUG 🐞")

# --- ÁREA DE DEBUGGING VISÍVEL ---
with st.expander("PAINEL DE CONTROLE DE DEBUG", expanded=True):
    st.header("Estado Atual da Sessão")
    st.info("Este painel mostra o que está na memória do aplicativo em tempo real, a cada recarga da página.")
    
    st.write("**Conteúdo atual de `st.session_state.text_content`:**")
    st.text(st.session_state.get('text_content', 'Variável ainda não existe.'))

# --- SIDEBAR ---
with st.sidebar:
    st.header("Informações do Manuscrito")
    st.session_state.book_title = st.text_input("Título do Livro", st.session_state.book_title)
    st.session_state.author_name = st.text_input("Nome do Autor(a)", st.session_state.author_name)
    st.session_state.contact_info = st.text_input("Email ou Contato", st.session_state.contact_info)
    
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
tab1, tab2, tab3 = st.tabs(["1. Escrever & Editar", "2. Sugestões de Estilo (Opcional)", "3. Finalizar & Baixar"])

with tab1:
    st.subheader("Cole ou Faça o Upload do seu Manuscrito")
    st.file_uploader(
        "Formatos: .txt, .docx",
        type=["txt", "docx"],
        key="file_uploader_key",
        on_change=processar_arquivo_carregado_DEBUG # Chamando a versão de debug
    )

    st.subheader("Editor Principal")
    st.text_area(
        "Seu texto aparecerá aqui...",
        value=st.session_state.text_content,
        height=600,
        key="editor_principal"
    )

with tab2:
    st.header("Assistente de Escrita com IA (Opcional)")
    # Código da aba 2 omitido para simplicidade

with tab3:
    st.header("Finalize e Exporte seu Manuscrito Profissional")
    # Código da aba 3 omitido para simplicidade
