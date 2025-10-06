import os
import streamlit as st
from openai import OpenAI
from docx import Document
from io import BytesIO
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from concurrent.futures import ThreadPoolExecutor, as_completed
from stqdm import stqdm
import pathlib
import json
import time

# ---------- CONSTANTES ----------
KDP_SIZES = {
    "Padrão EUA (6x9 in)": {"name": "6 x 9 in", "width_in": 6.0, "height_in": 9.0, "width_cm": 15.24, "height_cm": 22.86, "papel_fator": 0.00115},
    "Padrão A5 (5.83x8.27 in)": {"name": "A5 (14.8 x 21 cm)", "width_in": 5.83, "height_in": 8.27, "width_cm": 14.8, "height_cm": 21.0, "papel_fator": 0.00115},
    "Pocket (5x8 in)": {"name": "5 x 8 in", "width_in": 5.0, "height_in": 8.0, "width_cm": 12.7, "height_cm": 20.32, "papel_fator": 0.00115},
    "Maior (7x10 in)": {"name": "7 x 10 in", "width_in": 7.0, "height_in": 10.0, "width_cm": 17.78, "height_cm": 25.4, "papel_fator": 0.00115},
}

STYLE_TEMPLATES = {
    "Romance Clássico (Garamond)": {"font_name": "Garamond", "font_size_pt": 11, "line_spacing": 1.15, "indent": 0.5},
    "Thriller Moderno (Droid Serif)": {"font_name": "Droid Serif", "font_size_pt": 10, "line_spacing": 1.05, "indent": 0.3},
    "Acadêmico/ABNT (Times New Roman 12)": {"font_name": "Times New Roman", "font_size_pt": 12, "line_spacing": 1.5, "indent": 0.0},
}

API_KEY_NAME    = "OPENAI_API_KEY"
PROJECT_ID_NAME = "OPENAI_PROJECT_ID"
MODEL_NAME      = "gpt-4o-mini"

# ---------- LEITURA SEGURA DA CHAVE ----------
def get_secret(key: str) -> str:
    """Tenta st.secrets (Cloud) ou variável de ambiente (local)."""
    try:
        return st.secrets[key]
    except (FileNotFoundError, KeyError):
        return os.getenv(key, "")

API_KEY    = get_secret(API_KEY_NAME)
PROJECT_ID = get_secret(PROJECT_ID_NAME)
client     = OpenAI(api_key=API_KEY, project=PROJECT_ID) if API_KEY else None
is_api_ready = bool(client)

# ---------- FUNÇÕES DA OPENAI ----------
def call_openai(system: str, user: str, max_tokens: int = 2000) -> str:
    if not is_api_ready:
        return "[ERRO] Chave OpenAI não configurada."
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user}],
            temperature=0.7,
            max_tokens=max_tokens
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERRO] {e}"

def gerar_copyright(titulo: str, autor: str, ano: int, amostra: str) -> str:
    sys = "Você é um editor. Gere apenas a página de copyright e créditos."
    usr = f"Título: {titulo} | Autor: {autor} | Ano: {ano} | Texto: {amostra[:3000]}"
    return call_openai(sys, usr, 600)

def gerar_biografia(titulo: str, autor: str, amostra: str) -> str:
    sys = "Você é um editor. Escreva uma bio do autor (2-3 parágrafos)."
    usr = f"Título: {titulo} | Autor: {autor} | Texto: {amostra[:3000]}"
    return call_openai(sys, usr, 500)

def gerar_blurb(titulo: str, autor: str, amostra: str) -> str:
    sys = "Você é copywriter de best-sellers. Crie um blurb de 3-4 parágrafos."
    usr = f"Título: {titulo} | Autor: {autor} | Texto: {amostra[:5000]}"
    return call_openai(sys, usr, 800)

def gerar_relatorio_estrutural(amostra: str) -> str:
    sys = "Você é editor-chefe. Faça um relatório curto: ritmo, personagens, estrutura."
    usr = f"Texto: {amostra[:15000]}"
    return call_openai(sys, usr, 1000)

def gerar_capa_dalle(prompt_visual: str, titulo: str, autor: str, blurb: str, largura_cm: float, altura_cm: float, espessura_cm: float) -> str:
    if not is_api_ready:
        return "[ERRO] Chave DALL-E inativa."
    full_prompt = f"""
    Capa completa (frente, lombada, verso) {largura_cm} cm x {altura_cm} cm, lombada {espessura_cm} cm.
    Estilo: {prompt_visual}
    1. Frente: título '{titulo}' e autor '{autor}'
    2. Lombada: título e autor legíveis
    3. Verso: blurb "{blurb[:400]}..."
    """
    try:
        resp = client.images.generate(model="dall-e-3", prompt=full_prompt,
                                      size="1792x1024", quality="hd", n=1)
        return resp.data[0].url
    except Exception as e:
        return f"[ERRO] {e}"

