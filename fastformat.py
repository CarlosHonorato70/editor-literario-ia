# fastformat.py
from dataclasses import dataclass
from typing import Dict, Tuple
import re
import difflib

@dataclass
class FastFormatOptions:
    # Espaços e quebras de linha
    normalize_spaces: bool = True               # remove espaços duplicados, espaços no fim de linha
    compress_blank_lines: bool = True           # reduz linhas em branco consecutivas
    max_blank_lines: int = 1                    # mantém no máximo 1 linha em branco
    # Pontuação e sinais
    punctuation_spacing: bool = True            # espaço correto antes/depois de pontuação
    ellipses: bool = True                       # "..." -> "…", normaliza espaços ao redor
    fix_double_punct: bool = True               # "!!" -> "!", "??" -> "?"
    dashes_ranges_en: bool = True               # "10-20" -> "10–20" (en dash, sem espaços)
    dashes_aside_em: bool = True                # " - " -> " — " em incisos/asides
    # Aspas
    quotes: bool = True
    quotes_style: str = "typographic"           # "typographic" (pt-BR “ ” e ‘ ’) ou "straight" (" ' )
    # Capitalização
    capitalize_sentences: bool = False          # capitaliza início de frases (heurístico)
    # Unidades e símbolos
    tidy_units_nbsp: bool = True                # 10 kg -> 10 kg (NBSP), 10 % -> 10% (sem espaço)

def default_options() -> FastFormatOptions:
    return FastFormatOptions()

# ------------------------
# Regras básicas
# ------------------------

def _normalize_line_endings(text: str) -> str:
    # Garante \n
    return text.replace("\r\n", "\n").replace("\r", "\n")

def _trim_trailing_spaces(text: str) -> str:
    return re.sub(r"[ \t]+(\n|$)", r"\1", text)

def _collapse_multiple_spaces(text: str) -> str:
    # Mantém simples dentro da linha (sem mexer em espaços de indentação no começo)
    def collapse_line(line: str) -> str:
        # Não mexe em indentação no começo da linha
        m = re.match(r"^(\s*)(.*)$", line)
        if not m:
            return line
        indent, rest = m.groups()
        rest = re.sub(r"[ \t]{2,}", " ", rest)
        return indent + rest
    return "\n".join(collapse_line(ln) for ln in text.split("\n"))

def _compress_blank_lines(text: str, max_blank_lines: int) -> str:
    # Reduz várias linhas em branco para no máx N
    blank_block = "\n" * (max_blank_lines + 1)
    # Substitui 3+ quebras por (max+1) quebras
    pattern = re.compile(r"\n{"+str(max_blank_lines+2)+",}")
    return pattern.sub(blank_block, text)

def _fix_punctuation_spacing(text: str) -> str:
    # Remove espaço antes de pontuação
    text, _ = re.subn(r"\s+([,.;:!?])", r"\1", text)
    # Garante 1 espaço após pontuação (se não for fim de linha/fechamento)
    text, _ = re.subn(r"([,.;:!?])([^\s\)\]}»”’…])", r"\1 \2", text)
    # Ajuste para dois-pontos: sem espaço extra antes, um depois
    text, _ = re.subn(r"\s*:\s*", r": ", text)
    return text

def _normalize_ellipses(text: str) -> str:
    # ". . ." ou "..." -> "…"
    text, _ = re.subn(r"\.\s*\.\s*\.", "…", text)
    # Espaçamento: sem espaço antes, um espaço depois se vier palavra
    text, _ = re.subn(r"\s+…", "…", text)  # remove espaços antes
    text, _ = re.subn(r"…(?=\w)", "… ", text)  # garante espaço depois quando seguido de palavra
    return text

def _fix_double_punct(text: str) -> str:
    text, _ = re.subn(r"([!?]){2,}", r"\1", text)
    # 4+ pontos vira apenas "…"
    text, _ = re.subn(r"\.{4,}", "…", text)
    return text

def _normalize_dashes(text: str, ranges_en: bool = True, aside_em: bool = True) -> str:
    # Ranges numéricos: 10-20 -> 10–20 (sem espaços)
    if ranges_en:
        text, _ = re.subn(r"(?<=\d)\s*-\s*(?=\d)", "–", text)
    # Asides/incisos: espaço-hífen-espaço -> espaço—espaço, evitando linhas iniciadas com hífen (listas)
    if aside_em:
        text, _ = re.subn(r"(?<!^|\n)\s-\s", " — ", text)
    return text

