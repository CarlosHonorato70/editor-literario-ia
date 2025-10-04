import os
import streamlit as st
from google import genai
from docx import Document
from io import BytesIO
from docx.shared import Inches # Necessário para Margens

# --- 0. Configuração e Inicialização ---

st.set_page_config(page_title="Editor Literário IA", layout="wide")
st.title("📚 Editor Literário com Gemini AI")
st.subheader("Revisão de Coerência, Gramática e Diagramação Inicial.")

# Configuração da API (Lendo a chave de ambiente ou Streamlit Secrets)
try:
    # 1. Tenta ler a chave de variável de ambiente (para uso local)
    API_KEY = os.environ.get("GEMINI_API_KEY")
    
    # 2. Tenta ler a chave dos secrets do Streamlit (para hospedagem na nuvem)
    if not API_KEY and hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
         API_KEY = st.secrets['GEMINI_API_KEY']
    
    if not API_KEY:
        st.error("ERRO: A Chave de API do Gemini não está configurada.")
        st.info("Para uso local, configure a variável de ambiente. Para uso online, configure o Streamlit Secrets.")
        st.stop()
        
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Erro na inicialização da API: {e}")
    st.stop()


# --- 1. Função do Prompt de Edição Aprimorado (Foco na Coerência) ---

def get_edicao_prompt(texto: str) -> str:
    """Cria o prompt detalhado para guiar a IA na edição, focando em gramática, estilo e coerência."""
    
    prompt = f"""
    Você é um editor literário de nível sênior, com foco em ficção.
    Sua tarefa é revisar, editar e aprimorar o parágrafo a seguir, garantindo que esteja pronto para a publicação.
    
    Instruções de Edição:
    1. **Revisão Gramatical e Ortográfica:** Corrija todos os erros.
    2. **Edição de Estilo (Força Narrativa):** Sugira reescritas para frases fracas, utilizando o princípio "Mostre, Não Diga" (use ações para descrever emoções) e favorecendo a voz ativa.
    3. **Coerência de Linguagem e Narrativa:** Mantenha um tom consistente. Se identificar nomes, locais ou fatos que claramente contradizem o contexto de um livro (ex: mudança de nome de personagem, erro de cronologia), sinalize e corrija.
    
    ATENÇÃO: Retorne *apenas* o parágrafo revisado, sem comentários, introduções ou explicações.
    
    Parágrafo a ser editado:
    ---
    {texto}
    ---
    """
    return prompt

# --- 2. Função de Revisão com Gemini ---

def revisar_paragrafo(paragrafo_texto: str) -> str:
    """Envia o parágrafo para a API do Gemini e recebe a versão editada."""
    
    if not paragrafo_texto.strip():
        return "" 

    prompt = get_edicao_prompt(paragrafo_texto)
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt
        )
        return response.text.strip()
    
    except Exception as e:
        print(f"[ERRO DE IA] Falha ao processar o parágrafo. Retornando texto original: {e}")
        return paragrafo_texto

# --- 3. Função Principal: Revisão e Diagramação DOCX ---

def processar_manuscrito(uploaded_file):
    """
    Carrega, processa o manuscrito com a IA e aplica a diagramação de livro no DOCX.
    """
    documento_original = Document(uploaded_file)
    documento_revisado = Document()
    
    # Aplicação das Margens e Configurações de Página (Diagramação de Livro - Ponto 2)
    section = documento_revisado.sections[0]
    section.page_width = Inches(5.83)   # Largura A5 (14.8 cm)
    section.page_height = Inches(8.27)  # Altura A5 (21 cm)

    # Margens de Livro (Encadernação e Corte)
    section.left_margin = Inches(1.0)   # 2.54 cm (Margem interna mais larga)
    section.right_margin = Inches(0.6)  # 1.5 cm (Margem externa de corte)
    section.top_margin = Inches(0.8)    # 2.0 cm (Superior)
    section.bottom_margin = Inches(0.8) # 2.0 cm (Inferior)
    
    # Processamento dos Parágrafos pela IA
    paragrafos = documento_original.paragraphs
    total_paragrafos = len(paragrafos)
    
    progress_bar = st.progress(0, text="Processando 0%")
    
    for i, paragrafo in enumerate(paragrafos):
        texto_original = paragrafo.text
        
        percent_complete = int((i + 1) / total_paragrafos * 100)
        progress_bar.progress(percent_complete, text=f"Processando {percent_complete}% ({i+1}/{total_paragrafos})")

        if len(texto_original.strip()) < 10:
            documento_revisado.add_paragraph(texto_original)
            continue 

        texto_revisado = revisar_paragrafo(texto_original)
        
        novo_paragrafo = documento_revisado.add_paragraph(texto_revisado)
        novo_paragrafo.style = paragrafo.style
        
    progress_bar.progress(100, text="Processamento concluído! 🎉")
    st.success("Manuscrito revisado, com coerência checada e diagramado para impressão.")
    
    return documento_revisado

# --- 4. Interface do Streamlit (UI) ---

uploaded_file = st.file_uploader(
    "1. Faça o upload do seu arquivo .docx", 
    type=['docx'],
    help="O processamento de arquivos grandes pode levar alguns minutos."
)

st.warning("""
    AVISO SOBRE PDF/X: A diagramação de margens de livro (A5) foi aplicada neste DOCX. 
    Para gerar o PDF/X (formato final da gráfica), abra o DOCX baixado e utilize a função 
    "Exportar para PDF" em seu editor de texto (Word ou LibreOffice).
""")


if uploaded_file is not None:
    if st.button("2. Iniciar Revisão, Coerência e Diagramação"):
        st.info("Atenção: O processo de Revisão de Conteúdo e Diagramação foi iniciado.")
        
        documento_revisado = processar_manuscrito(uploaded_file)
        
        if documento_revisado:
            buffer = BytesIO()
            documento_revisado.save(buffer)
            buffer.seek(0)
            
            st.download_button(
                label="3. ⬇️ Baixar Manuscrito Diagramado (.docx)",
                data=buffer,
                file_name=f"{uploaded_file.name.replace('.docx', '')}_FINAL_DIAGRAMADO.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            st.balloons()
