import os
import streamlit as st
from openai import OpenAI
from docx import Document
from io import BytesIO
from docx.shared import Inches

# --- 0. Configuração e Inicialização (CORREÇÃO PARA CHAVE DE PROJETO SK-PROJ-) ---

st.set_page_config(page_title="Editor Literário IA - Pré-Impressão", layout="wide")
st.title("📚 Editor Literário com GPT AI")
st.subheader("Pré-Impressão Completa: Conteúdo, Coerência, Diagramação e Capa.")

# Nomes das variáveis que o Streamlit irá ler do secrets.toml
API_KEY_NAME = "OPENAI_API_KEY"
PROJECT_ID_NAME = "OPENAI_PROJECT_ID"
MODEL_NAME = "gpt-4o-mini" 

# Configuração da API 
try:
    # 1. Busca a Chave da API e o Project ID dos Streamlit Secrets
    API_KEY = None
    PROJECT_ID = None

    # Lógica de segurança para ler os secrets no Streamlit Cloud
    if hasattr(st, 'secrets'):
         if API_KEY_NAME in st.secrets:
             API_KEY = st.secrets[API_KEY_NAME]
         if PROJECT_ID_NAME in st.secrets:
             PROJECT_ID = st.secrets[PROJECT_ID_NAME]
    
    # Verifica se os dois valores essenciais estão presentes
    if not API_KEY or not PROJECT_ID:
        # Se falhar, exibe uma mensagem específica para o autor saber o que falta no secrets.toml
        st.error(f"ERRO: A Chave da API e o ID do Projeto da OpenAI ({API_KEY_NAME} e {PROJECT_ID_NAME}) não estão configurados corretamente no Secrets.")
        st.info("Atenção: Para chaves 'sk-proj-', você precisa salvar o 'OPENAI_API_KEY' E o 'OPENAI_PROJECT_ID' no Streamlit Secrets.")
        st.stop()
        
    # 2. Inicialização do cliente OpenAI usando Project ID (essencial para chaves sk-proj-)
    client = OpenAI(
        api_key=API_KEY,
        project=PROJECT_ID # Este parâmetro é a solução definitiva para o erro 401/sk-proj-
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
        return f"[ERRO DE CONEXÃO DA API] Falha ao se comunicar com a OpenAI. Verifique se o Project ID está correto. Detalhes: {e}"


# --- 2. Prompts de Edição e Revisão ---

def get_edicao_prompt_system() -> str:
    return """
    Você é um editor literário de nível sênior, com foco em ficção.
    Sua tarefa é revisar, editar e aprimorar o parágrafo a seguir, garantindo que esteja pronto para a publicação.
    Instruções de Edição:
    1. **Revisão Gramatical e Ortográfica:** Corrija todos os erros.
    2. **Edição de Estilo (Força Narrativa):** Sugira reescritas para frases fracas, utilizando o princípio "Mostre, Não Diga" e favorecendo a voz ativa.
    3. **Coerência de Linguagem e Narrativa:** Mantenha um tom consistente.
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


# --- 3. Geração de Relatório Estrutural (Editor-Chefe) ---

def gerar_relatorio_estrutural(texto_completo: str) -> str:
    """Analisa o texto completo para dar feedback estrutural."""
    system_prompt = """
    Você é um Editor-Chefe de uma grande editora. Sua tarefa é analisar o manuscrito e gerar um breve Relatório de Revisão para o autor.
    Foque em: Ritmo da Narrativa, Desenvolvimento de Personagens e Estrutura Geral (início, clímax e resolução).
    Formate o relatório usando títulos e bullet points.
    """
    user_content = f"MANUSCRITO PARA ANÁLISE:\n---\n{texto_completo[:15000]}\n---"
    return call_openai_api(system_prompt, user_content)


# --- 4. Geração do Conteúdo de Capa e Contracapa (Marketing) ---

def gerar_conteudo_capa_contracapa(titulo: str, autor: str, texto_completo: str) -> str:
    """Analisa o manuscrito e gera o blurb (texto da contracapa) e sugestões de design."""
    system_prompt = """
    Você é um especialista em Marketing e um copywriter de best-sellers.
    Analise o manuscrito para gerar o conteúdo da Capa e Contracapa.
    Requisitos: 1. Blurb (Contracapa): 3-4 parágrafos curtos, envolventes, criando suspense. 2. Palavras-chave: Sugira 3 palavras-chave de marketing. 3. Sugestão de Imagem: Descreva a imagem ideal para a capa.
    Use o formato estrito de saída.
    """
    user_content = f"""
    Título: {titulo}
    Autor: {autor}
    MANUSCRITO PARA ANÁLISE:
    ---
    {texto_completo[:15000]}
    ---
    """
    
    prompt_final = f"{system_prompt}\n\n{user_content}\n\nUse o seguinte formato de saída:\n## Título: {titulo}\n## Autor: {autor}\n\n**BLURB DA CONTRACAPA:**\n[Seu texto de blurb aqui...]\n\n**PALAVRAS-CHAVE DE MARKETING:**\n[Palavra 1], [Palavra 2], [Palavra 3]\n\n**SUGESTÃO DE ARTE PARA A CAPA:**\n[Sua descrição de imagem aqui...]"
    
    return call_openai_api(system_prompt, prompt_final)


# --- 5. NOVA FUNÇÃO: Geração do Relatório de Conformidade KDP (Amazon) ---

def gerar_relatorio_conformidade_kdp(titulo: str, autor: str, page_count: int, espessura_cm: float) -> str:
    """
    Gera um checklist de conformidade técnica para upload na Amazon KDP (Kindle Direct Publishing).
    """
    
    # Define o tamanho de corte físico (A5)
    tamanho_corte = "14.8cm x 21cm (A5)"
    
    prompt_kdp = f"""
    Você é um Especialista Técnico em Publicação e Conformidade da Amazon KDP (Kindle Direct Publishing).
    Sua tarefa é gerar um Relatório de Conformidade para o manuscrito a seguir, focado em garantir um upload bem-sucedido para Livros Físicos (Brochura) e eBooks (EPUB).

    Use os dados fornecidos:
    - Título do Livro: {titulo}
    - Autor: {autor}
    - Páginas (Estimado): {page_count}
    - Espessura da Lombada (Calculada): {espessura_cm} cm
    - Tamanho de Corte: {tamanho_corte}

    Gere o relatório usando este formato:
    
    ---
    ### 1. Livro Físico (Brochura - Miolo e Capa)
    - **Requisito de Upload (Miolo):** O arquivo final deve ser um PDF sem marcas de corte e no tamanho de corte exato ({tamanho_corte}). O arquivo DOCX diagramado já tem as margens de livro (A5) aplicadas.
    - **Requisito de Upload (Capa):** O PDF de capa completa (Capa, Lombada, Contracapa) deve ser gerado com as dimensões totais de: (14.8cm x 2) + {espessura_cm} cm de largura e 21cm de altura.

    ### 2. eBook (EPUB/Kindle)
    Gere um checklist de 5 itens essenciais que o autor deve verificar na formatação do DOCX para garantir um EPUB de qualidade. Foque em:
    - Uso correto de Estilos (Heading 1 para Títulos de Capítulos).
    - Remoção de espaços duplos e tabulações no início de parágrafos.
    - Sumário lógico (Table of Contents - TOC) criado automaticamente pela IA do Kindle.
    
    ### 3. Otimização de Metadados (SEO Básico KDP)
    Com base no Título e Autor, sugira 3 (três) categorias de nicho da Amazon (Ex: Ficção Científica > Steampunk) e 3 (três) palavras-chave de cauda longa (long-tail keywords) que o autor deve usar no backend do KDP para atrair leitores.
    ---
    
    Retorne apenas o texto formatado do relatório.
    """
    try:
        response = call_openai_api("Você é um especialista em publicação KDP.", prompt_kdp)
        return response
    except Exception as e:
        return f"Falha ao gerar o Relatório de Conformidade KDP: {e}"


# --- 6. Função Principal: Processamento de Revisão e Diagramação DOCX ---

def processar_manuscrito(uploaded_file):
    documento_original = Document(uploaded_file)
    documento_revisado = Document()
    
    # Configurações de Diagramação (A5 e Margens de Livro)
    section = documento_revisado.sections[0]
    section.page_width = Inches(5.83)
    section.page_height = Inches(8.27)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(0.6)
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    
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
        
        novo_paragrafo = documento_revisado.add_paragraph(texto_revisado)
        novo_paragrafo.style = paragrafo.style
        
    progress_bar.progress(100, text="Processamento concluído! 🎉")
    st.success("Manuscrito revisado, com coerência checada e diagramado com sucesso.")
    
    return documento_revisado, texto_completo


# --- 7. Interface do Streamlit (UI) ---

# Coleta de Metadados
st.markdown("---")
st.subheader("1. Informações do Livro")
col1, col2, col3 = st.columns(3)
with col1:
    book_title = st.text_input("Título do Livro", "O Último Código de Honra")
with col2:
    book_author = st.text_input("Nome do Autor", "Carlos Honorato")
with col3:
    page_count = st.number_input("Contagem Aproximada de Páginas", min_value=10, value=250, step=10, help="Use a contagem de páginas do seu DOCX antes da diagramação.")


st.markdown("---")
st.subheader("2. Arquivo do Manuscrito")

uploaded_file = st.file_uploader(
    "Faça o upload do seu arquivo .docx", 
    type=['docx'],
    help="O processamento de arquivos grandes pode levar alguns minutos."
)

st.warning("""
    AVISO: A diagramação de margens de livro (A5) foi aplicada neste DOCX.
    Para gerar o PDF/X final, utilize a função "Exportar para PDF" em seu editor de texto (Word/LibreOffice).
""")

if uploaded_file is not None and st.button("3. Iniciar PRÉ-IMPRESSÃO COMPLETA"):
    if not book_title or not book_author:
        st.error("Por favor, preencha o Título e o Autor antes de iniciar.")
        st.stop()
        
    st.info("Atenção: O processo de Pré-Impressão foi iniciado. Isso pode levar alguns minutos...")
    
    # Processa o manuscrito (revisão e diagrama)
    documento_revisado, texto_completo = processar_manuscrito(uploaded_file)
    
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

        
        # --- PASSO C: Cálculos Técnicos ---
        # Fórmula genérica para espessura da lombada 
        espessura_cm = round(page_count * 0.00115 * 10, 2) 
        
        # --- PASSO D: Geração do Relatório de Conformidade KDP (NOVO) ---
        st.subheader("RESULTADO 3: Relatório de Conformidade KDP (Amazon)")
        with st.spinner("Gerando checklist técnico e de SEO para o upload na Amazon..."):
            relatorio_kdp = gerar_relatorio_conformidade_kdp(book_title, book_author, page_count, espessura_cm)
        
        st.markdown(relatorio_kdp)

        
        # --- PASSO E: Resumo Técnico Final ---
        st.subheader("RESULTADO 4: Resumo Técnico e Downloads")
        
        st.markdown(f"""
        O seu produto de pré-impressão está pronto. Entregue os arquivos abaixo ao seu designer gráfico ou gráfica:

        #### 📄 Especificações do Livro Físico (Amazon KDP)
        - **Formato do Miolo:** A5 (14.8cm x 21cm)
        - **Número de Páginas (Estimado):** {page_count}
        - **Espessura da Lombada (Estimada):** **{espessura_cm} cm**
        - **Requisito de Entrega da Gráfica:** PDF/X-1a ou PDF/X-3 (Gerado manualmente a partir do DOCX baixado)
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
            file_name=f"{book_title.replace(' ', '_')}_FINAL_DIAGRAMADO.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        st.balloons()
