import streamlit as st
import io
import re
import math
import smartypants
import language_tool_python
from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from openai import OpenAI

# --- CONFIGURAÇÃO DA PÁGINA E ESTADO ---
st.set_page_config(page_title="Adapta ONE - Editor Editorial", page_icon="📚", layout="wide")

# Inicializa o estado da sessão para persistir os dados
def inicializar_estado():
    chaves_estado = {
        "text_content": "", "file_processed": False, "last_uploaded_file_id": None,
        "book_title": "Sem Título", "author_name": "Autor Desconhecido",
        "correcoes_gramaticais": None, "sugestoes_estilo": None,
        "metadados_gerados": None
    }
    for key, value in chaves_estado.items():
        if key not in st.session_state:
            st.session_state[key] = value

inicializar_estado()

# --- FUNÇÕES DE PROCESSAMENTO (BACKEND) ---

# Cache para carregar o modelo de linguagem pesado apenas uma vez
@st.cache_resource
def carregar_ferramenta_gramatical():
    st.write("Carregando modelo de revisão gramatical (apenas na primeira vez)...")
    return language_tool_python.LanguageTool('pt-BR')

def limpar_e_otimizar_tipografia(texto: str) -> str:
    # Aplica aspas curvas, travessões e outras melhorias tipográficas
    texto = smartypants.smartypants(texto, 2)
    # Garante que travessões de diálogo sejam formatados corretamente
    texto = re.sub(r'^\s*-\s+', '— ', texto, flags=re.MULTILINE)
    # Normaliza espaços e quebras de linha
    texto = re.sub(r' +', ' ', texto)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto.strip()

# Ponto 2: Revisão Ortográfica e Gramatical
def revisar_gramatica_estilo(texto: str, ferramenta):
    return ferramenta.check(texto)

# Ponto 3 & 6: Análise de Estilo e Consistência (via IA)
def gerar_sugestoes_estilo_ia(texto: str, client: OpenAI):
    prompt = f"""
    Analise o seguinte trecho de texto como um editor literário sênior.
    Forneça 3 a 5 sugestões concisas para melhorar o estilo, clareza, concisão ou impacto.
    Identifique também possíveis inconsistências simples (ex: "Maria" vs "Marta").
    Apresente cada sugestão em um novo parágrafo, começando com 'Sugestão:'.

    Texto:
    ---
    {texto}
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content.split('Sugestão:')[1:]

# Ponto 7: Geração de Metadados
def gerar_metadados_ia(texto: str, client: OpenAI):
    prompt = f"""
    Com base no manuscrito a seguir, gere os seguintes metadados para um livro:
    1. Título Sugerido: [Um título criativo e relevante]
    2. Palavras-chave: [Uma lista de 5 a 7 palavras-chave separadas por vírgula]
    3. Sinopse (150 palavras): [Uma sinopse envolvente para a contracapa]

    Manuscrito:
    ---
    {texto}
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    # Extrai os dados da resposta
    content = response.choices[0].message.content
    try:
        titulo = re.search(r"Título Sugerido: (.*?)\n", content).group(1)
        palavras_chave = re.search(r"Palavras-chave: (.*?)\n", content).group(1)
        sinopse = re.search(r"Sinopse \$150 palavras\$: (.*)", content, re.DOTALL).group(1)
        return {"titulo": titulo, "palavras_chave": palavras_chave, "sinopse": sinopse}
    except AttributeError:
        return {"titulo": "Não foi possível gerar", "palavras_chave": "Não foi possível gerar", "sinopse": content}

# Ponto 4, 5 e 8: Formatação e Exportação para .DOCX
def gerar_manuscrito_final_docx(titulo: str, autor: str, texto_manuscrito: str):
    texto_final = limpar_e_otimizar_tipografia(texto_manuscrito)
    document = Document()

    # Ponto 4: Define margens
    for section in document.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Adiciona Página de Rosto
    p_titulo = document.add_paragraph()
    p_titulo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_titulo.add_run(titulo.upper()).bold = True
    p_titulo.runs[0].font.size = Pt(16)
    p_titulo.runs[0].font.name = 'Times New Roman'
    
    document.add_paragraph("\n\n\n\n") # Espaçamento
    p_autor = document.add_paragraph()
    p_autor.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_autor.add_run(autor).font.size = Pt(12)
    p_autor.runs[0].font.name = 'Times New Roman'
    document.add_page_break()

    # Ponto 4: Define estilo do corpo do texto
