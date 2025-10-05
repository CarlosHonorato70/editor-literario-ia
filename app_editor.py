import os
import streamlit as st
from openai import OpenAI
from docx import Document
from io import BytesIO
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import requests
from docx.enum.style import WD_STYLE_TYPE
import time
from typing import Optional, Dict, Tuple, Any, List
import math
import json
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from stqdm import stqdm

# --- CONFIGURAÇÃO DE CONSTANTES ---

# 1. DICIONÁRIO DE TAMANHOS KDP/GRÁFICA (Miolo)
KDP_SIZES: Dict[str, Dict] = {
    "Padrão EUA (6x9 in)": {"name": "6 x 9 in", "width_in": 6.0, "height_in": 9.0, "width_cm": 15.24, "height_cm": 22.86, "papel_fator": 0.00115},
    "Padrão A5 (5.83x8.27 in)": {"name": "A5 (14.8 x 21 cm)", "width_in": 5.83, "height_in": 8.27, "width_cm": 14.8, "height_cm": 21.0, "papel_fator": 0.00115},
    "Pocket (5x8 in)": {"name": "5 x 8 in", "width_in": 5.0, "height_in": 8.0, "width_cm": 12.7, "height_cm": 20.32, "papel_fator": 0.00115},
    "Maior (7x10 in)": {"name": "7 x 10 in", "width_in": 7.0, "height_in": 10.0, "width_cm": 17.78, "height_cm": 25.4, "papel_fator": 0.00115},
}

# 2. TEMPLATES DE ESTILO DE DIAGRAMAÇÃO (Ficção e Acadêmico)
STYLE_TEMPLATES: Dict[str, Dict] = {
    "Romance Clássico (Garamond)": {"font_name": "Garamond", "font_size_pt": 11, "line_spacing": 1.15, "indent": 0.5},
    "Thriller Moderno (Droid Serif)": {"font_name": "Droid Serif", "font_size_pt": 10, "line_spacing": 1.05, "indent": 0.3},
    "Acadêmico/ABNT (Times New Roman 12)": {"font_name": "Times New Roman", "font_size_pt": 12, "line_spacing": 1.5, "indent": 0.0},
}

# 3. CONFIGURAÇÃO DA IA
API_KEY_NAME = "OPENAI_API_KEY"
PROJECT_ID_NAME = "OPENAI_PROJECT_ID"
MODEL_NAME = "gpt-4o-mini"

# --- CONFIGURAÇÃO SEGURA DAS CHAVES ---
os.environ[API_KEY_NAME] = "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"
os.environ[PROJECT_ID_NAME] = "proj_cJeNgv5MxhOLW7SmpKxzF9wb"

# --- INICIALIZAÇÃO DA IA E LAYOUT ---
st.set_page_config(page_title="Editor Pro IA", layout="wide", initial_sidebar_state="expanded")
st.title("🚀 Editor Pro IA: Publicação Sem Complicações")
st.subheader("Transforme seu manuscrito em um livro profissional, pronto para ABNT e KDP.")

# Variáveis globais para rastrear o status da API
client: Optional[OpenAI] = None
API_KEY: Optional[str] = None
PROJECT_ID: Optional[str] = None
is_api_ready: bool = False

def initialize_openai_client():
    """Inicializa o cliente OpenAI e verifica a disponibilidade da API."""
    global client, API_KEY, PROJECT_ID, is_api_ready
    try:
        API_KEY = os.environ.get(API_KEY_NAME)
        PROJECT_ID = os.environ.get(PROJECT_ID_NAME)

        if API_KEY and PROJECT_ID:
            client = OpenAI(api_key=API_KEY, project=PROJECT_ID)
            is_api_ready = True
            st.sidebar.success("✅ Conexão OpenAI Pronta!")
        else:
            st.sidebar.error("❌ Conexão OpenAI Inativa.")
            st.warning("Chave e ID do Projeto OpenAI não configurados. A revisão e a geração de capa **NÃO** funcionarão.")
            is_api_ready = False

    except Exception as e:
        st.error(f"Erro na inicialização do ambiente. Detalhes: {e}")
        client = None
        is_api_ready = False

