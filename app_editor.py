import os
import streamlit as st
from openai import OpenAI
from docx import Document
from io import BytesIO
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import requests # Para baixar a imagem da URL

# --- CONFIGURAÇÃO 1: DICIONÁRIO DE TAMANHOS KDP (Miolo) ---
KDP_SIZES = {
    "Padrão EUA (6x9 in)": {"name": "6 x 9 in", "width_in": 6.0, "height_in": 9.0, "width_cm": 15.24, "height_cm": 22.86, "papel_fator": 0.00115},
    "Padrão A5 (5.83x8.27 in)": {"name": "A5 (14.8 x 21 cm)", "width_in": 5.83, "height_in": 8.27, "width_cm": 14.8, "height_cm": 21.0, "papel_fator": 0.00115},
    "Pocket (5x8 in)": {"name": "5 x 8 in", "width_in": 5.0, "height_in": 8.0, "width_cm": 12.7, "height_cm": 20.32, "papel_fator": 0.00115},
    "Maior (7x10 in)": {"name": "7 x 10 in", "width_in": 7.0, "height_in": 10.0, "width_cm": 17.78, "height_cm": 25.4, "papel_fator": 0.00115},
}

# --- CONFIGURAÇÃO 2: TEMPLATES DE ESTILO DE DIAGRAMAÇÃO ---
STYLE_TEMPLATES = {
    "Romance Clássico (Garamond)": {"font_name": "Garamond", "font_size_pt": 11, "line_spacing": 1.15, "indent": 0.5},
    "Thriller Moderno (Droid Serif)": {"font_name": "Droid Serif", "font_size_pt": 10, "line_spacing": 1.05, "indent": 0.3},
    "Não-Ficção (Times New Roman)": {"font_name": "Times New Roman", "font_size_pt": 12, "line_spacing": 1.5, "indent": 0.0},
}

# --- 0. Configuração e Inicialização (Chave OpenAI) ---

st.set_page_config(page_title="Editor Literário IA - Pré-Impressão", layout="wide")
st.title("📚 Editor Literário com GPT AI")
st.subheader("Pré-Impressão Completa: Editoração Avançada, KDP e Geração de Capa.")

API_KEY_NAME = "OPENAI_API_KEY"
PROJECT_ID_NAME = "OPENAI_PROJECT_ID"
MODEL_NAME = "gpt-4o-mini" 

try:
    API_KEY = None
    PROJECT_ID = None
    if hasattr(st, 'secrets'):
         if API_KEY_NAME in st.secrets:
             API_KEY = st.secrets[API_KEY_NAME]
         if PROJECT_ID_NAME in st.secrets:
             PROJECT_ID = st.secrets[PROJECT_ID_NAME]
    
    if not API_KEY or not PROJECT_ID:
        # Apenas mostra o erro se a API não estiver definida, mas permite a execução
        # para visualização da interface (embora as funções de IA falhem).
        st.error(f"ERRO: Chave e ID do Projeto OpenAI não configurados. Por favor, adicione '{API_KEY_NAME}' e '{PROJECT_ID_NAME}' no Streamlit Secrets.")
        
    client = OpenAI(
        api_key=API_KEY if API_KEY else "dummy_key", # Usa dummy key se não estiver em secrets
        project=PROJECT_ID if PROJECT_ID else "dummy_project"
    )
except Exception as e:
    st.error(f"Erro na inicialização da API: {e}")
    st.stop()


# --- 1. Função de Chamada da API (UNIFICADA) ---
def call_openai_api(system_prompt: str, user_content: str, max_tokens: int = 3000) -> str:
    """Função genérica para chamar a API da OpenAI."""
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
        return f"[ERRO DE CONEXÃO DA API] Falha ao se comunicar com a OpenAI. Detalhes: {e}"


