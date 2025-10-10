import os
import io
import re
import difflib
import base64
from datetime import datetime

import streamlit as st

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False
    OpenAI = None  # type: ignore

try:
    from docx import Document
    DOCX_AVAILABLE = True
except Exception:
    DOCX_AVAILABLE = False
    Document = None  # type: ignore


# =========================
# Configurações e Templates
# =========================

STYLE_TEMPLATES = {
    "padrao_br": {
        "label": "Padrão BR (neutro)",
        "normalize_spaces": True,
        "normalize_ellipses": True,
        "typographic_dashes": True,
        "quotes_style": "typographic",  # typographic | straight
        "remove_double_blank_lines": True,
    },
    "abnt": {
        "label": "ABNT (básico textual)",
        "normalize_spaces": True,
        "normalize_ellipses": True,
        "typographic_dashes": True,
        "quotes_style": "straight",
        "remove_double_blank_lines": True,
    },
    "apa": {
        "label": "APA (básico textual)",
        "normalize_spaces": True,
        "normalize_ellipses": True,
        "typographic_dashes": True,
        "quotes_style": "typographic",
        "remove_double_blank_lines": True,
    },
    "jornalistico": {
        "label": "Jornalístico (BR)",
        "normalize_spaces": True,
        "normalize_ellipses": True,
        "typographic_dashes": True,
        "quotes_style": "straight",
        "remove_double_blank_lines": True,
    },
}


# =========================
# Utilidades de IO
# =========================

def read_text_file(uploaded_file) -> str:
    content = uploaded_file.read()
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return content.decode("latin-1")
        except UnicodeDecodeError:
            return content.decode("utf-8", errors="ignore")


def read_docx_file(uploaded_file) -> str:
    if not DOCX_AVAILABLE:
        st.error("python-docx não está instalado. Instale com: pip install python-docx")
        return ""
    # Carrega o arquivo em memória
    data = uploaded_file.read()
    bio = io.BytesIO(data)
    doc = Document(bio)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)


def export_docx(text: str) -> bytes:
    if not DOCX_AVAILABLE:
        st.error("python-docx não está instalado. Instale com: pip install python-docx")
        return b""
    doc = Document()
    for block in text.split("\n"):
        # Parágrafos vazios também são representados
        doc.add_paragraph(block)
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()


# =========================
# Normalizações e Formatação
# =========================

def normalize_spaces(text: str) -> str:
    # Remove espaços duplos, espaços antes de pontuação, trims de linha
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *([,;:.!?…])", r"\1", text)
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)  # compacta múltiplas linhas em no máx. 2
    # Remove espaços no início/fim de cada linha
    text = "\n".join([line.strip() for line in text.splitlines()])
    return text


def normalize_ellipses(text: str) -> str:
    # Normaliza reticências: três pontos no formato …
    text = re.sub(r"\.\.\.+", "…", text)
    # Garante espaço antes/depois se necessário
    text = re.sub(r"\s*…\s*", " … ", text)
    # Compacta espaços
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def to_typographic_quotes(text: str) -> str:
    # Converte aspas retas para tipográficas de forma simples/heurística.
    # Nota: solução heurística; casos complexos podem não ficar perfeitos.
    result = []
    double_is_open = True
    single_is_open = True
    for ch in text:
        if ch == '"':
            result.append("“" if double_is_open else "”")
            double_is_open = not double_is_open
        elif ch == "'":
            result.append("‘" if single_is_open else "’")
            single_is_open = not single_is_open
        else:
            result.append(ch)
    return "".join(result)


def to_straight_quotes(text: str) -> str:
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    return text


def typographic_dashes(text: str) -> str:
    # Substitui -- por — (travessão), preservando espaços apropriados
    text = re.sub(r"\s?--\s?", " — ", text)
    # Normaliza espaços em torno do travessão
    text = re.sub(r"\s*—\s*", " — ", text)
    # Remove espaços duplicados
    text = re.sub(r"\s{2,}", " ", text)
    # Ajusta travessão no início de fala
    text = re.sub(r"^\s*-\s+", "— ", text, flags=re.MULTILINE)
    return text.strip()


def remove_double_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


