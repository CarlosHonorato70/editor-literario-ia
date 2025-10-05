import os
import streamlit as st
from openai import OpenAI
from docx import Document
from io import BytesIO
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.section import WD_SECTION
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.section import Section, _HeaderFooter
import requests 
import time 
from typing import Optional, Dict, Tuple, Any, List
import math 
import json 

# --- CONFIGURAÇÃO DE CONSTANTES E ESTADO INICIAL ---

# 1. DICIONÁRIO DE TAMANHOS KDP/GRÁFICA (Miolo)
KDP_SIZES: Dict[str, Dict] = {
    "Padrão EUA (6x9 in)": {"name": "6 x 9 in", "width_in": 6.0, "height_in": 9.0, "width_cm": 15.24, "height_cm": 22.86, "papel_fator": 0.00115}, 
    "Padrão A5 (5.83x8.27 in)": {"name": "A5 (14.8 x 21 cm)", "width_in": 5.83, "height_in": 8.27, "width_cm": 14.8, "height_cm": 21.0, "papel_fator": 0.00115},
    "Pocket (5x8 in)": {"name": "5 x 8 in", "width_in": 5.0, "height_in": 8.0, "width_cm": 12.7, "height_cm": 20.32, "papel_fator": 0.00115},
}

# 2. VOZES DE GERAÇÃO
GENERATION_VOICES: List[str] = [
    "Clássico/Literário", "Diálogo Rápido", "Narrativa Lenta", "Acadêmico Formal", "Jornalístico Neutro"
]

# 3. ESTILOS DE CAPA
COVER_STYLES: List[str] = [
    "Capa de Fantasia Épica", "Capa de Romance Dramático", "Capa Minimalista Moderna", 
    "Capa de Suspense Noir", "Capa de Ficção Científica Futurista", "Capa de Não-Ficção Profissional"
]

# 4. INICIALIZAÇÃO DE ESTADO DO STREAMLIT
def init_state():
    """Inicializa as variáveis de estado de sessão necessárias."""
    if 'processed_state' not in st.session_state:
        st.session_state['processed_state'] = [] # Lista de capítulos e conteúdo
    if 'book_title' not in st.session_state:
        st.session_state['book_title'] = "Meu Livro IA"
    if 'book_genre' not in st.session_state:
        st.session_state['book_genre'] = "Ficção"
    if 'book_size' not in st.session_state:
        st.session_state['book_size'] = "Padrão EUA (6x9 in)"
    if 'openai_client' not in st.session_state:
        st.session_state['openai_client'] = None
    if 'generated_image_url' not in st.session_state:
        st.session_state['generated_image_url'] = None
    if 'system_prompt' not in st.session_state:
        # Prompt base para o modelo de texto
        st.session_state['system_prompt'] = "Você é um autor de best-sellers. Seu trabalho é escrever o próximo capítulo de um livro de {genre} intitulado '{title}', seguindo as diretrizes de escrita de {voice}. Mantenha o tom da narrativa consistente e desenvolva a trama a partir do ponto em que parou. O capítulo deve ter cerca de 1000 a 1500 palavras."
    if 'custom_cover_image_bytes' not in st.session_state:
        st.session_state['custom_cover_image_bytes'] = None

# --- FUNÇÕES DE CONEXÃO E LLM ---

def get_client(api_key: str, endpoint_url: str = None) -> Optional[OpenAI]:
    """Cria e retorna uma instância do cliente OpenAI, verificando a validade da chave."""
    if not api_key:
        return None
    try:
        if endpoint_url:
            # Assumindo que a chave Copilot/Microsoft usa um endpoint Azure/compatível
            client = OpenAI(
                api_key=api_key,
                base_url=endpoint_url 
            )
        else:
            client = OpenAI(api_key=api_key)
        
        # Tentativa de chamada leve (como listar modelos) para validar a chave
        client.models.list() 
        return client
    except Exception as e:
        st.error(f"Erro ao conectar à API: {e}. Verifique sua chave.")
        return None

