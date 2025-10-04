import os
import streamlit as st
from openai import OpenAI
from docx import Document
from io import BytesIO
from docx.shared import Inches

# --- CONFIGURAÇÃO: DICIONÁRIO DE TAMANHOS KDP (Pol: polegadas / CM: centímetros) ---

KDP_SIZES = {
    "Padrão EUA (6x9 in)": {"name": "6 x 9 in", "width_in": 6.0, "height_in": 9.0, "width_cm": 15.24, "height_cm": 22.86, "papel_fator": 0.00115},
    "Padrão A5 (5.83x8.27 in)": {"name": "A5 (14.8 x 21 cm)", "width_in": 5.83, "height_in": 8.27, "width_cm": 14.8, "height_cm": 21.0, "papel_fator": 0.00115},
    "Pocket (5x8 in)": {"name": "5 x 8 in", "width_in": 5.0, "height_in": 8.0, "width_cm": 12.7, "height_cm": 20.32, "papel_fator": 0.00115},
    "Maior (7x10 in)": {"name": "7 x 10 in", "width_in": 7.0, "height_in": 10.0, "width_cm": 17.78, "height_cm": 25.4, "papel_fator": 0.00115},
}


# --- 0. Configuração e Inicialização ---

st.set_page_config(page_title="Editor Literário IA - Pré-Impressão", layout="wide")
st.title("📚 Editor Literário com GPT AI")
st.subheader("Pré-Impressão Completa: Controle Total de Formato e KDP.")

# Nomes das variáveis que o Streamlit irá ler do secrets.toml
API_KEY_NAME = "OPENAI_API_KEY"
PROJECT_ID_NAME = "OPENAI_PROJECT_ID"
MODEL_NAME = "gpt-4o-mini" 

# Configuração da API 
try:
    API_KEY = None
    PROJECT_ID = None
    if hasattr(st, 'secrets'):
         if API_KEY_NAME in st.secrets:
             API_KEY = st.secrets[API_KEY_NAME]
         if PROJECT_ID_NAME in st.secrets:
             PROJECT_ID = st.secrets[PROJECT_ID_NAME]
    
    if not API_KEY or not PROJECT_ID:
        st.error(f"ERRO: A Chave da API e o ID do Projeto da OpenAI ({API_KEY_NAME} e {PROJECT_ID_NAME}) não estão configurados corretamente no Secrets.")
        st.stop()
        
    client = OpenAI(
        api_key=API_KEY,
        project=PROJECT_ID 
    )
except Exception as e:
    st.error(f"Erro na inicialização da API: {e}")
    st.stop()


# --- 1. Função de Chamada da API (UNIFICADA) ---

def call_openai_api(system_prompt: str, user_content: str) -> str:
    """Função genérica para chamar a API da OpenAI."""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERRO DE CONEXÃO DA API] Falha ao se comunicar com a OpenAI. Detalhes: {e}"


# --- 2. Prompts de Edição e Revisão (Mantidos) ---
def get_edicao_prompt_system() -> str:
    return """
    Você é um editor literário de nível sênior, com foco em ficção.
    Sua tarefa é revisar, editar e aprimorar o parágrafo a seguir, garantindo que esteja pronto para a publicação.
    Instruções de Edição: 1. Revisão Gramatical e Ortográfica. 2. Edição de Estilo (Força Narrativa). 3. Coerência de Linguagem e Narrativa.
    ATENÇÃO: Retorne *apenas* o parágrafo revisado, sem comentários, introduções ou explicações.
    """

def revisar_paragrafo(paragrafo_texto: str) -> str:
    """Envia o parágrafo para a API da OpenAI e recebe a versão editada."""
    if not paragrafo_texto.strip(): return "" 
    
    system_prompt = get_edicao_prompt_system()
    user_content = f"Parágrafo a ser editado:\n---\n{paragrafo_texto}\n---"
    
    texto_revisado = call_openai_api(system_prompt, user_content)
    
    if "[ERRO DE CONEXÃO DA API]" in texto_revisado:
        return paragrafo_texto
    
    return texto_revisado


