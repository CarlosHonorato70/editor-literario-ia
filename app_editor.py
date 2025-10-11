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

# --- CONFIGURAÇÃO DA PÁGINA E ESTADO DA SESSÃO ---
st.set_page_config(page_title="Adapta ONE - Editor Editorial Completo", page_icon="📚", layout="wide")

def inicializar_estado():
    # Inicializa todas as chaves necessárias para evitar erros
    chaves_estado = {
        "text_content": "", "file_processed": False, "last_uploaded_file_id": None,
        "book_title": "Sem Título", "author_name": "Autor Desconhecido",
        "correcoes_gramaticais": None, "sugestoes_estilo": None,
        "metadados_gerados": None, "api_key_valida": False
    }
    for key, value in chaves_estado.items():
        if key not in st.session_state:
            st.session_state[key] = value

inicializar_estado()

# --- FUNÇÕES DE PROCESSAMENTO (O "CÉREBRO" DO APP) ---

@st.cache_resource
def carregar_ferramenta_gramatical():
    """Carrega o modelo de linguagem (pesado) apenas uma vez para otimizar."""
    try:
        return language_tool_python.LanguageTool('pt-BR')
    except Exception as e:
        st.error(f"Falha ao carregar o revisor gramatical: {e}")
        return None

def limpar_e_otimizar_tipografia(texto: str) -> str:
    """Aplica aspas curvas, travessões e outras melhorias tipográficas."""
    texto = smartypants.smartypants(texto, 2)
    texto = re.sub(r'^\s*-\s+', '— ', texto, flags=re.MULTILINE)
    texto = re.sub(r' +', ' ', texto)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto.strip()

def revisar_gramatica_estilo(texto: str, ferramenta):
    if not ferramenta: return []
    return ferramenta.check(texto)

def gerar_sugestoes_estilo_ia(texto: str, client: OpenAI):
    prompt = f"""
    Analise o seguinte trecho de texto como um editor literário sênior.
    Forneça 3 a 5 sugestões concisas para melhorar o estilo, clareza, concisão ou impacto.
    Identifique também possíveis inconsistências simples (ex: "Maria" vs "Marta").
    Apresente cada sugestão em um novo parágrafo, começando com 'Sugestão:'.

    Texto:
    ---
    {texto[:15000]}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        sugestoes = response.choices[0].message.content.split('Sugestão:')
        return [s.strip() for s in sugestoes if s.strip()]
    except Exception as e:
        st.error(f"Ocorreu um erro ao chamar a IA para análise de estilo: {e}")
        return ["Não foi possível gerar as sugestões de estilo. Verifique sua chave de API e a conexão."]

def gerar_metadados_ia(texto: str, client: OpenAI):
    prompt = f"""
    Com base no manuscrito a seguir, gere os seguintes metadados para um livro:
    1. Título Sugerido: [Um título criativo e relevante]
    2. Palavras-chave: [Uma lista de 5 a 7 palavras-chave separadas por vírgula]
    3. Sinopse (150 palavras): [Uma sinopse envolvente para a contracapa]

    Manuscrito:
    ---
    {texto[:15000]}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        titulo_match = re.search(r"Título Sugerido: (.*?)\n", content, re.IGNORECASE)
        titulo = titulo_match.group(1).strip() if titulo_match else "Não foi possível extrair o título."
        palavras_chave_match = re.search(r"Palavras-chave: (.*?)\n", content, re.IGNORECASE)
        palavras_chave = palavras_chave_match.group(1).strip() if palavras_chave_match else "Não foi possível extrair as palavras-chave."
        sinopse_match = re.search(r"Sinopse(?: \(150 palavras\))?: (.*)", content, re.DOTALL | re.IGNORECASE)
        sinopse = sinopse_match.group(1).strip() if sinopse_match else "Não foi possível extrair a sinopse. Resposta completa da IA: " + content
        return {"titulo": titulo, "palavras_chave": palavras_chave, "sinopse": sinopse}
    except Exception as e:
        st.error(f"Ocorreu um erro ao chamar a IA para geração de metadados: {e}")
        return {"titulo": "Erro", "palavras_chave": "Erro", "sinopse": f"Falha ao se comunicar com a API. Verifique sua chave e a conexão."}

