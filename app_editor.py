import os
import streamlit as st
from docx import Document
from io import BytesIO
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import requests 
import time 
from typing import Optional, Dict, Tuple, Any, List
import math 
import json 
from docx.oxml.ns import qn # Para manipulação de XML de estilo (Ex: fontes)

# --- CONFIGURAÇÃO DE CONSTANTES GLOBAIS ---

# 1. DICIONÁRIO DE TAMANHOS KDP/GRÁFICA (Miolo)
# width_in, height_in: para diagramação DOCX
KDP_SIZES: Dict[str, Dict] = {
    "Padrão EUA (6x9 in)": {"name": "6 x 9 in", "width_in": 6.0, "height_in": 9.0, "papel_fator": 0.00115}, 
    "Padrão A5 (5.83x8.27 in)": {"name": "A5 (14.8 x 21 cm)", "width_in": 5.83, "height_in": 8.27, "papel_fator": 0.00115},
    "Pocket (5x8 in)": {"name": "5 x 8 in", "width_in": 5.0, "height_in": 8.0, "papel_fator": 0.00115},
    "A4 (8.27x11.69 in)": {"name": "A4 (21 x 29.7 cm)", "width_in": 8.27, "height_in": 11.69, "papel_fator": 0.00115},
}

# 2. DICIONÁRIO DE DENSIDADE DE PAPEL (Para cálculo de lombada)
# Os valores são milímetros por página (mm/page). Ex: 0.00115mm/page
# Estes são fatores cruciais para o cálculo preciso da lombada em gráficas
PAPER_DENSITIES_MM_PER_PAGE: Dict[str, float] = {
    "Pólen Soft (75g/m²)": 0.115,  # 0.115mm/folha = 0.00115mm/page (KDP padrão para Cream Paper)
    "Offset Branco (90g/m²)": 0.10,
    "Couché Fosco (120g/m²)": 0.08, 
}

# 3. TEMPLATES DE ESTILO (Para diagramação)
STYLE_TEMPLATES: Dict[str, Tuple[str, str]] = {
    "Romance Clássico (Garamond)": ("Garamond", "JUSTIFY"),
    "Thriller Moderno (Droid Serif)": ("Droid Serif", "LEFT"),
    "Acadêmico (Times New Roman)": ("Times New Roman", "JUSTIFY"),
}

# 4. MAPEAMENTO DE TÍTULOS DO PROCESSO (8 Passos)
STEP_TITLES: Dict[int, str] = {
    1: "1. Configuração Inicial e Formato do Livro",
    2: "2. Upload do Manuscrito",
    3: "3. Iniciar PRÉ-IMPRESSÃO COMPLETA (Revisão P.P.)",
    4: "4. Relatório Estrutural (Editor-Chefe)",
    5: "5. Relatório de Estilo (Vícios/Clichês)",
    6: "6. Conteúdo de Capa/Contracapa (Marketing)",
    7: "7. Criação de Capa com IA (DALL-E 3)",
    8: "8. Resumo Técnico Final e Downloads",
}

# Configuração de API (O Streamlit/Canvas injeta a chave automaticamente no fetch)
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"
IMAGEN_MODEL = "imagen-3.0-generate-002"
API_KEY = "" # Mantido vazio para injeção automática

# --- INICIALIZAÇÃO E GESTÃO DE ESTADO (SESSION STATE) ---

