# -*- coding: utf-8 -*-
"""
# Editor Pro IA: Publicação Sem Complicações
## Otimizado para GitHub: Um Assistente Completo de Edição, Revisão, Design e Formatação de Livros
Este script Streamlit transforma seu manuscrito em um livro profissional, pronto para ABNT e KDP,
utilizando a inteligência artificial da OpenAI para revisão, marketing e design de capa,
junto com funcionalidades avançadas de diagramação DOCX.

**Principais funcionalidades:**
- **Configuração Inicial**: Definição de título, autor, formato KDP/Gráfica (miolo), template de estilo de texto
- **Manuscrito**: Upload .txt/.docx, edição ao vivo
- **Revisão IA**: ortografia, clareza, tom literário, resumo, sinopse de marketing
- **Capa (brief)**: ideias e diretrizes textuais por IA (sem geração de imagem direta)
- **FastFormat**: microtipografia, aspas, travessões, NBSP, normalizações; diff e aplicação ao manuscrito
- **Exportação**: DOCX com estilos, EPUB/PDF placeholders desativados
"""

import os
import io
import re
import json
import time
import math
import difflib
import requests
import streamlit as st
from io import BytesIO
from typing import Optional, Dict, Any, Tuple, List
import hashlib # <--- NOVA IMPORTAÇÃO AQUI!

# IA
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OpenAI = None
    OPENAI_AVAILABLE = False

# DOCX
try:
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.style import WD_STYLE_TYPE
    DOCX_AVAILABLE = True
except Exception:
    Document = None
    Pt = None
    Inches = None
    WD_ALIGN_PARAGRAPH = None
    WD_STYLE_TYPE = None
    DOCX_AVAILABLE = False

# FastFormat (será fornecido em fastformat.py na próxima etapa)
try:
    from fastformat import FastFormatOptions, apply_fastformat, make_unified_diff, get_fastformat_default_options
    FASTFORMAT_AVAILABLE = True
except Exception as e:
    FASTFORMAT_AVAILABLE = False
    st.error(f"Erro ao carregar o módulo fastformat.py: {e}. Certifique-se de que o arquivo existe e está correto.")
    # Fallback dummies para evitar erros de execução se fastformat.py não estiver presente
    class FastFormatOptions:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    def apply_fastformat(text: str, options: Dict[str, Any]) -> str:
        return text
    def make_unified_diff(a: str, b: str, fromfile: str = "original", tofile: str = "formatado") -> str:
        return "".join(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile=fromfile, tofile=tofile))
    def get_fastformat_default_options():
        return FastFormatOptions(
            quotes_style="curly", dialogue_dash="emdash", number_range_dash="endash",
            normalize_whitespace=True, trim_line_spaces=True, collapse_blank_lines=True,
            ensure_final_newline=True, normalize_ellipsis=True, smart_ptbr_punctuation=True,
            normalize_bullets=True, safe_mode=True
        )


# ------------------------------------------------------------------------------------
# CONSTANTES E PRESETS
# ------------------------------------------------------------------------------------

APP_TITLE = "Editor Pro IA: Publicação Sem Complicações"
APP_SUBTITLE = "Edição, revisão, diagramação e formatação de livros (ABNT e KDP) com IA"

# Tamanhos KDP/Gráfica (Miolo)
KDP_SIZES: Dict[str, Dict[str, float]] = {
    "KDP 6 x 9 in (152 x 229 mm)": {"width_in": 6.0, "height_in": 9.0, "margin_in": 0.75},
    "KDP 5.5 x 8.5 in (140 x 216 mm)": {"width_in": 5.5, "height_in": 8.5, "margin_in": 0.75},
    "KDP 5 x 8 in (127 x 203 mm)": {"width_in": 5.0, "height_in": 8.0, "margin_in": 0.75},
    "KDP 7 x 10 in (178 x 254 mm)": {"width_in": 7.0, "height_in": 10.0, "margin_in": 0.75},
    "A5 148 x 210 mm (~5.83 x 8.27 in)": {"width_in": 5.83, "height_in": 8.27, "margin_in": 0.79},
}
# Templates de estilo (exemplos básicos)
STYLE_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "Romance Clássico (Garamond)": {
        "font_name": "Garamond",
        "font_size_pt": 12,
        "line_spacing": 1.25,
        "space_after_pt": 6,
        "justify": True,
        "first_line_indent_in": 0.25,
    },
    "ABNT Acadêmico (Times New Roman)": {
        "font_name": "Times New Roman",
        "font_size_pt": 12,
        "line_spacing": 1.5,
        "space_after_pt": 0,
        "justify": True,
        "first_line_indent_in": 0.0,
    },
    "Didático Digital (Inter)": {
        "font_name": "Inter",
        "font_size_pt": 11,
        "line_spacing": 1.4,
        "space_after_pt": 4,
        "justify": False,
        "first_line_indent_in": 0.0,
    },
}
# ------------------------------------------------------------------------------------
# FUNÇÕES DE SUPORTE
# ------------------------------------------------------------------------------------

