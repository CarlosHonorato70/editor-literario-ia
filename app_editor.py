import streamlit as st
import io
import time
import re # <-- NOVA IMPORTAÇÃO para expressões regulares
import smartypants # <-- NOVA IMPORTAÇÃO para tipografia inteligente
from docx import Document
from openai import OpenAI

# --- Configurações da Página Streamlit ---
st.set_page_config(
    page_title="Adapta ONE: Editor Literário IA",
    page_icon="✍️",
    layout="wide"
)

# --- Funções de Lógica ---

def analisar_texto(texto: str):
    # (Função de análise permanece a mesma)
    if not texto: return None
    palavras = texto.split()
    num_palavras = len(palavras)
    return {
        "Contagem de Palavras": num_palavras,
        "Contagem de Caracteres": len(texto),
        "Tempo Estimado de Leitura": f"{math.ceil(num_palavras / 225)} min"
    }

def gerar_resumo_ia(texto: str):
    # (Função de resumo permanece a mesma)
    if not texto: return "Erro: Não há texto para resumir."
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente de escrita..."},
                {"role": "user", "content": f"Por favor, gere um resumo de um parágrafo para o seguinte trecho:\n\n{texto}"}
            ],
            temperature=0.7, max_tokens=250
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Ocorreu um erro ao conectar com a IA: {e}")
        return "Não foi possível gerar o resumo."

# <-- NOVA FUNÇÃO AQUI: Implementa a formatação de texto (Fase 1) -->
def formatar_manuscrito_texto(texto: str) -> str:
    """
    Aplica regras de micro-tipografia e limpeza ao texto, similar ao FastFormat.
    """
    if not texto:
        return ""

    # 1. Normalizar quebras de linha (evita problemas com Windows/Mac/Linux)
    texto = texto.replace('\r\n', '\n').replace('\r', '\n')

    # 2. Corrigir espaços múltiplos entre palavras, mas preservar parágrafos
    # Primeiro, remove espaços no início/fim de cada linha
    linhas = [linha.strip() for linha in texto.split('\n')]
    # Junta as linhas e depois usa regex para corrigir espaços múltiplos
    texto = '\n'.join(linhas)
    texto = re.sub(r' +', ' ', texto)

    # 3. Usar smartypants para aspas curvas e travessões corretos
    #    '“...”' em vez de '"..."'
    #    '‘...’' em vez de "'...'"
    #    '—' (em-dash) para '--' e '---'
    #    '…' (ellipsis) para '...'
    texto = smartypants.smartypants(texto)

    # 4. Regra específica para diálogos: transformar hífen no início de parágrafo em travessão
    #    Usa regex com a flag MULTILINE para encontrar '-' no início de cada linha
    texto = re.sub(r'^\s*-\s+', '— ', texto, flags=re.MULTILINE)

    # 5. Garantir que parágrafos sejam separados por uma única linha em branco
    texto = re.sub(r'\n{3,}', '\n\n', texto)

    return texto.strip()

# --- Barra Lateral (permanece a mesma) ---
st.sidebar.title("Configuração Inicial")
# ... (código da barra lateral) ...

# --- Conteúdo Principal ---
st.title("Adapta ONE: Editor Literário IA")

tab1, tab2 = st.tabs(["Manuscrito", "Exportar"])

with tab1:
    st.subheader("Selecione seu arquivo (.txt ou .docx) aqui:")
    uploaded_file = st.file_uploader("Arraste e solte o arquivo", type=["txt", "docx"])

    # Inicialização do estado da sessão
    if 'text_content' not in st.session_state: st.session_state.text_content = ""
    # ... (outras inicializações de estado) ...

    # Lógica de upload (permanece a mesma)
    if uploaded_file is not None:
        # ... (código de upload e processamento do arquivo) ...
        pass

    # Seção de exibição do conteúdo e ferramentas
    if st.session_state.get('file_processed') and st.session_state.get('text_content'):
        st.write("---")
        st.subheader("Conteúdo do Manuscrito:")
        edited_text = st.text_area("Edite seu texto aqui:", st.session_state.text_content, height=500, key="editor")
        if edited_text != st.session_state.text_content:
            st.session_state.text_content = edited_text
        
        st.write("---")
        st.subheader("Ferramentas de Edição:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Analisar Texto"):
                # ... (código de análise) ...
                pass
        with col2:
            # <-- LÓGICA DO BOTÃO "FORMATAR" ATUALIZADA -->
            if st.button("Formatar Manuscrito", help="Aplica regras de tipografia e limpeza ao texto."):
                with st.spinner("Aplicando formatação profissional..."):
                    texto_original = st.session_state.text_content
                    texto_formatado = formatar_manuscrito_texto(texto_original)
                    
                    # Atualiza o editor apenas se houver mudanças
                    if texto_formatado != texto_original:
                        st.session_state.text_content = texto_formatado
                        st.success("Manuscrito formatado com sucesso!")
                        # Força o rerender para o text_area atualizar imediatamente
                        st.experimental_rerun()
                    else:
                        st.info("O texto já estava bem formatado. Nenhuma mudança necessária.")

        # Seção de resumo com IA
        st.write("---")
        st.subheader("Resumo com Inteligência Artificial")
        # ... (código de resumo) ...
        pass

    elif not st.session_state.get('text_content'):
        st.info("Aguardando o carregamento de um arquivo para começar.")


with tab2:
    st.write("Funcionalidade de Exportação aqui.")
