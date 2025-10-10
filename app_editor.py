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
from fastformat import FastFormatOptions, apply_fastformat, make_unified_diff, default_options

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

# --- INICIALIZAÇÃO DA IA E LAYOUT ---
st.set_page_config(page_title="Editora Literária IA", layout="wide")
st.title("🚀 Editora Literária IA: Publicação Inteligente")
st.subheader("Transforme seu manuscrito em um livro profissional, pronto para ABNT e KDP, com o poder da IA.")

# Variáveis globais para rastrear o status da API
client: Optional[OpenAI] = None
API_KEY: Optional[str] = None
PROJECT_ID: Optional[str] = None
is_api_ready: bool = False  # Inicializa como False

def initialize_openai_client():
    """Inicializa o cliente OpenAI e verifica a disponibilidade da API."""
    global client, API_KEY, PROJECT_ID, is_api_ready
    try:
        if hasattr(st, 'secrets'):
            API_KEY = st.secrets.get(API_KEY_NAME, os.environ.get(API_KEY_NAME))
            PROJECT_ID = st.secrets.get(PROJECT_ID_NAME, os.environ.get(PROJECT_ID_NAME))
        else:
            API_KEY = os.environ.get(API_KEY_NAME)
            PROJECT_ID = os.environ.get(PROJECT_ID_NAME)

        if API_KEY and PROJECT_ID:
            client = OpenAI(api_key=API_KEY, project=PROJECT_ID)
            is_api_ready = True
            st.sidebar.success("✅ Conexão OpenAI Pronta!")
        else:
            st.sidebar.error("❌ Conexão OpenAI Inativa.")
            st.warning(f"Chave e ID do Projeto OpenAI não configurados. A revisão e a geração de capa **NÃO** funcionarão.")
            is_api_ready = False

    except Exception as e:
        st.error(f"Erro na inicialização do ambiente (secrets/env). Detalhes: {e}")
        client = None
        is_api_ready = False

initialize_openai_client()

# --- FUNÇÕES DE AUXÍLIO ---