def get_openai_client() -> Optional[Any]:
    if not OPENAI_AVAILABLE:
        return None
    try:
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        client = OpenAI()
        return client
    except Exception:
        return None

def load_text_from_file(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    if name.endswith(".docx"):
        if not DOCX_AVAILABLE:
            st.error("python-docx não está instalado. Instale com: pip install python-docx")
            return ""
        doc = Document(uploaded_file)
        paras = []
        for p in doc.paragraphs:
            paras.append(p.text)
        return "\n".join(paras)
    return ""

def split_paragraphs_preserving(text: str) -> List[str]:
    # Divide por duplas quebras para preservar parágrafos em branco
    parts = re.split(r"\n\s*\n", text.strip(), flags=re.MULTILINE)
    return [p.strip("\n") for p in parts]

def apply_style_to_document(doc: Document, style_key: str):
    if not DOCX_AVAILABLE: return
    tpl = STYLE_TEMPLATES.get(style_key, STYLE_TEMPLATES["Romance Clássico (Garamond)"])
    base_style = doc.styles["Normal"]
    font = base_style.font
    font.name = tpl["font_name"]
    font.size = Pt(tpl["font_size_pt"])
    
    para_format = base_style.paragraph_format
    para_format.line_spacing = tpl["line_spacing"]
    para_format.space_after = Pt(tpl["space_after_pt"])

def set_page_kdp(doc: Document, kdp_key: str):
    if not DOCX_AVAILABLE: return
    cfg = KDP_SIZES.get(kdp_key, KDP_SIZES["KDP 6 x 9 in (152 x 229 mm)"])
    for section in doc.sections:
        section.page_width = Inches(cfg["width_in"])
        section.page_height = Inches(cfg["height_in"])
        mg = cfg["margin_in"]
        section.left_margin = Inches(mg)
        section.right_margin = Inches(mg)
        section.top_margin = Inches(mg)
        section.bottom_margin = Inches(mg)

def add_text_as_paragraphs(doc: Document, text: str, style_key: str):
    if not DOCX_AVAILABLE: return
    tpl = STYLE_TEMPLATES.get(style_key, STYLE_TEMPLATES["Romance Clássico (Garamond)"])
    justify = tpl.get("justify", True)
    first_line_indent_in = tpl.get("first_line_indent_in", 0.0)
    
    paragraphs = split_paragraphs_preserving(text)
    for para_text in paragraphs:
        p = doc.add_paragraph()
        run = p.add_run(para_text)
        if justify:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if first_line_indent_in > 0:
            p.paragraph_format.first_line_indent = Inches(first_line_indent_in)

def build_docx_from_text(text: str, title: str, author: str, style_key: str, kdp_key: str) -> BytesIO:
    if not DOCX_AVAILABLE:
        st.error("python-docx não está instalado. Não é possível gerar DOCX.")
        return BytesIO()

    doc = Document()

    set_page_kdp(doc, kdp_key)
    apply_style_to_document(doc, style_key)

    if title or author:
        h1 = doc.add_paragraph()
        h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = h1.add_run(title if title else "")
        run.bold = True
        run.font.size = Pt(18)
        if author:
            h2 = doc.add_paragraph()
            h2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run2 = h2.add_run(author)
            run2.italic = True
            run2.font.size = Pt(12)
        doc.add_page_break()

    add_text_as_paragraphs(doc, text, style_key)

    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

def ai_transform_text(
    client: Any,
    text: str,
    task: str = "revisao",
    tone: str = "neutro",
    extras: Optional[str] = None,
) -> str:
    if client is None:
        return "Configure sua OPENAI_API_KEY para usar a revisão por IA."
    if not text.strip():
        return "Cole ou carregue seu manuscrito primeiro."

    system_base = (
        "Você é um editor literário brasileiro experiente. "
        "Revise mantendo a voz do autor, aplique português brasileiro, e aponte mudanças relevantes quando solicitado."
    )
    if task == "revisao":
        user = f"Revise ortografia, concordância e pontuação, preservando estilo. Texto:\n\n{text}"
    elif task == "clareza":
        user = f"Reescreva para máxima clareza e fluidez, mantendo o tom {tone}. Texto:\n\n{text}"
    elif task == "tom":
        user = f"Ajuste o tom literário para {tone}, sem perder a voz autoral. Texto:\n\n{text}"
    elif task == "resumo":
        user = f"Resuma o texto em 3 versões: 1 frase, 1 parágrafo e 3 parágrafos. Texto:\n\n{text}"
    elif task == "sinopse":
        user = (
            "Escreva uma sinopse de marketing atraente (120-180 palavras) para a contracapa e Amazon. "
            f"Considere o tom {tone}. Texto-base:\n\n{text}"
        )
    else:
        user = f"Faça uma revisão geral do texto, mantendo o tom {tone}. Texto:\n\n{text}"
    if extras:
        user += f"\n\nInstruções extras do autor: {extras}"

    try:
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_base},
                {"role": "user", "content": user},
            ],
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao chamar o modelo: {e}"