def _smart_quotes(text: str, style: str = "typographic") -> str:
    # Converte aspas simples/apóstrofos internos e depois aspas duplas por alternância
    # Apostrofos dentro de palavras -> ’
    text, _ = re.subn(r"(\w)'(\w)", r"\1’\2", text)

    if style == "straight":
        # Tudo vira " e '
        text = text.replace("“", '"').replace("”", '"')
        text = text.replace("‘", "'").replace("’", "'")
        # Normaliza variações
        return text

    # Tipográficas: “ ” e ‘ ’
    # Primeiro uniformiza para straight para facilitar alternância
    t = text.replace("“", '"').replace("”", '"').replace("''", '"')
    # Aspas simples externas: alternância ingênua
    # Troca aspas simples fora de palavras (não apóstrofo já tratado) por alternância
    parts = re.split(r"(')", t)
    opened = False
    for i in range(len(parts)):
        if parts[i] == "'":
            parts[i] = "‘" if not opened else "’"
            opened = not opened
    t = "".join(parts)
    # Aspas duplas por alternância
    pieces = t.split('"')
    out = []
    open_double = True
    for i, chunk in enumerate(pieces):
        out.append(chunk)
        if i < len(pieces) - 1:
            out.append("“" if open_double else "”")
            open_double = not open_double
    return "".join(out)

def _capitalize_sentences(text: str) -> str:
    # Heurística: capitaliza primeira letra de frases após (.!?…)
    def cap_first_alpha(s: str) -> str:
        for i, ch in enumerate(s):
            if ch.isalpha():
                return s[:i] + ch.upper() + s[i+1:]
        return s
    # Divide conservando delimitadores
    parts = re.split(r"([\.!\?…]+[”’"\)\]]*\s+)", text)
    if len(parts) <= 1:
        return cap_first_alpha(text)
    result = []
    for i in range(0, len(parts), 2):
        seg = parts[i]
        if i == 0:
            result.append(cap_first_alpha(seg))
        else:
            result.append(cap_first_alpha(seg))
        if i + 1 < len(parts):
            result.append(parts[i+1])
    return "".join(result)

def _tidy_units(text: str) -> str:
    # Espaço NBSP entre número e unidade SI comuns, remover espaço antes de %
    units = ["kg", "g", "mg", "km", "m", "cm", "mm", "L", "l", "ml", "°C"]
    for u in units:
        text, _ = re.subn(rf"(\d)\s+{u}\b", r"\1\u00A0" + u, text)  # NBSP
    # Percentual sem espaço: 10% (pt-BR usual em textos correntes)
    text, _ = re.subn(r"(\d)\s+%", r"\1%", text)
    return text

# ------------------------
# Aplicação e Diff
# ------------------------

def apply_fastformat(text: str, options: FastFormatOptions) -> Tuple[str, Dict]:
    report: Dict[str, int] = {
        "spaces_trimmed": 0,
        "spaces_collapsed": 0,
        "blank_lines_compressed": 0,
        "punctuation_spacing": 0,
        "ellipses": 0,
        "double_punct": 0,
        "dashes_ranges": 0,
        "dashes_aside": 0,
        "quotes": 0,
        "capitalized_sentences": 0,
        "units_nbsp": 0,
    }

    original = text
    s = _normalize_line_endings(text)

    if options.normalize_spaces:
        before = s
        s = _trim_trailing_spaces(s)
        report["spaces_trimmed"] += (len(before) - len(s))
        before = s
        s2 = _collapse_multiple_spaces(s)
        # Como _collapse_multiple_spaces pode não alterar tamanho sempre, marcamos se mudou
        if s2 != s:
            report["spaces_collapsed"] += 1
        s = s2

    if options.compress_blank_lines:
        before = s
        s2 = _compress_blank_lines(s, options.max_blank_lines)
        if s2 != s:
            report["blank_lines_compressed"] += 1
        s = s2

    if options.punctuation_spacing:
        before = s
        s2 = _fix_punctuation_spacing(s)
        if s2 != s:
            report["punctuation_spacing"] += 1
        s = s2

    if options.ellipses:
        before = s
        s2 = _normalize_ellipses(s)
        if s2 != s:
            report["ellipses"] += 1
        s = s2

    if options.fix_double_punct:
        before = s
        s2 = _fix_double_punct(s)
        if s2 != s:
            report["double_punct"] += 1
        s = s2

    if options.dashes_ranges_en or options.dashes_aside_em:
        before = s
        s2 = _normalize_dashes(s, options.dashes_ranges_en, options.dashes_aside_em)
        if s2 != s:
            if options.dashes_ranges_en:
                report["dashes_ranges"] += 1
            if options.dashes_aside_em:
                report["dashes_aside"] += 1
        s = s2

    if options.quotes:
        before = s
        s2 = _smart_quotes(s, style=options.quotes_style)
        if s2 != s:
            report["quotes"] += 1
        s = s2

    if options.capitalize_sentences:
        before = s
        s2 = _capitalize_sentences(s)
        if s2 != s:
            report["capitalized_sentences"] += 1
        s = s2

    if options.tidy_units_nbsp:
        before = s
        s2 = _tidy_units(s)
        if s2 != s:
            report["units_nbsp"] += 1
        s = s2

    return s, report

def make_unified_diff(original: str, formatted: str) -> str:
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        formatted.splitlines(keepends=True),
        fromfile="original",
        tofile="formatado",
        lineterm=""
    )
    return "".join(diff)