def apply_local_formatting(text: str, opts: dict) -> str:
    out = text

    if opts.get("normalize_spaces"):
        out = normalize_spaces(out)

    if opts.get("normalize_ellipses"):
        out = normalize_ellipses(out)

    if opts.get("typographic_dashes"):
        out = typographic_dashes(out)

    quotes_style = opts.get("quotes_style", "typographic")
    if quotes_style == "typographic":
        out = to_typographic_quotes(out)
    else:
        out = to_straight_quotes(out)

    if opts.get("remove_double_blank_lines"):
        out = remove_double_blank_lines(out)

    return out.strip()


def apply_ai_refinement(text: str, opts: dict, tone_hint: str = "") -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not (OPENAI_AVAILABLE and api_key):
        st.warning("OPENAI_API_KEY não configurada ou SDK indisponível. Pulando etapa de IA.")
        return text

    client = OpenAI(api_key=api_key)

    # Monta um breve prompt de instruções
    template_label = opts.get("template_label", "Padrão BR")
    quotes = opts.get("quotes_style", "typographic")
    dash_pref = "travessão" if opts.get("typographic_dashes") else "hífen"
    ellipses_pref = "use reticências como …" if opts.get("normalize_ellipses") else "mantenha reticências como '...'"
    quotes_pref = "aspas tipográficas" if quotes == "typographic" else "aspas retas"
    tone = tone_hint or "mantenha o tom e o conteúdo original"

    system_msg = (
        "Você é um formatter de texto. Aplique APENAS formatação e microedição, "
        "sem reescrever ou alterar conteúdo."
    )
    user_msg = f"""
Regras:
- Template: {template_label}
- Aspas: {quotes_pref}
- Dashes: {dash_pref}
- Reticências: {ellipses_pref}
- {tone}

Instruções:
- Não adicione nem remova ideias.
- Não resuma.
- Preserve quebras de linha.
- Retorne somente o texto final formatado, sem explicações.

Texto:
{text}
""".strip()

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.1,
        )
        ai_text = completion.choices[0].message.content if completion.choices else ""
        return ai_text.strip() if ai_text else text
    except Exception as e:
        st.error(f"Falha na etapa de IA: {e}")
        return text


# =========================
# Diff e Exibição
# =========================

def render_html_diff(a: str, b: str) -> str:
    # Gera uma tabela HTML com difflib.HtmlDiff
    a_lines = a.splitlines()
    b_lines = b.splitlines()
    differ = difflib.HtmlDiff(wrapcolumn=80)
    html = differ.make_table(
        fromlines=a_lines,
        tolines=b_lines,
        fromdesc="Original",
        todesc="Formatado",
        context=True,
        numlines=2,
    )
    style = """
    <style>
      table.diff { font-family: monospace; border: 1px solid #ddd; border-collapse: collapse; width: 100%; }
      .diff_header { background: #f6f8fa; }
      td, th { padding: 4px 6px; border: 1px solid #eee; vertical-align: top; }
      .diff_add { background: #e6ffed; }
      .diff_chg { background: #fff5b1; }
      .diff_sub { background: #ffeef0; }
    </style>
    """
    return style + html


# =========================
# UI - Streamlit
# =========================

st.set_page_config(page_title="FastFormat — Editor Literário IA", layout="wide")

st.title("FastFormat — Editor Literário IA")
st.caption("Pré-visualize, compare, aplique e exporte formatações de texto de forma rápida.")

