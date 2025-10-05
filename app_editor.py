import os
import streamlit as st
from openai import OpenAI
from docx import Document
from io import BytesIO
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import requests 
import time 
from typing import Optional, Dict, Tuple, Any, List
import math 
import json 

# --- CONFIGURAÇÃO DE CONSTANTES GERAIS ---

KDP_SIZES: Dict[str, Dict] = {
    "Padrão EUA (6x9 in)": {"name": "6 x 9 in", "width_in": 6.0, "height_in": 9.0, "width_cm": 15.24, "height_cm": 22.86}, 
    "Padrão A5 (5.83x8.27 in)": {"name": "A5 (14.8 x 21 cm)", "width_in": 5.83, "height_in": 8.27, "width_cm": 14.8, "height_cm": 21.0},
    "Pocket (5x8 in)": {"name": "5 x 8 in", "width_in": 5.0, "height_in": 8.0, "width_cm": 12.7, "height_cm": 20.32},
}

# Configurações de Formatação (Simulação ABNT/KDP)
FONT_NAME = 'Arial'
BODY_FONT_SIZE = Pt(12)
TITLE_FONT_SIZE = Pt(14)
LINE_SPACING = 1.5
MARGIN_INNER = Inches(1.25) # 3.0 cm for inner margin (gutter)
MARGIN_OUTER = Inches(0.8) # 2.0 cm for outer margin
MARGIN_TOP = Inches(1.25) # 3.0 cm for top margin
MARGIN_BOTTOM = Inches(0.8) # 2.0 cm for bottom margin

# --- INICIALIZAÇÃO E ESTADO DA SESSÃO ---

def init_state():
    """Inicializa as variáveis de estado de sessão."""
    if 'processed_state' not in st.session_state:
        # Estrutura principal para armazenar capítulos: {'chapters': [{'title': '...', 'content': '...'}]}
        st.session_state['processed_state'] = {'chapters': []}
    if 'book_title' not in st.session_state:
        st.session_state['book_title'] = "Título Provisório do Livro"
    if 'book_author' not in st.session_state:
        st.session_state['book_author'] = "Nome do Autor"
    if 'book_genre' not in st.session_state:
        st.session_state['book_genre'] = "Ficção"
    if 'book_size' not in st.session_state:
        st.session_state['book_size'] = "Padrão EUA (6x9 in)"
    if 'openai_client' not in st.session_state:
        st.session_state['openai_client'] = None
    if 'generated_image_url' not in st.session_state:
        st.session_state['generated_image_url'] = None
    if 'document_bytes' not in st.session_state:
        st.session_state['document_bytes'] = None
    if 'dedication_text' not in st.session_state:
        st.session_state['dedication_text'] = "Para todos os leitores..."
    if 'glossary_entries' not in st.session_state:
        st.session_state['glossary_entries'] = [{'term': '', 'definition': ''}]
    if 'about_author_text' not in st.session_state:
        st.session_state['about_author_text'] = "O autor é um entusiasta de..."

# Inicializa o estado
init_state()

# --- FUNÇÕES DE CONEXÃO E LLM (MANTIDAS A PEDIDO) ---

def get_client(api_key: str) -> Optional[OpenAI]:
    """Cria e retorna uma instância do cliente OpenAI."""
    if not api_key:
        return None
    try:
        client = OpenAI(api_key=api_key)
        # Tentativa leve para validar
        client.models.list() 
        return client
    except Exception:
        return None

def generate_text_content(prompt: str, client: OpenAI, title: str, genre: str, previous_chapters: List[Dict[str, Any]] = None) -> str:
    """Gera o conteúdo de um novo capítulo."""
    if not client:
        return "Erro: Cliente API não inicializado."
    
    messages = [{"role": "system", "content": f"Você é um autor de best-sellers de {genre}. Escreva o próximo capítulo do livro '{title}'. O capítulo deve ter cerca de 1000 palavras."}]
    if previous_chapters:
        for chapter in previous_chapters[-2:]: # Últimos 2 capítulos para contexto
            messages.append({"role": "assistant", "content": f"Capítulo {chapter['title']}:\n{chapter['content'][:500]}..."}) 
    
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=4000,
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na geração de texto: {e}"

# --- FUNÇÃO DE PROCESSAMENTO DE MANUSCRITO ENVIADO (NOVA) ---