def gerar_manuscrito_final_docx(titulo: str, autor: str, texto_manuscrito: str):
    texto_final = limpar_e_otimizar_tipografia(texto_manuscrito)
    document = Document()
    for section in document.sections:
        section.top_margin = section.bottom_margin = section.left_margin = section.right_margin = Inches(1)
    document.add_paragraph(titulo.upper(), style='Title').runs[0].font.size = Pt(16)
    document.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_paragraph(f"\n\npor\n\n{autor}").alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_page_break()
    style = document.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    style.paragraph_format.first_line_indent = Cm(1.25)
    for para_texto in texto_final.split('\n\n'):
        if para_texto.strip(): document.add_paragraph(para_texto.strip())
    for section in document.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        fld_char_1 = OxmlElement('w:fldChar')
        fld_char_1.set(qn('w:fldCharType'), 'begin')
        instr_text = OxmlElement('w:instrText')
        instr_text.set(qn('xml:space'), 'preserve')
        instr_text.text = 'PAGE'
        fld_char_2 = OxmlElement('w:fldChar')
        fld_char_2.set(qn('w:fldCharType'), 'end')
        p.add_run()._r.append(fld_char_1)
        p.add_run()._r.append(instr_text)
        p.add_run()._r.append(fld_char_2)
    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFACE DO USUÁRIO (FRONTEND) ---
st.title("Adapta ONE - Editor Literário IA ��")
st.markdown("Transforme seu rascunho em um manuscrito profissional pronto para publicação.")

with st.sidebar:
    st.header("Configuração do Projeto")
    st.session_state.book_title = st.text_input("Título do Livro", st.session_state.book_title)
    st.session_state.author_name = st.text_input("Nome do Autor(a)", st.session_state.author_name)
    st.divider()
    st.header("Chave da OpenAI")
    api_key = st.text_input("Sua API Key", type="password", help="Necessária para as funções de análise de estilo e metadados.")
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            client.models.list()
            st.session_state.api_key_valida = True
            st.session_state.openai_client = client
            st.success("API Key válida!")
        except Exception:
            st.error("API Key inválida ou erro de conexão.")
            st.session_state.api_key_valida = False
    st.divider()
    st.header("Sobre")
    st.info("**Privacidade**: Seus textos são processados em memória e não são armazenados em nossos servidores.", icon="🛡️")
    st.markdown("[Reportar um problema ou dar feedback](mailto:seu-email-de-suporte@exemplo.com)")

tab1, tab2, tab3 = st.tabs(["1. Upload & Edição", "2. Revisão & IA", "3. Exportação Final"])

with tab1:
    st.subheader("Faça o upload do seu manuscrito")
    uploaded_file = st.file_uploader("Formatos aceitos: .txt, .docx", type=["txt", "docx"])
    if uploaded_file:
        current_file_id = f"{uploaded_file.name}-{uploaded_file.size}"
        if st.session_state.last_uploaded_file_id != current_file_id:
            st.session_state.last_uploaded_file_id = current_file_id
            st.session_state.correcoes_gramaticais = None
            st.session_state.sugestoes_estilo = None
            st.session_state.metadados_gerados = None
            with st.spinner("Processando arquivo..."):
                if uploaded_file.name.endswith('.txt'):
                    st.session_state.text_content = io.StringIO(uploaded_file.getvalue().decode("utf-8")).read()
                else:
                    doc = Document(io.BytesIO(uploaded_file.read()))
                    st.session_state.text_content = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            st.session_state.file_processed = True
    if st.session_state.file_processed:
        st.subheader("Editor de Manuscrito")
        edited_text = st.text_area("Faça ajustes finos no seu texto aqui:", value=st.session_state.text_content, height=600)
        if edited_text != st.session_state.text_content:
            st.session_state.text_content = edited_text

