# -*- coding: utf-8 -*-
"""
Editor Pro IA: Publicação Sem Complicações
Otimizado para GitHub: Um Assistente Completo de Edição, Revisão, Design e Formatação de Livros

- Configuração Inicial: Título, autor, formato KDP/Gráfica (miolo), template de estilo de texto
- Manuscrito: Upload .txt/.docx, edição ao vivo
- Revisão IA: ortografia, clareza, tom literário, resumo, sinopse de marketing
- Capa (brief): ideias e diretrizes textuais por IA (sem geração de imagem direta)
- Exportação: DOCX com estilos, EPUB/PDF placeholders desativados (como no código antigo)
- FastFormat: microtipografia, aspas, travessões, NBSP, normalizações; diff e aplicação ao manuscrito
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

# IA
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# DOCX
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

# FastFormat (será fornecido em fastformat.py na próxima etapa)
# Se ainda não existir, o app exibirá um aviso na seção correspondente.
try:
    from fastformat import FastFormatOptions, apply_fastformat, make_unified_diff, default_options
    FASTFORMAT_AVAILABLE = True
except Exception:
    FASTFORMAT_AVAILABLE = False
    FastFormatOptions = Any
    def apply_fastformat(text: str, options: Dict[str, Any]) -> str:
        return text
    def make_unified_diff(a: str, b: str, fromfile: str = "original", tofile: str = "formatado") -> str:
        return "".join(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile=fromfile, tofile=tofile))
    default_options = {
        "aspas": "pt_curly",
        "travessao": "mdash",
        "normalize_spaces": True,
        "nbsp_abreviacoes": True,
        "nbsp_numeros_unidades": True,
        "reticencias": True,
        "hifens_range": True,
        "pontuacao_espacos": True,
        "linhas_brancas_excesso": True,
        "limpar_espacos_finais": True,
    }

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
    if OpenAI is None:
        return None
    try:
        # Usa variável de ambiente OPENAI_API_KEY ou st.secrets["OPENAI_API_KEY"]
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
    tpl = STYLE_TEMPLATES.get(style_key, STYLE_TEMPLATES["Romance Clássico (Garamond)"])
    base_style = doc.styles["Normal"]
    font = base_style.font
    font.name = tpl["font_name"]
    font.size = Pt(tpl["font_size_pt"])

    # Ajusta parágrafo normal
    para_format = base_style.paragraph_format
    para_format.line_spacing = tpl["line_spacing"]
    para_format.space_after = Pt(tpl["space_after_pt"])

def set_page_kdp(doc: Document, kdp_key: str):
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
    doc = Document()

    # Configura página
    set_page_kdp(doc, kdp_key)
    # Aplica estilo base
    apply_style_to_document(doc, style_key)

    # Capa interna
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

    # Miolo
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

    # Prompts de sistema e usuário
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
        # Modelos recomendados (ajuste conforme necessário)
        # Exemplos: "gpt-4o-mini", "gpt-4o"
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
# FASTFORMAT UI SECTION
# ------------------------------------------------------------------------------------

def fastformat_section(texto_existente: str) -> str:
    st.markdown("### FastFormat")
    if not FASTFORMAT_AVAILABLE:
        st.info(
            "Módulo fastformat não encontrado. Após você adicionar o arquivo fastformat.py ao repositório, "
            "esta seção habilitará as transformações de microtipografia, aspas e travessões com diff."
        )
        return texto_existente

    # Estado inicial das opções
    if "fastformat_options" not in st.session_state:
        st.session_state["fastformat_options"] = dict(default_options)

    opts = st.session_state["fastformat_options"]

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        aspas = st.radio(
            "Estilo de aspas",
            options=[
                ("pt_curly", "Português (“ ”)"),
                ("en_curly", "Inglês (“ ”)"),
                ("single_curly", "Simples (‘ ’)"),
                ("straight", 'Retas (")'),
            ],
            index=["pt_curly", "en_curly", "single_curly", "straight"].index(opts.get("aspas", "pt_curly")),
            format_func=lambda x: x[1] if isinstance(x, tuple) else x,
        )
        if isinstance(aspas, tuple):
            aspas = aspas[0]
        opts["aspas"] = aspas

    with col2:
        trav = st.radio(
            "Travessão/hífen",
            options=[("mdash", "Travessão —"), ("ndash", "Meia-risca –"), ("hyphen", "Hífen -")],
            index=["mdash", "ndash", "hyphen"].index(opts.get("travessao", "mdash")),
            format_func=lambda x: x[1] if isinstance(x, tuple) else x,
        )
        if isinstance(trav, tuple):
            trav = trav[0]
        opts["travessao"] = trav

    with col3:
        st.markdown("Correções automáticas")
        opts["normalize_spaces"] = st.checkbox("Normalizar múltiplos espaços e quebras", value=opts.get("normalize_spaces", True))
        opts["nbsp_abreviacoes"] = st.checkbox("NBSP em abreviações (Sr., Dra., Prof.)", value=opts.get("nbsp_abreviacoes", True))
        opts["nbsp_numeros_unidades"] = st.checkbox("NBSP em números + unidade (10 km)", value=opts.get("nbsp_numeros_unidades", True))
        opts["reticencias"] = st.checkbox("Reticências (…) em vez de ...", value=opts.get("reticencias", True))
        opts["hifens_range"] = st.checkbox("Meia-risca (–) em intervalos numéricos", value=opts.get("hifens_range", True))
        opts["pontuacao_espacos"] = st.checkbox("Ajustar espaços antes/depois de pontuação", value=opts.get("pontuacao_espacos", True))
        opts["linhas_brancas_excesso"] = st.checkbox("Reduzir excesso de linhas em branco", value=opts.get("linhas_brancas_excesso", True))
        opts["limpar_espacos_finais"] = st.checkbox("Remover espaços ao fim da linha", value=opts.get("limpar_espacos_finais", True))

    st.divider()
    if not texto_existente.strip():
        st.warning("Cole ou carregue um texto no manuscrito para aplicar o FastFormat.")
        return texto_existente

    texto_formatado = apply_fastformat(texto_existente, opts)

    # Visualização/diff
    show_diff = st.toggle("Mostrar diff unificado", value=False)
    if show_diff:
        diff = make_unified_diff(texto_existente, texto_formatado, fromfile="manuscrito.txt", tofile="manuscrito_fastformat.txt")
        st.code(diff, language="diff")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("Original")
            st.text_area("Texto original", value=texto_existente, height=280, key="ff_original_textarea")
        with col_b:
            st.markdown("Prévia (FastFormat)")
            st.text_area("Texto formatado (prévia)", value=texto_formatado, height=280, key="ff_formatado_textarea")

    col_apply1, col_apply2 = st.columns([1, 4])
    with col_apply1:
        aplicar = st.button("Aplicar ao manuscrito")
    with col_apply2:
        st.caption("Dica: use o diff para revisar as mudanças antes de aplicar.")

    if aplicar:
        st.success("FastFormat aplicado ao manuscrito.")
        return texto_formatado

    return texto_existente

# ------------------------------------------------------------------------------------
# LAYOUT E INTERFACE
# ------------------------------------------------------------------------------------

def init_session():
    st.session_state.setdefault("book_title", "")
    st.session_state.setdefault("book_author", "")
    st.session_state.setdefault("kdp_size_key", "KDP 6 x 9 in (152 x 229 mm)")
    st.session_state.setdefault("style_option", "Romance Clássico (Garamond)")
    st.session_state.setdefault("texto_principal", "")

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
    )

    # Template de Estilo (corrigido — sem string truncada)
    style_keys = list(STYLE_TEMPLATES.keys())
    current_style_key = st.session_state.get("style_option", style_keys[0])
    st.session_state["style_option"] = st.sidebar.selectbox(
        "Template de Estilo",
        options=style_keys,
        index=style_keys.index(current_style_key) if current_style_key in style_keys else 0,
    )

    st.sidebar.divider()
    st.sidebar.caption("Dica: você pode alternar o template de estilo e formato KDP a qualquer momento.")

def tab_manuscript():
    st.subheader("Manuscrito")
    st.write("Carregue seu arquivo ou cole o texto para começar a editar.")

    uploaded = st.file_uploader("Carregar arquivo (.txt ou .docx)", type=["txt", "docx"])
    colu1, colu2, colu3 = st.columns([1, 1, 4])

    with colu1:
        if st.button("Ler arquivo"):
            if uploaded:
                st.session_state["texto_principal"] = load_text_from_file(uploaded)
                st.success("Arquivo carregado e texto inserido no editor.")
            else:
                st.warning("Selecione um arquivo primeiro.")

    with colu2:
        if st.button("Limpar texto"):
            st.session_state["texto_principal"] = ""
            st.info("Texto limpo.")

    texto_atual = st.text_area(
        "Editor de texto",
        value=st.session_state.get("texto_principal", ""),
        height=400,
        key="editor_textarea",
    )
    if texto_atual != st.session_state.get("texto_principal", ""):
        st.session_state["texto_principal"] = texto_atual

def tab_ai_review():
    st.subheader("Revisão por IA")
    st.write("Selecione o tipo de revisão e aplique ao texto. É necessário configurar a OPENAI_API_KEY.")

    client = get_openai_client()
    tone = st.selectbox("Tom desejado", ["neutro", "poético", "informal", "acadêmico"])
    extras = st.text_input("Instruções adicionais (opcional)")

    col1, col2, col3, col4, col5 = st.columns(5)
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
    )
    if isinstance(tipo, tuple):
        tipo = tipo[0]

    if st.button("Executar IA"):
        with st.spinner("Gerando..."):
            result = ai_transform_text(
                client=