# --- 2. Revisão Parágrafo a Parágrafo (Mantido) ---
def revisar_paragrafo(paragrafo_texto: str) -> str:
    """Envia o parágrafo para a API da OpenAI e recebe a versão editada."""
    if not paragrafo_texto.strip(): return "" 
    system_prompt = "Você é um editor literário de nível sênior. Sua tarefa é revisar, editar e aprimorar o parágrafo. Corrija gramática, aprimore o estilo e garanta a coerência. Retorne *apenas* o parágrafo revisado, sem comentários."
    user_content = f"Parágrafo a ser editado:\n---\n{paragrafo_texto}\n---"
    texto_revisado = call_openai_api(system_prompt, user_content, max_tokens=500)
    if "[ERRO DE CONEXÃO DA API]" in texto_revisado:
        return paragrafo_texto
    return texto_revisado


# --- 3. Geração de Relatório Estrutural (Mantido) ---
def gerar_relatorio_estrutural(texto_completo: str) -> str:
    """Analisa o texto completo para dar feedback estrutural."""
    system_prompt = "Você é um Editor-Chefe. Gere um breve Relatório de Revisão para o autor. Foque em: Ritmo da Narrativa, Desenvolvimento de Personagens e Estrutura Geral. Use títulos e bullet points."
    user_content = f"MANUSCRITO PARA ANÁLISE:\n---\n{texto_completo[:15000]}\n---"
    return call_openai_api(system_prompt, user_content)


# --- 4. Geração de Elementos Pré-Textuais (Copyright, Sobre o Autor) ---
def gerar_elementos_pre_textuais(titulo: str, autor: str, ano: int, texto_completo: str) -> str:
    """Gera o texto de Copyright e a bio para a página Sobre o Autor."""
    system_prompt = """
    Você é um gerente de editora. Gere o conteúdo essencial de abertura e fechamento para um livro (Ficção/Não-Ficção).
    Use os dados fornecidos e o tom do manuscrito para criar uma bio atraente.
    """
    user_content = f"""
    Título: {titulo}
    Autor: {autor}
    Ano: {ano}
    Manuscrito (Amostra): {texto_completo[:5000]}
    
    Gere o resultado no formato estrito:
    
    ### 1. Página de Copyright e Créditos
    
    [Informações sobre Copyright (Ex: Direitos Autorais 2025, Carlos Honorato. Todos os direitos reservados. Proibida a reprodução.)]
    [Informações de Publicação (Ex: Primeira Edição, E-book/Impresso, 2025)]
    [Aviso Legal padrão]
    
    ### 2. Página 'Sobre o Autor'
    
    [Bio envolvente de 2-3 parágrafos, formatada para uma página de livro.]
    """
    return call_openai_api(system_prompt, user_content)


# --- 5. Relatório de Estilo Avançado (Contra Clichês e Vícios) ---
def gerar_relatorio_estilo_avancado(texto_completo: str) -> str:
    """Análise de Estilo focada em clichês, redundâncias e voz passiva."""
    system_prompt = """
    Você é um Crítico de Estilo Literário. Sua função é analisar o manuscrito para identificar e criticar vícios de escrita.
    Gere um relatório focado nos 3 itens abaixo.
    
    1. **Vícios de Linguagem:** Cite 3-5 exemplos de advérbios desnecessários ou clichês (Ex: "correu rapidamente", "sorriu ironicamente") e sugira como reescrever.
    2. **Voz Passiva:** Identifique onde a voz passiva torna o texto fraco e sugira a conversão para voz ativa.
    3. **Ritmo e Leitura (Pontuação):** Dê uma pontuação de 1 a 10 para a fluidez do texto e justifique (Frases longas? Uso excessivo de vírgulas?).
    """
    user_content = f"MANUSCRITO PARA ANÁLISE DE ESTILO:\n---\n{texto_completo[:10000]}\n---"
    return call_openai_api(system_prompt, user_content)