# --- 3. Geração de Relatório Estrutural (Mantido) ---
def gerar_relatorio_estrutural(texto_completo: str) -> str:
    """Analisa o texto completo para dar feedback estrutural."""
    system_prompt = "Você é um Editor-Chefe de uma grande editora. Gere um breve Relatório de Revisão para o autor. Foque em: Ritmo da Narrativa, Desenvolvimento de Personagens e Estrutura Geral. Formate o relatório usando títulos e bullet points."
    user_content = f"MANUSCRITO PARA ANÁLISE:\n---\n{texto_completo[:15000]}\n---"
    return call_openai_api(system_prompt, user_content)


# --- 4. Geração do Conteúdo de Capa e Contracapa (Mantido) ---
def gerar_conteudo_capa_contracapa(titulo: str, autor: str, texto_completo: str) -> str:
    """Analisa o manuscrito e gera o blurb (texto da contracapa) e sugestões de design."""
    system_prompt = "Você é um especialista em Marketing e copywriter de best-sellers. Gere o conteúdo da Capa/Contracapa. Requisitos: Blurb (3-4 parágrafos), 3 Palavras-chave de Marketing, Sugestão de Imagem. Use o formato estrito de saída."
    user_content = f"Título: {titulo}\nAutor: {autor}\nMANUSCRITO PARA ANÁLISE:\n---\n{texto_completo[:15000]}\n---"
    prompt_final = f"{system_prompt}\n\n{user_content}\n\nUse o seguinte formato de saída:\n## Título: {titulo}\n## Autor: {autor}\n\n**BLURB DA CONTRACAPA:**\n[Seu texto de blurb aqui...]\n\n**PALAVRAS-CHAVE DE MARKETING:**\n[Palavra 1], [Palavra 2], [Palavra 3]\n\n**SUGESTÃO DE ARTE PARA A CAPA:**\n[Sua descrição de imagem aqui...]"
    return call_openai_api(system_prompt, prompt_final)


# --- 5. Geração do Relatório de Conformidade KDP (Melhorado) ---
def gerar_relatorio_conformidade_kdp(titulo: str, autor: str, page_count: int, format_data: dict, espessura_cm: float, capa_largura_total_cm: float, capa_altura_total_cm: float) -> str:
    """
    Gera um checklist de conformidade técnica para upload na Amazon KDP.
    """
    tamanho_corte = format_data['name']
    
    prompt_kdp = f"""
    Você é um Especialista Técnico em Publicação e Conformidade da Amazon KDP.
    Gere um Relatório de Conformidade para o manuscrito, focado em upload bem-sucedido para Livros Físicos (Brochura) e eBooks.

    Dados Fornecidos:
    - Formato Escolhido: {tamanho_corte}
    - Páginas (Estimado): {page_count}
    - Espessura da Lombada (Calculada): {espessura_cm} cm
    - Capa Completa: {capa_largura_total_cm} cm (Largura) x {capa_altura_total_cm} cm (Altura)

    Gere o relatório usando o formato de lista e títulos:
    
    ---
    ### 1. Livro Físico (Brochura - Especificações)
    - **Tamanho de Corte Final (Miolo):** {tamanho_corte} ({format_data['width_cm']} x {format_data['height_cm']} cm).
    - **Dimensões do Arquivo de Capa:** O seu designer deve criar um PDF único com sangria de 0.3 cm. As dimensões mínimas com sangria devem ser: **{capa_largura_total_cm} cm (Largura) x {capa_altura_total_cm} cm (Altura).**
    - **Requisito de Miolo:** O DOCX baixado já tem as margens para este formato. O arquivo final de upload deve ser um PDF sem marcas de corte.

    ### 2. eBook (EPUB/Kindle)
    Gere um checklist de 5 itens essenciais que o autor deve verificar na formatação do DOCX para garantir um EPUB de qualidade. Foque em: Títulos (Heading 1), Sumário lógico, e espaçamento.
    
    ### 3. Otimização de Metadados (SEO Básico KDP)
    Sugira 3 categorias de nicho da Amazon e 3 palavras-chave de cauda longa para otimizar a listagem do livro.
    ---
    
    Retorne apenas o texto formatado do relatório.
    """
    response = call_openai_api("Você é um especialista em publicação KDP.", prompt_kdp)
    return response