def process_uploaded_manuscript(uploaded_file, client: Optional[OpenAI]):
    """Lê um arquivo DOCX ou TXT e tenta dividir em capítulos."""
    
    file_type = uploaded_file.name.split('.')[-1].lower()
    content_raw = ""
    new_chapters = []

    if file_type == 'txt':
        # Leitura simples de TXT
        content_raw = uploaded_file.read().decode('utf-8')
        # Tenta dividir por quebras de linha duplas para obter capítulos
        potential_chapters = content_raw.split('\n\n\n')
        
        for i, block in enumerate(potential_chapters):
            block = block.strip()
            if block:
                # Usa a primeira linha como título e o resto como conteúdo
                lines = block.split('\n')
                title = lines[0].strip() if lines else f"Capítulo {i+1}"
                content = "\n".join(lines[1:]).strip() if len(lines) > 1 else title
                
                # Se o bloco for muito pequeno, assume que é um subtítulo ou continuação
                if len(title.split()) > 20 and len(content) < 50:
                     title = f"Capítulo {i+1}"
                     content = block
                     
                new_chapters.append({'title': title, 'content': content})
        
        if not new_chapters:
             # Se a divisão falhar, trata como um único grande capítulo
             new_chapters = [{'title': st.session_state['book_title'] + " (Manuscrito Completo)", 'content': content_raw}]


    elif file_type == 'docx':
        # Leitura de DOCX, procurando por Heading 1 para títulos
        document = Document(uploaded_file)
        current_content = []
        current_title = f"Capítulo 1"

        for paragraph in document.paragraphs:
            if paragraph.style.name.startswith('Heading 1') or paragraph.style.name.startswith('Heading 2'):
                if current_content:
                    new_chapters.append({'title': current_title, 'content': "\n".join(current_content)})
                    current_content = []
                current_title = paragraph.text.strip()
            elif paragraph.text.strip():
                current_content.append(paragraph.text)

        # Adiciona o último capítulo
        if current_content:
            new_chapters.append({'title': current_title, 'content': "\n".join(current_content)})
        
        if not new_chapters:
             # Se a divisão falhar, trata como um único grande capítulo
             full_text = "\n".join([p.text for p in document.paragraphs if p.text.strip()])
             new_chapters = [{'title': st.session_state['book_title'] + " (Manuscrito Completo)", 'content': full_text}]
             
    else:
        st.error(f"Tipo de arquivo não suportado: .{file_type}")
        return

    if new_chapters:
        st.session_state['processed_state']['chapters'] = new_chapters
        st.success(f"Manuscrito carregado e dividido em {len(new_chapters)} seções/capítulos para edição.")

# --- FUNÇÕES DOCX (FORMATO E ESTRUTURA) ---

def apply_abnt_style(doc: Document):
    """Aplica o estilo de corpo de texto e formata as margens ABNT/KDP."""
    
    size_config = KDP_SIZES[st.session_state['book_size']]
    section = doc.sections[0]
    section.page_width = Inches(size_config['width_in'])
    section.page_height = Inches(size_config['height_in'])
    section.left_margin = MARGIN_INNER
    section.right_margin = MARGIN_OUTER
    section.top_margin = MARGIN_TOP
    section.bottom_margin = MARGIN_BOTTOM

    # Estilo Normal
    style = doc.styles['Normal']
    font = style.font
    font.name = FONT_NAME
    font.size = BODY_FONT_SIZE
    paragraph_format = style.paragraph_format
    paragraph_format.line_spacing = LINE_SPACING
    paragraph_format.space_after = Pt(0)
    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Estilo Título de Capítulo (Heading 1)
    try:
        title_style = doc.styles['Heading 1']
    except KeyError:
        title_style = doc.styles.add_style('Heading 1', WD_STYLE_TYPE.PARAGRAPH)
        
    title_style.font.name = FONT_NAME
    title_style.font.size = TITLE_FONT_SIZE
    title_style.font.bold = True
    title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_style.paragraph_format.space_before = Pt(36)
    title_style.paragraph_format.space_after = Pt(24)