def generate_text_content(prompt: str, client: OpenAI, voice: str, title: str, genre: str, previous_chapters: List[Dict[str, Any]] = None) -> str:
    """Gera o conteúdo de um novo capítulo."""
    if not client:
        return "Erro: Cliente API não inicializado. Verifique as chaves."
    
    # Monta o histórico de conversação/capítulos anteriores para contexto
    messages = [{"role": "system", "content": st.session_state['system_prompt'].format(genre=genre, title=title, voice=voice)}]
    if previous_chapters:
        # Adiciona o conteúdo dos últimos 3 capítulos para contexto, se existirem
        for chapter in previous_chapters[-3:]:
            messages.append({"role": "assistant", "content": f"Capítulo {chapter['chapter_number']}: {chapter['content'][:500]}..."}) # Limita o contexto
    
    messages.append({"role": "user", "content": prompt})

    try:
        with st.spinner("Gerando novo capítulo..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini", # Modelo atualizado para melhor desempenho
                messages=messages,
                max_tokens=4000,
                temperature=0.8
            )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro na geração de texto: {e}")
        return f"Erro na geração de texto: {e}"

def generate_cover_art_url(prompt: str, client: OpenAI) -> Optional[str]:
    """Gera a imagem de capa usando DALL-E e retorna a URL."""
    if not client:
        st.error("Cliente API não inicializado para geração de imagem.")
        return None
    try:
        with st.spinner("Gerando arte da capa..."):
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792", # Proporção ideal para capa de livro (9:16)
                quality="hd",
                n=1,
            )
        return response.data[0].url
    except Exception as e:
        st.error(f"Erro na geração de imagem (DALL-E): {e}")
        return None

def generate_book_summary(client: OpenAI, title: str, genre: str, chapters: List[Dict[str, Any]]) -> str:
    """Gera um sumário completo (TOC) e sinopse do livro."""
    if not client:
        return "Erro: Cliente API não inicializado."
    
    # Constrói o conteúdo total para o contexto
    full_text = f"Livro: {title} ({genre})\n\n"
    for chapter in chapters:
        full_text += f"Capítulo {chapter['chapter_number']}:\n{chapter['content'][:1500]}...\n\n" # Limita o contexto

    summary_prompt = (
        f"Com base no texto completo do livro fornecido abaixo, composto por {len(chapters)} capítulos, "
        "gere a **Sinopse** (um parágrafo conciso e cativante) e a **Lista de Capítulos** (apenas títulos, 1 a 2 frases por título) "
        "em formato Markdown, usando o seguinte formato:\n\n"
        "## Sinopse\n[Sinopse aqui]\n\n"
        "## Capítulos (Apenas Títulos)\n* Capítulo 1: [Título do Capítulo 1]\n* Capítulo 2: [Título do Capítulo 2]\n..."
    )
    
    messages = [
        {"role": "system", "content": "Você é um editor literário experiente. Sua tarefa é analisar o livro e gerar uma sinopse profissional e a lista de títulos de capítulos."},
        {"role": "user", "content": f"{summary_prompt}\n\n--- LIVRO COMPLETO ---\n{full_text}"}
    ]

    try:
        with st.spinner("Gerando Sinopse e Sumário..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=messages,
                max_tokens=3000,
                temperature=0.2
            )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro na geração do sumário: {e}")
        return f"Erro na geração do sumário: {e}"

# --- FUNÇÕES DOCX (INCLUINDO NUMERAÇÃO DE PÁGINAS E SUMÁRIO) ---

def create_page_number_footer(section: Section, page_num_start: int):
    """Adiciona a numeração de página ao rodapé da seção, começando em um número específico."""
    footer = section.footer
    
    # Cria o parágrafo de numeração no rodapé
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Adiciona a numeração de página (campo PAGE)
    run = paragraph.add_run()
    # Adiciona o campo PAGE (código XML para numeração automática)
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    run._element.append(fldChar)
    
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'PAGE \\* MERGEFORMAT'
    run._element.append(instrText)
    
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'end')
    run._element.append(fldChar)

    # Configura o número inicial de página desta seção
    sect_pr = section._sectPr
    if sect_pr is None:
        sect_pr = OxmlElement('w:sectPr')
        section._element.append(sect_pr)
        
    pgNumType = OxmlElement('w:pgNumType')
    pgNumType.set(qn('w:start'), str(page_num_start))
    sect_pr.append(pgNumType)

