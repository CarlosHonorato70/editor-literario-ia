import os
import streamlit as st
from google import genai
from docx import Document
from io import BytesIO
from docx.shared import Inches

# --- 0. Configuração e Inicialização ---

st.set_page_config(page_title="Editor Literário IA", layout="wide")
st.title("📚 Editor Literário com Gemini AI")
st.subheader("Pré-Impressão Completa: Conteúdo, Coerência e Diagramação.")

# Configuração da API
try:
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY and hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
         API_KEY = st.secrets['GEMINI_API_KEY']
    
    if not API_KEY:
        st.error("ERRO: A Chave de API do Gemini não está configurada.")
        st.stop()
        
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Erro na inicialização da API: {e}")
    st.stop()


# --- 1. Função do Prompt de Edição de Parágrafo (Mantida) ---

def get_edicao_prompt(texto: str) -> str:
    """Cria o prompt detalhado para edição gramatical e coerência."""
    # ... (O prompt existente que foca na correção de parágrafos)
    prompt = f"""
    Você é um editor literário de nível sênior, com foco em ficção.
    Sua tarefa é revisar, editar e aprimorar o parágrafo a seguir, garantindo que esteja pronto para a publicação.
    
    Instruções de Edição:
    1. **Revisão Gramatical e Ortográfica:** Corrija todos os erros.
    2. **Edição de Estilo (Força Narrativa):** Sugira reescritas para frases fracas, utilizando o princípio "Mostre, Não Diga" e favorecendo a voz ativa.
    3. **Coerência de Linguagem e Narrativa:** Mantenha um tom consistente. Se identificar nomes, locais ou fatos que claramente contradizem o contexto de um livro, sinalize e corrija.
    
    ATENÇÃO: Retorne *apenas* o parágrafo revisado, sem comentários, introduções ou explicações.
    
    Parágrafo a ser editado:
    ---
    {texto}
    ---
    """
    return prompt

def revisar_paragrafo(paragrafo_texto: str) -> str:
    # Função que envia o parágrafo para a IA
    if not paragrafo_texto.strip(): return "" 
    prompt = get_edicao_prompt(paragrafo_texto)
    try:
        response = client.models.generate_content(model='gemini-2.5-pro', contents=prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[ERRO DE IA] Falha ao processar o parágrafo: {e}")
        return paragrafo_texto

# --- NOVA FUNÇÃO: Geração do Relatório Estrutural (Editor-Chefe) ---

def gerar_relatorio_estrutural(texto_completo: str) -> str:
    """
    Analisa o texto completo para dar feedback estrutural, de ritmo e de personagem.
    """
    prompt_relatorio = f"""
    Você é um Editor-Chefe de uma grande editora. Sua tarefa é analisar o manuscrito e gerar um breve Relatório de Revisão para o autor, focando em:
    
    1. **Ritmo da Narrativa:** Em quais momentos o ritmo está lento (excesso de descrição) ou muito acelerado (falta de desenvolvimento).
    2. **Desenvolvimento de Personagens:** A motivação e arco dos personagens principais são claros e consistentes?
    3. **Estrutura Geral:** O início e o final (clímax e resolução) são satisfatórios?
    
    Formate o relatório usando títulos e bullet points, com no máximo 500 palavras.
    
    MANUSCRITO:
    ---
    {texto_completo[:15000]} 
    ---
    """
    # Limita o texto completo a 15000 caracteres para evitar ultrapassar o limite de tokens, 
    # pois o Gemini-2.5-pro possui limite de 32768 tokens, e o prompt em si já é grande.
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt_relatorio
        )
        return response.text
    except Exception as e:
        return f"Falha ao gerar o Relatório Estrutural: {e}"


# --- FUNÇÃO PRINCIPAL: Revisão, Diagramação e Coleta de Texto Completo ---

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
        texto_completo += texto_original + "\n" # Coleta o texto completo para o relatório
        
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
    
    return documento_revisado, texto_completo # Retorna os dois resultados


# --- 4. Interface do Streamlit (UI) ---

uploaded_file = st.file_uploader(
    "1. Faça o upload do seu arquivo .docx", 
    type=['docx'],
    help="O processamento de arquivos grandes pode levar alguns minutos."
)

st.warning("""
    AVISO: A diagramação de margens de livro (A5) foi aplicada neste DOCX.
    Para gerar o PDF/X final, utilize a função "Exportar para PDF" em seu editor de texto (Word/LibreOffice).
""")

if uploaded_file is not None:
    if st.button("2. Iniciar Revisão, Coerência e Diagramação"):
        st.info("Atenção: O processo de Pré-Impressão foi iniciado. Isso pode levar alguns minutos...")
        
        # Chama a função principal que agora retorna 2 resultados
        documento_revisado, texto_completo = processar_manuscrito(uploaded_file)
        
        if documento_revisado:
            # --- 3. Geração do Relatório Estrutural ---
            st.subheader("Relatório de Conteúdo (Editor-Chefe)")
            with st.spinner("Analisando ritmo e personagens para o relatório estrutural..."):
                relatorio = gerar_relatorio_estrutural(texto_completo)
            
            # Mostra o relatório na tela e permite download
            st.text_area("Relatório Estrutural da IA:", relatorio, height=300)
            
            # Prepara o relatório para download como arquivo de texto
            relatorio_buffer = BytesIO(relatorio.encode('utf-8'))
            st.download_button(
                label="3A. ⬇️ Baixar Relatório Estrutural (.txt)",
                data=relatorio_buffer,
                file_name="Relatorio_Estrutural.txt",
                mime="text/plain"
            )

            # Prepara e disponibiliza o DOCX revisado
            buffer = BytesIO()
            documento_revisado.save(buffer)
            buffer.seek(0)
            
            st.download_button(
                label="3B. ⬇️ Baixar Manuscrito Diagramado (.docx)",
                data=buffer,
                file_name=f"{uploaded_file.name.replace('.docx', '')}_FINAL_DIAGRAMADO.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            st.balloons()