# --- 6. Geração de Conteúdo de Capa/Contracapa (Marketing) ---
def gerar_conteudo_capa_contracapa(titulo: str, autor: str, texto_completo: str) -> str:
    """Gera o blurb para contracapa e sugestões de arte."""
    system_prompt = """
    Você é um Copywriter de Best-sellers e Designer de Capas. Sua tarefa é criar um blurb de contracapa envolvente e dar sugestões visuais.
    Gere o resultado no formato estrito:
    
    ### BLURB (Contracapa)
    [Texto de 3-4 parágrafos, emocionante e com gancho, para a contracapa.]
    
    ### SUGESTÃO DE ARTE PARA A CAPA:
    [Descrição visual detalhada (prompt) para uma IA de geração de imagem (DALL-E 3). Foque em cores, elementos e estilo artístico que capturem a essência do livro.]
    """
    user_content = f"Título: {titulo}, Autor: {autor}. Manuscrito (Amostra): {texto_completo[:5000]}"
    return call_openai_api(system_prompt, user_content)


# --- 7. Geração do Relatório de Conformidade KDP (Mantido) ---
def gerar_relatorio_conformidade_kdp(titulo: str, autor: str, page_count: int, format_data: dict, espessura_cm: float, capa_largura_total_cm: float, capa_altura_total_cm: float) -> str:
    """Gera um checklist de conformidade técnica para upload na Amazon KDP."""
    tamanho_corte = format_data['name']
    prompt_kdp = f"""
    Você é um Especialista Técnico em Publicação e Conformidade da Amazon KDP. Gere um Relatório de Conformidade focado em upload bem-sucedido para Livros Físicos (Brochura) e eBooks.
    [Dados de Formato Omitidos para concisão do prompt]
    
    Gere o relatório usando o formato de lista e títulos, focando em:
    
    ### 1. Livro Físico (Brochura - Especificações)
    - **Tamanho de Corte Final (Miolo):** {tamanho_corte} ({format_data['width_cm']} x {format_data['height_cm']} cm).
    - **Dimensões do Arquivo de Capa (para Designer):** {capa_largura_total_cm} cm (Largura Total) x {capa_altura_total_cm} cm (Altura Total).
    - **Requisito do Miolo/Sumário:** Para gerar o Sumário/TOC automático no PDF/EPUB, verifique se todos os títulos de capítulos estão marcados com o estilo 'Título 1' no DOCX baixado.

    ### 2. eBook (EPUB/Kindle)
    Checklist de 5 itens essenciais para um EPUB de qualidade (uso de estilos, remoção de espaços duplos, etc.).
    
    ### 3. Otimização de Metadados (SEO Básico KDP)
    Sugira 3 categorias de nicho da Amazon e 3 palavras-chave de cauda longa para otimizar a listagem do livro.
    """
    return call_openai_api("Você é um especialista em publicação KDP.", prompt_kdp)


# --- 8. Função: Geração de Imagem para Capa ---
def gerar_capa_ia(prompt_capa: str) -> str:
    """
    Chama a API DALL-E 3 para gerar uma imagem para a capa do livro.
    """
    if not prompt_capa.strip():
        return "Por favor, insira um prompt para gerar a capa."

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt_capa,
            size="1024x1024",  # Tamanho comum para capas digitais
            quality="standard", # Pode ser "hd" para melhor qualidade, mas mais caro
            n=1 # Apenas uma imagem
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        return f"[ERRO GERAÇÃO DE CAPA] Falha ao gerar a imagem: {e}. Verifique se sua conta OpenAI tem créditos para DALL-E 3."


# --- 9. Funções de Diagramação: Inserção de Páginas Pré-textuais e Sumário ---

def adicionar_pagina_rosto(documento: Document, titulo: str, autor: str, style_data: dict):
    """Adiciona uma página de rosto formatada."""
    font_name = style_data['font_name']
    
    documento.add_page_break()

    p_title = documento.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.add_run(titulo).bold = True
    p_title.runs[0].font.size = Pt(24) # Título maior
    p_title.runs[0].font.name = font_name
    
    for _ in range(5):
        documento.add_paragraph()
    
    p_author = documento.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author.add_run(autor)
    p_author.runs[0].font.size = Pt(16)
    p_author.runs[0].font.name = font_name

    documento.add_page_break()