with tab2:
    if not st.session_state.file_processed:
        st.warning("Por favor, carregue um arquivo na aba '1. Upload & Edição' primeiro.")
    else:
        st.header("Ferramentas de Revisão")
        if st.button("Revisar Ortografia e Gramática", use_container_width=True):
            tool = carregar_ferramenta_gramatical()
            if tool:
                with st.spinner("Analisando seu texto em busca de erros..."):
                    st.session_state.correcoes_gramaticais = revisar_gramatica_estilo(st.session_state.text_content, tool)
            else:
                st.error("Ferramenta de revisão não pôde ser carregada.")
        if st.session_state.correcoes_gramaticais is not None:
            with st.expander(f"Resultados da Revisão ({len(st.session_state.correcoes_gramaticais)} problemas encontrados)", expanded=True):
                if not st.session_state.correcoes_gramaticais:
                    st.success("Nenhum erro gramatical encontrado. Ótimo trabalho!")
                for erro in st.session_state.correcoes_gramaticais:
                    st.error(f"**Problema:** {erro.message}", icon="❗")
                    st.caption(f"Trecho: ...{erro.context}... | Sugestões: {', '.join(erro.replacements)}")
        st.divider()
        st.header("Assistente de Escrita com IA")
        if not st.session_state.api_key_valida:
            st.warning("Insira uma chave de API válida da OpenAI na barra lateral para usar as ferramentas de IA.")
        else:
            col_ia1, col_ia2 = st.columns(2)
            with col_ia1:
                if st.button("Analisar Estilo e Coerência (IA)", use_container_width=True):
                    with st.spinner("IA está lendo seu texto para dar sugestões de estilo..."):
                        st.session_state.sugestoes_estilo = gerar_sugestoes_estilo_ia(st.session_state.text_content, st.session_state.openai_client)
            with col_ia2:
                if st.button("Gerar Metadados (IA)", use_container_width=True):
                    with st.spinner("IA está criando uma sinopse, título e palavras-chave..."):
                        st.session_state.metadados_gerados = gerar_metadados_ia(st.session_state.text_content, st.session_state.openai_client)
            if st.session_state.sugestoes_estilo:
                with st.expander("Sugestões de Estilo e Coerência da IA", expanded=False):
                    for sugestao in st.session_state.sugestoes_estilo:
                        st.info(sugestao.strip(), icon="��")
            if st.session_state.metadados_gerados:
                with st.expander("Metadados Gerados pela IA", expanded=False):
                    st.text_input("Título Sugerido", value=st.session_state.metadados_gerados['titulo'])
                    # --- LINHA CORRIGIDA ---
                    st.text_input("Palavras-chave Sugeridas", value=st.session_state.metadados_gerados['palavras_chave'])
                    st.text_area("Sinopse Sugerida", value=st.session_state.metadados_gerados['sinopse'], height=200)

with tab3:
    if not st.session_state.file_processed:
        st.warning("Por favor, carregue e edite seu arquivo nas abas anteriores.")
    else:
        st.header("Seu Manuscrito está Pronto para Exportação")
        st.success("O arquivo .docx final incluirá todas as formatações profissionais, como página de rosto, numeração de página, margens e recuo de parágrafo.")
        if st.session_state.text_content:
            docx_buffer = gerar_manuscrito_final_docx(st.session_state.book_title, st.session_state.author_name, st.session_state.text_content)
            st.download_button(
                label="BAIXAR MANUSCRITO FINAL (.DOCX)",
                data=docx_buffer,
                file_name=f"{st.session_state.book_title}_ProntoParaEditora.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
                help="Gera e baixa o arquivo .docx com formatação completa."
            )