# --- 6. Função Principal: Processamento de Revisão e Diagramação DOCX (AGORA DINÂMICA) ---

def processar_manuscrito(uploaded_file, format_data):
    documento_original = Document(uploaded_file)
    documento_revisado = Document()
    
    # --- CONFIGURAÇÃO DINÂMICA DO LIVRO ---
    width_in = format_data['width_in']
    height_in = format_data['height_in']

    section = documento_revisado.sections[0]
    section.page_width = Inches(width_in)
    section.page_height = Inches(height_in)
    
    # Margens de Livro (Padrão para a maioria dos tamanhos, em polegadas)
    section.left_margin = Inches(1.0) # Margem Externa
    section.right_margin = Inches(0.6) # Margem Interna (Gutter/Lombada)
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)

    # --- CONFIGURAÇÃO DE ESTILO PROFISSIONAL (EDITORAÇÃO BÁSICA) ---
    style = documento_revisado.styles['Normal']
    style.font.name = 'Garamond'
    style.font.size = Inches(0.15) # Aproximadamente 11pt

    paragraph_format = style.paragraph_format
    paragraph_format.line_spacing = 1.15 # Espaçamento entre linhas
    paragraph_format.first_line_indent = Inches(0.5) # Recuo de 1,25 cm
    
    paragrafos = documento_original.paragraphs
    total_paragrafos = len(paragrafos)
    texto_completo = ""
    
    progress_bar = st.progress(0, text="Processando 0%")
    
    for i, paragrafo in enumerate(paragrafos):
        texto_original = paragrafo.text
        texto_completo += texto_original + "\n"
        
        percent_complete = int((i + 1) / total_paragrafos * 100)
        progress_bar.progress(percent_complete, text=f"Processando {percent_complete}% ({i+1}/{total_paragrafos})")

        if len(texto_original.strip()) < 10:
            documento_revisado.add_paragraph(texto_original)
            continue 

        texto_revisado = revisar_paragrafo(texto_original)
        
        # Aplica o estilo 'Normal' recém-definido
        novo_paragrafo = documento_revisado.add_paragraph(texto_revisado)
        novo_paragrafo.style = 'Normal' 
        
    progress_bar.progress(100, text="Processamento concluído! 🎉")
    st.success(f"Manuscrito revisado, formatado e diagramado no formato {format_data['name']} com sucesso.")
    
    return documento_revisado, texto_completo


# --- 7. Interface do Streamlit (UI) ---

# Coleta de Metadados
st.markdown("---")
st.subheader("1. Informações e Formato do Livro")

col1, col2, col3 = st.columns([1.5, 1.5, 2])
with col1:
    book_title = st.text_input("Título do Livro", "O Último Código de Honra")
with col2:
    book_author = st.text_input("Nome do Autor", "Carlos Honorato")

# NOVO: Seleção de Tamanho de Corte
format_option = st.selectbox(
    "Escolha o Formato do Miolo (Tamanho de Corte) - Essencial para o KDP:",
    options=list(KDP_SIZES.keys()),
    index=1, # Padrão A5
    help="O formato define as dimensões do livro físico e o cálculo da lombada."
)

selected_format_data = KDP_SIZES[format_option]

st.markdown("---")

col4, col5 = st.columns(2)
with col4:
    page_count = st.number_input("Contagem Aproximada de Páginas (Miolo)", min_value=10, value=250, step=10, help="Use a contagem de páginas do seu DOCX antes da diagramação.")
with col5:
    uploaded_file = st.file_uploader(
        "2. Faça o upload do seu arquivo .docx", 
        type=['docx'],
        help="O processamento de arquivos grandes pode levar alguns minutos."
    )

st.warning("""
    AVISO: As margens e o tamanho de corte para impressão foram aplicados neste DOCX. 
    Para gerar o PDF/X final, utilize a função "Exportar para PDF" em seu editor de texto (Word/LibreOffice).
""")