def adicionar_sumario_placeholder(documento: Document):
    """Adiciona a página de Sumário e instruções para o campo de TOC."""
    documento.add_page_break()
    
    p_header = documento.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.add_run("Sumário").bold = True
    p_header.runs[0].font.size = Pt(18)
    
    documento.add_paragraph("").add_run().add_break() # Espaço
    documento.add_paragraph("").add_run().add_break() # Espaço

    p_inst = documento.add_paragraph("Para gerar o índice automático no documento final, vá em 'Referências' -> 'Sumário' e clique em 'Inserir Sumário'. Todos os títulos de capítulo já foram marcados.")
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.runs[0].font.size = Pt(10)

    documento.add_page_break()


# --- 10. Função Principal: Processamento de Revisão e Diagramação DOCX ---

def processar_manuscrito(uploaded_file, format_data, style_data, pre_text_content, status_placeholder):
    documento_original = Document(uploaded_file)
    documento_revisado = Document()
    
    # --- CONFIGURAÇÃO DINÂMICA DO LIVRO (Diagramação) ---
    width_in = format_data['width_in']
    height_in = format_data['height_in']
    
    section = documento_revisado.sections[0]
    section.page_width = Inches(width_in)
    section.page_height = Inches(height_in)
    section.left_margin = Inches(1.0) 
    section.right_margin = Inches(0.6) 
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)

    # --- CONFIGURAÇÃO DE ESTILO PROFISSIONAL (EDITORAÇÃO) ---
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
    
    # --- INSERÇÃO DE ELEMENTOS PRÉ-TEXTUAIS ---
    
    # Página de Rosto (Título e Autor)
    adicionar_pagina_rosto(documento_revisado, st.session_state['book_title'], st.session_state['book_author'], style_data)
    
    # Página de Copyright (Conteúdo gerado pela IA)
    copyright_text_full = pre_text_content.split('### 2. Página \'Sobre o Autor\'')[0].strip()
    p_copy_header = documento_revisado.add_paragraph()
    p_copy_header.add_run("### 1. Página de Copyright e Créditos").bold = True # Adiciona o cabeçalho original
    p_copy = documento_revisado.add_paragraph(copyright_text_full.replace("### 1. Página de Copyright e Créditos", "").strip()) # Remove o cabeçalho duplicado
    p_copy.style = 'Normal'
    p_copy.runs[0].font.size = Pt(8) # Fonte menor para copyright
    documento_revisado.add_page_break()

    # Sumário (Placeholder e Instruções)
    adicionar_sumario_placeholder(documento_revisado)

    
    # --- PROCESSAMENTO DO MIOLO (Revisão Parágrafo a Parágrafo) ---
    
    paragrafos = documento_original.paragraphs
    total_paragrafos = len(paragrafos)
    texto_completo = ""
    
    progress_bar = st.progress(0, text="Processando 0%")
    
    for i, paragrafo in enumerate(paragrafos):
        texto_original = paragrafo.text
        texto_completo += texto_original + "\n"
        
        percent_complete = int((i + 1) / total_paragrafos * 100)
        progress_bar.progress(percent_complete, text=f"Fase 2/7: Revisando e diagramando o miolo... {percent_complete}%")

        if len(texto_original.strip()) < 10:
            documento_revisado.add_paragraph(texto_original)
            continue 

        texto_revisado = revisar_paragrafo(texto_original)
        
        novo_paragrafo = documento_revisado.add_paragraph(texto_revisado)
        
        # Heurística para identificar títulos de capítulo e aplicar estilo "Heading 1"
        if len(texto_original.strip()) > 0 and (
            texto_original.strip().lower().startswith("capítulo") or
            texto_original.strip().lower().startswith("introdução") or
            texto_original.strip().lower().startswith("prólogo") or
            texto_original.strip().lower().startswith("epílogo") or
            texto_original.strip().lower().startswith("conclusão") or
            (len(texto_original.strip().split()) <= 5 and texto_original.strip().isupper()) # Ex: CAPÍTULO UM
        ):
            novo_paragrafo.style = 'Heading 1' 
            novo_paragrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
            novo_paragrafo.runs[0].font.size = Pt(18) # Títulos maiores
            novo_paragrafo.runs[0].font.name = font_name
            documento_revisado.add_paragraph("") # Espaço após o título
        else:
            novo_paragrafo.style = 'Normal'
        
    progress_bar.progress(100, text="Fase 2/7: Revisão e diagramação do miolo concluída! 🎉")

    # --- INSERÇÃO DA PÁGINA PÓS-TEXTUAL ---
    documento_revisado.add_page_break()
    about_author_text_full = pre_text_content.split('### 2. Página \'Sobre o Autor\'')[1].strip()
    
    p_header = documento_revisado.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.add_run("Sobre o Autor").bold = True
    p_header.runs[0].font.size = Pt(16)
    
    documento_revisado.add_paragraph(about_author_text_full, style='Normal')

    return documento_revisado, texto_completo