initialize_openai_client()

# --- FUNÇÕES DE AUXÍLIO ---

def call_openai_api(system_prompt: str, user_content: str, max_tokens: int = 3000, retries: int = 5) -> str:
    """
    Função genérica para chamar a API da OpenAI com backoff exponencial.
    """
    global client, is_api_ready

    if not is_api_ready or client is None:
        return "[ERRO DE CONEXÃO DA API] Chaves OPENAI_API_KEY e/ou OPENAI_PROJECT_ID não configuradas."

    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_msg = str(e)

            if "Invalid API key" in error_msg or "Error code: 401" in error_msg:
                st.error("ERRO DE AUTENTICAÇÃO: Sua chave de API está incorreta ou expirada.")
                return "[ERRO DE CONEXÃO DA API] Chave de API Inválida."

            elif i < retries - 1:
                wait_time = 2 ** i
                st.warning(f"Erro de API/Rede. Tentando novamente em {wait_time} segundos... (Tentativa {i+1}/{retries})")
                time.sleep(wait_time)
            else:
                st.error(f"Falha ao se comunicar com a OpenAI após {retries} tentativas. Detalhes: {e}")
                return f"[ERRO DE CONEXÃO DA API] Falha: {e}"

    return "[ERRO DE CONEXÃO DA API] Tentativas de conexão esgotadas."

def run_fast_process_with_timer(message: str, func: callable, *args: Any, **kwargs: Any) -> Tuple[str, float]:
    """Executa uma função, mede o tempo e exibe feedback ao usuário."""
    start_time = time.time()

    with st.spinner(f"⏳ {message}..."):
        result = func(*args, **kwargs)

    duration = round(time.time() - start_time, 1)

    if "[ERRO DE CONEXÃO DA API]" in str(result):
        st.error(f"❌ {message} falhou em **{duration}s**. Verifique o log de erros.")
        return result, duration
    else:
        st.success(f"✅ {message} concluída em **{duration}s**.")
        return result, duration

# --- FUNÇÕES ESPECÍFICAS DA IA ---

def revisar_paragrafo(paragrafo_texto: str, delay_s: float) -> str:
    """Revisão de um único parágrafo, utilizando o delay ajustável."""
    if not paragrafo_texto.strip():
        return ""
    
    system_prompt = "Você é um editor literário. Revise, edite e aprimore o parágrafo. Corrija gramática, aprimore o estilo e garanta a coerência. Retorne *apenas* o parágrafo revisado, sem comentários."
    user_content = f"Parágrafo a ser editado: {paragrafo_texto}"
    texto_revisado = call_openai_api(system_prompt, user_content, max_tokens=500)

    if "[ERRO DE CONEXÃO DA API]" in texto_revisado:
        return paragrafo_texto

    time.sleep(delay_s)
    return texto_revisado

def gerar_conteudo_marketing(titulo: str, autor: str, texto_completo: str) -> str:
    """Gera um blurb de contracapa envolvente para marketing."""
    system_prompt = "Você é um Copywriter de Best-sellers. Sua tarefa é criar um blurb de contracapa envolvente (3-4 parágrafos). Gere o resultado *APENAS* com o texto do blurb, sem títulos."
    user_content = f"Crie um blurb de contracapa de 3-4 parágrafos para este livro: Título: {titulo}, Autor: {autor}. Amostra: {texto_completo[:5000]}"
    return call_openai_api(system_prompt, user_content, max_tokens=1000)

def gerar_relatorio_estrutural(texto_completo: str) -> str:
    """Gera um relatório de revisão estrutural para o autor."""
    system_prompt = "Você é um Editor-Chefe. Gere um breve Relatório de Revisão para o autor. Foque em: Ritmo da Narrativa, Desenvolvimento de Personagens e Estrutura Geral. Use títulos e bullet points."
    user_content = f"MANUSCRITO PARA ANÁLISE (Amostra): {texto_completo[:15000]}"
    return call_openai_api(system_prompt, user_content)