def initialize_session_state():
    """Inicializa todos os estados necessários para o fluxo completo."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.progress_step = 1
        st.session_state.current_docx_name = None
        
        # Dados de Configuração
        st.session_state.book_title = "Título Não Definido"
        st.session_state.author_name = "Autor Desconhecido"
        st.session_state.trim_size_name = list(KDP_SIZES.keys())[0]
        st.session_state.paper_density_name = list(PAPER_DENSITIES_MM_PER_PAGE.keys())[0]
        st.session_state.style_template_name = list(STYLE_TEMPLATES.keys())[0]
        st.session_state.page_count_estimate = 250
        
        # Dados do Manuscrito
        st.session_state.manuscrito_original: List[Dict] = []
        st.session_state.manuscrito_revisado: List[Dict] = []
        st.session_state.paragrafos_revisados_indices: set = set()
        st.session_state.total_paragrafos_processar = 0
        st.session_state.processed_state: Dict[str, Any] = {} # Armazena todos os resultados
        
        # Resultados de IA/Cálculos
        st.session_state.report_estrutural: Optional[str] = None
        st.session_state.report_estilo: Optional[str] = None
        st.session_state.report_capa_blurb: Optional[str] = None
        st.session_state.report_capa_prompt: Optional[str] = None
        st.session_state.spine_thickness_mm: Optional[float] = None
        st.session_state.generated_image_url: Optional[str] = None
        
        # Checkpoints
        st.session_state.checkpoints_fired: set = set() # Registra quais % já dispararam o checkpoint

initialize_session_state()

def update_processed_state():
    """Atualiza o dicionário de estado para salvamento em JSON."""
    st.session_state.processed_state = {
        "book_title": st.session_state.book_title,
        "author_name": st.session_state.author_name,
        "config": {
            "trim_size": st.session_state.trim_size_name,
            "paper_density": st.session_state.paper_density_name,
            "style_template": st.session_state.style_template_name,
            "page_count_estimate": st.session_state.page_count_estimate,
        },
        "manuscrito_original": st.session_state.manuscrito_original,
        "manuscrito_revisado": st.session_state.manuscrito_revisado,
        "paragrafos_revisados_indices": list(st.session_state.paragrafos_revisados_indices),
        "total_paragrafos_processar": st.session_state.total_paragrafos_processar,
        "progress_step": st.session_state.progress_step,
        "checkpoints_fired": list(st.session_state.checkpoints_fired),
        "reports": {
            "estrutural": st.session_state.report_estrutural,
            "estilo": st.session_state.report_estilo,
            "blurb": st.session_state.report_capa_blurb,
            "prompt_capa": st.session_state.report_capa_prompt,
            "spine_thickness_mm": st.session_state.spine_thickness_mm,
            "cover_image_url": st.session_state.generated_image_url,
        },
        "timestamp": time.time(),
    }
    
def carregar_checkpoint(uploaded_file):
    """Carrega o estado do processamento a partir de um arquivo JSON."""
    try:
        data = json.load(uploaded_file)
        
        # Carrega a configuração
        st.session_state.book_title = data.get("book_title", st.session_state.book_title)
        st.session_state.author_name = data.get("author_name", st.session_state.author_name)
        config = data.get("config", {})
        st.session_state.trim_size_name = config.get("trim_size", st.session_state.trim_size_name)
        st.session_state.paper_density_name = config.get("paper_density", st.session_state.paper_density_name)
        st.session_state.style_template_name = config.get("style_template", st.session_state.style_template_name)
        st.session_state.page_count_estimate = config.get("page_count_estimate", st.session_state.page_count_estimate)
        
        # Carrega o estado de processamento
        st.session_state.manuscrito_original = data.get("manuscrito_original", [])
        st.session_state.manuscrito_revisado = data.get("manuscrito_revisado", [])
        st.session_state.paragrafos_revisados_indices = set(data.get("paragrafos_revisados_indices", []))
        st.session_state.total_paragrafos_processar = data.get("total_paragrafos_processar", 0)
        st.session_state.progress_step = data.get("progress_step", 1)
        st.session_state.checkpoints_fired = set(data.get("checkpoints_fired", []))
        
        # Carrega os resultados dos relatórios
        reports = data.get("reports", {})
        st.session_state.report_estrutural = reports.get("estrutural")
        st.session_state.report_estilo = reports.get("estilo")
        st.session_state.report_capa_blurb = reports.get("blurb")
        st.session_state.report_capa_prompt = reports.get("prompt_capa")
        st.session_state.spine_thickness_mm = reports.get("spine_thickness_mm")
        st.session_state.generated_image_url = reports.get("cover_image_url")
        
        st.success(f"Checkpoint carregado com sucesso! Restaurado para Etapa: {STEP_TITLES.get(st.session_state.progress_step, 'Configuração')}.")
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Erro ao carregar o checkpoint: O arquivo pode estar corrompido ou no formato incorreto. Detalhe: {e}")

# --- FUNÇÕES DE LÓGICA DE NEGÓCIO ---

def extract_docx_paragraphs(uploaded_file):
    """Extrai parágrafos de um arquivo DOCX, ignorando títulos e vazios."""
    document = Document(uploaded_file)
    paragrafos = []
    
    # Índice baseado na ordem de extração
    for i, p in enumerate(document.paragraphs):
        # Ignora parágrafos vazios ou muito curtos (títulos, quebras de linha)
        if len(p.text.strip()) > 10 and not p.style.name.startswith(('Heading', 'Título', 'List')):
            # Armazenamos o índice original do parágrafo no documento para manter a ordem
            paragrafos.append({"indice": i, "texto": p.text})
    return paragrafos

def calculate_spine_thickness(page_count: int, paper_density_name: str, trim_size_name: str) -> float:
    """
    Calcula a espessura da lombada em milímetros (mm).
    Fórmula: (Contagem de Páginas) * (mm por página)
    """
    if page_count <= 0:
        return 0.0

    mm_per_page = PAPER_DENSITIES_MM_PER_PAGE.get(paper_density_name)
    
    if mm_per_page is None:
        st.error(f"Densidade do papel '{paper_density_name}' não encontrada. Usando padrão.")
        mm_per_page = PAPER_DENSITIES_MM_PER_PAGE[list(PAPER_DENSITIES_MM_PER_PAGE.keys())[0]]

    # A espessura é o número total de páginas (frente e verso) vezes a densidade da folha (mm/page)
    spine_in_mm = page_count * mm_per_page
    
    return round(spine_in_mm, 2)


# --- FUNÇÕES DE SIMULAÇÃO DE API (HIGH FIDELITY) ---

def api_call_with_backoff(system_prompt: str, user_query: str, structured_json: bool = False, max_retries: int = 5) -> Optional[str]:
    """
    Simula uma chamada de API Gemini estruturada com backoff e tratamento de erros.
    No código de produção, isso faria um 'fetch' para a API.
    """
    st.toast("Simulando chamada API Gemini...", icon="🤖")
    
    for attempt in range(max_retries):
        try:
            # Simulação de latência de rede e processamento (backoff)
            time.sleep(0.5 + 0.1 * (2 ** attempt)) 
            
            if "REVISÃO LITERÁRIA" in system_prompt:
                # Simula a revisão parágrafo a parágrafo
                return f"**(Rev. IA)** {user_query.strip()} *[Aprimorado em clareza, gramática e fluidez na Tentativa {attempt+1}]*"
            
            elif structured_json:
                # Simula o JSON estruturado para Marketing/Capa (Passo 6)
                if "Marketing e Capa" in system_prompt:
                    return json.dumps({
                        "blurb": f"O ano é 2057. Numa metrópole digital, o hacker {st.session_state.author_name} descobre um segredo que pode apagar a história. Um thriller eletrizante, gerado na Tentativa {attempt+1}.",
                        "prompt_capa": f"Digital painting, dramatic contrast, focused on the main theme of the book '{st.session_state.book_title}'. Use cinematic lighting, high detail, 8k, inspired by the requested visual style. (Attempt {attempt+1})"
                    })
                
            elif "Relatório" in system_prompt:
                # Simula a geração de relatórios (Passos 4 e 5)
                report_type = "Estrutural" if "Estrutural" in system_prompt else "Estilo"
                return (
                    f"## Relatório {report_type} - Análise Completa\n\n"
                    f"**Título:** {st.session_state.book_title}\n"
                    f"**Data da Análise:** {time.strftime('%Y-%m-%d')}\n\n"
                    f"**Conclusão da IA (Tentativa {attempt+1}):** O manuscrito apresenta grande potencial. No entanto, o **ritmo narrativo** (conforme solicitado) desacelera no segundo terço da obra. A voz do autor é consistente, mas recomendamos a revisão dos 5 advérbios de modo mais comuns para reduzir vícios de linguagem. "
                    f"\n\n---\n\n{user_query[:500]}..." # Inclui um pedaço do texto para contextualizar
                )

            return f"Conteúdo Gerado pela IA (Tentativa {attempt+1})"

        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"Erro de API (Tentativa {attempt+1}): {e}. Tentando novamente...")
                continue
            else:
                st.error("Falha na chamada da API após várias tentativas. Verifique a chave de API e a rede.")
                return None

def dalle_image_generation(prompt_capa: str) -> Optional[str]:
    """Simula a chamada à API Imagen/DALL-E 3 para gerar imagem de capa."""
    st.toast("Simulando geração de capa com IA (Imagen/DALL-E 3)...", icon="🖼️")
    
    # Simula o tempo de geração real, que pode ser longo
    time.sleep(5) 
    
    # A URL da imagem gerada pela IA seria salva aqui.
    # Usamos uma URL de placeholder que muda com o prompt (para simular unicidade)
    try:
        hash_color = abs(hash(prompt_capa)) % 0xFFFFFF
        hex_color = format(hash_color, '06x')
        
        # Placeholder que imita um resultado 2:3 (vertical) para capa
        image_url = f"https://placehold.co/600x900/{hex_color}/ffffff?text=Capa+Gerada+por+IA"
        st.session_state.generated_image_url = image_url
        st.success("Imagem de capa gerada e salva no estado.")
        return image_url
    except Exception as e:
        st.error(f"Falha na simulação da geração da imagem: {e}")
        return None

# --- FUNÇÕES DE DIAGRAMAÇÃO DOCX (ALTO NÍVEL) ---

def apply_docx_styles(document: Document, style_template_name: str, trim_size_name: str):
    """Configura margens, tamanho do papel e estilos base (Normal, Heading 1) no DOCX."""
    
    font_name, alignment_type = STYLE_TEMPLATES.get(style_template_name, ("Garamond", "JUSTIFY"))
    width_in, height_in = KDP_SIZES.get(trim_size_name, KDP_SIZES[list(KDP_SIZES.keys())[0]])['width_in'], KDP_SIZES.get(trim_size_name, KDP_SIZES[list(KDP_SIZES.keys())[0]])['height_in']

    # 1. Configurar margens e tamanho do papel
    section = document.sections[0]
    section.page_width = Inches(width_in)
    section.page_height = Inches(height_in)
    
    # Margens Padrão para 6x9 (0.75 polegadas)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)

    # 2. Configurar o estilo "Normal" (Miolo)
    style_normal = document.styles['Normal']
    font_normal = style_normal.font
    font_normal.name = font_name
    font_normal.size = Pt(11) 
    
    paragraph_format = style_normal.paragraph_format
    
    # Converte string de alinhamento para enumeração do DOCX
    alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if alignment_type == "LEFT":
        alignment = WD_ALIGN_PARAGRAPH.LEFT
        
    paragraph_format.alignment = alignment
    paragraph_format.line_spacing = 1.0 # 1.0 = espaçamento simples
    paragraph_format.space_before = Pt(0)
    paragraph_format.space_after = Pt(0)
    
    # 3. Configurar estilo "Heading 1" (Títulos dos Capítulos)
    try:
        style_heading1 = document.styles['Heading 1']
    except KeyError:
        # Se não existir, adiciona
        style_heading1 = document.styles.add_style('Heading 1', WD_STYLE_TYPE.PARAGRAPH)

    heading_font = style_heading1.font
    heading_font.name = font_name
    heading_font.size = Pt(16)
    heading_font.bold = True
    
    style_heading1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_heading1.paragraph_format.space_before = Inches(0.75)
    style_heading1.paragraph_format.space_after = Inches(0.5)

def create_front_matter(document: Document):
    """Cria Páginas de Rosto, Copyright e Sumário (Elementos pré-textuais)."""
    
    # --- Página de Rosto (1) ---
    document.add_paragraph().add_run().add_break() # Espaçamento
    document.add_paragraph(st.session_state.book_title, 'Title').alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_paragraph().add_run(st.session_state.author_name).bold = True
    document.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_page_break()

    # --- Página de Copyright (2) ---
    document.add_heading('Ficha Técnica', 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    copyright_text = [
        f"© {time.strftime('%Y')} {st.session_state.author_name}",
        "Todos os direitos reservados para esta edição.",
        "\n",
        "Diagramação e Revisão por Editor Literário IA.",
        f"Design de Capa: Arte Gerada por IA ({st.session_state.report_capa_prompt or 'Não Gerado'})",
        f"Formato: {st.session_state.trim_size_name}",
        "ISBN-13: 978-X-XXXX-XXXX-X (Placeholder)",
        "\n",
        "É proibida a reprodução total ou parcial, sem a permissão expressa do autor."
    ]
    for line in copyright_text:
        p = document.add_paragraph(line)
        p.style = document.styles['Normal']
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    document.add_page_break()
    
    # --- Placeholder para Sumário (3) ---
    document.add_heading("Sumário", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_info = document.add_paragraph()
    p_info.add_run("INSTRUÇÃO: No Word, use ALT+A, F, L (ou Referências > Sumário > Tabela Automática) para gerar o Sumário dinâmico aqui, pois todos os capítulos foram marcados como 'Heading 1'.").bold = True
    p_info.style = document.styles['Normal']
    document.add_page_break()

def gerar_docx_final(manuscrito_revisado: List[Dict]) -> BytesIO:
    """Orquestra a geração do DOCX final com todas as regras de diagramação."""
    document = Document()
    
    # 1. Aplica o template de estilo e as dimensões
    apply_docx_styles(document, st.session_state.style_template_name, st.session_state.trim_size_name)
    
    # 2. Cria as páginas iniciais (pré-textuais)
    create_front_matter(document)

    # 3. Adicionar conteúdo revisado (ordenado)
    manuscrito_revisado_ordenado = sorted(manuscrito_revisado, key=lambda x: x['indice'])
    
    # Adicionar uma quebra de página (Page Break) antes do primeiro capítulo
    document.add_page_break() 
    
    paragrafos_por_capitulo = 50 # Heurística para simular a criação de capítulos
    current_chapter = 1

    for i, item in enumerate(manuscrito_revisado_ordenado):
        
        # Simular início de capítulo
        if i % paragrafos_por_capitulo == 0:
            if i > 0:
                document.add_page_break() # Quebra de página antes de todo novo capítulo
                
            document.add_heading(f"CAPÍTULO {current_chapter}", 1)
            # Adiciona o título do capítulo no estilo Heading 1 (para o Sumário)
            current_chapter += 1

        # Adicionar o parágrafo revisado (usando o estilo Normal já configurado)
        p = document.add_paragraph(item['texto'])
        
        # Se for Justificado, adiciona o recuo da primeira linha
        if STYLE_TEMPLATES[st.session_state.style_template_name][1] == "JUSTIFY":
            p.paragraph_format.first_line_indent = Inches(0.3)
        # Se for um parágrafo que não é o primeiro do capítulo, pode-se adicionar um recuo maior
        # A lógica DOCX é complexa, mas garantimos o estilo 'Normal'

    # 4. Salvar em buffer
    file_stream = BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream


# --- LÓGICA PRINCIPAL DO PROCESSAMENTO (FLUXO DE 8 PASSOS) ---

def process_manuscript():
    """Executa o fluxo de trabalho completo de pré-impressão em 8 etapas."""
    
    st.header(STEP_TITLES[3] if st.session_state.progress_step < 8 else STEP_TITLES[8])
    
    if st.session_state.total_paragrafos_processar == 0:
        st.error("Nenhum manuscrito carregado ou configurado. Por favor, carregue o DOCX.")
        return

    total_paragrafos = st.session_state.total_paragrafos_processar
    
    # --- Passo 3: Revisão Parágrafo a Parágrafo (P.P.) ---
    if st.session_state.progress_step == 3:
        st.subheader("Sub-etapa 3.1: Revisão do Miolo com IA")
        
        paragrafos_para_revisar = [
            p for p in st.session_state.manuscrito_original 
            if p['indice'] not in st.session_state.paragrafos_revisados_indices
        ]
        
        paragrafos_restantes = len(paragrafos_para_revisar)
        paragrafos_ja_revisados = total_paragrafos - paragrafos_restantes
        st.info(f"Revisados: **{paragrafos_ja_revisados}** de **{total_paragrafos}** | Restantes: **{paragrafos_restantes}**")
        
        if paragrafos_restantes > 0:
            
            # Cálculo dos Checkpoints (10%, 20%, ..., 90%)
            # Armazena os % que devem disparar o checkpoint
            checkpoint_milestones_perc = {p for p in range(10, 100, 10)} 

            # Inicia a barra de progresso
            progresso_barra_val = paragrafos_ja_revisados / total_paragrafos if total_paragrafos > 0 else 0
            st.session_state.barra_progresso = st.progress(progresso_barra_val, text=f"Progresso de Revisão: {progresso_barra_val*100:.1f}%")

            for i, paragrafo_obj in enumerate(paragrafos_para_revisar):
                indice_absoluto = paragrafo_obj['indice']
                
                # Chamada de IA (Simulada)
                system_prompt_rev = "REVISÃO LITERÁRIA PROFISSIONAL: Otimize clareza, gramática e fluidez, mantendo a voz narrativa."
                paragrafo_revisado = api_call_with_backoff(system_prompt_rev, paragrafo_obj['texto'])
                
                if paragrafo_revisado:
                    st.session_state.paragrafos_revisados_indices.add(indice_absoluto)
                    st.session_state.manuscrito_revisado.append({"indice": indice_absoluto, "texto": paragrafo_revisado})

                    progresso_atual = len(st.session_state.paragrafos_revisados_indices)
                    progresso_barra = progresso_atual / total_paragrafos
                    
                    # Calcula o percentual atual para o checkpoint
                    percentual_atual = math.floor(progresso_barra * 100)

                    # Atualiza a barra
                    st.session_state.barra_progresso.progress(progresso_barra, text=f"Progresso: {progresso_atual} de {total_paragrafos} parágrafos ({progresso_barra*100:.1f}%)")
                    
                    # Checagem de Checkpoint Automático a cada 10%
                    for milestone in checkpoint_milestones_perc:
                        # Se o percentual atual cruzou o marco E o marco ainda não foi disparado
                        if percentual_atual >= milestone and milestone not in st.session_state.checkpoints_fired:
                            
                            # Evita disparar o checkpoint de 90% se o total for 100%
                            if milestone == 90 and progresso_atual == total_paragrafos:
                                continue 
                                
                            st.session_state.checkpoints_fired.add(milestone) # Marca como disparado
                            update_processed_state() # Atualiza o estado para o salvamento
                            checkpoint_json = json.dumps(st.session_state.processed_state, indent=2, ensure_ascii=False)
                            filename = f"checkpoint_editor_ia_{milestone}pc.json"
                            
                            st.session_state.checkpoint_placeholder.download_button(
                                label=f"⬇️ CHECKPOINT {milestone}% ATINGIDO! BAIXAR",
                                data=checkpoint_json.encode('utf-8'),
                                file_name=filename,
                                mime="application/json",
                                key=f"download_checkpoint_auto_{milestone}_{time.time()}"
                            )
                            st.toast(f"Checkpoint Automático {milestone}% salvo!", icon="💾")
                            # Rerun para mostrar o botão imediatamente (opcional, mas garante que o botão apareça)
                            # st.experimental_rerun() 
                            break # Só dispara um checkpoint por loop
                        
            st.session_state.barra_progresso.progress(1.0, text="Revisão Parágrafo a Parágrafo concluída!")
        
        # Se todos os parágrafos foram revisados
        if len(st.session_state.paragrafos_revisados_indices) == total_paragrafos:
            st.success("Revisão de miolo concluída. Avançando para Relatórios de IA.")
            st.session_state.progress_step = 4
            st.experimental_rerun()


    # --- Fluxo de Geração de Relatórios e Capa (Passos 4, 5, 6, 7) ---
    
    texto_para_analise = "\n\n".join([p['texto'] for p in st.session_state.manuscrito_revisado])
    
    # Passo 4: Relatório Estrutural
    if st.session_state.progress_step == 4 and not st.session_state.report_estrutural:
        system_prompt_4 = f"Relatório Estrutural (Editor-Chefe): Analise o livro '{st.session_state.book_title}' de {st.session_state.author_name}. Avalie o arco narrativo, o ritmo e a coesão geral da trama em 300 palavras."
        st.session_state.report_estrutural = api_call_with_backoff(system_prompt_4, texto_para_analise)
        if st.session_state.report_estrutural:
            st.success("Relatório Estrutural concluído.")
            st.session_state.progress_step = 5
            st.experimental_rerun()
        else:
            st.warning("Relatório Estrutural falhou.")
            
    # Passo 5: Relatório de Estilo
    if st.session_state.progress_step == 5 and not st.session_state.report_estilo:
        system_prompt_5 = "Relatório de Estilo (Vícios e Clichês): Analise o texto em busca de repetições, advérbios desnecessários e clichês. Forneça 5 exemplos de melhoria em 300 palavras."
        st.session_state.report_estilo = api_call_with_backoff(system_prompt_5, texto_para_analise)
        if st.session_state.report_estilo:
            st.success("Relatório de Estilo concluído.")
            st.session_state.progress_step = 6
            st.experimental_rerun()
        else:
            st.warning("Relatório de Estilo falhou.")
            
    # Passo 6: Conteúdo de Capa/Contracapa (JSON Estruturado)
    if st.session_state.progress_step == 6 and not st.session_state.report_capa_blurb:
        system_prompt_6 = f"Marketing e Capa: Gere um blurb persuasivo (150 palavras) e um prompt de arte visual detalhado para o DALL-E 3/Imagen, representando o clímax. A saída DEVE ser um JSON: {{\"blurb\": \"...\", \"prompt_capa\": \"...\"}}."
        json_output = api_call_with_backoff(system_prompt_6, texto_para_analise, structured_json=True)
        
        if json_output:
            try:
                # Tenta parsear o JSON retornado (mesmo que simulado)
                result = json.loads(json_output)
                st.session_state.report_capa_blurb = result.get('blurb')
                st.session_state.report_capa_prompt = result.get('prompt_capa')
                
                st.success("Conteúdo de Marketing concluído.")
                st.session_state.progress_step = 7
                st.experimental_rerun()
            except json.JSONDecodeError:
                st.error("Falha ao analisar o JSON do relatório de marketing. Retentando...")
        else:
            st.warning("Conteúdo de Marketing falhou.")
            
    # Passo 7: Criação de Capa (Imagem)
    if st.session_state.progress_step == 7 and st.session_state.report_capa_prompt and not st.session_state.generated_image_url:
         dalle_image_generation(st.session_state.report_capa_prompt)
         if st.session_state.generated_image_url:
            st.success("Geração de Capa concluída.")
            st.session_state.progress_step = 8
            st.experimental_rerun()
         else:
             st.warning("Geração de Capa falhou.")
            
    # Passo 8: Cálculos Finais e Conclusão
    if st.session_state.progress_step == 8:
        if st.session_state.spine_thickness_mm is None:
             st.session_state.spine_thickness_mm = calculate_spine_thickness(
                 st.session_state.page_count_estimate,
                 st.session_state.paper_density_name,
                 st.session_state.trim_size_name
             )
        st.success("Processamento concluído. Todos os resultados estão prontos para download.")

# --- LAYOUT DA APLICAÇÃO STREAMLIT (UI) ---

st.set_page_config(layout="wide", page_title="Editor Literário IA - Pré-Impressão Completa")

# --- SIDEBAR: Configuração e Upload ---

with st.sidebar:
    st.title("📚 Editor Literário IA Profissional")
    st.markdown("---")
    
    st.header(STEP_TITLES[1])
    
    # 1. Configuração Inicial
    st.session_state.book_title = st.text_input("Título do Livro", value=st.session_state.book_title)
    st.session_state.author_name = st.text_input("Nome do Autor", value=st.session_state.author_name)
    st.session_state.page_count_estimate = st.number_input("Páginas Estimadas", min_value=1, max_value=2000, value=st.session_state.page_count_estimate)
    
    st.markdown("---")
    st.subheader("Configurações de Diagramação")
    st.session_state.trim_size_name = st.selectbox("Tamanho de Corte (Trim Size)", list(KDP_SIZES.keys()), index=list(KDP_SIZES.keys()).index(st.session_state.trim_size_name))
    st.session_state.paper_density_name = st.selectbox("Tipo de Papel (Para Cálculo de Lombada)", list(PAPER_DENSITIES_MM_PER_PAGE.keys()), index=list(PAPER_DENSITIES_MM_PER_PAGE.keys()).index(st.session_state.paper_density_name))
    st.session_state.style_template_name = st.selectbox("Template de Estilo do Miolo", list(STYLE_TEMPLATES.keys()), index=list(STYLE_TEMPLATES.keys()).index(st.session_state.style_template_name))

    st.markdown("---")
    st.header("Carregar Estado")
    uploaded_checkpoint = st.file_uploader("⬆️ Carregar Checkpoint Anterior (.json)", type=["json"], key="checkpoint_upload")
    if uploaded_checkpoint:
        carregar_checkpoint(uploaded_checkpoint)
    
    st.markdown("---")
    st.header(STEP_TITLES[2])
    uploaded_file = st.file_uploader("⬆️ Carregar Arquivo DOCX Original", type=["docx"], key="docx_upload")
    
    if uploaded_file:
        paragrafos_do_arquivo = extract_docx_paragraphs(uploaded_file)
        
        if paragrafos_do_arquivo:
            # Detecta se é um novo arquivo ou se o nome mudou e reseta
            if uploaded_file.name != st.session_state.current_docx_name or st.session_state.total_paragrafos_processar == 0:
                st.session_state.manuscrito_original = paragrafos_do_arquivo
                st.session_state.total_paragrafos_processar = len(paragrafos_do_arquivo)
                st.session_state.paragrafos_revisados_indices = set()
                st.session_state.manuscrito_revisado = []
                st.session_state.progress_step = 3 # Volta para o início do processo de revisão
                st.session_state.current_docx_name = uploaded_file.name
                st.session_state.spine_thickness_mm = None # Recalcula no passo 8
                st.session_state.checkpoints_fired = set() # Reseta os checkpoints
                st.success(f"DOCX carregado: '{uploaded_file.name}'. {len(paragrafos_do_arquivo)} parágrafos válidos.")
            else:
                 st.success(f"DOCX carregado: {len(paragrafos_do_arquivo)} parágrafos. Continuar da Etapa {st.session_state.progress_step}.")
        else:
            st.error("O arquivo DOCX não contém parágrafos significativos para processamento. Certifique-se de que não é apenas uma página de título.")


# --- MAIN CONTENT: Execução e Resultados ---

st.header("🚀 Fluxo de Pré-Impressão em 8 Passos")
st.markdown(f"**Status Atual:** **{STEP_TITLES.get(st.session_state.progress_step, 'Configuração')}**")
st.markdown("---")

# Placeholder para o botão de checkpoint automático
st.session_state.checkpoint_placeholder = st.empty()

# Botão principal de INICIAR/CONTINUAR (Step 3)
btn_label = f"▶️ {STEP_TITLES[st.session_state.progress_step]}" if st.session_state.progress_step < 8 else "✅ FINALIZAR PROCESSAMENTO E VER RESULTADOS"

if st.button(btn_label, type="primary"):
    if st.session_state.total_paragrafos_processar == 0 or st.session_state.progress_step < 3:
        st.error("Por favor, complete as Etapas 1 e 2 (Configuração e Upload) antes de iniciar a pré-impressão.")
        st.session_state.progress_step = 1 # Garante que o usuário volte para a config
    else:
        # Inicia a função principal de processamento
        process_manuscript()
        
# --- Exibição de Status e Salvamento Manual ---

st.markdown("---")
st.subheader("💾 Salvamento Manual e Status")

col_prog, col_btn = st.columns([0.7, 0.3])

with col_prog:
    if st.session_state.total_paragrafos_processar > 0:
        prog_revisados = len(st.session_state.paragrafos_revisados_indices)
        prog_total = st.session_state.total_paragrafos_processar
        prog_perc = prog_revisados / prog_total if prog_total > 0 else 0
        st.metric("Progresso de Revisão", f"{prog_revisados} / {prog_total} parágrafos", f"{prog_perc*100:.1f}% completo")
    else:
        st.info("Nenhum progresso ainda.")

with col_btn:
    if st.session_state.total_paragrafos_processar > 0:
        update_processed_state()
        processed_json = json.dumps(st.session_state.processed_state, indent=4, ensure_ascii=False)
        st.download_button(
            label="⬇️ Salvar Checkpoint Manual (JSON)",
            data=processed_json.encode('utf-8'),
            file_name=f"{st.session_state.book_title.replace(' ', '_')}_CHECKPOINT_MANUAL.json",
            mime="application/json",
            key="download_checkpoint_manual_final"
        )
    
st.markdown("---")
st.subheader("✅ Resultados de Análise e Criação")

# --- Exibição de Resultados (Expanders) ---

# Passo 4
with st.expander(STEP_TITLES[4], expanded=(st.session_state.progress_step >= 4)):
    if st.session_state.report_estrutural:
        st.markdown(st.session_state.report_estrutural)
    else:
        st.info("Relatório pendente: Inicie ou continue a Etapa 3.")

# Passo 5
with st.expander(STEP_TITLES[5], expanded=(st.session_state.progress_step >= 5)):
    if st.session_state.report_estilo:
        st.markdown(st.session_state.report_estilo)
    else:
        st.info("Relatório pendente: Relatório Estrutural precisa ser concluído.")

# Passo 6
with st.expander(STEP_TITLES[6], expanded=(st.session_state.progress_step >= 6)):
    if st.session_state.report_capa_blurb:
        st.subheader("📝 Blurb (Texto de Contracapa)")
        st.markdown(st.session_state.report_capa_blurb)
        st.subheader("🎨 Prompt Visual Detalhado para IA")
        st.code(st.session_state.report_capa_prompt, language='text')
    else:
        st.info("Conteúdo de Marketing pendente.")

# Passo 7
with st.expander(STEP_TITLES[7], expanded=(st.session_state.progress_step >= 7)):
    if st.session_state.generated_image_url:
        st.subheader("Prévia da Arte da Capa")
        st.image(st.session_state.generated_image_url, caption=f"Capa Gerada por IA: {st.session_state.report_capa_prompt[:50]}...")
        # Simulação do download da imagem real (com dados de placeholder)
        st.download_button(
            label="⬇️ Baixar Arte da Capa (Simulação PNG)",
            data=b"Simulated PNG Data",
            file_name=f"{st.session_state.book_title.replace(' ', '_')}_Capa_Arte.png",
            mime="image/png"
        )
    elif st.session_state.progress_step >= 6:
        st.info("Clique no botão Continuar para acionar a geração da capa.")
        if st.button("Gerar Capa Agora (Manual)", key="generate_cover_manual"):
            process_manuscript() # Força a execução da Etapa 7

# Passo 8
with st.expander(STEP_TITLES[8], expanded=(st.session_state.progress_step == 8)):
    if st.session_state.progress_step == 8 and st.session_state.spine_thickness_mm is not None:
        
        st.subheader("📐 Dados Técnicos para Capa e Impressão")
        
        # Recupera as dimensões do trim size
        width, height = KDP_SIZES[st.session_state.trim_size_name]['width_in'], KDP_SIZES[st.session_state.trim_size_name]['height_in']
        spine_mm = st.session_state.spine_thickness_mm
        
        col_spine, col_dims = st.columns(2)
        
        with col_spine:
            st.metric("Espessura da Lombada (Spine Thickness)", f"**{spine_mm} mm**", help="Valor crucial para o design da capa.")
            st.metric("Páginas Contadas", f"{st.session_state.page_count_estimate}", help=f"Baseado no papel {st.session_state.paper_density_name}")
            
        with col_dims:
            # Largura total da capa (Contra-capa + Lombada + Capa)
            # 1 polegada = 25.4 mm. (spine_mm / 25.4) = lombada em polegadas
            spine_in = spine_mm / 25.4
            total_width_in = width * 2 + spine_in
            
            st.metric("Dimensões do Miolo", f"{width} in x {height} in")
            st.metric("Largura Total da Capa (Plana)", f"**{total_width_in:.3f} in**", help="Esta é a largura total para o designer: Capa + Lombada + Contracapa.")
        
        st.markdown("**Instruções:** Envie a arte da capa em PDF ou JPG com pelo menos 300 dpi. O miolo deve ser enviado em DOCX ou PDF-X/1a.")

        st.subheader("Downloads Finais de Produção")
        
        # Botão de Download do DOCX Final
        if st.session_state.manuscrito_revisado and len(st.session_state.paragrafos_revisados_indices) == st.session_state.total_paragrafos_processar:
            docx_file_stream = gerar_docx_final(st.session_state.manuscrito_revisado)
            st.download_button(
                label="⬇️ Baixar Miolo Diagramado e Formatado (.docx)",
                data=docx_file_stream,
                file_name=f"{st.session_state.book_title.replace(' ', '_')}_MIOLO_PRONTO.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="download_docx_final"
            )
        else:
            st.warning("O download do DOCX final estará disponível após a conclusão da Revisão P.P. (Etapa 3).")
    else:
        st.info("Aguardando conclusão das etapas anteriores.")