def cover_brief_by_ai(client: Any, title: str, author: str, genre: str, synopsis: str) -> str:
    if client is None:
        return "Configure sua OPENAI_API_KEY para gerar o brief por IA."
    prompt = (
        "Crie um brief de capa para um livro. Inclua: público-alvo, referências visuais, paleta de cores, tipografia sugerida, "
        "elementos-chave e 3 variações de direção de arte (clean, artística e comercial). "
        "Evite clichês e informe restrições KDP (sangria, margens de segurança). "
        f"Título: {title}\nAutor: {author}\nGênero: {genre}\nSinopse:\n{synopsis}\n"
    )
    try:
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Você é um diretor de arte e designer de capas experiente."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao chamar o modelo: {e}"


# ------------------------------------------------------------------------------------
# FASTFORMAT UI SECTION (INTEGRADA AQUI)
# ------------------------------------------------------------------------------------

def fastformat_tab_ui(st_obj, session_state_obj):
    st_obj.header("FastFormat — Normalização e Estilo")
    
    if not FASTFORMAT_AVAILABLE:
        st_obj.info(
            "Módulo fastformat.py não encontrado ou com erros. "
            "Certifique-se de que o arquivo 'fastformat.py' está na mesma pasta que 'app_editor.py' "
            "e que não há erros de sintaxe ou importação nele."
        )
        st_obj.caption("Você pode continuar usando as outras funcionalidades do editor normalmente.")
        return # Sai da função se o módulo não está disponível

    # Estado inicial das opções FastFormat
    if "ff_options" not in session_state_obj:
        session_state_obj["ff_options"] = get_fastformat_default_options()

    opt: FastFormatOptions = session_state_obj["ff_options"]

    col1, col2, col3 = st_obj.columns([1, 1, 1])

    with col1:
        st_obj.markdown("##### Espaços e Quebras")
        opt.normalize_whitespace = st_obj.checkbox("Normalizar múltiplos espaços", value=getattr(opt, "normalize_whitespace", True), help="Remove múltiplos espaços para um, e quebras de linha excessivas.")
        opt.trim_line_spaces = st_obj.checkbox("Remover espaços nas bordas da linha", value=getattr(opt, "trim_line_spaces", True), help="Remove espaços no início e fim de cada linha.")
        opt.collapse_blank_lines = st_obj.checkbox("Compactar linhas em branco", value=getattr(opt, "collapse_blank_lines", True), help="Reduz múltiplas linhas em branco para, no máximo, uma.")
        opt.ensure_final_newline = st_obj.checkbox("Garantir quebra de linha final", value=getattr(opt, "ensure_final_newline", True), help="Adiciona uma quebra de linha no final do texto se ausente.")
    with col2:
        st_obj.markdown("##### Pontuação e Tipografia")
        # CORREÇÃO AQUI: String literal da format_func estava incorreta.
        opt.quotes_style = st_obj.radio(
            "Estilo de aspas",
            options=["curly", "straight"],
            index=0 if getattr(opt, "quotes_style", "curly") == "curly" else 1,
            format_func=lambda x: "Tipográficas (“ ” e ‘ ’)" if x == "curly" else 'Retas (" e \')', # CORRIGIDO
            horizontal=True,
            key="ff_quotes_style_radio"
        )
        
        opt.dialogue_dash = st_obj.radio(
            "Diálogo (início de fala)",
            options=["emdash", "hyphen"],
            index=0 if getattr(opt, "dialogue_dash", "emdash") == "emdash" else 1,
            format_func=lambda x: "Travessão (—)" if x == "emdash" else "Hífen (-)",
            horizontal=True,
            key="ff_dialogue_dash_radio"
        )
        opt.number_range_dash = st_obj.radio(
            "Intervalos numéricos (10–20)",
            options=["endash", "hyphen"],
            index=0 if getattr(opt, "number_range_dash", "endash") == "endash" else 1,
            format_func=lambda x: "En dash (–)" if x == "endash" else "Hífen (-)",
            horizontal=True,
            key="ff_number_range_dash_radio"
        )
        opt.normalize_ellipsis = st_obj.checkbox("Normalizar reticências (...) para (…) ", value=getattr(opt, "normalize_ellipsis", True), help="Substitui três pontos por um caractere de reticências único.")

    with col3:
        st_obj.markdown("##### Outras Regras")
        opt.normalize_bullets = st_obj.checkbox("Normalizar bullets (- ou *) para (•)", value=getattr(opt, "normalize_bullets", True))
        opt.smart_ptbr_punctuation = st_obj.checkbox("Ajustes leves PT-BR", value=getattr(opt, "smart_ptbr_punctuation", True), help="Ajustes em espaços de pontuação específicos do português brasileiro.")
        opt.safe_mode = st_obj.checkbox("Modo seguro (evita agressividade)", value=getattr(opt, "safe_mode", True), help="Evita transformações que podem alterar muito o conteúdo em casos específicos.")
    
    st_obj.markdown("---")

    texto_base = session_state_obj.get("texto_principal", "") or ""
    
    if not texto_base.strip():
        st_obj.warning("Cole ou carregue um texto na aba 'Manuscrito' para aplicar o FastFormat.")
        return # Sai da função se não houver texto
    
    texto_formatado_preview = apply_fastformat(texto_base, opt)

    # Ações
    st_obj.markdown("##### Ações")
    col_actions_1, col_actions_2, col_actions_3, col_actions_4 = st_obj.columns([1,1,1,1])
    
    with col_actions_1:
        show_diff = st_obj.button("Pré-visualizar diff", key="ff_show_diff_btn")
    with col_actions_2:
        apply_now = st_obj.button("Aplicar ao texto principal", key="ff_apply_btn", type="primary")
    with col_actions_3:
        dl_txt = st_obj.button("Baixar .txt formatado", key="ff_dl_txt_btn")
    with col_actions_4:
        dl_docx = st_obj.button("Baixar .docx formatado", key="ff_dl_docx_btn")

    # Visualização de diff
    if show_diff:
        diff = make_unified_diff(texto_base, texto_formatado_preview, fromfile="manuscrito.txt", tofile="manuscrito_fastformat.txt")
        if not diff.strip():
            st_obj.success("Nenhuma diferença encontrada. O texto já está normalizado conforme as opções.")
        else:
            st_obj.caption("Diff unificado (formato patch):")
            st_obj.code(diff, language="diff")
            st_obj.info("Linhas verdes (+) foram adicionadas, vermelhas (-) foram removidas.")
    else:
        col_preview_1, col_preview_2 = st_obj.columns(2)
        with col_preview_1:
            st_obj.markdown("Original")
            st_obj.text_area("Texto original", value=texto_base, height=300, key="ff_original_textarea", disabled=True)
        with col_preview_2:
            st_obj.markdown("Prévia (FastFormat)")
            st_obj.text_area("Texto formatado (prévia)", value=texto_formatado_preview, height=300, key="ff_formatado_preview_textarea", disabled=True)

    # Aplicar ao texto principal
    if apply_now:
        session_state_obj["texto_principal"] = texto_formatado_preview
        st_obj.success("FastFormat aplicado ao texto principal. Acesse a aba 'Manuscrito' para ver o resultado.")
        
    # Downloads
    if dl_txt:
        st_obj.download_button(
            label="Baixar TXT",
            data=texto_formatado_preview.encode("utf-8"),
            file_name="manuscrito_fastformat.txt",
            mime="text/plain",
            use_container_width=True,
            key="ff_download_txt"
        )
    if dl_docx:
        if DOCX_AVAILABLE:
            doc_fastformat_bytes = build_docx_from_text(
                texto_formatado_preview,
                session_state_obj.get("book_title", "Livro sem título"),
                session_state_obj.get("book_author", "Autor desconhecido"),
                session_state_obj.get("style_option", "Romance Clássico (Garamond)"), # Usa o estilo selecionado na config inicial
                session_state_obj.get("kdp_size_key", "KDP 6 x 9 in (152 x 229 mm)")
            )
            st_obj.download_button(
                label="Baixar DOCX",
                data=doc_fastformat_bytes,
                file_name=f"manuscrito_fastformat_{session_state_obj.get('book_title', 'sem_titulo')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key="ff_download_docx"
            )
        else:
            st_obj.error("python-docx não está instalado. Não é possível gerar DOCX.")