if uploaded_file is not None and st.button("3. Iniciar PRÉ-IMPRESSÃO COMPLETA"):
    if not book_title or not book_author:
        st.error("Por favor, preencha o Título e o Autor antes de iniciar.")
        st.stop()
        
    st.info("Atenção: O processo de Pré-Impressão foi iniciado. Isso pode levar alguns minutos...")
    
    # Processa o manuscrito (revisão e diagrama)
    documento_revisado, texto_completo = processar_manuscrito(uploaded_file, selected_format_data)
    
    if documento_revisado:
        # --- PASSO A: Geração do Relatório Estrutural ---
        st.subheader("RESULTADO 1: Relatório Estrutural (Editor-Chefe)")
        with st.spinner("Analisando ritmo e personagens para o relatório estrutural..."):
            relatorio = gerar_relatorio_estrutural(texto_completo)
        
        st.text_area("Relatório Estrutural da IA:", relatorio, height=300)
        
        # --- PASSO B: Geração do Conteúdo da Capa/Contracapa ---
        st.subheader("RESULTADO 2: Conteúdo de Capa/Contracapa (Marketing)")
        with st.spinner("Criando o blurb de marketing e sugestões de design..."):
            conteudo_capa = gerar_conteudo_capa_contracapa(book_title, book_author, texto_completo)
        
        st.text_area("Conteúdo de Vendas e Sugestões de Arte:", conteudo_capa, height=400)

        
        # --- PASSO C: Cálculos Técnicos DINÂMICOS ---
        # Fator de cálculo (assumindo papel offset 90g)
        papel_fator = selected_format_data['papel_fator'] 
        
        # 1. Espessura da Lombada (cm)
        espessura_cm = round(page_count * papel_fator, 2) 

        # 2. Largura da Capa Completa (cm) = Capa + Contracapa + Lombada
        capa_largura_total_cm = round((selected_format_data['width_cm'] * 2) + espessura_cm, 2)
        
        # 3. Altura da Capa Completa (cm) - Não muda, adicionamos 0.6 cm para sangria (0.3cm topo e 0.3cm rodapé)
        capa_altura_total_cm = round(selected_format_data['height_cm'] + 0.6, 2)


        # --- PASSO D: Geração do Relatório de Conformidade KDP (NOVO) ---
        st.subheader("RESULTADO 3: Relatório de Conformidade KDP (Amazon)")
        with st.spinner("Gerando checklist técnico e de SEO para o upload na Amazon..."):
            relatorio_kdp = gerar_relatorio_conformidade_kdp(
                book_title, book_author, page_count, selected_format_data, 
                espessura_cm, capa_largura_total_cm, capa_altura_total_cm
            )
        
        st.markdown(relatorio_kdp)

        
        # --- PASSO E: Resumo Técnico Final e Downloads ---
        st.subheader("RESULTADO 4: Resumo Técnico Final e Downloads")
        
        st.markdown(f"""
        O seu produto de pré-impressão está pronto para publicação. Entregue os arquivos abaixo ao seu designer gráfico ou gráfica:

        #### 📄 Especificações do Livro Físico (Amazon KDP / Gráfica)
        - **Formato Escolhido:** **{selected_format_data['name']}**
        - **Miolo (PDF) Tamanho:** {selected_format_data['width_cm']} cm x {selected_format_data['height_cm']} cm
        - **Número de Páginas (Estimado):** {page_count}
        - **Espessura da Lombada (Estimada):** **{espessura_cm} cm**
        - **Capa Completa (Arquivo PDF):** **{capa_largura_total_cm} cm (Largura) x {capa_altura_total_cm} cm (Altura)** (Incluindo 0.3cm de sangria em cada lado)
        """)


        # --- PASSO F: Download dos Arquivos ---
        st.markdown("#### ⬇️ Downloads Finais")
        
        # Download do Relatório
        relatorio_buffer = BytesIO(relatorio.encode('utf-8'))
        st.download_button(
            label="1. Baixar Relatório Estrutural (.txt)",
            data=relatorio_buffer,
            file_name="Relatorio_Estrutural.txt",
            mime="text/plain"
        )
        
        # Download do DOCX Diagramado
        buffer = BytesIO()
        documento_revisado.save(buffer)
        buffer.seek(0)
        st.download_button(
            label="2. Baixar Manuscrito Diagramado (.docx)",
            data=buffer,
            file_name=f"{book_title.replace(' ', '_')}_FINAL_DIAGRAMADO_{selected_format_data['name'].replace(' ', '_').replace('x','_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        st.balloons()