def set_section_orientation(section: Section, orientation: WD_ORIENT):
    """Configura a orientação da seção (usado para garantir quebras limpas)."""
    section.orientation = orientation
    new_width, new_height = section.page_height, section.page_width
    section.page_width = new_width
    section.page_height = new_height

def export_docx(chapters: List[Dict[str, Any]], title: str, size_key: str, custom_cover_bytes: Optional[bytes], generated_image_url: Optional[str]) -> Tuple[bytes, str]:
    """Cria e salva o documento DOCX com numeração e sumário."""
    if not chapters:
        raise ValueError("Nenhum capítulo encontrado para exportação.")
        
    doc = Document()
    size_config = KDP_SIZES.get(size_key, KDP_SIZES["Padrão EUA (6x9 in)"])
    
    # 1. ESTILOS BASE E TAMANHO DE PÁGINA
    
    # Define o tamanho de página no Word (KDP/Gráfica)
    section = doc.sections[0]
    section.page_width = Inches(size_config['width_in'])
    section.page_height = Inches(size_config['height_in'])
    
    # Estilo base
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Georgia' # Fonte padrão para miolo de livro
    font.size = Pt(12)
    
    # Adiciona estilo de Título de Capítulo (Heading 1)
    h1_style = doc.styles['Heading 1']
    h1_font = h1_style.font
    h1_font.size = Pt(18)
    h1_font.name = 'Georgia'

    # --- INÍCIO DO CONTEÚDO ---
    
    # PÁGINA 1: CAPA
    if custom_cover_bytes:
        cover_image_bytes = custom_cover_bytes
        image_name = "Capa Externa.jpg"
    elif generated_image_url:
        try:
            response = requests.get(generated_image_url, timeout=10)
            response.raise_for_status() # Lança exceção para erros HTTP
            cover_image_bytes = BytesIO(response.content).read()
            image_name = "Capa Gerada IA.jpg"
        except Exception as e:
            st.warning(f"Não foi possível baixar a capa gerada para inclusão no DOCX: {e}. Usando apenas texto.")
            cover_image_bytes = None
    else:
        cover_image_bytes = None

    # Quebra de Seção para isolar a Capa (não numerada)
    if cover_image_bytes:
        # Pág. 1: Capa (toda a página)
        doc.sections[0].header.is_linked_to_previous = True
        doc.sections[0].footer.is_linked_to_previous = True
        
        # Inserir imagem de capa (redimensionada para preencher a página)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Salva o arquivo temporário para inserir a imagem
        img_stream = BytesIO(cover_image_bytes)
        run = p.add_run()
        
        # Cálculo para preencher a página sem distorção (simplesmente forçando a largura)
        run.add_picture(img_stream, width=Inches(size_config['width_in']), height=Inches(size_config['height_in']))
        
        # Quebra de página
        doc.add_page_break()
    else:
        # Pág. 1: Capa (somente texto)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"\n\n\n{title.upper()}\n\n")
        run.font.size = Pt(36)
        run.bold = True
        doc.add_page_break()
    
    # Quebra de Seção 1 (Miolo): Começa a contagem de páginas, mas oculta a numeração na Pág. 2
    # A numeração lógica do livro deve começar aqui, mas a numeração *física* visível deve começar mais tarde.
    
    # Adiciona a quebra de seção (necessária para resetar ou configurar a numeração)
    doc.add_section(WD_SECTION.NEW_PAGE)
    
    # 2. PÁGINA DE TÍTULO (Pág. 2)
    p = doc.add_paragraph(title)
    p.style = 'Title'
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()
    
    # 3. PÁGINA DE DIREITOS AUTORAIS/DEDICATÓRIA (Pág. 3)
    p = doc.add_paragraph("Direitos Autorais - 2025")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    # 4. SUMÁRIO (Pág. 4)
    doc.add_heading("Sumário", level=1)
    
    # Simula as páginas onde o conteúdo real começa (após Capa, Título, Direitos, Sumário)
    # Conteúdo real (Capítulo 1) começará na página 5 (ou 4 no índice lógico da Seção 2)
    current_physical_page = 4 
    
    # TOC Estático - Simulação de Numeração (apenas para fins de alinhamento)
    
    toc_data = []
    # Estima o número de páginas por capítulo (muito simplificado: 4500 caracteres/página)
    CHARS_PER_PAGE = 4500
    
    # Páginas de conteúdo real, começando após o Sumário (Pág. 4)
    content_page_counter = current_physical_page + 1 
    
    for idx, chapter in enumerate(chapters):
        chapter_title = f"Capítulo {chapter['chapter_number']}: {chapter['chapter_title']}"
        # Estima quantas páginas o capítulo ocupará
        pages_estimate = math.ceil(len(chapter['content']) / CHARS_PER_PAGE) if len(chapter['content']) > 0 else 1
        
        toc_data.append({
            'title': chapter_title, 
            'page_num': content_page_counter
        })
        content_page_counter += pages_estimate 
    
    # Cria o TOC estático
    for item in toc_data:
        p = doc.add_paragraph()
        run = p.add_run(item['title'])
        run.font.size = Pt(12)
        
        # Adiciona os pontos de preenchimento e o número de página alinhado à direita
        p.add_run(" " * (120 - len(item['title'])) + str(item['page_num'])) # Alinhamento manual simples
        
        # Adiciona a formatação de hiperlink (opcional, mas bom para TOC)
        # Este é um placeholder, pois docx não suporta âncoras facilmente
        
    doc.add_page_break()
    
    # 5. CONTEÚDO PRINCIPAL E NUMERAÇÃO DE PÁGINAS

    # Quebra de Seção 2: Onde a numeração de páginas deve se tornar visível e iniciar em '1' ou '5' (se for numeração física)
    doc.add_section(WD_SECTION.NEW_PAGE) 
    
    # Configura a Seção 2 (Conteúdo)
    content_section = doc.sections[-1]
    
    # Desliga a ligação com a seção anterior (para que a numeração comece/apareça aqui)
    content_section.header.is_linked_to_previous = False
    content_section.footer.is_linked_to_previous = False
    
    # Cria o rodapé com a numeração (o número físico começa no 5, mas a contagem de Word deve começar aqui)
    # Para o Word, a contagem REAL visível deve começar em 1, mas o documento anterior já conta 4 páginas.
    # O código abaixo define o rodapé e força a numeração a começar a partir de onde o Word está.
    create_page_number_footer(content_section, page_num_start=1)
    
    # Insere os capítulos
    for idx, chapter in enumerate(chapters):
        # Título do Capítulo
        p_title = doc.add_paragraph(f"Capítulo {chapter['chapter_number']}: {chapter['chapter_title']}")
        p_title.style = 'Heading 1'
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Conteúdo
        p_content = doc.add_paragraph(chapter['content'])
        p_content.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        # Quebra de página no final de cada capítulo, exceto o último
        if idx < len(chapters) - 1:
            doc.add_page_break()

    # Salva o documento em um buffer de bytes
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    filename = f"{title.replace(' ', '_')}_Completo.docx"
    return file_stream.read(), filename