def call_openai_api(system_prompt: str, user_content: str, max_tokens: int = 3000, retries: int = 5) -> str:
    """
    Função genérica para chamar a API da OpenAI com backoff exponencial.
    O número de tentativas é 5 para resiliência contra instabilidade de rede ou da API.
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
                st.error(f"ERRO DE AUTENTICAÇÃO: Sua chave de API está incorreta ou expirada.")
                return "[ERRO DE CONEXÃO DA API] Chave de API Inválida."

            elif i < retries - 1:
                wait_time = 2 ** i  # Backoff exponencial
                st.warning(f"Erro de API/Rede. Tentando novamente em {wait_time} segundos... (Tentativa {i+1}/{retries})")
                time.sleep(wait_time)
            else:
                st.error(f"Falha ao se comunicar com a OpenAI após {retries} tentativas. Detalhes: {e}")
                return f"[ERRO DE CONEXÃO DA API] Falha: {e}"

    return "[ERRO DE CONEXÃO DA API] Tentativas de conexão esgotadas."

def run_fast_process_with_timer(message: str, func: callable, *args: Any, **kwargs: Any) -> Tuple[Any, float]:
    """Executa uma função, mede o tempo e exibe feedback ao usuário."""
    start_time = time.time()

    with st.spinner(f"⏳ {message}..."): 
        result = func(*args, **kwargs)

    duration = round(time.time() - start_time, 1)

    if isinstance(result, str) and "[ERRO DE CONEXÃO DA API]" in result:
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
        # Se houver erro de API, retorna o texto original para não perder o parágrafo.
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
    system_prompt = '''
    Você é um gerente de editora. Gere o conteúdo essencial de abertura e fechamento para um livro.
    Gere o resultado no formato estrito:
    ### 1. Página de Copyright e Créditos
    [Texto de Copyright e Créditos (inclua ano 2025)]
    ### 2. Página 'Sobre o Autor'
    [Bio envolvente de 2-3 parágrafos, formatada para uma página de livro.]
    '''
    user_content = f'''
    Título: {titulo}, Autor: {autor}, Ano: {ano}. Analise o tom do manuscrito (Amostra): {texto_completo[:5000]}
    '''
    return call_openai_api(system_prompt, user_content)

def gerar_relatorio_conformidade_kdp(titulo: str, autor: str, page_count: int, format_data: Dict, espessura_cm: float, capa_largura_total_cm: float, capa_altura_total_cm: float) -> str:
    """Gera um relatório de conformidade KDP para publicação de livros físicos e eBooks."""
    tamanho_corte = format_data['name']
    prompt_kdp = f'''
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
    '''
    return call_openai_api("Você é um especialista em publicação KDP.", prompt_kdp)

def gerar_capa_ia_completa(prompt_visual: str, blurb: str, autor: str, titulo: str, largura_cm: float, altura_cm: float, espessura_cm: float) -> str:
    """Chama a API DALL-E 3 para gerar a imagem da capa COMPLETA."""

    global client, is_api_ready

    if not is_api_ready or client is None:
        return "[ERRO GERAÇÃO DE CAPA] Chaves OPENAI_API_KEY e/ou OPENAI_PROJECT_ID não configuradas."

    full_prompt = f'''
    Crie uma imagem de CAPA COMPLETA E ÚNICA para impressão, com texto. As dimensões físicas totais (largura x altura) são: {largura_cm} cm x {altura_cm} cm. A lombada tem {espessura_cm} cm de espessura, localizada no centro.

    O design deve seguir o estilo: "{prompt_visual}".
    A arte DEVE incluir:
    1. Título '{titulo}' e Autor '{autor}' na capa (Frente).
    2. Título e Autor CLARAMENTE visíveis e centralizados na LOMBADA.
    3. O Blurb de vendas (texto do verso) na CONTRACAPA. Texto: "{blurb[:500]}..." (Use o máximo do texto possível, estilizado).
    4. Crie uma composição coesa que se estenda pela frente, lombada e verso. O design deve ser profissional e pronto para impressão.
    '''

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


# --- FUNÇÃO PRINCIPAL DE DIAGRAMAÇÃO E REVISÃO (Com Checkpointing) ---

def processar_manuscrito(uploaded_file, format_data: Dict, style_data: Dict, incluir_indices_abnt: bool, status_container, time_rate_s: float):
    """Processa o manuscrito, aplicando diagramação, revisão e checkpointing."""
    global is_api_ready
    status_container.empty()

    documento_original = Document(uploaded_file)
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
    uploaded_file.seek(0)
    # Lendo o arquivo como bytes e decodificando para obter uma amostra
    manuscript_sample = uploaded_file.getvalue().decode('utf-8', errors='ignore')[:5000]

    with status_container:
        st.subheader("Fase 1/3: Geração de Elementos Pré-textuais")

    if is_api_ready:
        pre_text_content, duration = run_fast_process_with_timer(
            "Geração de Copyright e Bio do Autor (IA)",
            gerar_elementos_pre_textuais,
            st.session_state['book_title'],
            st.session_state['book_author'],
            2025,
            manuscript_sample
        )
    else:
        pre_text_content = "### 1. Página de Copyright e Créditos\n[Placeholder de Copyright]\n### 2. Página 'Sobre o Autor'\n[Placeholder de Bio]"
        with status_container:
            st.warning("⚠️ Elementos Pré-textuais pulados: Conexão OpenAI inativa.")

    # Inserção de Páginas de Abertura
    adicionar_pagina_rosto(documento_revisado, st.session_state['book_title'], st.session_state['book_author'], style_data)

    try:
        copyright_text_full = pre_text_content.split('### 1. Página de Copyright e Créditos')[1].split('### 2. Página \'Sobre o Autor\'')[0].strip()
    except IndexError:
        copyright_text_full = "[Erro ao extrair Copyright. Verifique a conexão da API.]"

    adicionar_pagina_generica(documento_revisado, "Página de Créditos", "Informações de Copyright e ISBN")
    for line in copyright_text_full.split('\n'):
        if line.strip():
            documento_revisado.add_paragraph(line.strip(), style='Normal')

    adicionar_pagina_generica(documento_revisado, "Sumário")

    # --- 3. Processamento do Miolo (Fase 2 - Revisão Parágrafo a Parágrafo com Checkpointing) ---

    paragrafos = documento_original.paragraphs
    # Filtra apenas parágrafos com conteúdo significativo para revisão IA
    paragrafos_para_revisar = [p for p in paragrafos if len(p.text.strip()) >= 10]

    total_paragrafos = len(paragrafos)  # Total de todos os parágrafos (incluindo vazios/curtos)
    total_a_revisar = len(paragrafos_para_revisar)  # Total de parágrafos que a IA realmente processa

    texto_completo = ""
    revisados_count = 0

    # Obtém a referência para o estado de checkpoint
    processed_state_map = st.session_state['processed_state']

    with status_container:
        st.subheader("Fase 2/3: Revisão do Miolo (Parágrafo a Parágrafo)")
        progress_bar = st.progress(0, text="Iniciando revisão...")
        auto_checkpoint_placeholder = st.empty()

    start_loop_time = time.time()
    newly_reviewed_count = 0
    current_revisados_total = 0

    for i, paragrafo in enumerate(paragrafos):
        original_text = paragrafo.text.strip()

        if len(original_text) >= 10:
            # Este é um parágrafo que será potencialmente revisado pela IA
            current_revisados_total += 1

            if original_text in processed_state_map:
                # Carrega do checkpoint
                revisado_text = processed_state_map[original_text]
                with auto_checkpoint_placeholder:
                    st.info(f"✅ Carregado do checkpoint: \"...{original_text[:50]}...\"")
            elif is_api_ready:
                # Revisa com a IA
                revisado_text = revisar_paragrafo(original_text, time_rate_s)
                processed_state_map[original_text] = revisado_text  # Salva no checkpoint
                newly_reviewed_count += 1
                with auto_checkpoint_placeholder:
                    st.success(f"✨ Revisado pela IA: \"...{original_text[:50]}...\"")
            else:
                # IA não disponível e não está no checkpoint
                revisado_text = original_text
                with auto_checkpoint_placeholder:
                    st.warning(f"⚠️ IA inativa, usando original: \"...{original_text[:50]}...\"")
        else:
            # Parágrafos curtos ou vazios não são revisados pela IA, mas são mantidos
            revisado_text = original_text

        # Adiciona o parágrafo (revisado ou original) ao novo documento
        if paragrafo.style.name.startswith('Heading'):
            # Mantém o estilo de título original
            documento_revisado.add_paragraph(revisado_text, style=paragrafo.style.name)
        else:
            # Aplica o estilo 'Normal' configurado
            new_paragraph = documento_revisado.add_paragraph(revisado_text, style='Normal')
            # Se for um título, garante que o estilo 'Título 1' seja aplicado para TOC
            if 'Título 1' in paragrafo.style.name or 'Heading 1' in paragrafo.style.name:
                new_paragraph.style = 'Heading 1'

        texto_completo += revisado_text + "\n\n"

        # Atualiza a barra de progresso e estimativa de tempo
        if total_a_revisar > 0:
            percent_complete = int((current_revisados_total / total_a_revisar) * 100)
            elapsed_time = time.time() - start_loop_time

            progress_text_template = "{percent}% Concluído. {done}/{total} parágrafos revisados. Tempo restante estimado: {remaining_time}"

            if newly_reviewed_count > 0:
                # Calcula o tempo médio por novo parágrafo revisado
                avg_time_per_newly_reviewed = elapsed_time / newly_reviewed_count
                # Estima o tempo restante
                remaining_time_s = (total_a_revisar - current_revisados_total) * avg_time_per_newly_reviewed

                remaining_minutes = int(remaining_time_s // 60)
                remaining_seconds = int(remaining_time_s % 60)
                remaining_time_str = f"{remaining_minutes}m {remaining_seconds}s"
            else:
                remaining_time_str = "Calculando..."

            progress_bar.progress(
                percent_complete / 100.0,
                text=progress_text_template.format(
                    percent=percent_complete,
                    done=current_revisados_total,
                    total=total_a_revisar,
                    remaining_time=remaining_time_str
                )
            )

    # Após o loop
    end_loop_time = time.time()
    total_loop_duration = round(end_loop_time - start_loop_time, 1)

    with status_container:
        progress_bar.empty()
        st.success(f"Fase 2/3 concluída: Miolo processado em **{total_loop_duration}s**! 🎉 Total de parágrafos revisados pela IA nesta rodada: **{newly_reviewed_count}**.")

    # Limpa o placeholder no final
    auto_checkpoint_placeholder.empty()


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
    with status_container:
        st.subheader("Fase 3/3: Geração de Elementos de Marketing")

    if is_api_ready:
        blurb_gerado, duration = run_fast_process_with_timer(
            "Geração do Blurb de Marketing (Contracapa)",
            gerar_conteudo_marketing,
            st.session_state['book_title'],
            st.session_state['book_author'],
            texto_completo
        )
    else:
        blurb_gerado = "[Blurb não gerado. Conecte a API para um texto de vendas profissional.]"
        with status_container:
            st.warning("⚠️ Blurb de Marketing pulado: Conexão OpenAI inativa.")

    return documento_revisado, texto_completo, blurb_gerado

# --- INICIALIZAÇÃO DE ESTADO (Com processed_state) ---
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
    if 'style_option' not in st.session_state:
        st.session_state['style_option'] = "Romance Clássico (Garamond)"
    if 'time_rate_s' not in st.session_state:
        st.session_state['time_rate_s'] = 0.2
    # NOVO: Estado de Checkpoint - Mapeia texto original -> texto revisado
    st.session_state['processed_state'] = {}

# --- CÁLCULOS DINÂMICOS ---
format_option_default = "Padrão A5 (5.83x8.27 in)"
selected_format_data_calc = KDP_SIZES.get(st.session_state.get('format_option', format_option_default), KDP_SIZES[format_option_default])

espessura_cm = round(st.session_state['page_count'] * selected_format_data_calc['papel_fator'], 2)
# Adiciona 0.6cm de sangria (0.3cm de cada lado)
capa_largura_total_cm = round((selected_format_data_calc['width_cm'] * 2) + espessura_cm + 0.6, 2)
capa_altura_total_cm = round(selected_format_data_calc['height_cm'] + 0.6, 2)
# --- FIM CÁLCULOS DINÂMICOS ---

# --- FUNÇÃO PARA CARREGAR CHECKPOINT ---
def load_checkpoint_from_json(uploaded_json):
    """Lê o arquivo JSON e carrega o estado de volta para a sessão."""
    try:
        bytes_data = uploaded_json.read()
        data = json.loads(bytes_data.decode('utf-8'))

        if isinstance(data, dict):
            st.session_state['processed_state'] = data
            st.success(f"Checkpoint carregado com sucesso! **{len(data)}** parágrafos revisados restaurados.")
        else:
            st.error("Formato JSON inválido. O arquivo deve conter um objeto (dicionário).")
    except Exception as e:
        st.error(f"Erro ao ler ou processar o arquivo JSON de checkpoint: {e}")


# --- FLUXO PRINCIPAL DO APLICATIVO (Tabs) ---

config_tab, miolo_tab, capa_tab, export_tab, revisao_tab, referencias_tab, colaboracao_tab, stem_tab, slides_tab = st.tabs([
    "1. Configuração Inicial",
    "2. Diagramação & Elementos",
    "3. Capa Completa IA",
    "4. Análise & Exportar",
    "5. Revisão de Estilo e Gramática",
    "6. Gerenciador de Referências",
    "7. Revisão Colaborativa",
    "8. Ferramentas STEM/Gêneros",
    "9. Geração de Slides"
])

# --- TAB 1: CONFIGURAÇÃO INICIAL (Com Upload de Checkpoint) ---

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
        default_style_key = "Romance Clássico (Garamond)"
        current_style_key = st.session_state.get('style_option', default_style_key)

        style_option = st.selectbox(
            "Template de Estilo de Diagramação:",
            options=list(STYLE_TEMPLATES.keys()),
            index=list(STYLE_TEMPLATES.keys()).index(current_style_key),
            key='style_option',
        )
        selected_style_data = STYLE_TEMPLATES[style_option]

    with col5:
        incluir_indices_abnt = st.checkbox(
            "Incluir Índices/Apêndices ABNT",
            value=st.session_state['incluir_indices_abnt'],
            key='incluir_indices_abnt_checkbox',
        )
        st.session_state['incluir_indices_abnt'] = incluir_indices_abnt

    st.subheader("Controle de Velocidade da IA (Controle de Taxa/Rate Limit)")
    st.session_state['time_rate_s'] = st.slider(
        "Atraso por Parágrafo (segundos):",
        min_value=0.1,
        max_value=1.0,
        value=st.session_state['time_rate_s'],
        step=0.1,
        help="Controla a velocidade da revisão IA para evitar o limite de taxa (Rate Limit) da OpenAI. Use uma taxa mais alta (ex: 0.5s) para manuscritos longos."
    )

    st.subheader("Upload e Checkpoint")
    uploaded_file = st.file_uploader(
        "Carregue o arquivo .docx do seu manuscrito:",
        type=['docx'],
    )
    st.session_state['uploaded_file'] = uploaded_file

    # --- LÓGICA DE UPLOAD DE CHECKPOINT ---
    checkpoint_file = st.file_uploader(
        "⬆️ Carregar Checkpoint Anterior (.json):",
        type=['json'],
        help="Carregue o arquivo JSON de estado para continuar uma revisão interrompida. Isso definirá o ponto de reinício. **ATENÇÃO:** O nome do arquivo DOCX deve ser o mesmo do processamento anterior."
    )

    if checkpoint_file is not None:
        load_checkpoint_from_json(checkpoint_file)

    st.info(f"**Status do Checkpoint:** **{len(st.session_state['processed_state'])}** parágrafos revisados em memória.")

    st.info(f"**Cálculo da Lombada (Spine):** **{espessura_cm} cm**. **Dimensão Total da Capa (com sangria 0.3cm):** **{capa_largura_total_cm} cm x {capa_altura_total_cm} cm**.")


# --- TAB 2: DIAGRAMAÇÃO & ELEMENTOS ---

with miolo_tab:
    st.header("Fluxo de Diagramação e Revisão com IA")

    uploaded_file = st.session_state.get('uploaded_file')

    if uploaded_file is None:
        st.warning("Por favor, carregue um arquivo .docx na aba **'1. Configuração Inicial'** para começar.")
    else:
        status_container = st.container()

        if st.button("▶️ Iniciar Processamento do Miolo (Diagramação e Revisão)"):
            if not is_api_ready and len(st.session_state['processed_state']) == 0:
                st.error("Atenção: A revisão IA está desativada e nenhum Checkpoint foi carregado. Apenas a diagramação será realizada.")

            with status_container:
                st.info("Processamento iniciado! Acompanhe o progresso abaixo...")

            selected_format_data = KDP_SIZES[st.session_state['format_option']]
            current_style_key = st.session_state.get('style_option', "Romance Clássico (Garamond)")
            selected_style_data = STYLE_TEMPLATES[current_style_key]

            uploaded_file.seek(0)
            documento_revisado, texto_completo, blurb_gerado = processar_manuscrito(
                uploaded_file,
                selected_format_data,
                selected_style_data,
                st.session_state['incluir_indices_abnt'],
                status_container,
                st.session_state['time_rate_s']
            )

            st.session_state['documento_revisado'] = documento_revisado
            st.session_state['texto_completo'] = texto_completo
            st.session_state['blurb'] = blurb_gerado

            # Limpa relatórios anteriores para forçar a regeração se necessário
            st.session_state['relatorio_estrutural'] = ""
            st.session_state['relatorio_kdp'] = ""
            st.session_state['generated_image_url'] = None

            st.toast("Miolo Pronto!", icon="✅")

        if st.session_state['documento_revisado']:
            current_style_key = st.session_state.get('style_option', "Romance Clássico (Garamond)")
            selected_style_data = STYLE_TEMPLATES[current_style_key]
            st.success(f"Miolo diagramado no formato **{st.session_state['format_option']}** com o estilo **'{selected_style_data['font_name']}**'.")

            st.subheader("Intervenção: Blurb da Contracapa")
            st.warning("O Blurb abaixo será usado no design da Capa Completa. **Edite-o** antes de gerar a capa.")
            st.session_state['blurb'] = st.text_area("Texto de Vendas (Blurb):", st.session_state['blurb'], height=300, key='blurb_text_area')


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
            key='capa_prompt_area',
            help="Descreva a arte que deve aparecer, o estilo (ex: óleo, arte digital, surrealismo) e as cores predominantes."
        )

        st.subheader("Passo 2: Geração")
        st.warning(f"Atenção: A Capa Completa será gerada com as dimensões de **{capa_largura_total_cm}cm x {capa_altura_total_cm}cm** (calculado com base nas páginas).")

        if st.button("🎨 Gerar Capa COMPLETA com IA"):
            if not is_api_ready:
                st.error("Chaves OpenAI não configuradas. Não é possível gerar a imagem.")
            else:
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


# --- TAB 4: ANÁLISE & EXPORTAR (Com Download de Checkpoint) ---

with export_tab:
    st.header("Relatórios Finais e Exportação")

    if not st.session_state.get('documento_revisado'):
        st.warning("Por favor, execute o processamento do Miolo (Aba 2) antes de exportar.")
    else:

        # --- Relatórios ---
        st.subheader("1. Relatórios de Análise")

        col_rel1, col_rel2 = st.columns(2)
        with col_rel1:
            if is_api_ready and st.button("Gerar/Atualizar Relatório Estrutural"):
                relatorio, duration = run_fast_process_with_timer(
                    "Geração do Relatório Estrutural",
                    gerar_relatorio_estrutural,
                    st.session_state['texto_completo']
                )
                st.session_state['relatorio_estrutural'] = relatorio

        with col_rel2:
            if is_api_ready and st.button("Gerar/Atualizar Relatório Técnico KDP"):
                relatorio, duration = run_fast_process_with_timer(
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

        # --- Exportação de Arquivos ---
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

        # Botão para baixar o checkpoint
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


# --- Integração de Funcionalidades do FastFormat (Esboço) ---

# As funcionalidades do FastFormat serão integradas e otimizadas com IA nas próximas fases.
# Abaixo, um esboço de como elas seriam representadas no código, com placeholders para a lógica de IA.

# --- Verificador de Estilo e Gramática com IA (Fase 3) ---
def verificar_estilo_gramatica_ia(texto: str) -> Dict:
    """Verifica o estilo e a gramática de um texto usando IA, retornando sugestões e o texto corrigido."""
    if not is_api_ready:
        return {"status": "IA Inativa", "sugestoes": "Conecte a API para verificação avançada.", "texto_corrigido": texto}

    system_prompt = "Você é um revisor de texto profissional. Analise o texto fornecido para erros gramaticais, ortográficos, de pontuação e sugestões de melhoria de estilo. Retorne um JSON com 'texto_corrigido' e uma lista de 'sugestoes' (ex: [{'tipo': 'gramatica', 'descricao': 'Erro de concordância'}, {'tipo': 'estilo', 'descricao': 'Evitar clichês'}]). Se não houver erros ou sugestões, retorne o texto original e uma lista vazia de sugestões. Mantenha o texto corrigido o mais próximo possível do original, apenas corrigindo erros claros."
    user_content = f"Analise o seguinte texto: {texto}"
    
    response_json_str = call_openai_api(system_prompt, user_content, max_tokens=2000)
    
    try:
        response_data = json.loads(response_json_str)
        # Validação básica da estrutura da resposta
        if "texto_corrigido" in response_data and "sugestoes" in response_data and isinstance(response_data["sugestoes"], list):
            return response_data
        else:
            st.error("Resposta da IA em formato inesperado para verificação de estilo/gramática.")
            return {"status": "Erro na resposta da IA", "sugestoes": [{"tipo": "erro", "descricao": "Resposta da IA em formato inesperado."}], "texto_corrigido": texto}
    except json.JSONDecodeError:
        st.error(f"Erro ao decodificar JSON da IA para verificação de estilo/gramática: {response_json_str}")
        return {"status": "Erro na resposta da IA", "sugestoes": [{"tipo": "erro", "descricao": "Resposta da IA não é um JSON válido para verificação de estilo/gramática."}], "texto_corrigido": texto}

# --- Gerenciador de Referências Integrado com IA (Fase 4) ---
def gerenciar_referencias_ia(texto_com_citacoes: str, tipo_norma: str) -> Tuple[str, List[Dict]]:
    """Simula o gerenciamento e formatação de referências com IA."""
    # Placeholder para integração com LLM para identificar citações e formatar a lista de referências.
    # A IA pode extrair dados de citações e formatar a lista de referências automaticamente.
    if not is_api_ready:
        return texto_com_citacoes, [{"tipo": "IA Inativa", "descricao": "Conecte a API para gerenciamento de referências."}]

    system_prompt = f"Você é um especialista em normas acadêmicas. Dado um texto com citações, identifique as citações e gere uma lista de referências formatada na norma {tipo_norma}. Retorne um JSON com 'texto_formatado' (com citações ajustadas) e 'referencias' (lista de objetos com 'autor', 'titulo', 'ano', 'norma_formatada'). Se não houver citações, retorne o texto original e uma lista vazia de referências."
    user_content = f"Texto com citações: {texto_com_citacoes}\nNorma: {tipo_norma}"
    
    response_json_str = call_openai_api(system_prompt, user_content, max_tokens=3000)
    
    try:
        response_data = json.loads(response_json_str)
        if "texto_formatado" in response_data and "referencias" in response_data and isinstance(response_data["referencias"], list):
            return response_data.get("texto_formatado", texto_com_citacoes), response_data.get("referencias", [])
        else:
            st.error("Resposta da IA em formato inesperado para gerenciamento de referências.")
            return texto_com_citacoes, [{"tipo": "erro", "descricao": "Resposta da IA em formato inesperado para referências."}]
    except json.JSONDecodeError:
        st.error(f"Erro ao decodificar JSON da IA para gerenciamento de referências: {response_json_str}")
        return texto_com_citacoes, [{"tipo": "erro", "descricao": "Resposta da IA não é um JSON válido para referências."}]

# --- Ferramentas de Revisão e Colaboração com IA (Fase 5) ---
def sugerir_revisoes_colaborativas_ia(texto_original: str, texto_editado: str) -> List[Dict]:
    """Simula a sugestão de revisões e comentários para colaboração com IA."""
    # Placeholder para integração com LLM para comparar versões e sugerir comentários/revisões
    # A IA pode identificar diferenças significativas e sugerir pontos de discussão.
    if not is_api_ready:
        return [{"tipo": "IA Inativa", "descricao": "Conecte a API para sugestões de revisão."}]

    system_prompt = "Você é um editor colaborativo. Compare o 'texto_original' com o 'texto_editado'. Identifique as principais diferenças e sugira comentários ou pontos de revisão para o autor. Retorne uma lista de objetos JSON com 'localizacao' (trecho do texto), 'tipo' (sugestao/comentario), 'descricao'. Se não houver diferenças significativas, retorne uma lista vazia."
    user_content = f"Texto Original: {texto_original}\nTexto Editado: {texto_editado}"
    
    response_json_str = call_openai_api(system_prompt, user_content, max_tokens=2000)
    
    try:
        response_data = json.loads(response_json_str)
        if isinstance(response_data, list):
            return response_data
        else:
            st.error("Resposta da IA em formato inesperado para revisões colaborativas.")
            return [{"tipo": "erro", "descricao": "Resposta da IA em formato inesperado para revisões colaborativas."}]
    except json.JSONDecodeError:
        st.error(f"Erro ao decodificar JSON da IA para revisões colaborativas: {response_json_str}")
        return [{"tipo": "erro", "descricao": "Resposta da IA não é um JSON válido para revisões colaborativas."}]

# --- Adaptação de Ferramentas para Conteúdo Específico (STEM/Gêneros) com IA (Fase 6) ---
def formatar_conteudo_especifico_ia(conteudo: str, tipo_conteudo: str) -> str:
    """Simula a formatação de conteúdo específico (ex: código, fórmulas) com IA."""
    # Placeholder para integração com LLM para formatar e validar conteúdo especializado
    # A IA pode garantir a sintaxe correta de código, formatação de fórmulas, etc.
    if not is_api_ready:
        return f"[IA Inativa] Conteúdo original: {conteudo}"

    system_prompt = f"Você é um especialista em formatação de {tipo_conteudo}. Formate o conteúdo fornecido de acordo com as melhores práticas para {tipo_conteudo}. Retorne apenas o conteúdo formatado. Não adicione nenhum texto explicativo, apenas o conteúdo formatado."
    user_content = f"Conteúdo a formatar ({tipo_conteudo}): {conteudo}"
    
    return call_openai_api(system_prompt, user_content, max_tokens=1500)

# --- Geração de Apresentações de Slides com IA (Fase 7) ---
def gerar_slides_ia(texto_base: str, tema: str, num_slides: int) -> List[Dict]:
    """Simula a geração de apresentações de slides com IA."""
    # Placeholder para integração com LLM para criar slides a partir de um texto base
    # A IA pode resumir o texto, criar tópicos, sugerir imagens e layout.
    if not is_api_ready:
        return [{"titulo": "IA Inativa", "conteudo": "Conecte a API para gerar slides.", "layout": "texto"}]

    if num_slides > 12:
        st.warning("A geração de apresentações com mais de 12 slides requer uma assinatura premium. Gerando 12 slides.")
        num_slides = 12

    system_prompt = f"Você é um designer de apresentações. Crie uma apresentação de {num_slides} slides sobre o texto fornecido, com o tema '{tema}'. Para cada slide, forneça um 'titulo', 'conteudo' (em bullet points) e 'layout' (ex: 'titulo_e_texto', 'imagem_e_texto'). Retorne uma lista de objetos JSON representando os slides. Certifique-se de que a resposta seja um JSON válido e nada mais."
    user_content = f"Texto base para a apresentação: {texto_base}"
    
    response_json_str = call_openai_api(system_prompt, user_content, max_tokens=4000)
    
    try:
        response_data = json.loads(response_json_str)
        if isinstance(response_data, list) and all("titulo" in s and "conteudo" in s and "layout" in s for s in response_data):
            return response_data
        else:
            st.error("Resposta da IA em formato inesperado para geração de slides.")
            return [{"titulo": "Erro na Geração", "conteudo": "Resposta da IA em formato inesperado para slides.", "layout": "texto"}]
    except json.JSONDecodeError:
        st.error(f"Erro ao decodificar JSON da IA para geração de slides: {response_json_str}")
        return [{"titulo": "Erro na Geração", "conteudo": "Resposta da IA não é um JSON válido para slides.", "layout": "texto"}]


# --- UI para as novas funcionalidades ---

with revisao_tab:
    st.header("Verificador de Estilo e Gramática com IA")
    st.write("Utilize a inteligência artificial para aprimorar a qualidade textual do seu manuscrito, corrigindo erros e sugerindo melhorias de estilo.")

    if st.session_state.get('texto_completo'):
        texto_para_verificar = st.text_area(
            "Insira o texto para verificação (ou o texto do miolo será usado):",
            st.session_state['texto_completo'],
            height=400,
            key='grammar_check_input'
        )
    else:
        texto_para_verificar = st.text_area(
            "Insira o texto para verificação:",
            "Escreva seu texto aqui para que a IA possa verificar a gramática e o estilo.",
            height=400,
            key='grammar_check_input_empty'
        )

    if st.button("✨ Verificar Estilo e Gramática com IA"):
        if not texto_para_verificar.strip():
            st.warning("Por favor, insira algum texto para verificar.")
        else:
            with st.spinner("Analisando texto com IA..."):
                analise = verificar_estilo_gramatica_ia(texto_para_verificar)
            
            if analise and isinstance(analise, dict) and ("[ERRO DE CONEXÃO DA API]" in analise.get("status", "") or "Erro na resposta da IA" in analise.get("status", "")):
                st.error(f"Falha na verificação: {analise.get('status', 'Erro desconhecido')}")
            elif analise and isinstance(analise, dict):
                st.subheader("Texto Corrigido e Aprimorado:")
                st.markdown(analise["texto_corrigido"])

                st.subheader("Sugestões de Melhoria:")
                if analise["sugestoes"]:
                    for sugestao in analise["sugestoes"]:
                        st.info(f"**{sugestao.get('tipo', 'Geral').capitalize()}**: {sugestao.get('descricao', 'Sem descrição.')}")
                else:
                    st.success("Nenhum erro significativo ou sugestão de melhoria encontrada. Ótimo trabalho!")

with referencias_tab:
    st.header("Gerenciador de Referências Integrado com IA")
    st.write("Formate suas citações e referências bibliográficas automaticamente, seguindo diversas normas acadêmicas com o auxílio da IA.")

    texto_com_cit = st.text_area(
        "Insira o texto com citações (ex: Um estudo recente (Silva, 2023) mostrou que...):",
        st.session_state['texto_completo'] if st.session_state.get('texto_completo') else "Um estudo recente (Silva, 2023) mostrou que a interocepção é crucial para a saúde mental (Souza & Lima, 2022).",
        height=300,
        key='ref_manager_input'
    )
    norma_ref = st.selectbox(
        "Selecione a Norma para Formatação:",
        ["ABNT", "APA", "Vancouver", "Harvard", "Chicago"],
        key='ref_norma_select'
    )
    if st.button("📚 Formatar Referências com IA"):
        if not texto_com_cit.strip():
            st.warning("Por favor, insira algum texto com citações para formatar.")
        else:
            with st.spinner("Formatando referências com IA..."):
                texto_formatado, refs = gerenciar_referencias_ia(texto_com_cit, norma_ref)
            
            if refs and isinstance(refs, list) and refs[0] and isinstance(refs[0], dict) and "[ERRO DE CONEXÃO DA API]" in refs[0].get("descricao", ""):
                st.error(f"Falha na formatação de referências: {refs[0].get('descricao', 'Erro desconhecido')}")
            else:
                st.subheader("Texto com Citações Formatadas:")
                st.markdown(texto_formatado)

                st.subheader("Lista de Referências Gerada:")
                if refs:
                    for ref in refs:
                        st.write(ref.get('norma_formatada', 'Formato não disponível.'))
                else:
                    st.info("Nenhuma referência identificada ou gerada.")

with colaboracao_tab:
    st.header("Ferramentas de Revisão e Colaboração com IA")
    st.write("Compare diferentes versões do seu manuscrito e receba sugestões de revisão e comentários inteligentes da IA para facilitar a colaboração.")

    col_orig, col_edit = st.columns(2)
    with col_orig:
        texto_original_colab = st.text_area(
            "Versão Original do Texto:",
            st.session_state['texto_completo'] if st.session_state.get('texto_completo') else "Este é o texto original do manuscrito. Ele contém algumas frases que podem ser melhoradas.",
            height=300,
            key='colab_original'
        )
    with col_edit:
        texto_editado_colab = st.text_area(
            "Versão Editada do Texto:",
            st.session_state['texto_completo'] if st.session_state.get('texto_completo') else "Este é o texto editado do manuscrito. Algumas frases foram aprimoradas e corrigidas.",
            height=300,
            key='colab_editado'
        )

    if st.button("🤝 Sugerir Revisões Colaborativas com IA"):
        if not texto_original_colab.strip() or not texto_editado_colab.strip():
            st.warning("Por favor, insira ambas as versões do texto para comparação.")
        else:
            with st.spinner("Comparando textos e gerando sugestões..."):
                sugestoes_colab = sugerir_revisoes_colaborativas_ia(texto_original_colab, texto_editado_colab)
            
            if sugestoes_colab and isinstance(sugestoes_colab, list) and sugestoes_colab[0] and isinstance(sugestoes_colab[0], dict) and "[ERRO DE CONEXÃO DA API]" in sugestoes_colab[0].get("descricao", ""):
                st.error(f"Falha na geração de sugestões: {sugestoes_colab[0].get('descricao', 'Erro desconhecido')}")
            else:
                st.subheader("Sugestões de Revisão e Comentários da IA:")
                if sugestoes_colab:
                    for sug in sugestoes_colab:
                        st.markdown(f"**Tipo:** {sug.get('tipo', 'Comentário').capitalize()}")
                        st.markdown(f"**Localização:** `{sug.get('localizacao', 'Não especificado')}`")
                        st.markdown(f"**Descrição:** {sug.get('descricao', 'Sem descrição.')}")
                        st.markdown("--- ")
                else:
                    st.info("Nenhuma diferença significativa ou sugestão de revisão encontrada.")

with stem_tab:
    st.header("Ferramentas para Conteúdo Específico (STEM/Gêneros) com IA")
    st.write("Formate e valide conteúdo especializado como código-fonte, fórmulas matemáticas ou outros formatos específicos do seu gênero literário com o auxílio da IA.")

    tipo_conteudo_especifico = st.selectbox(
        "Tipo de Conteúdo Específico:",
        ["Código Python", "Fórmula LaTeX", "Roteiro de Cinema", "Partitura Musical"],
        key='stem_content_type'
    )
    conteudo_bruto = st.text_area(
        f"Insira o {tipo_conteudo_especifico} para formatação:",
        "def hello_world():\n    print(\"Hello, World!\")" if tipo_conteudo_especifico == "Código Python" else "\\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}}",
        height=300,
        key='stem_content_input'
    )

    if st.button(f"⚙️ Formatar {tipo_conteudo_especifico} com IA"):
        if not conteudo_bruto.strip():
            st.warning(f"Por favor, insira o {tipo_conteudo_especifico} para formatar.")
        else:
            with st.spinner(f"Formatando {tipo_conteudo_especifico} com IA..."):
                conteudo_formatado = formatar_conteudo_especifico_ia(conteudo_bruto, tipo_conteudo_especifico)
            
            if "[ERRO DE CONEXÃO DA API]" in conteudo_formatado:
                st.error(f"Falha na formatação: {conteudo_formatado}")
            else:
                st.subheader(f"{tipo_conteudo_especifico} Formatado:")
                st.code(conteudo_formatado, language='python' if tipo_conteudo_especifico == 'Código Python' else 'latex')

with slides_tab:
    st.header("Geração de Apresentações de Slides com IA")
    st.write("Crie apresentações profissionais automaticamente a partir do seu texto, com layouts e conteúdos sugeridos pela IA.")

    texto_base_slides = st.text_area(
        "Insira o texto base para a apresentação (ou o texto do miolo será usado):",
        st.session_state['texto_completo'][:2000] if st.session_state.get('texto_completo') else "A interocepção é a percepção do estado interno do corpo. Ela desempenha um papel fundamental na regulação emocional e na autoconsciência. Estudos recentes indicam que a interocepção está ligada a diversas condições de saúde mental, como ansiedade e depressão. O treinamento da interocepção pode ser uma nova abordagem terapêutica.",
        height=300,
        key='slides_text_input'
    )
    tema_slides = st.text_input(
        "Tema da Apresentação:",
        "A Importância da Interocepção na Saúde Mental",
        key='slides_theme_input'
    )
    num_slides_input = st.slider(
        "Número de Slides (máx. 12 para esta versão):",
        min_value=1,
        max_value=12,
        value=5,
        step=1,
        key='slides_num_input'
    )

    if st.button("📊 Gerar Slides com IA"):
        if not texto_base_slides.strip():
            st.warning("Por favor, insira um texto base para gerar os slides.")
        else:
            with st.spinner("Gerando slides com IA..."):
                slides_gerados = gerar_slides_ia(texto_base_slides, tema_slides, num_slides_input)
            
            if slides_gerados and isinstance(slides_gerados, list) and slides_gerados[0] and isinstance(slides_gerados[0], dict) and "[ERRO DE CONEXÃO DA API]" in slides_gerados[0].get("conteudo", ""):
                st.error(f"Falha na geração de slides: {slides_gerados[0].get('conteudo', 'Erro desconhecido')}")
            elif slides_gerados and isinstance(slides_gerados, list):
                st.subheader("Slides Gerados:")
                for i, slide in enumerate(slides_gerados):
                    st.markdown(f"### Slide {i+1}: {slide.get('titulo', 'Sem Título')}")
                    st.markdown(f"**Layout Sugerido:** {slide.get('layout', 'Texto')}")
                    st.write(slide.get('conteudo', ''))
                    st.markdown("--- ")

def fastformat_options_ui() -> FastFormatOptions:
    st.sidebar.markdown("## FastFormat")
    preset = st.sidebar.selectbox(
        "Preset",
        ["Básico (recomendado)", "Tipográfico (ênfase em aspas/dashes)", "Conservador", "Personalizado"],
        index=0
    )

    # Valores padrão
    opts = default_options()

    if preset == "Básico (recomendado)":
        opts.normalize_spaces = True
        opts.compress_blank_lines = True
        opts.max_blank_lines = 1
        opts.punctuation_spacing = True
        opts.ellipses = True
        opts.fix_double_punct = True
        opts.dashes_ranges_en = True
        opts.dashes_aside_em = True
        opts.quotes = True
        opts.quotes_style = "typographic"
        opts.capitalize_sentences = False
        opts.tidy_units_nbsp = True

    elif preset == "Tipográfico (ênfase em aspas/dashes)":
        opts.normalize_spaces = True
        opts.compress_blank_lines = True
        opts.max_blank_lines = 1
        opts.punctuation_spacing = True
        opts.ellipses = True
        opts.fix_double_punct = True
        opts.dashes_ranges_en = True
        opts.dashes_aside_em = True
        opts.quotes = True
        opts.quotes_style = "typographic"
        opts.capitalize_sentences = True
        opts.tidy_units_nbsp = True

    elif preset == "Conservador":
        opts.normalize_spaces = True
        opts.compress_blank_lines = True
        opts.max_blank_lines = 1
        opts.punctuation_spacing = True
        opts.ellipses = False
        opts.fix_double_punct = True
        opts.dashes_ranges_en = False
        opts.dashes_aside_em = False
        opts.quotes = False
        opts.quotes_style = "straight"
        opts.capitalize_sentences = False
        opts.tidy_units_nbsp = False

    else:
        st.sidebar.caption("Personalize as regras abaixo:")

    # Se for "Personalizado", renderiza os toggles; nos outros, permite ajustes finos se quiser
    with st.sidebar.expander("Regras do FastFormat", expanded=(preset == "Personalizado")):
        opts.normalize_spaces = st.checkbox("Normalizar espaços (duplicados, finais de linha)", value=opts.normalize_spaces)
        opts.compress_blank_lines = st.checkbox("Comprimir linhas em branco", value=opts.compress_blank_lines)
        if opts.compress_blank_lines:
            opts.max_blank_lines = st.number_input("Máximo de linhas em branco consecutivas", min_value=1, max_value=3, value=opts.max_blank_lines, step=1)
        opts.punctuation_spacing = st.checkbox("Ajustar espaçamento de pontuação", value=opts.punctuation_spacing)
        opts.ellipses = st.checkbox("Normalizar reticências", value=opts.ellipses)
        opts.fix_double_punct = st.checkbox("Corrigir pontuação repetida (!!, ??)", value=opts.fix_double_punct)
        c1, c2 = st.columns(2)
        with c1:
            opts.dashes_ranges_en = st.checkbox("En dash em intervalos numéricos (10–20)", value=opts.dashes_ranges_en)
        with c2:
            opts.dashes_aside_em = st.checkbox("Em dash em incisos ( — )", value=opts.dashes_aside_em)
        opts.quotes = st.checkbox("Normalizar aspas", value=opts.quotes)
        if opts.quotes:
            opts.quotes_style = st.radio("Estilo de aspas", options=["typographic", "straight"], format_func=lambda x: "Tipográficas (“ ”, ‘ ’)" if x=="typographic" else "Retas (" ')", index=0 if opts.quotes_style=="typographic" else 1)
        opts.capitalize_sentences = st.checkbox("Capitalizar início de frases (heurístico)", value=opts.capitalize_sentences)
        opts.tidy_units_nbsp = st.checkbox("Espaço irredutível em unidades (10 kg) e 10% sem espaço", value=opts.tidy_units_nbsp)

    return opts

def fastformat_section(texto_inicial: str = "") -> str:
    st.markdown("## FastFormat")
    st.caption("Padronize o texto com regras tipográficas e de espaçamento. Pré-visualize as alterações antes de aplicar.")

    opts = fastformat_options_ui()

    texto_original = st.text_area("Texto de entrada", value=texto_inicial, height=240, key="ff_texto_original")
    col_a, col_b, col_c = st.columns([1,1,1])

    formatted_preview = None
    report = None

    with col_a:
        if st.button("Pré-visualizar alterações"):
            if not texto_original.strip():
                st.warning("Cole ou digite um texto para pré-visualizar.")
            else:
                formatted_preview, report = apply_fastformat(texto_original, opts)
                diff = make_unified_diff(texto_original, formatted_preview)
                if not diff:
                    st.info("Nenhuma alteração necessária segundo as regras atuais.")
                else:
                    st.code(diff, language="diff")
                    st.json(report)

    with col_b:
        aplicar = st.button("Aplicar FastFormat")
    with col_c:
        exportar = st.button("Gerar DOCX formatado")

    # Aplica de fato no texto
    texto_final = texto_original
    if aplicar:
        texto_final, report = apply_fastformat(texto_original, opts)
        st.success("FastFormat aplicado ao texto.")
        with st.expander("Relatório de alterações"):
            st.json(report)
        st.text_area("Texto formatado (resultado)", value=texto_final, height=240, key="ff_texto_formatado")

    # Exporta DOCX com o resultado atual (se houve aplicação, usa texto_final; caso contrário, aplica on-the-fly)
    if exportar:
        resultado = texto_final
        if resultado == texto_original:
            resultado, report = apply_fastformat(texto_original, opts)

        # Gera DOCX simples, respeitando parágrafos
        doc = Document()
        for bloco in resultado.split("\n\n"):
            p = doc.add_paragraph()
            for linha in bloco.split("\n"):
                if linha:
                    p.add_run(linha)
                p.add_run("\n")
        # Remover a última quebra extra (opcional)
        bio = __import__("io").BytesIO()
        doc.save(bio)
        st.download_button(
            label="Baixar DOCX",
            data=bio.getvalue(),
            file_name="texto_fastformat.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    return texto_final

with st.expander("FastFormat (clique para abrir)", expanded=True):
    # Se você já mantém um texto principal em session_state, passe aqui:
    texto_existente = st.session_state.get("texto_principal", "")
    texto_formatado = fastformat_section(texto_existente)
    # Se quiser, salve o resultado no estado principal após aplicar:
    if texto_formatado != texto_existente:
        st.session_state["texto_principal"] = texto_formatado