def gerar_elementos_pre_textuais(titulo: str, autor: str, ano: int, texto_completo: str) -> str:
    """Gera conteúdo essencial de abertura e fechamento para um livro."""
    system_prompt = """
    Você é um gerente de editora. Gere o conteúdo essencial de abertura e fechamento para um livro.
    Gere o resultado no formato estrito:
    ### 1. Página de Copyright e Créditos
    [Texto de Copyright e Créditos (inclua ano 2025)]
    ### 2. Página 'Sobre o Autor'
    [Bio envolvente de 2-3 parágrafos, formatada para uma página de livro.]
    """
    user_content = f"""
    Título: {titulo}, Autor: {autor}, Ano: {ano}. Analise o tone do manuscrito (Amostra): {texto_completo[:5000]}
    """
    return call_openai_api(system_prompt, user_content)

def gerar_relatorio_conformidade_kdp(titulo: str, autor: str, page_count: int, format_data: Dict, espessura_cm: float, capa_largura_total_cm: float, capa_altura_total_cm: float) -> str:
    """Gera um relatório de conformidade KDP para publicação de livros físicos e eBooks."""
    tamanho_corte = format_data['name']
    prompt_kdp = f"""
    Você é um Especialista Técnico em Publicação e Conformidade da Amazon KDP. Gere um Relatório de Conformidade focado em upload bem-sucedido para Livros Físicos (Brochura) e eBooks.

    Gere o relatório usando o formato de lista e títulos, focando em:

    ### 1. Livro Físico (Brochura - Especificações)
    - **Tamanho de Corte Final (Miolo):** {tamanho_corte} ({format_data['width_cm']} x {format_data['height_cm']} cm).
    - **Espessura da Lombada (Calculada):** **{espessura_cm} cm**.
    - **Dimensões do Arquivo de Capa (Arte Completa com Sangria):** **{capa_largura_total_cm} cm (Largura Total) x {capa_altura_total_cm} cm (Altura Total)**.
    - **Margens:** Verifique se as margens internas do DOCX (lado da lombada) estão em 1.0 polegadas para segurança do corte.

    ### 2. Checklist de Miolo (DOCX)
    - Confirme que todos os títulos de capítulos estão marcados com o estilo **'Título 1'** no DOCX baixado (essencial para Sumário/TOC automático).
    - As quebras de página foram usadas corretamente entre os capítulos.

    ### 3. Otimização de Metadados (SEO Básico KDP)
    Sugira 3 categorias de nicho da Amazon e 3 palavras-chave de cauda longa para otimizar a listagem do livro '{titulo}' por '{autor}'.
    """
    return call_openai_api("Você é um especialista em publicação KDP.", prompt_kdp)

def gerar_capa_ia_completa(prompt_visual: str, blurb: str, autor: str, titulo: str, largura_cm: float, altura_cm: float, espessura_cm: float) -> str:
    """Chama a API DALL-E 3 para gerar a imagem da capa COMPLETA."""
    global client, is_api_ready

    if not is_api_ready or client is None:
        return "[ERRO GERAÇÃO DE CAPA] Chaves OPENAI_API_KEY e/ou OPENAI_PROJECT_ID não configuradas."

    full_prompt = f"""
    Crie uma imagem de CAPA COMPLETA E ÚNICA para impressão, com texto. As dimensões físicas totais (largura x altura) são: {largura_cm} cm x {altura_cm} cm. A lombada tem {espessura_cm} cm de espessura, localizada no centro.

    O design deve seguir o estilo: "{prompt_visual}".
    A arte DEVE incluir:
    1. Título '{titulo}' e Autor '{autor}' na capa (Frente).
    2. Título e Autor CLARAMENTE visíveis e centralizados na LOMBADA.
    3. O Blurb de vendas (texto do verso) na CONTRACAPA. Texto: "{blurb[:500]}..." (Use o máximo do texto possível, estilizado).
    4. Crie uma composição coesa que se estenda pela frente, lombada e verso. O design deve ser profissional e pronto para impressão.
    """

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1792x1024",
            quality="hd",
            n=1
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        return f"[ERRO GERAÇÃO DE CAPA] Falha ao gerar a imagem: {e}. Verifique se sua conta OpenAI tem créditos para DALL-E 3."