def add_table_of_contents(doc: Document):
    """Adiciona um campo de Sumário (TOC) no documento."""
    doc.add_page_break()
    p = doc.add_paragraph('SUMÁRIO', style='Heading 1')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Adiciona o campo TOC
    p = doc.add_paragraph()
    run = p.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    run._element.append(fldChar)
    
    run = doc.add_paragraph().add_run()
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = r'TOC \o "1-1" \h \z \t "Heading 1,1"' 
    run._element.append(instrText)

    run = doc.add_paragraph().add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'end')
    run._element.append(fldChar)
    
    doc.add_page_break()

def add_cover(doc: Document, title: str, author: str, cover_image_url: Optional[str]):
    """Cria a capa simples com imagem, título e autor."""
    
    doc.add_page_break()
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Inches(2)
    run_title = p_title.add_run(title.upper())
    run_title.font.size = Pt(28)
    run_title.font.bold = True
    run_title.font.name = FONT_NAME
    
    if cover_image_url:
        try:
            response = requests.get(cover_image_url, stream=True)
            response.raise_for_status()
            image_stream = BytesIO(response.content)
            size_config = KDP_SIZES[st.session_state['book_size']]
            max_width_in = size_config['width_in'] * 0.7 
            
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Inches(0.5)
            doc.add_picture(image_stream, width=Inches(max_width_in))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

        except Exception:
            p_img = doc.add_paragraph("--- Arte da Capa Não Carregada ---")
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Inches(1.5)

    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author.paragraph_format.space_before = Inches(2)
    run_author = p_author.add_run(author)
    run_author.font.size = Pt(18)
    run_author.font.name = FONT_NAME
    
    doc.add_page_break()
    
def add_page_numbers(doc: Document):
    """Adiciona numeração de página no rodapé."""
    
    # Adiciona o campo de número de página em todas as seções
    for section in doc.sections:
        footer = section.footer
        
        # Limpa conteúdo existente no rodapé
        for p in list(footer.paragraphs):
            footer._element.remove(p._element)

        # Adiciona novo parágrafo para o número da página
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # Campo para o número da página (PAGE)
        run = p.add_run()
        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'begin')
        run._element.append(fldChar)

        instrText = OxmlElement('w:instrText')
        instrText.text = 'PAGE' 
        run._element.append(instrText)

        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'end')
        run._element.append(fldChar)
        
        # Define a fonte e tamanho
        for r in p.runs:
            r.font.name = FONT_NAME
            r.font.size = Pt(10)

def create_and_process_document(
    processed_state: Dict, 
    book_title: str, 
    book_author: str, 
    dedication_text: str, 
    glossary_entries: List[Dict], 
    about_author_text: str
) -> Tuple[bytes, int]:
    """Cria, formata e retorna o documento DOCX completo."""
    
    if not processed_state.get('chapters'):
        raise ValueError("O documento não contém capítulos para processamento.")
        
    doc = Document()
    
    # 1. Configurações de estilo e margem
    apply_abnt_style(doc)
    
    # 2. Elementos Pré-textuais (Capa, Folha de Rosto, Dedicatória)
    add_cover(doc, book_title, book_author, st.session_state['generated_image_url'])
    
    # Folha de Rosto
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Inches(3)
    run_title = p_title.add_run(book_title)
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    doc.add_page_break()

    # Dedicatória
    if dedication_text and dedication_text.strip():
        doc.add_paragraph('DEDICATÓRIA', style='Heading 1').alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_dedication = doc.add_paragraph(dedication_text)
        p_dedication.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_page_break()
    
    # 3. Sumário
    add_table_of_contents(doc)
    
    # 4. Conteúdo do Livro
    for chapter in processed_state['chapters']:
        p_title = doc.add_paragraph(chapter['title'].upper(), style='Heading 1')
        for paragraph_text in chapter['content'].split('\n'):
            if paragraph_text.strip():
                # Adiciona o parágrafo com a primeira linha recuada, como padrão de livro
                p = doc.add_paragraph(paragraph_text.strip())
                p.paragraph_format.first_line_indent = Inches(0.5) 
        
        if chapter != processed_state['chapters'][-1]:
            doc.add_page_break()
    
    # 5. Elementos Pós-textuais (Glossário, Sobre o Autor)
    glossary_present = glossary_entries and any(g.get('term') and g.get('definition') for g in glossary_entries)
    if glossary_present:
        doc.add_page_break()
        doc.add_paragraph('GLOSSÁRIO', style='Heading 1')
        for entry in glossary_entries:
            if entry.get('term') and entry.get('definition'):
                p = doc.add_paragraph()
                p.add_run(f"{entry['term'].upper()}: ").bold = True
                p.add_run(entry['definition'])
        
    if about_author_text and about_author_text.strip():
        doc.add_page_break()
        doc.add_paragraph('SOBRE O AUTOR', style='Heading 1')
        doc.add_paragraph(about_author_text)
        
    # 6. Numeração de Páginas (adiciona o campo)
    add_page_numbers(doc)
    
    # 7. Salva o documento
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    # A contagem de páginas no python-docx é complexa, retorna 0 e confia que o Word fará o cálculo.
    return file_stream.read(), 0 