# --- 11. Interface do Streamlit (UI) ---

# Inicialização dos dados na sessão
if 'book_title' not in st.session_state:
    st.session_state['book_title'] = "O Último Código de Honra"
    st.session_state['book_author'] = "Carlos Honorato"
if 'capa_prompt' not in st.session_state:
    st.session_state['capa_prompt'] = "Uma antiga biblioteca secreta com um livro empoeirado aberto, luz mística emanando dele, estilo arte digital, cores escuras e douradas, suspense."
if 'generated_image_url' not in st.session_state:
    st.session_state['generated_image_url'] = None


st.markdown("---")
st.subheader("1. Informações e Formato do Livro")

col1, col2 = st.columns(2)
with col1:
    st.session_state['book_title'] = st.text_input("Título do Livro", st.session_state['book_title'])
with col2:
    st.session_state['book_author'] = st.text_input("Nome do Autor", st.session_state['book_author'])

col3, col4 = st.columns(2)
with col3:
    format_option = st.selectbox(
        "Escolha o Formato do Miolo (Tamanho de Corte):",
        options=list(KDP_SIZES.keys()),
        index=1, 
    )
    selected_format_data = KDP_SIZES[format_option]

with col4:
    style_option = st.selectbox(
        "Escolha o Template de Estilo de Diagramação:",
        options=list(STYLE_TEMPLATES.keys()),
        index=0, 
        help="Altera a fonte, tamanho e espaçamento para o estilo escolhido (Ex: Garamond para romance)."
    )
    selected_style_data = STYLE_TEMPLATES[style_option]


st.markdown("---")

col5, col6 = st.columns(2)
with col5:
    page_count = st.number_input("Contagem Aproximada de Páginas (Miolo)", min_value=10, value=250, step=10, help="Use a contagem de páginas do seu DOCX antes da diagramação.")
with col6:
    uploaded_file = st.file_uploader(
        "2. Faça o upload do seu arquivo .docx", 
        type=['docx'],
        help="O processamento de arquivos grandes pode levar alguns minutos."
    )

st.warning("O documento final será um DOCX completo com PÁGINA DE ROSTO, COPYRIGHT, SUMÁRIO (instruções), PÁGINA SOBRE O AUTOR, além do miolo diagramado e revisado.")

