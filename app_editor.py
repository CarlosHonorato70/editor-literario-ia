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
st.set_page_config(page_title="Adapta ONE - Editor Profissional", page_icon="✒️", layout="wide")

def inicializar_estado():
    chaves_estado = {
        "text_content": "", "file_processed": False, "last_uploaded_file_id": None,
        "book_title": "Sem Título", "author_name": "Autor Desconhecido", "contact_info": "seuemail@exemplo.com",
        "sugestoes_estilo": None, "api_key_valida": False
    }
    for key, value in chaves_estado.items():
        if key not in st.session_state:
            st.session_state[key] = value

inicializar_estado()

# --- FUNÇÕES DE PROCESSAMENTO (O "CÉREBRO" DO APP) ---

@st.cache_resource
def carregar_ferramenta_gramatical():
    try:
        return language_tool_python.LanguageTool('pt-BR')
    except Exception as e:
        st.error(f"Falha ao carregar o revisor gramatical: {e}")
        return None

# ★ NOVA FUNÇÃO DE AUTOMAÇÃO ★
def aplicar_correcoes_automaticas(texto: str, ferramenta) -> str:
    """Aplica correções gramaticais e ortográficas diretas e inequívocas."""
    if not ferramenta: return texto
    # O método .correct() aplica as melhores sugestões automaticamente
    return ferramenta.correct(texto)

def gerar_sugestoes_estilo_ia(texto: str, client: OpenAI):
    # (Esta função permanece a mesma, pois o estilo é subjetivo e precisa da aprovação do autor)
    prompt = f"Analise o texto como um editor sênior. Forneça 3-5 sugestões concisas para melhorar estilo, clareza e impacto. Comece cada uma com 'Sugestão:'."
    try:
        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"{prompt}\n---{texto[:15000]}"}], temperature=0.5)
        sugestoes = response.choices[0].message.content.split('Sugestão:')
        return [s.strip() for s in sugestoes if s.strip()]
    except Exception as e:
        st.error(f"Erro ao chamar a IA para análise de estilo: {e}")
        return ["Não foi possível gerar sugestões."]

# ★ NOVA FUNÇÃO DE APRESENTAÇÃO PROFISSIONAL ★
def gerar_manuscrito_profissional_docx(titulo: str, autor: str, contato: str, texto_manuscrito: str):
    """Gera um DOCX com formatação profissional completa, incluindo cabeçalhos e quebras de cena."""
    
    # 1. Limpeza Tipográfica Inicial
    texto_limpo = smartypants.smartypants(texto_manuscrito, 2)
    texto_limpo = re.sub(r'^\s*-\s+', '— ', texto_limpo, flags=re.MULTILINE)
    texto_limpo = re.sub(r' +', ' ', texto_limpo)
    
    document = Document()
    
    # 2. Configurações Globais do Documento
    for section in document.sections:
        section.top_margin = section.bottom_margin = section.left_margin = section.right_margin = Inches(1)
        
        # Criação do Cabeçalho Profissional
        header = section.header
        p_header = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        p_header.text = f"{autor.split(' ')[-1]} / {titulo} / "
        p_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Adiciona o campo de número da página ao final do cabeçalho
        fld_char_1 = OxmlElement('w:fldChar')
        fld_char_1.set(qn('w:fldCharType'), 'begin')
        instr_text = OxmlElement('w:instrText')
        instr_text.set(qn('xml:space'), 'preserve')
        instr_text.text = 'PAGE'
        fld_char_2 = OxmlElement('w:fldChar')
        fld_char_2.set(qn('w:fldCharType'), 'end')
        
        # Adiciona os elementos ao parágrafo do cabeçalho
        run = p_header.add_run()
        run._r.append(fld_char_1)
        run._r.append(instr_text)
        run._r.append(fld_char_2)
    
    # 3. Página de Rosto Aprimorada
    p_autor_contato = document.add_paragraph(f"{autor}\n{contato}")
    p_autor_contato.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    
    contagem_palavras = len(texto_manuscrito.split())
    p_palavras = document.add_paragraph(f"Aproximadamente {math.ceil(contagem_palavras / 100.0) * 100:,} palavras")
    p_palavras.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    
    p_titulo = document.add_paragraph(f"\n\n\n\n{titulo}")
    p_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_titulo.runs[0].font.bold = True
    p_titulo.runs[0].font.size = Pt(16)
    
    document.add_page_break()
    
    # 4. Estilo do Corpo do Texto
    style = document.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    style.paragraph_format.first_line_indent = Cm(1.25)
    
    # 5. Processamento do Texto com Lógica de Quebra de Cena
    for para_texto in texto_limpo.split('\n'):
        para_strip = para_texto.strip()
        if not para_strip:
            continue
        
        # Lógica para Quebra de Cena
        if para_strip in ['#', '***']:
            p_quebra = document.add_paragraph(para_strip)
            p_quebra.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_quebra.paragraph_format.first_line_indent = None
        else:
            document.add_paragraph(para_strip)
            
    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFACE DO USUÁRIO ---