# --- FUNÇÕES DOCX AVANÇADAS ---

def adicionar_pagina_rosto(documento: Document, titulo: str, autor: str, style_data: Dict):
    """Adiciona a página de rosto ao documento DOCX."""
    font_name = style_data['font_name']
    documento.add_page_break()
    p_title = documento.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.add_run(titulo).bold = True
    p_title.runs[0].font.size = Pt(24)
    p_title.runs[0].font.name = font_name
    for _ in range(5):
        documento.add_paragraph()
    p_author = documento.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author.add_run(autor)
    p_author.runs[0].font.size = Pt(16)
    p_author.runs[0].font.name = font_name
    documento.add_page_break()

def adicionar_pagina_generica(documento: Document, titulo: str, subtitulo: Optional[str] = None):
    """Adiciona uma página genérica com título e subtítulo ao documento DOCX."""
    documento.add_page_break()
    p_header = documento.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.add_run(titulo).bold = True
    p_header.runs[0].font.size = Pt(18)
    if subtitulo:
        p_sub = documento.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sub.add_run(subtitulo).italic = True
        p_sub.runs[0].font.size = Pt(12)
    documento.add_paragraph("")
    if titulo == "Sumário":
        p_inst = documento.add_paragraph("⚠️ Para gerar o índice automático, use a função 'Referências' -> 'Sumário' do seu editor de texto. Todos os títulos de capítulo já foram marcados (**Estilo: Título 1**).")
    else:
        p_inst = documento.add_paragraph("⚠️ Este é um placeholder. Insira o conteúdo real aqui após o download. O espaço e a numeração já estão configurados.")
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.runs[0].font.size = Pt(10)
    documento.add_page_break()

# --- FUNÇÃO PRINCIPAL DE DIAGRAMAÇÃO E REVISÃO (Com Checkpointing e Paralelismo) ---