# ---------- FUNÇÕES DOCX ----------
def adicionar_pagina_rosto(doc: Document, titulo: str, autor: str, estilo: dict):
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(titulo)
    run.bold, run.font.size, run.font.name = True, Pt(24), estilo["font_name"]
    for _ in range(5): doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(autor)
    run.font.size, run.font.name = Pt(16), estilo["font_name"]
    doc.add_page_break()

def adicionar_pagina_generica(doc: Document, titulo: str, subtitulo: str = None):
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(titulo)
    run.bold, run.font.size = True, Pt(18)
    if subtitulo:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(subtitulo)
        run.italic, run.font.size = True, Pt(12)
    doc.add_paragraph()
    doc.add_page_break()

# ---------- PROCESSAMENTO DO MIOLO ----------
def processar_miolo(uploaded_file, formato, estilo, incluir_abnt):
    doc_orig = Document(uploaded_file)
    doc_rev  = Document()

    # layout
    sec = doc_rev.sections[0]
    sec.page_width  = Inches(formato["width_in"])
    sec.page_height = Inches(formato["height_in"])
    sec.left_margin, sec.right_margin = Inches(1.0), Inches(0.6)
    sec.top_margin, sec.bottom_margin = Inches(0.8), Inches(0.8)

    # estilo
    style = doc_rev.styles["Normal"]
    style.font.name = estilo["font_name"]
    style.font.size = Pt(estilo["font_size_pt"])
    pf = style.paragraph_format
    pf.line_spacing      = estilo["line_spacing"]
    pf.first_line_indent = Inches(estilo["indent"])

    # elementos pré-textuais
    amostra = "\n".join([p.text for p in doc_orig.paragraphs[:50]])
    copyright_text = "[Placeholder copyright]"
    bio_text       = "[Placeholder bio]"
    if is_api_ready:
        copyright_text = gerar_copyright(st.session_state["book_title"], st.session_state["book_author"], 2025, amostra)
        bio_text       = gerar_biografia(st.session_state["book_title"], st.session_state["book_author"], amostra)

    adicionar_pagina_rosto(doc_rev, st.session_state["book_title"], st.session_state["book_author"], estilo)
    adicionar_pagina_generica(doc_rev, "Página de Créditos")
    doc_rev.add_paragraph(copyright_text)
    adicionar_pagina_generica(doc_rev, "Sumário")

    # revisão parágrafo-a-parágrafo (paralela)
    def revisar(p):
        txt = p.text.strip()
        if len(txt) < 10: return txt
        if is_api_ready:
            return call_openai("Você é um editor. Corrija gramática e estilo. Devolva só o texto.", txt, 500)
        return txt

    with ThreadPoolExecutor(max_workers=10) as ex:
        futuros = {ex.submit(revisar, p): p for p in doc_orig.paragraphs if len(p.text.strip()) >= 10}
        for fut in stqdm(as_completed(futuros), total=len(futuros), desc="Revisando"):
            p = futuros[fut]
            novo = fut.result()
            if p.style.name.startswith("Heading"):
                doc_rev.add_paragraph(novo, style=p.style.name)
            else:
                doc_rev.add_paragraph(novo)

    # pós-textual
    adicionar_pagina_generica(doc_rev, "Sobre o Autor")
    doc_rev.add_paragraph(bio_text)
    if incluir_abnt:
        adicionar_pagina_generica(doc_rev, "Apêndice A")
        adicionar_pagina_generica(doc_rev, "Anexo I")

    # blurb
    blurb = "[Placeholder blurb]"
    if is_api_ready:
        blurb = gerar_blurb(st.session_state["book_title"], st.session_state["book_author"], amostra)

    return doc_rev, amostra, blurb

# ---------- ESTADO ----------
if "book_title" not in st.session_state:
    st.session_state["book_title"]   = "O Último Código de Honra"
    st.session_state["book_author"]  = "Carlos Honorato"
    st.session_state["page_count"]   = 250
    st.session_state["capa_prompt"]  = "Portal antigo em floresta escura, fantasia épica, tons roxo/preto"
    st.session_state["blurb"]        = "A IA gerará o blurb aqui. Edite antes de criar a capa!"
    st.session_state["generated_image_url"] = None
    st.session_state["documento_revisado"]  = None
    st.session_state["texto_completo"]      = ""
    st.session_state["format_option"]  = "Padrão A5 (5.83x8.27 in)"
    st.session_state["style_option"]   = "Romance Clássico (Garamond)"
    st.session_state["incluir_abnt"]   = False