# --- INTERFACE STREAMLIT PRINCIPAL ---

st.set_page_config(layout="wide", page_title="Assistente de Publicação")

st.title("📚 Assistente de Formatação e Publicação")
st.caption("Ferramenta para carregar, editar, formatar e gerar o DOCX final para KDP/Gráfica.")

# --- SIDEBAR: CONFIGURAÇÕES, METADADOS E CHAVES ---

with st.sidebar:
    st.header("🔑 Configuração de API")
    openai_key = st.text_input("Chave OpenAI (GPT/DALL-E)", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
    
    # Inicializa o cliente na sessão
    st.session_state['openai_client'] = get_client(openai_key)
    
    if st.session_state['openai_client']:
        st.success("API Key OK. Funções de IA ativas.")
    else:
        st.warning("Insira sua chave OpenAI para habilitar a geração de texto.")

    st.divider()

    st.header("1. Metadados do Livro")
    st.session_state['book_title'] = st.text_input("Título do Livro", st.session_state['book_title'])
    st.session_state['book_author'] = st.text_input("Nome do Autor", st.session_state['book_author'])
    st.session_state['book_genre'] = st.selectbox("Gênero", options=["Ficção", "Não-Ficção", "Aventura", "Romance", "Suspense"], index=0)
    st.session_state['book_size'] = st.selectbox("Tamanho do Miolo (KDP/Gráfica)", 
                                                 list(KDP_SIZES.keys()), 
                                                 index=list(KDP_SIZES.keys()).index(st.session_state['book_size']))
    
    st.divider()
    
    st.header("2. Carregar/Salvar Progresso")
    uploaded_checkpoint = st.file_uploader("Carregar Progresso (JSON)", type="json")
    if uploaded_checkpoint is not None:
        try:
            data = json.load(uploaded_checkpoint)
            st.session_state['processed_state'] = data.get('processed_state', {'chapters': []})
            st.session_state['book_title'] = data.get('book_title', st.session_state['book_title'])
            st.session_state['book_author'] = data.get('book_author', st.session_state['book_author'])
            st.session_state['book_genre'] = data.get('book_genre', st.session_state['book_genre'])
            st.session_state['generated_image_url'] = data.get('generated_image_url', None)
            st.session_state['document_bytes'] = None
            st.success(f"Checkpoint carregado com sucesso! ({len(st.session_state['processed_state'].get('chapters', []))} capítulos)")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao ler arquivo JSON: {e}")
            
    # Download do Checkpoint
    processed_json_data = {
        'processed_state': st.session_state['processed_state'],
        'book_title': st.session_state['book_title'],
        'book_author': st.session_state['book_author'],
        'book_genre': st.session_state['book_genre'],
        'book_size': st.session_state['book_size'],
        'generated_image_url': st.session_state['generated_image_url'],
    }
    processed_json = json.dumps(processed_json_data, indent=4, ensure_ascii=False)
    processed_bytes = processed_json.encode('utf-8')
    st.download_button(
        label="💾 Baixar Checkpoint (JSON)",
        data=processed_bytes,
        file_name=f"{st.session_state['book_title']}_CHECKPOINT.json",
        mime="application/json",
        help=f"Salva o progresso de {len(st.session_state['processed_state'].get('chapters', []))} capítulos."
    )


# --- ABAS PRINCIPAIS ---

tab_content, tab_elements, tab_download = st.tabs(["1. Escrever e Carregar Conteúdo", "2. Elementos de Publicação", "3. Geração Final (Download)"])

# --- TAB 1: CONTEÚDO ---
with tab_content:
    
    # ----------------------------------------------------
    st.subheader("Opção A: Carregar Manuscrito Pronto")
    uploaded_manuscript = st.file_uploader(
        "Selecione seu manuscrito (DOCX ou TXT)", 
        type=['docx', 'txt'], 
        help="O sistema tentará dividir o arquivo em capítulos (seções) para edição."
    )
    if uploaded_manuscript:
        if st.button("▶️ Processar Manuscrito Carregado"):
            process_uploaded_manuscript(uploaded_manuscript, st.session_state['openai_client'])
    
    st.markdown("---")
    
    # ----------------------------------------------------
    st.subheader("Opção B: Escrever/Continuar com IA")
    
    current_chapters = st.session_state['processed_state'].get('chapters', [])
    last_chapter_content = current_chapters[-1]['content'] if current_chapters else ""
    chapter_number = len(current_chapters) + 1

    st.info(f"O manuscrito atual possui {len(current_chapters)} capítulos. Você está no Capítulo {chapter_number}.")
    if last_chapter_content:
         st.markdown(f"**Final do último capítulo:** *...{last_chapter_content[-200:]}*")

    col_prompt, col_title = st.columns([3, 1])

    with col_prompt:
        next_chapter_prompt = st.text_area(
            f"Instrução para o Capítulo {chapter_number}:", 
            value=f"Continue a história, introduzindo um novo conflito principal e revelando o passado secreto do personagem.", 
            height=100
        )
    with col_title:
        next_chapter_title = st.text_input(f"Título do Cap. {chapter_number}", value=f"O Inesperado")

    if st.button(f"🤖 Gerar Capítulo {chapter_number} com IA", disabled=(not st.session_state['openai_client'])):
        if st.session_state['openai_client']:
            generated_content = generate_text_content(
                prompt=next_chapter_prompt,
                client=st.session_state['openai_client'],
                title=st.session_state['book_title'],
                genre=st.session_state['book_genre'],
                previous_chapters=current_chapters
            )
            
            if "Erro" not in generated_content:
                st.session_state['processed_state']['chapters'].append({
                    "title": next_chapter_title,
                    "content": generated_content,
                })
                st.success(f"Capítulo {chapter_number} gerado e salvo.")
                st.rerun()
            else:
                st.error("Falha na geração do capítulo.")
        else:
            st.error("Cliente API não configurado.")
            
    st.markdown("---")
    st.subheader("Edição do Manuscrito")
    
    if current_chapters:
        new_chapters = []
        for i, chapter in enumerate(current_chapters):
            with st.expander(f"Capítulo {i+1}: {chapter['title']}"):
                col_e_t, col_e_d = st.columns([3, 1])
                new_title = col_e_t.text_input(f"Título do Capítulo {i+1}", chapter['title'], key=f"ch_title_{i}")
                
                if col_e_d.button("🗑️ Excluir", key=f"del_chp_{i}"):
                    st.session_state['processed_state']['chapters'].pop(i)
                    st.success(f"Capítulo {i+1} excluído.")
                    st.rerun()
                    
                new_content = st.text_area(f"Conteúdo do Capítulo {i+1}", chapter['content'], height=300, key=f"ch_content_{i}")
                new_chapters.append({'title': new_title, 'content': new_content})
                
        st.session_state['processed_state']['chapters'] = new_chapters
        if st.button("📝 Salvar Edições Manuais"):
             st.success("Todas as edições manuais foram salvas no estado de progresso.")
             st.rerun()
    else:
        st.info("Nenhum conteúdo ainda. Carregue seu manuscrito ou escreva com a IA para começar a editar.")


# --- TAB 2: ELEMENTOS DE PUBLICAÇÃO ---
with tab_elements:
    col_img_settings, col_elements = st.columns(2)
    
    with col_img_settings:
        st.subheader("2.1 Capa do Livro (Imagem)")
        
        cover_url = st.text_input("URL da Imagem de Capa (Opcional)", st.session_state['generated_image_url'] if st.session_state['generated_image_url'] else "")
        if cover_url:
            st.session_state['generated_image_url'] = cover_url
            st.image(cover_url, caption="Prévia da Capa", use_column_width=True)
        else:
            st.session_state['generated_image_url'] = None
            st.warning("Insira uma URL de imagem de alta resolução para a capa.")
            
        # Simulação para DALL-E (apenas para quem usa a chave)
        if st.session_state['openai_client']:
            cover_prompt = st.text_area("Prompt para Geração de Capa (DALL-E)", 
                                        value=f"Capa de livro profissional para {st.session_state['book_title']} no gênero {st.session_state['book_genre']}.", height=100)
            if st.button("🎨 Gerar Capa com IA (DALL-E)", key='generate_cover'):
                # (A geração DALL-E real é omitida aqui para simplicidade, mas o prompt está pronto)
                # Neste ambiente, simulo:
                st.session_state['generated_image_url'] = f"https://placehold.co/600x900/4F46E5/FFFFFF/png?text={st.session_state['book_title'].replace(' ', '+')}"
                st.success("Simulação de URL de Capa gerada!")
                st.rerun()

    with col_elements:
        st.subheader("2.2 Elementos Pré e Pós-textuais")
        
        st.markdown("**Dedicatória**")
        st.session_state['dedication_text'] = st.text_area("Texto da Dedicatória", st.session_state['dedication_text'], height=100)
        
        st.markdown("**Sobre o Autor**")
        st.session_state['about_author_text'] = st.text_area("Biografia do Autor", st.session_state['about_author_text'], height=150)

        # Edição de Glossário
        st.markdown("**Glossário** (Termo: Definição)")
        if 'glossary_entries' not in st.session_state or not st.session_state['glossary_entries'] or len(st.session_state['glossary_entries']) == 0:
            st.session_state['glossary_entries'] = [{'term': '', 'definition': ''}]
            
        new_glossary = []
        for i in range(min(len(st.session_state['glossary_entries']), 5)): # Limita a 5 na pré-visualização
            entry = st.session_state['glossary_entries'][i]
            col_t, col_d = st.columns([1, 2])
            term = col_t.text_input(f"Termo {i+1}", entry['term'], key=f"term_final_{i}")
            definition = col_d.text_input(f"Definição {i+1}", entry['definition'], key=f"def_final_{i}")
            new_glossary.append({'term': term, 'definition': definition})
            
        st.session_state['glossary_entries'] = new_glossary
        
        if st.button("Adicionar Termo ao Glossário", key='add_term'):
            st.session_state['glossary_entries'].append({'term': '', 'definition': ''})
            st.experimental_rerun()


# --- TAB 3: GERAÇÃO FINAL (DOWNLOAD) ---
with tab_download:
    st.header("3. Geração e Download do DOCX Final")
    
    if not st.session_state['processed_state'].get('chapters'):
        st.error("Não há capítulos carregados. Por favor, carregue seu manuscrito ou escreva conteúdo na Aba 1.")
    else:
        st.success(f"Pronto para formatar e gerar o DOCX com {len(st.session_state['processed_state']['chapters'])} capítulos.")
        
        if st.button("🚀 Gerar e Baixar Documento Final (DOCX)", type="primary"):
            try:
                with st.spinner("Gerando e formatando o documento (capa, sumário, numeração, ABNT)..."):
                    document_bytes, total_pages = create_and_process_document(
                        processed_state=st.session_state['processed_state'],
                        book_title=st.session_state['book_title'],
                        book_author=st.session_state['book_author'],
                        dedication_text=st.session_state['dedication_text'],
                        glossary_entries=st.session_state['glossary_entries'],
                        about_author_text=st.session_state['about_author_text'],
                    )
                    st.session_state['document_bytes'] = document_bytes
                    st.success("Documento formatado e pronto!")
                    st.rerun()
            except ValueError as ve:
                 st.error(f"Erro de Conteúdo: {ve}")
            except Exception as e:
                st.error(f"Erro ao gerar o documento final: {e}")

    # Botão de download (só aparece se o documento foi gerado)
    if st.session_state['document_bytes']:
        st.divider()
        st.download_button(
            label="⬇️ Baixar Arquivo DOCX Final Formatado",
            data=st.session_state['document_bytes'],
            file_name=f"{st.session_state['book_title']}_PUBLICACAO_FINAL.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        st.info("""
        **Instruções Importantes:**
        1.  O arquivo está formatado para **Miolo de Livro** (margens e fonte Arial/Georgia 12, espaçamento 1,5).
        2.  **Atualização do Sumário:** Abra o DOCX no Word, clique com o botão direito no texto 'SUMÁRIO' e selecione **'Atualizar Campo...'** > **'Atualizar o índice inteiro'** para gerar a numeração de páginas correta.
        3.  A **numeração de página** é inserida no rodapé.
        """)