st.title("Adapta ONE - Editor Profissional ✒️")
st.markdown("**A evolução da preparação de manuscritos.** Carregue seu texto, faça ajustes e, com um clique, obtenha um manuscrito profissional e revisado.")

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
            client = OpenAI(api_key=api_key)
            client.models.list()
            st.session_state.api_key_valida = True
            st.session_state.openai_client = client
            st.success("API Key válida!")
        except Exception:
            st.error("API Key inválida.")
            st.session_state.api_key_valida = False

# --- ABAS DE FLUXO DE TRABALHO ---
tab1, tab2, tab3 = st.tabs(["1. Escrever & Editar", "2. Sugestões de Estilo (Opcional)", "3. Finalizar & Baixar"])

with tab1:
    st.subheader("Cole ou Faça o Upload do seu Manuscrito")
    uploaded_file = st.file_uploader("Formatos: .txt, .docx", type=["txt", "docx"])
    if uploaded_file:
        # Lógica de upload... (igual à anterior)
        with st.spinner("Processando..."):
            if uploaded_file.name.endswith('.txt'):
                st.session_state.text_content = io.StringIO(uploaded_file.getvalue().decode("utf-8")).read()
            else:
                doc = Document(io.BytesIO(uploaded_file.read()))
                st.session_state.text_content = "\n\n".join([p.text for p in doc.paragraphs])
        st.session_state.file_processed = True

    st.subheader("Editor Principal")
    edited_text = st.text_area("Seu texto vive aqui. Faça os ajustes necessários antes de finalizar.", value=st.session_state.text_content, height=600, key="editor_principal")
    if edited_text != st.session_state.text_content:
        st.session_state.text_content = edited_text

with tab2:
    st.header("Assistente de Escrita com IA (Opcional)")
    st.info("Use esta ferramenta para obter ideias e refinar seu estilo. Nenhuma mudança é aplicada automaticamente aqui.")
    if not st.session_state.api_key_valida:
        st.warning("Insira uma chave de API válida da OpenAI na barra lateral para usar esta função.")
    elif not st.session_state.text_content:
        st.info("Escreva ou carregue um texto na primeira aba para começar.")
    else:
        if st.button("Analisar Estilo e Coerência (IA)", use_container_width=True):
            with st.spinner("IA está lendo seu texto..."):
                st.session_state.sugestoes_estilo = gerar_sugestoes_estilo_ia(st.session_state.text_content, st.session_state.openai_client)
        
        if st.session_state.sugestoes_estilo:
            st.subheader("Sugestões da IA")
            for sugestao in st.session_state.sugestoes_estilo:
                st.info(sugestao, icon="💡")

with tab3:
    st.header("Finalize e Exporte seu Manuscrito Profissional")
    if not st.session_state.text_content:
        st.warning("Não há texto para finalizar. Escreva ou carregue seu manuscrito na primeira aba.")
    else:
        st.markdown("""
        **O que este botão faz?**
        1.  **Revisão Automática:** Aplica centenas de correções ortográficas e gramaticais comuns.
        2.  **Formatação Profissional:** Gera um arquivo `.docx` com:
            *   Página de rosto completa (autor, contato, título, contagem de palavras).
            *   Cabeçalho em todas as páginas com `Sobrenome / Título / Página`.
            *   Formatação padrão da indústria (fonte, espaçamento, margens).
            *   Identificação automática de quebras de cena (`#` ou `***`).
        """)
        
        if st.button("Revisão Automática & Download Profissional (.DOCX)", type="primary", use_container_width=True):
            with st.spinner("Automatizando revisões e montando seu manuscrito profissional... Isso pode levar um momento."):
                tool = carregar_ferramenta_gramatical()
                
                # ★ A MÁGICA DA AUTOMAÇÃO ACONTECE AQUI ★
                texto_corrigido = aplicar_correcoes_automaticas(st.session_state.text_content, tool)
                
                docx_buffer = gerar_manuscrito_profissional_docx(
                    st.session_state.book_title,
                    st.session_state.author_name,
                    st.session_state.contact_info,
                    texto_corrigido
                )
                
                st.success("Manuscrito finalizado! O download começará em breve.")
                
                # Botão de download aparece após o processamento
                st.download_button(
                    label="Download Falhou? Clique aqui para tentar novamente.",
                    data=docx_buffer,
                    file_name=f"{st.session_state.book_title}_ManuscritoProfissional.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