@st.cache_data(show_spinner=False)
def processar_manuscrito_cached(uploaded_file_bytes, filename, format_data, style_data, incluir_indices_abnt, time_rate_s):
    """Processa o manuscrito com cache para evitar reprocessamento."""
    from docx import Document
    documento_original = Document(BytesIO(uploaded_file_bytes))
    documento_revisado = Document()

    # 1. Configuração de Layout e Estilo
    section = documento_revisado.sections[0]
    section.page_width = Inches(format_data['width_in'])
    section.page_height = Inches(format_data['height_in'])
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(0.6)
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)

    font_name = style_data['font_name']
    font_size_pt = style_data['font_size_pt']
    line_spacing = style_data['line_spacing']
    indent_in = style_data['indent']

    style = documento_revisado.styles['Normal']
    style.font.name = font_name
    style.font.size = Pt(font_size_pt)
    paragraph_format = style.paragraph_format
    paragraph_format.line_spacing = line_spacing
    paragraph_format.first_line_indent = Inches(indent_in)

    # --- 2. Geração dos Elementos Pré-textuais (Fase 1) ---
    manuscript_sample = "\n".join([p.text for p in documento_original.paragraphs[:50]])

    if is_api_ready:
        pre_text_content, _ = run_fast_process_with_timer(
            "Geração de Copyright e Bio do Autor (IA)",
            gerar_elementos_pre_textuais,
            "Título do Livro", "Autor", 2025, manuscript_sample
        )
    else:
        pre_text_content = "### 1. Página de Copyright e Créditos\n[Placeholder de Copyright]\n### 2. Página 'Sobre o Autor'\n[Placeholder de Bio]"

    # Inserção de Páginas de Abertura
    adicionar_pagina_rosto(documento_revisado, "Título do Livro", "Autor", style_data)

    try:
        copyright_text_full = pre_text_content.split('### 1. Página de Copyright e Créditos')[1].split('### 2. Página \'Sobre o Autor\'')[0].strip()
    except IndexError:
        copyright_text_full = "[Erro ao extrair Copyright. Verifique a conexão da API.]"

    adicionar_pagina_generica(documento_revisado, "Página de Créditos", "Informações de Copyright e ISBN")
    for line in copyright_text_full.split('\n'):
        if line.strip():
            documento_revisado.add_paragraph(line.strip(), style='Normal')

    adicionar_pagina_generica(documento_revisado, "Sumário")

    # --- 3. Processamento do Miolo (Fase 2 - Revisão Parágrafo a Parágrafo com Checkpointing e Paralelismo) ---
    paragrafos = documento_original.paragraphs
    paragrafos_para_revisar = [p for p in paragrafos if len(p.text.strip()) >= 10]

    texto_completo = ""
    processed_state_map = st.session_state.get('processed_state', {})

    # Revisão paralela com controle de concorrência
    sem = threading.Semaphore(10)
    def revisar_com_controle(paragrafo):
        with sem:
            original_text = paragrafo.text.strip()
            if original_text in processed_state_map:
                return processed_state_map[original_text]
            elif is_api_ready:
                revisado = revisar_paragrafo(original_text, time_rate_s)
                processed_state_map[original_text] = revisado
                return revisado
            else:
                return original_text

    # Processamento paralelo com barra de progresso
    with ThreadPoolExecutor(max_workers=10) as executor:
        futuros = {executor.submit(revisar_com_controle, p): p for p in paragrafos_para_revisar}
        for fut in stqdm(as_completed(futuros), total=len(futuros), desc="Revisando parágrafos"):
            paragrafo = futuros[fut]
            texto_revisado = fut.result()
            
            if paragrafo.style.name.startswith('Heading'):
                documento_revisado.add_paragraph(texto_revisado, style=paragrafo.style.name)
            else:
                new_paragraph = documento_revisado.add_paragraph(texto_revisado, style='Normal')
                if 'Título 1' in paragrafo.style.name or 'Heading 1' in paragrafo.style.name:
                    new_paragraph.style = 'Heading 1'
            
            texto_completo += texto_revisado + "\n\n"

    # --- 4. Inserção da Página Pós-Textual ---
    documento_revisado.add_page_break()
    try:
        about_author_text_full = pre_text_content.split('### 2. Página \'Sobre o Autor\'')[1].strip()
        about_author_text_full = about_author_text_full.replace("### 2. Página 'Sobre o Autor'", "").strip()
    except IndexError:
        about_author_text_full = "[Erro ao extrair a bio do Autor. Verifique a conexão da API.]"

    adicionar_pagina_generica(documento_revisado, "Sobre o Autor", "Sua biografia gerada pela IA")
    for line in about_author_text_full.split('\n'):
        if line.strip():
            documento_revisado.add_paragraph(line.strip(), style='Normal')

    if incluir_indices_abnt:
        adicionar_pagina_generica(documento_revisado, "Apêndice A", "Título do Apêndice")
        adicionar_pagina_generica(documento_revisado, "Anexo I", "Título do Anexo")

    # --- 5. Geração do Blurb de Marketing (Fase 3) ---
    if is_api_ready:
        blurb_gerado, _ = run_fast_process_with_timer(
            "Geração do Blurb de Marketing (Contracapa)",
            gerar_conteudo_marketing,
            "Título do Livro", "Autor", texto_completo
        )
    else:
        blurb_gerado = "[Blurb não gerado. Conecte a API para um texto de vendas profissional.]"

    # Salva checkpoint automaticamente
    pathlib.Path("checkpoints").mkdir(exist_ok=True)
    checkpoint_path = pathlib.Path("checkpoints") / "checkpoint.json"
    checkpoint_path.write_text(json.dumps(processed_state_map))

    return documento_revisado, texto_completo, blurb_gerado

# --- INICIALIZAÇÃO DE ESTADO ---
if 'book_title' not in st.session_state:
    st.session_state['book_title'] = "O Último Código de Honra"
    st.session_state['book_author'] = "Carlos Honorato"
    st.session_state['page_count'] = 250
    st.session_state['capa_prompt'] = "Um portal antigo se abrindo no meio de uma floresta escura, estilo fantasia épica e mistério, cores roxo e preto, alta resolução."
    st.session_state['blurb'] = "A IA gerará o Blurb (Contracapa) aqui. Edite antes de gerar a capa completa!"
    st.session_state['generated_image_url'] = None
    st.session_state['texto_completo'] = ""
    st.session_state['documento_revisado'] = None
    st.session_state['relatorio_kdp'] = ""
    st.session_state['relatorio_estrutural'] = ""
    st.session_state['format_option'] = "Padrão A5 (5.83x8.27 in)"
    st.session_state['incluir_indices_abnt'] = False
    st.session_state['style_option'] = "Romance Clássico (Garamond)"
    st.session_state['time_rate_s'] = 0.2
    st.session_state['processed_state'] = {}