# --- INTERFACE STREAMLIT ---

init_state()

st.set_page_config(
    page_title="Editor Literário IA",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("✍️ Editor Literário IA (Projeto Avançado)")
st.caption("Geração de Conteúdo, Arte da Capa e Exportação DOCX com Sumário e Numeração de Página.")

# --- SIDEBAR: CONFIGURAÇÕES E CHAVES ---
with st.sidebar:
    st.header("🔑 Configuração de API")
    
    # 1. Chave OpenAI (Padrão)
    openai_key = st.text_input(
        "Chave OpenAI (GPT/DALL-E)", 
        type="password", 
        value=os.environ.get("OPENAI_API_KEY", "")
    )
    
    # 2. Chave Copilot/Microsoft (Azure/Compatível)
    copilot_key = st.text_input(
        "Chave Copilot/Azure (Opcional)",
        type="password",
        help="Use esta chave para serviços compatíveis com o endpoint da API OpenAI (ex: Azure OpenAI/Copilot Studio). Se fornecida, substituirá a chave OpenAI para as chamadas LLM."
    )
    
    copilot_endpoint = st.text_input(
        "Endpoint Copilot/Azure (Base URL)",
        help="Ex: https://[nome-do-seu-recurso].openai.azure.com/openai/deployments/[seu-modelo]"
    )
    
    api_key_to_use = openai_key
    endpoint_to_use = None
    
    # Lógica de prioridade: Copilot > OpenAI
    if copilot_key and copilot_endpoint:
        api_key_to_use = copilot_key
        endpoint_to_use = copilot_endpoint
        st.info("Usando a Chave Copilot/Azure.")
    elif openai_key:
        api_key_to_use = openai_key
        st.info("Usando a Chave OpenAI.")
    else:
        st.warning("Insira uma chave API para continuar.")
    
    if api_key_to_use:
        # Inicializa o cliente na sessão
        st.session_state['openai_client'] = get_client(api_key_to_use, endpoint_to_use)
    else:
        st.session_state['openai_client'] = None

    st.divider()

    st.header("📚 Detalhes do Livro")
    
    st.session_state['book_title'] = st.text_input("Título do Livro", value=st.session_state['book_title'])
    st.session_state['book_genre'] = st.selectbox("Gênero", options=["Ficção", "Não-Ficção", "Aventura", "Romance", "Suspense"], index=0)
    st.session_state['book_voice'] = st.selectbox("Voz Narrativa", options=GENERATION_VOICES, index=0)
    st.session_state['book_size'] = st.selectbox("Formato de Miolo DOCX (KDP)", options=list(KDP_SIZES.keys()), index=0)
    
    st.divider()
    
    st.header("⬆️ Carregar Checkpoint")
    uploaded_file = st.file_uploader("Carregar Progresso (JSON)", type="json")
    if uploaded_file is not None:
        try:
            # Lendo o JSON e atualizando o estado
            data = json.load(uploaded_file)
            st.session_state['processed_state'] = data.get('chapters', [])
            st.session_state['book_title'] = data.get('title', "Livro Carregado")
            st.session_state['book_genre'] = data.get('genre', "Ficção")
            st.session_state['generated_image_url'] = data.get('cover_url', None)
            st.success(f"Checkpoint de '{st.session_state['book_title']}' carregado com sucesso! ({len(st.session_state['processed_state'])} capítulos)")
        except Exception as e:
            st.error(f"Erro ao ler arquivo JSON: {e}")

# --- CORPO PRINCIPAL ---

# Tabs para Navegação
tab_generate, tab_cover, tab_export = st.tabs(["✍️ Escrever Conteúdo", "🖼️ Capa e Sumário", "💾 Exportar Livro"])

# --- TAB 1: GERAÇÃO DE CONTEÚDO ---
with tab_generate:
    st.subheader(f"Geração de Capítulos ({len(st.session_state['processed_state'])} capítulos salvos)")
    
    last_chapter_content = ""
    if st.session_state['processed_state']:
        last_chapter_content = st.session_state['processed_state'][-1]['content']
        st.info(f"O último capítulo salvo termina com: \n\n{last_chapter_content[-300:]}...")
        
        chapter_number = st.session_state['processed_state'][-1]['chapter_number'] + 1
    else:
        st.info("Nenhum capítulo ainda. Comece a escrever!")
        chapter_number = 1

    prompt_col, title_col = st.columns([3, 1])

    with prompt_col:
        next_chapter_prompt = st.text_area(
            f"Instrução para o Capítulo {chapter_number} (Baseado no final acima):", 
            value=f"Continue a história a partir do ponto em que o último capítulo parou, introduzindo um novo personagem e um conflito inesperado.", 
            height=150
        )
    with title_col:
        next_chapter_title = st.text_input(f"Título (Rascunho) do Cap. {chapter_number}", value=f"O Inesperado")

    if st.button(f"🚀 Gerar Capítulo {chapter_number}", disabled=(not st.session_state['openai_client'])):
        if st.session_state['openai_client']:
            generated_content = generate_text_content(
                prompt=next_chapter_prompt,
                client=st.session_state['openai_client'],
                voice=st.session_state['book_voice'],
                title=st.session_state['book_title'],
                genre=st.session_state['book_genre'],
                previous_chapters=st.session_state['processed_state']
            )
            
            # Adiciona o novo capítulo ao estado
            if "Erro" not in generated_content:
                st.session_state['processed_state'].append({
                    "chapter_number": chapter_number,
                    "chapter_title": next_chapter_title,
                    "content": generated_content,
                    "timestamp": time.time()
                })
                st.success(f"Capítulo {chapter_number} gerado e salvo com sucesso!")
                st.rerun()
            else:
                st.error("Falha na geração do capítulo.")
        else:
            st.error("Cliente API não configurado. Verifique suas chaves na sidebar.")
    
    st.divider()
    
    st.subheader("Conteúdo do Livro")
    
    if st.session_state['processed_state']:
        for idx, chapter in enumerate(st.session_state['processed_state']):
            
            col_content, col_actions = st.columns([4, 1])
            
            with col_content:
                st.markdown(f"**Capítulo {chapter['chapter_number']}: {chapter['chapter_title']}**")
                # Permite edição do conteúdo
                edited_content = st.text_area(
                    "Conteúdo:",
                    value=chapter['content'],
                    key=f"edit_chp_{chapter['chapter_number']}",
                    height=250
                )
                
            with col_actions:
                st.text("") # Espaçamento
                
                # Botão Salvar Edições
                if st.button("📝 Salvar Edição", key=f"save_chp_{chapter['chapter_number']}"):
                    st.session_state['processed_state'][idx]['content'] = edited_content
                    st.success(f"Capítulo {chapter['chapter_number']} editado e salvo.")
                
                # Botão Excluir
                if st.button("🗑️ Excluir", key=f"delete_chp_{chapter['chapter_number']}"):
                    del st.session_state['processed_state'][idx]
                    st.success(f"Capítulo {chapter['chapter_number']} excluído.")
                    st.rerun()
    else:
        st.info("Nenhum conteúdo ainda. Comece a gerar seu primeiro capítulo!")

# --- TAB 2: CAPA E SUMÁRIO ---
with tab_cover:
    col_img_prompt, col_img_settings = st.columns([3, 1])
    
    with col_img_settings:
        st.subheader("1. Geração IA")
        cover_style = st.selectbox("Estilo de Arte", options=COVER_STYLES, index=0)
        
    with col_img_prompt:
        st.text("") # Espaçamento
        cover_prompt = st.text_area(
            "Prompt para DALL-E (descreva a capa em detalhes):",
            value=f"Capa de livro profissional para o livro de {st.session_state['book_genre']} '{st.session_state['book_title']}' no estilo de {cover_style}. Inclua o título de forma elegante. Alta resolução.",
            height=120
        )
        
    if st.button("🎨 Gerar Nova Arte da Capa", disabled=(not st.session_state['openai_client'])):
        if st.session_state['openai_client']:
            new_url = generate_cover_art_url(cover_prompt, st.session_state['openai_client'])
            if new_url:
                st.session_state['generated_image_url'] = new_url
                st.session_state['custom_cover_image_bytes'] = None # Limpa a capa externa
                st.success("Capa gerada com sucesso!")
            else:
                st.error("Falha na geração da capa.")
        else:
            st.error("Cliente API não configurado.")

    st.subheader("2. Carregar Capa Externa")
    
    uploaded_cover = st.file_uploader("Upload de Imagem de Capa (JPG/PNG)", type=["jpg", "jpeg", "png"])
    if uploaded_cover:
        # Armazena os bytes da imagem externa no estado
        st.session_state['custom_cover_image_bytes'] = uploaded_cover.read()
        st.session_state['generated_image_url'] = None # Limpa a capa gerada
        st.success("Capa externa carregada com sucesso!")

    st.divider()

    col_view, col_summary = st.columns([1, 1])
    
    with col_view:
        st.subheader("Capa Atual")
        # Visualização da Capa
        if st.session_state['custom_cover_image_bytes']:
            st.image(st.session_state['custom_cover_image_bytes'], caption="Capa Externa Carregada", use_column_width=True)
            current_cover_url = None
        elif st.session_state['generated_image_url']:
            st.image(st.session_state['generated_image_url'], caption="Capa Gerada pela IA", use_column_width=True)
            current_cover_url = st.session_state['generated_image_url']
        else:
            st.warning("Nenhuma capa definida.")
            current_cover_url = None
            
        # Download da capa gerada (consertado: usa a URL salva para download)
        if current_cover_url and not st.session_state['custom_cover_image_bytes']:
             try:
                # Tenta baixar os bytes diretamente da URL
                image_response = requests.get(current_cover_url, timeout=10)
                image_response.raise_for_status()
                image_bytes = BytesIO(image_response.content).read()
                
                st.download_button(
                    label="⬇️ Baixar Arte da Capa Gerada",
                    data=image_bytes,
                    file_name=f"{st.session_state['book_title']}_Capa_Completa.jpg",
                    mime="image/jpeg" 
                )
             except Exception:
                st.warning("Capa gerada, mas houve erro no download. Tente novamente.")
        elif st.session_state['custom_cover_image_bytes']:
            st.download_button(
                label="⬇️ Baixar Capa Externa",
                data=st.session_state['custom_cover_image_bytes'],
                file_name=f"{st.session_state['book_title']}_Capa_Externa.jpg",
                mime="image/jpeg" # Assumindo JPG/PNG
            )
            
    with col_summary:
        st.subheader("3. Sumário e Sinopse")
        
        if st.button("📝 Gerar Sumário e Sinopse", disabled=(not st.session_state['openai_client'] or not st.session_state['processed_state'])):
            summary_content = generate_book_summary(
                client=st.session_state['openai_client'],
                title=st.session_state['book_title'],
                genre=st.session_state['book_genre'],
                chapters=st.session_state['processed_state']
            )
            st.session_state['summary_output'] = summary_content
            
        if 'summary_output' in st.session_state:
            st.markdown(st.session_state['summary_output'])
        else:
            st.info("Gere o sumário para ver a sinopse e títulos de capítulos aqui.")


# --- TAB 3: EXPORTAÇÃO ---
with tab_export:
    st.subheader("Exportação Final do Livro")
    
    col_dl1, col_dl2 = st.columns([1, 1])

    with col_dl1:
        # Exportar DOCX com numeração e sumário alinhados
        if st.session_state['processed_state']:
            try:
                docx_bytes, docx_filename = export_docx(
                    chapters=st.session_state['processed_state'], 
                    title=st.session_state['book_title'],
                    size_key=st.session_state['book_size'],
                    custom_cover_bytes=st.session_state['custom_cover_image_bytes'],
                    generated_image_url=st.session_state['generated_image_url']
                )
                
                st.success("Documento pronto para download.")
                st.download_button(
                    label=f"⬇️ Baixar Livro Completo ({st.session_state['book_size']})",
                    data=docx_bytes,
                    file_name=docx_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                st.caption("O arquivo DOCX contém a capa, sumário (TOC) e numeração de página automática no rodapé, começando na primeira página de conteúdo real.")
            except Exception as e:
                st.error(f"Erro ao preparar o DOCX: {e}. Certifique-se de ter pelo menos 1 capítulo.")
        else:
            st.warning("Adicione capítulos antes de exportar o DOCX.")
            
    with col_dl2:
        # --- LÓGICA DE DOWNLOAD MANUAL DO CHECKPOINT (Sempre disponível) ---
        
        # Cria um objeto completo do estado atual para salvar (preserva o progresso)
        state_to_save = {
            "title": st.session_state['book_title'],
            "genre": st.session_state['book_genre'],
            "size": st.session_state['book_size'],
            "cover_url": st.session_state['generated_image_url'],
            "chapters": st.session_state['processed_state']
        }
        
        processed_json = json.dumps(state_to_save, indent=4, ensure_ascii=False)
        processed_bytes = processed_json.encode('utf-8')
        
        st.download_button(
            label="💾 Baixar Checkpoint (JSON) Manual",
            data=processed_bytes,
            file_name=f"{st.session_state['book_title']}_CHECKPOINT_MANUAL.json",
            mime="application/json",
            help=f"Baixe este arquivo para salvar o progresso de {len(st.session_state['processed_state'])} capítulos."
        )

# Garante que o estado seja salvo no final
st.session_state['processed_state'] = st.session_state['processed_state']