if uploaded_file is not None and st.button("3. Iniciar PRÉ-IMPRESSÃO COMPLETA"):
    if not st.session_state['book_title'] or not st.session_state['book_author']:
        st.error("Por favor, preencha o Título e o Autor antes de iniciar.")
        st.stop()
        
    st.info("Atenção: O processo de Pré-Impressão foi iniciado. Isso pode levar alguns minutos...")
    
    # --- NOVO: Placeholder para o status detalhado ---
    status_placeholder = st.empty()
    
    # --- PASSO 0: Geração dos Elementos Pré-textuais ---
    status_placeholder.info("Fase 1/7: Gerando conteúdo de Copyright e 'Sobre o Autor' com IA...")
    with st.spinner("Gerando conteúdo de Copyright e a página 'Sobre o Autor' com a IA..."):
        # Usamos uma amostra do texto para que a IA capture o tom
        uploaded_file.seek(0)
        pre_text_content = gerar_elementos_pre_textuais(st.session_state['book_title'], st.session_state['book_author'], 2025, uploaded_file.getvalue().decode('utf-8', errors='ignore')[:5000])

    # Processa o manuscrito (revisão e diagrama)
    status_placeholder.info("Fase 2/7: Processando a Revisão e Diagramação Parágrafo a Parágrafo...")
    uploaded_file.seek(0)
    documento_revisado, texto_completo = processar_manuscrito(uploaded_file, selected_format_data, selected_style_data, pre_text_content, status_placeholder)
    
    if documento_revisado:
        
        # --- PASSO A: Geração do Relatório Estrutural ---
        status_placeholder.info("Fase 3/7: Gerando o Relatório Estrutural (Editor-Chefe)...")
        st.subheader("RESULTADO 1: Relatório Estrutural (Editor-Chefe)")
        with st.spinner("Analisando ritmo e personagens para o relatório estrutural..."):
            relatorio = gerar_relatorio_estrutural(texto_completo)
        st.text_area("Relatório Estrutural da IA:", relatorio, height=300)
        
        # --- PASSO B: Relatório de Estilo Avançado ---
        status_placeholder.info("Fase 4/7: Gerando o Relatório de Estilo Avançado (Vícios e Clichês)...")
        st.subheader("RESULTADO 2: Relatório de Estilo (Contra Vícios e Clichês)")
        with st.spinner("Análise de vícios de linguagem e fluidez da escrita..."):
            relatorio_estilo = gerar_relatorio_estilo_avancado(texto_completo)
        st.markdown(relatorio_estilo)
        
        # --- PASSO C: Conteúdo de Capa/Contracapa (Marketing) ---
        status_placeholder.info("Fase 5/7: Gerando o Blurb de Marketing e Sugestões de Arte...")
        st.subheader("RESULTADO 3: Conteúdo de Capa/Contracapa (Marketing)")
        with st.spinner("Criando o blurb de marketing e sugestões de design..."):
            conteudo_capa = gerar_conteudo_capa_contracapa(st.session_state['book_title'], st.session_state['book_author'], texto_completo)
        st.text_area("Conteúdo de Vendas e Sugestões de Arte:", conteudo_capa, height=400)

        # --- PASSO D: Cálculos Técnicos DINÂMICOS ---
        status_placeholder.info("Fase 6/7: Realizando Cálculos Técnicos (Lombada/Capa) e Relatório KDP...")
        papel_fator = selected_format_data['papel_fator'] 
        espessura_cm = round(page_count * papel_fator, 2) 
        capa_largura_total_cm = round((selected_format_data['width_cm'] * 2) + espessura_cm, 2)
        capa_altura_total_cm = round(selected_format_data['height_cm'] + 0.6, 2)

        # --- PASSO E: Geração do Relatório de Conformidade KDP ---
        st.subheader("RESULTADO 5: Relatório de Conformidade KDP (Amazon)")
        with st.spinner("Gerando checklist técnico e de SEO para o upload na Amazon..."):
            relatorio_kdp = gerar_relatorio_conformidade_kdp(
                st.session_state['book_title'], st.session_state['book_author'], page_count, selected_format_data, 
                espessura_cm, capa_largura_total_cm, capa_altura_total_cm
            )
        st.markdown(relatorio_kdp)
        
        # --- FIM DO FLUXO PRINCIPAL ---
        status_placeholder.success("Fase 7/7: Processamento Concluído! Resultados Prontos para Análise e Geração de Capa.")
        
        # --- RESULTADO 4: Geração de Capa com IA ---
        st.subheader("RESULTADO 4: Criação de Capa com IA")
        st.markdown("Use o prompt abaixo (ou edite) para gerar uma imagem de capa. Pode levar alguns segundos.")
        
        if "SUGESTÃO DE ARTE PARA A CAPA:" in conteudo_capa:
            sugestao_arte = conteudo_capa.split("SUGESTÃO DE ARTE PARA A CAPA:")[1].strip()
            # Garante que o prompt original da IA seja usado se a caixa não tiver sido modificada
            st.session_state['capa_prompt'] = st.text_area("Prompt para a Imagem da Capa:", sugestao_arte if st.session_state['capa_prompt'] == "Uma antiga biblioteca secreta com um livro empoeirado aberto, luz mística emanando dele, estilo arte digital, cores escuras e douradas, suspense." else st.session_state['capa_prompt'], height=100)
        else:
            st.session_state['capa_prompt'] = st.text_area("Prompt para a Imagem da Capa:", st.session_state['capa_prompt'], height=100)

        if st.button("Gerar Capa com IA"):
            with st.spinner("Gerando imagem de capa com DALL-E 3..."):
                image_output = gerar_capa_ia(st.session_state['capa_prompt'])
                if "http" in image_output: # Se for uma URL, foi bem-sucedido
                    st.session_state['generated_image_url'] = image_output
                    st.success("Capa gerada com sucesso!")
                else:
                    st.error(image_output) # Exibe a mensagem de erro da IA

        if st.session_state['generated_image_url']:
            st.image(st.session_state['generated_image_url'], caption="Capa Sugerida pela IA", use_column_width=True)
            # Botão para baixar a imagem (opcional)
            try:
                response = requests.get(st.session_state['generated_image_url'])
                if response.status_code == 200:
                    st.download_button(
                        label="Baixar Imagem da Capa (.png)",
                        data=response.content,
                        file_name=f"Capa_IA_{st.session_state['book_title'].replace(' ', '_')}.png",
                        mime="image/png"
                    )
            except Exception as e:
                st.warning(f"Não foi possível baixar a imagem da capa: {e}")

        
        # --- RESULTADO 6: Resumo Técnico Final e Downloads ---
        st.subheader("RESULTADO 6: Resumo Técnico Final e Downloads")
        
        st.markdown(f"""
        O seu produto de pré-impressão está pronto. A diagramação foi aplicada no formato **{selected_format_data['name']}** com o estilo **{selected_style_data['font_name']}**.

        #### 📄 Especificações do Livro Físico (KDP / Gráfica)
        - **Miolo (PDF) Tamanho:** {selected_format_data['width_cm']} cm x {selected_format_data['height_cm']} cm
        - **Espessura da Lombada (Estimada):** **{espessura_cm} cm**
        - **Capa Completa (Largura x Altura):** **{capa_largura_total_cm} cm x {capa_altura_total_cm} cm** (Entregue esta dimensão ao seu designer!)
        """)


        # --- Downloads Finais ---
        st.markdown("#### ⬇️ Downloads Finais")
        
        # Download do DOCX Diagramado
        buffer = BytesIO()
        documento_revisado.save(buffer)
        buffer.seek(0)
        st.download_button(
            label="1. Baixar Manuscrito Diagramado e Formatado (.docx)",
            data=buffer,
            file_name=f"{st.session_state['book_title'].replace(' ', '_')}_PRE_IMPRESSAO.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        # Downloads dos Relatórios (opcional)
        relatorio_buffer = BytesIO((relatorio + "\n\n---\n\n" + relatorio_estilo + "\n\n---\n\n" + relatorio_kdp).encode('utf-8'))
        st.download_button(
            label="2. Baixar Todos os Relatórios (Estrutura, Estilo e KDP) (.txt)",
            data=relatorio_buffer,
            file_name="Relatorios_Completos.txt",
            mime="text/plain"
        )
        st.balloons()