# --- CÁLCULOS DINÂMICOS ---
format_option_default = "Padrão A5 (5.83x8.27 in)"
selected_format_data_calc = KDP_SIZES.get(st.session_state.get('format_option', format_option_default), KDP_SIZES[format_option_default])

espessura_cm = round(st.session_state['page_count'] * selected_format_data_calc['papel_fator'], 2)
capa_largura_total_cm = round((selected_format_data_calc['width_cm'] * 2) + espessura_cm + 0.6, 2)
capa_altura_total_cm = round(selected_format_data_calc['height_cm'] + 0.6, 2)

# --- RESTAURAÇÃO AUTOMÁTICA DO CHECKPOINT ---
checkpoint_path = pathlib.Path("checkpoints") / "checkpoint.json"
if checkpoint_path.exists():
    st.session_state['processed_state'] = json.loads(checkpoint_path.read_text())

# --- FLUXO PRINCIPAL DO APLICATIVO (Tabs) ---
config_tab, miolo_tab, capa_tab, export_tab = st.tabs([
    "1. Configuração Inicial",
    "2. Diagramação & Elementos",
    "3. Capa Completa IA",
    "4. Análise & Exportar"
])

# --- TAB 1: CONFIGURAÇÃO INICIAL ---
with config_tab:
    st.header("Dados Essenciais para o Projeto")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state['book_title'] = st.text_input("Título do Livro", st.session_state['book_title'])
        st.session_state['page_count'] = st.number_input("Contagem Aproximada de Páginas (Miolo)", min_value=10, value=st.session_state['page_count'], step=10)
    with col2:
        st.session_state['book_author'] = st.text_input("Nome do Autor", st.session_state['book_author'])

    st.header("Escolha de Formato e Estilo")

    col3, col4, col5 = st.columns(3)
    with col3:
        st.session_state['format_option'] = st.selectbox(
            "Tamanho de Corte Final (KDP/Gráfica):",
            options=list(KDP_SIZES.keys()),
            index=list(KDP_SIZES.keys()).index(st.session_state['format_option']),
        )
        selected_format_data = KDP_SIZES[st.session_state['format_option']]

    with col4:
        st.session_state['style_option'] = st.selectbox(
            "Template de Estilo de Diagramação:",
            options=list(STYLE_TEMPLATES.keys()),
            index=list(STYLE_TEMPLATES.keys()).index(st.session_state['style_option']),
        )
        selected_style_data = STYLE_TEMPLATES[st.session_state['style_option']]

    with col5:
        st.session_state['incluir_indices_abnt'] = st.checkbox(
            "Incluir Índices/Apêndices ABNT",
            value=st.session_state['incluir_indices_abnt'],
        )

    st.subheader("Controle de Velocidade da IA")
    st.session_state['time_rate_s'] = st.slider(
        "Atraso por Parágrafo (segundos):",
        min_value=0.1,
        max_value=1.0,
        value=st.session_state['time_rate_s'],
        step=0.1,
        help="Controla a velocidade da revisão IA para evitar o limite de taxa (Rate Limit) da OpenAI."
    )

    st.subheader("Upload e Checkpoint")
    uploaded_file = st.file_uploader(
        "Carregue o arquivo .docx do seu manuscrito:",
        type=['docx'],
    )
    st.session_state['uploaded_file'] = uploaded_file

    st.info(f"**Status do Checkpoint:** **{len(st.session_state['processed_state'])}** parágrafos revisados em memória.")
    st.info(f"**Cálculo da Lombada:** **{espessura_cm} cm**. **Dimensão Total da Capa:** **{capa_largura_total_cm} cm x {capa_altura_total_cm} cm**.")