# ---------- CÁLCULOS ----------
fmt = KDP_SIZES[st.session_state["format_option"]]
espessura_cm = round(st.session_state["page_count"] * fmt["papel_fator"], 2)
capa_largura_cm = round(fmt["width_cm"] * 2 + espessura_cm + 0.6, 2)
capa_altura_cm  = round(fmt["height_cm"] + 0.6, 2)

# ---------- ABAS ----------
config_tab, miolo_tab, capa_tab, export_tab = st.tabs([
    "1. Configuração Inicial",
    "2. Diagramação & Elementos",
    "3. Capa Completa IA",
    "4. Análise & Exportar"
])

# ---------- CONFIGURAÇÃO ----------
with config_tab:
    st.header("Dados Essenciais")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state["book_title"]  = st.text_input("Título do Livro", st.session_state["book_title"])
        st.session_state["page_count"]  = st.number_input("Páginas (miolo)", min_value=10, value=st.session_state["page_count"], step=10)
    with c2:
        st.session_state["book_author"] = st.text_input("Autor", st.session_state["book_author"])

    st.header("Formato & Estilo")
    c3, c4, c5 = st.columns(3)
    with c3:
        st.session_state["format_option"] = st.selectbox("Tamanho Final", list(KDP_SIZES.keys()), index=list(KDP_SIZES.keys()).index(st.session_state["format_option"]))
    with c4:
        st.session_state["style_option"] = st.selectbox("Estilo de Diagramação", list(STYLE_TEMPLATES.keys()), index=list(STYLE_TEMPLATES.keys()).index(st.session_state["style_option"]))
    with c5:
        st.session_state["incluir_abnt"] = st.checkbox("Incluir Apêndices/Anexos ABNT", st.session_state["incluir_abnt"])

    st.info(f"Lombada: **{espessura_cm} cm** | Capa total: **{capa_largura_cm} cm × {capa_altura_cm} cm**")

    uploaded_file = st.file_uploader("Carregue o manuscrito (.docx)", type=["docx"])
    if uploaded_file:
        st.session_state["uploaded_file"] = uploaded_file

# ---------- DIAGRAMAÇÃO ----------
with miolo_tab:
    st.header("Diagramação e Revisão com IA")
    if "uploaded_file" not in st.session_state:
        st.warning("Por favor, carregue um arquivo na aba 1.")
    else:
        if st.button("▶️ Processar Miolo"):
            with st.spinner("Processando..."):
                doc, texto, blurb = processar_miolo(
                    st.session_state["uploaded_file"],
                    KDP_SIZES[st.session_state["format_option"]],
                    STYLE_TEMPLATES[st.session_state["style_option"]],
                    st.session_state["incluir_abnt"]
                )
                st.session_state["documento_revisado"]  = doc
                st.session_state["texto_completo"]      = texto
                st.session_state["blurb"]               = blurb
            st.success("Miolo pronto!")

        if st.session_state["documento_revisado"]:
            st.subheader("Blurb (contracapa) – edite se quiser:")
            st.session_state["blurb"] = st.text_area("Blurb", st.session_state["blurb"], height=300)

# ---------- CAPA ----------
with capa_tab:
    st.header("Capa Completa (DALL-E 3)")
    if not st.session_state["documento_revisado"]:
        st.warning("Processse o miolo primeiro.")
    else:
        st.session_state["capa_prompt"] = st.text_area("Descrição visual da capa:", st.session_state["capa_prompt"], height=150)
        if st.button("🎨 Gerar Capa"):
            url = gerar_capa_dalle(
                st.session_state["capa_prompt"],
                st.session_state["book_title"],
                st.session_state["book_author"],
                st.session_state["blurb"],
                capa_largura_cm,
                capa_altura_cm,
                espessura_cm
            )
            if url.startswith("http"):
                st.session_state["generated_image_url"] = url
                st.image(url, caption="Capa gerada", use_column_width=True)
            else:
                st.error(url)

# ---------- EXPORTAR ----------
with export_tab:
    st.header("Exportação & Relatórios")
    if not st.session_state["documento_revisado"]:
        st.warning("Processse o miolo primeiro.")
    else:
        if is_api_ready and st.button("Gerar Relatório Estrutural"):
            rep = gerar_relatorio_estrutural(st.session_state["texto_completo"])
            st.markdown("### Relatório Estrutural")
            st.markdown(rep)

        def docx_bytes(doc):
            buf = BytesIO()
            doc.save(buf)
            buf.seek(0)
            return buf.getvalue()

        st.download_button(
            label="⬇️ Baixar manuscrito revisado (.docx)",
            data=docx_bytes(st.session_state["documento_revisado"]),
            file_name=f"{st.session_state['book_title']}_revisado.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        if st.session_state["generated_image_url"]:
            st.markdown(f"[⬇️ Baixar imagem da capa (alta resolução)]({st.session_state['generated_image_url']})")