# ------------------------------------------------------------------------------------
# LAYOUT E INTERFACE
# ------------------------------------------------------------------------------------

st.set_page_config(page_title=APP_TITLE, layout="wide")

def init_session():
    st.session_state.setdefault("book_title", "")
    st.session_state.setdefault("book_author", "")
    st.session_state.setdefault("kdp_size_key", "KDP 6 x 9 in (152 x 229 mm)")
    st.session_state.setdefault("style_option", "Romance Clássico (Garamond)")
    st.session_state.setdefault("texto_principal", "")
    st.session_state.setdefault("genre_brief", "Ficção Científica")
    st.session_state.setdefault("synopsis_brief", "")

def sidebar_config():
    st.sidebar.header("Configuração Inicial")
    st.sidebar.text("Defina informações do livro e preferências do miolo.")

    st.session_state["book_title"] = st.sidebar.text_input("Título do livro", value=st.session_state.get("book_title", ""))
    st.session_state["book_author"] = st.sidebar.text_input("Autor(a)", value=st.session_state.get("book_author", ""))

    # Tamanho KDP
    kdp_keys = list(KDP_SIZES.keys())
    cur_kdp = st.session_state.get("kdp_size_key", kdp_keys[0])
    st.session_state["kdp_size_key"] = st.sidebar.selectbox(
        "Formato do miolo (KDP/Gráfica)",
        options=kdp_keys,
        index=kdp_keys.index(cur_kdp) if cur_kdp in kdp_keys else 0,
        key="kdp_size_select"
    )

    # Template de Estilo (CORREÇÃO AQUI)
    style_keys = list(STYLE_TEMPLATES.keys())
    current_style_key = st.session_state.get("style_option", style_keys[0])
    st.session_state["style_option"] = st.sidebar.selectbox(
        "Template de Estilo",
        options=style_keys,
        index=style_keys.index(current_style_key) if current_style_key in style_keys else 0,
        key="style_option_select",
        help="Selecione um template de diagramação tipográfica base"
    )

    st.sidebar.divider()
    st.sidebar.caption("Dica: você pode alternar o template de estilo e formato KDP a qualquer momento.")