# --- TAB 2: DIAGRAMAÇÃO & ELEMENTOS ---
with miolo_tab:
    st.header("Fluxo de Diagramação e Revisão com IA")

    uploaded_file = st.session_state.get('uploaded_file')

    if uploaded_file is None:
        st.warning("Por favor, carregue um arquivo .docx na aba **'1. Configuração Inicial'** para começar.")
    else:
        if st.button("▶️ Iniciar Processamento do Miolo (Diagramação e Revisão)"):
            if not is_api_ready and len(st.session_state['processed_state']) == 0:
                st.error("Atenção: A revisão IA está desativada e nenhum Checkpoint foi carregado. Apenas a diagramação será realizada.")

            uploaded_file.seek(0)
            documento_revisado, texto_completo, blurb_gerado = processar_manuscrito_cached(
                uploaded_file.getvalue(),
                uploaded_file.name,
                selected_format_data,
                selected_style_data,
                st.session_state['incluir_indices_abnt'],
                st.session_state['time_rate_s']
            )

            st.session_state['documento_revisado'] = documento_revisado
            st.session_state['texto_completo'] = texto_completo
            st.session_state['blurb'] = blurb_gerado
            st.session_state['relatorio_estrutural'] = ""
            st.session_state['relatorio_kdp'] = ""
            st.session_state['generated_image_url'] = None

            st.toast("Miolo Pronto!", icon="✅")

        if st.session_state['documento_revisado']:
            st.success(f"Miolo diagramado no formato **{st.session_state['format_option']}** com o estilo **'{selected_style_data['font_name']}'**.")

            st.subheader("Intervenção: Blurb da Contracapa")
            st.warning("O Blurb abaixo será usado no design da Capa Completa. **Edite-o** antes de gerar a capa.")
            st.session_state['blurb'] = st.text_area("Texto de Vendas (Blurb):", st.session_state['blurb'], height=300)

# --- TAB 3: CAPA COMPLETA IA ---
with capa_tab:
    st.header("Criação da Capa Completa (Frente, Lombada e Verso)")

    if st.session_state['texto_completo'] == "":
        st.warning("Por favor, execute o processamento do Miolo (Aba 2) para garantir que o Blurb e o Título estejam prontos.")
    else:
        st.subheader("Passo 1: Defina o Conteúdo Visual e de Texto")
        st.info(f"O Blurb atual (Contracapa) é: **{st.session_state['blurb'][:150]}...**")
        st.text_input("Título para Capa", st.session_state['book_title'], disabled=True)
        st.text_input("Autor para Capa", st.session_state['book_author'], disabled=True)

        st.session_state['capa_prompt'] = st.text_area(
            "Descrição VISUAL da Capa (Estilo DALL-E 3):",
            st.session_state['capa_prompt'],
            height=200,
            help="Descreva a arte que deve aparecer, o estilo (ex: óleo, arte digital, surrealismo) e as cores predominantes."
        )

        st.subheader("Passo 2: Geração")
        st.warning(f"Atenção: A Capa Completa será gerada com as dimensões de **{capa_largura_total_cm}cm x {capa_altura_total_cm}cm**.")

        if st.button("🎨 Gerar Capa COMPLETA com IA"):
            if not is_api_ready:
                st.error("Chaves OpenAI não configuradas. Não é possível gerar a imagem.")
            else:
                # Verifica créditos antes de gerar
                try:
                    client.images.generate(model="dall-e-3", prompt="test", size="256x256", n=1)
                except Exception as e:
                    if "billing" in str(e).lower():
                        st.error("❌ Sua conta OpenAI não tem créditos ativos para DALL-E 3.")
                        st.stop()

                image_output, duration = run_fast_process_with_timer(
                    "Geração do Design de Capa Completa (DALL-E 3)",
                    gerar_capa_ia_completa,
                    st.session_state['capa_prompt'],
                    st.session_state['blurb'],
                    st.session_state['book_author'],
                    st.session_state['book_title'],
                    capa_largura_total_cm,
                    capa_altura_total_cm,
                    espessura_cm
                )

                if "http" in image_output:
                    st.session_state['generated_image_url'] = image_output
                    st.toast("Capa Gerada!", icon="✅")
                else:
                    st.error(image_output)

        if st.session_state['generated_image_url']:
            st.subheader("Pré-visualização da Capa Gerada")
            st.image(st.session_state['generated_image_url'], caption="Capa Completa (Frente, Lombada e Verso)", use_column_width=True)