with st.sidebar:
    st.header("Configuração Inicial")

    # Template de Estilo (corrigido, string fechada)
    template_keys = list(STYLE_TEMPLATES.keys())
    template_labels = [STYLE_TEMPLATES[k]["label"] for k in template_keys]
    default_index = 0

    style_key = st.selectbox(
        "Template de Estilo",
        options=template_keys,
        index=default_index,
        format_func=lambda k: STYLE_TEMPLATES[k]["label"],
        help="Escolha um template de formatação base.",
    )

    base_opts = STYLE_TEMPLATES[style_key].copy()
    base_opts["template_label"] = base_opts.get("label", "Padrão BR")

    st.subheader("Ajustes finos")

    # Estilo de aspas (corrigido: atribuição, format_func e aspas internas)
    quotes_style = st.radio(
        "Estilo de aspas",
        options=["typographic", "straight"],
        index=0 if base_opts.get("quotes_style") == "typographic" else 1,
        format_func=lambda x: 'Tipográficas ("","")' if x == "typographic" else 'Retas ("","")',
        help='Tipográficas: “ ” e ‘ ’. Retas: " e \'.',
    )

    normalize_spaces_opt = st.checkbox(
        "Normalizar espaços e espaçamentos de pontuação",
        value=bool(base_opts.get("normalize_spaces", True)),
    )
    normalize_ellipses_opt = st.checkbox(
        "Normalizar reticências (…)",
        value=bool(base_opts.get("normalize_ellipses", True)),
    )
    dashes_opt = st.checkbox(
        "Usar travessões tipográficos (—) e padronizar diálogos",
        value=bool(base_opts.get("typographic_dashes", True)),
    )
    remove_blank_lines_opt = st.checkbox(
        "Compactar múltiplas linhas vazias",
        value=bool(base_opts.get("remove_double_blank_lines", True)),
    )

    use_ai = st.checkbox(
        "Usar IA para refinar o estilo sem alterar o conteúdo",
        value=False,
        help="Requer OPENAI_API_KEY configurada no ambiente.",
    )
    tone_hint = ""
    if use_ai:
        tone_hint = st.text_input(
            "Dica de tom (opcional)",
            placeholder="Ex.: manter tom literário, fluidez sutil, sem alterar conteúdo"
        )

    st.markdown("---")
    st.caption("Dica: Você pode colar um texto abaixo ou enviar um arquivo .txt / .docx no corpo do app.")

# Entrada de texto/arquivo
st.subheader("Entrada")
col1, col2 = st.columns([2, 1])

with col1:
    text_input = st.text_area(
        "Cole seu texto aqui",
        height=260,
        placeholder="Cole seu texto ou use o upload ao lado...",
    )

with col2:
    uploaded = st.file_uploader("Ou envie um arquivo", type=["txt", "docx"])
    if uploaded is not None:
        if uploaded.name.lower().endswith(".txt"):
            text_input = read_text_file(uploaded)
        elif uploaded.name.lower().endswith(".docx"):
            text_input = read_docx_file(uploaded)

if not text_input:
    st.info("Insira texto na caixa acima ou envie um arquivo para começar.")
    st.stop()

# Prepara opções consolidadas
opts = {
    "template_label": base_opts.get("template_label", "Padrão BR"),
    "quotes_style": quotes_style,
    "normalize_spaces": normalize_spaces_opt,
    "normalize_ellipses": normalize_ellipses_opt,
    "typographic_dashes": dashes_opt,
    "remove_double_blank_lines": remove_blank_lines_opt,
}

# Pré-visualização (local, sem IA)
preview_text = apply_local_formatting(text_input, opts)

st.subheader("Pré-visualização formatada (sem IA)")
st.text_area("Preview", value=preview_text, height=240)

# Diff
with st.expander("Ver Diff (Original vs. Formatado)", expanded=False):
    html = render_html_diff(text_input, preview_text)
    st.components.v1.html(html, height=360, scrolling=True)

# Aplicar e Exportar
st.markdown("---")
st.subheader("Aplicar formatação")

apply_btn = st.button("Aplicar agora", type="primary")
final_text = preview_text

if apply_btn:
    # Opcional: camadas — local + IA
    if use_ai:
        final_text = apply_ai_refinement(preview_text, opts, tone_hint=tone_hint or "")
    else:
        final_text = preview_text

    st.success("Formatação aplicada!")
    st.text_area("Resultado final", value=final_text, height=260)

    # Downloads
    colA, colB = st.columns(2)

    with colA:
        # Download TXT
        b64 = base64.b64encode(final_text.encode("utf-8")).decode("utf-8")
        filename_txt = f"texto_formatado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        href = f'<a href="data:text/plain;base64,{b64}" download="{filename_txt}">⬇️ Baixar .txt</a>'
        st.markdown(href, unsafe_allow_html=True)

    with colB:
        # Download DOCX
        if DOCX_AVAILABLE:
            docx_bytes = export_docx(final_text)
            filename_docx = f"texto_formatado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            st.download_button(
                "⬇️ Baixar .docx",
                data=docx_bytes,
                file_name=filename_docx,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        else:
            st.info("Instale python-docx para exportar .docx: pip install python-docx")
else:
    st.caption("Clique em “Aplicar agora” para confirmar e gerar os arquivos de download.")