def tab_manuscript():
    st.subheader("Manuscrito")
    st.write("Carregue seu arquivo ou cole o texto para começar a editar.")

    upload_message_placeholder = st.empty()

    uploaded_file = st.file_uploader(
        "Selecione seu arquivo (.txt ou .docx) aqui:",
        type=["txt", "docx"],
        key="file_uploader_main"
    )

    if uploaded_file is not None:
        try:
            # IMPORTANT: sempre seek(0) antes de ler para garantir que o cursor está no início
            # getvalue() consome o stream, então resetamos antes de passar para load_text_from_file
            uploaded_file.seek(0) 
            file_content_bytes = uploaded_file.getvalue()
            current_file_hash = hashlib.md5(file_content_bytes).hexdigest()

            # Verifica se este arquivo (pelo seu hash de conteúdo) já foi processado nesta sessão
            if st.session_state.get("last_processed_file_hash") != current_file_hash:
                # Processa o arquivo
                uploaded_file.seek(0) # Reset stream position again before loading content
                file_content = load_text_from_file(uploaded_file)
                st.session_state["texto_principal"] = file_content
                st.session_state["last_processed_file_hash"] = current_file_hash # Armazena o hash após o sucesso
                upload_message_placeholder.success("✅ Arquivo carregado com sucesso! O texto está no editor abaixo.")
            else:
                upload_message_placeholder.info("Arquivo já processado. Edite o texto ou carregue um novo.")

        except Exception as e:
            upload_message_placeholder.error(f"❌ Erro ao ler o arquivo: {e}")
            st.session_state["texto_principal"] = "" # Limpa o texto em caso de erro
            # Também limpa o hash na session state para que uma nova tentativa de upload possa ser feita
            if "last_processed_file_hash" in st.session_state:
                del st.session_state["last_processed_file_hash"]
    else: # uploaded_file is None, significando que nenhum arquivo está no uploader ou foi limpo
        # Limpa as informações de rastreamento quando o uploader está vazio
        if "last_processed_file_hash" in st.session_state:
            del st.session_state["last_processed_file_hash"]
        upload_message_placeholder.empty() # Remove a mensagem de status quando nenhum arquivo está presente

    # Botão para limpar o texto
    if st.button("Limpar todo o texto do editor", key="manuscript_clear_text_btn"):
        st.session_state["texto_principal"] = ""
        # Limpa qualquer hash/id de arquivo armazenado para garantir que o próximo upload seja tratado como novo
        if "last_processed_file_hash" in st.session_state:
            del st.session_state["last_processed_file_hash"]
        upload_message_placeholder.info("Editor de texto limpo.")
        # st.rerun() # Pode ser útil para resetar o widget do uploader visualmente, mas pode causar recargas indesejadas.

    # Área de texto principal
    texto_atual_no_editor = st.text_area(
        "Editor de texto (edite ou visualize o texto carregado)",
        value=st.session_state.get("texto_principal", ""),
        height=400,
        key="editor_textarea",
    )
    
    # Se o usuário editar o texto diretamente na área, atualizamos o session_state
    if texto_atual_no_editor != st.session_state.get("texto_principal", ""):
        st.session_state["texto_principal"] = texto_atual_no_editor