# --- TAB 4: ANÁLISE & EXPORTAR ---
with export_tab:
    st.header("Relatórios Finais e Exportação")

    if not st.session_state.get('documento_revisado'):
        st.warning("Por favor, execute o processamento do Miolo (Aba 2) antes de exportar.")
    else:
        st.subheader("1. Relatórios de Análise")
        col_rel1, col_rel2 = st.columns(2)
        with col_rel1:
            if is_api_ready and st.button("Gerar/Atualizar Relatório Estrutural"):
                relatorio, _ = run_fast_process_with_timer(
                    "Geração do Relatório Estrutural",
                    gerar_relatorio_estrutural,
                    st.session_state['texto_completo']
                )
                st.session_state['relatorio_estrutural'] = relatorio

        with col_rel2:
            if is_api_ready and st.button("Gerar/Atualizar Relatório Técnico KDP"):
                relatorio, _ = run_fast_process_with_timer(
                    "Geração do Relatório Técnico KDP",
                    gerar_relatorio_conformidade_kdp,
                    st.session_state['book_title'],
                    st.session_state['book_author'],
                    st.session_state['page_count'],
                    selected_format_data_calc,
                    espessura_cm,
                    capa_largura_total_cm,
                    capa_altura_total_cm
                )
                st.session_state['relatorio_kdp'] = relatorio

        if st.session_state.get('relatorio_estrutural'):
            st.markdown("### Relatório Estrutural:")
            st.markdown(st.session_state['relatorio_estrutural'])

        if st.session_state.get('relatorio_kdp'):
            st.markdown("### Relatório Técnico KDP:")
            st.markdown(st.session_state['relatorio_kdp'])

        st.subheader("2. Exportação de Arquivos Finais")
        def to_docx_bytes(document):
            file_stream = BytesIO()
            document.save(file_stream)
            file_stream.seek(0)
            return file_stream.getvalue()

        if st.session_state.get('documento_revisado'):
            st.download_button(
                label="⬇️ Baixar Manuscrito Revisado (.docx)",
                data=to_docx_bytes(st.session_state['documento_revisado']),
                file_name=f"{st.session_state['book_title']}_revisado.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        if st.session_state.get('processed_state'):
            checkpoint_json = json.dumps(st.session_state['processed_state'], indent=4)
            st.download_button(
                label="⬇️ Baixar Checkpoint de Revisão (.json)",
                data=checkpoint_json.encode('utf-8'),
                file_name=f"{st.session_state['book_title']}_checkpoint.json",
                mime="application/json",
                help="Salve este arquivo para continuar a revisão de onde parou, carregando-o na aba 'Configuração Inicial'."
            )

        if st.session_state.get('generated_image_url'):
            st.markdown(f"[Baixar Imagem da Capa Completa]({st.session_state['generated_image_url']})")
            st.warning("Clique no link acima para baixar a imagem da capa em alta resolução.")

# --- SIDEBAR COM LOGO E DARK MODE ---
with st.sidebar:
    st.image("https://via.placeholder.com/120x60/0d6efd/ffffff?text=Editor+Pro+IA", width=120)
    dark_mode = st.checkbox("🌙 Modo Escuro")
    if dark_mode:
        st.markdown("""
        <style>
        .stApp { background-color: #111; color: #eee; }
        .stButton>button { background-color: #0d6efd; color: white; }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ℹ️ Informações")
    st.info(f"**Lombada:** {espessura_cm} cm\n\n**Dimensões da Capa:** {capa_largura_total_cm} cm × {capa_altura_total_cm} cm")
    
    if is_api_ready:
        st.success("✅ API OpenAI Conectada")
    else:
        st.error("❌ API OpenAI Desconectada")