def tab_ai_review():
    st.subheader("Revisão por IA")
    st.write("Selecione o tipo de revisão e aplique ao texto. É necessário configurar a OPENAI_API_KEY.")
    client = get_openai_client()
    if client is None:
        st.warning("IA não disponível. Verifique se 'openai' está instalado e OPENAI_API_KEY configurada.")
        return

    tone = st.selectbox("Tom desejado", ["neutro", "poético", "informal", "acadêmico"], key="ai_review_tone")
    extras = st.text_input("Instruções adicionais (opcional)", key="ai_review_extras")

    tipo = st.radio(
        "Tipo de tarefa",
        options=[
            ("revisao", "Ortografia"),
            ("clareza", "Clareza"),
            ("tom", "Tom literário"),
            ("resumo", "Resumo"),
            ("sinopse", "Sinopse (marketing)"),
        ],
        index=0,
        format_func=lambda x: x[1],
        horizontal=True,
        key="ai_review_task_type"
    )
    if isinstance(tipo, tuple):
        tipo = tipo[0]
    
    if st.button("Executar IA", key="ai_review_execute_btn"):
        with st.spinner("Gerando..."):
            result = ai_transform_text(
                client=client,
                text=st.session_state.get("texto_principal", ""),
                task=tipo,
                tone=tone,
                extras=extras,
            )
            st.text_area(f"Resultado da IA ({tipo})", value=result, height=300, key=f"ai_review_result_{tipo}")
            if tipo != "resumo" and tipo != "sinopse":
                if st.button("Aplicar ao texto principal", key=f"ai_review_apply_{tipo}_btn"):
                    st.session_state["texto_principal"] = result
                    st.success("Resultado da IA aplicado ao manuscrito.")

def tab_cover_brief():
    st.subheader("Brief de Capa por IA")
    st.write("Gere um brief detalhado para designers de capa, usando IA.")
    client = get_openai_client()
    if client is None:
        st.warning("IA não disponível. Verifique se 'openai' está instalado e OPENAI_API_KEY configurada.")
        return

    title = st.text_input("Título do Livro (para o brief)", value=st.session_state.get("book_title", ""), key="cover_brief_title")
    author = st.text_input("Autor (para o brief)", value=st.session_state.get("book_author", ""), key="cover_brief_author")
    genre = st.text_input("Gênero do Livro", value=st.session_state.get("genre_brief", ""), key="cover_brief_genre")
    synopsis = st.text_area("Sinopse ou resumo (para o brief)", value=st.session_state.get("synopsis_brief", ""), height=150, key="cover_brief_synopsis")

    if st.button("Gerar Brief de Capa", key="cover_brief_generate_btn"):
        with st.spinner("Gerando brief..."):
            brief = cover_brief_by_ai(client, title, author, genre, synopsis)
            st.text_area("Brief de Capa Gerado", value=brief, height=400, key="cover_brief_result")

def tab_export():
    st.subheader("Exportar Manuscrito")
    st.write("Exporte seu manuscrito em diferentes formatos, com base nas configurações.")

    texto_final = st.session_state.get("texto_principal", "")
    current_title = st.session_state.get("book_title", "Livro sem título")
    current_author = st.session_state.get("book_author", "Autor desconhecido")
    current_style = st.session_state.get("style_option", "Romance Clássico (Garamond)")
    current_kdp_size = st.session_state.get("kdp_size_key", "KDP 6 x 9 in (152 x 229 mm)")

    if not texto_final.strip():
        st.warning("Nenhum texto no manuscrito para exportar. Acesse a aba 'Manuscrito' ou 'FastFormat'.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### DOCX (Word)")
        if DOCX_AVAILABLE:
            if st.button("Gerar DOCX", key="export_docx_btn"):
                docx_file = build_docx_from_text(texto_final, current_title, current_author, current_style, current_kdp_size)
                st.download_button(
                    label="⬇️ Baixar DOCX",
                    data=docx_file,
                    file_name=f"{current_title.replace(' ', '_').lower()}_by_{current_author.replace(' ', '_').lower()}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="download_docx_btn"
                )
        else:
            st.info("Instale 'python-docx' para exportar em DOCX.")

    with col2:
        st.markdown("##### EPUB (eBook)")
        st.download_button(
            label="❌ Gerar EPUB (Em Desenvolvimento)",
            data="Em breve!",
            file_name=f"{current_title.replace(' ', '_').lower()}.epub",
            mime="application/epub+zip",
            disabled=True,
            key="download_epub_btn"
        )

    with col3:
        st.markdown("##### PDF (para Impressão)")
        st.download_button(
            label="❌ Gerar PDF (Em Desenvolvimento)",
            data="Em breve!",
            file_name=f"{current_title.replace(' ', '_').lower()}_print.pdf",
            mime="application/pdf",
            disabled=True,
            key="download_pdf_btn"
        )


# --- INICIALIZAÇÃO E LAYOUT PRINCIPAL ---
init_session()
sidebar_config()

st.title(APP_TITLE)
st.markdown(APP_SUBTITLE)

# Abas do aplicativo (com a nova aba FastFormat)
# CORREÇÃO AQUI: Renomeando as variáveis dos objetos das abas para evitar conflito com as funções
_tab_manuscript, _tab_ai_review, _tab_cover_brief, _tab_fastformat, _tab_export = st.tabs(
    ["Manuscrito", "Revisão IA", "Brief Capa", "FastFormat", "Exportar"]
)

with _tab_manuscript: # Usando o novo nome da variável da aba
    tab_manuscript() # Chamando a FUNÇÃO que contém o conteúdo da aba Manuscrito

with _tab_ai_review: # Usando o novo nome da variável da aba
    tab_ai_review() # Chamando a FUNÇÃO que contém o conteúdo da aba Revisão IA

with _tab_cover_brief: # Usando o novo nome da variável da aba
    tab_cover_brief() # Chamando a FUNÇÃO que contém o conteúdo da aba Brief Capa

with _tab_fastformat: # Este já estava correto, chamando fastformat_tab_ui
    fastformat_tab_ui(st, st.session_state)

with _tab_export: # Usando o novo nome da variável da aba
    tab_export() # Chamando a FUNÇÃO que contém o conteúdo da aba Exportar
