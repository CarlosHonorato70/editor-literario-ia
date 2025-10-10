# fastformat.py
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional, Dict
import re
import difflib

@dataclass
class FastFormatOptions:
    # Espaços e quebras
    normalize_whitespace: bool = True               # espaços duplicados -> simples
    trim_line_spaces: bool = True                   # remove espaços à direita/esquerda de cada linha
    collapse_blank_lines: bool = True               # múltiplas linhas em branco -> 1
    ensure_final_newline: bool = True

    # Pontuação e microtipografia
    normalize_ellipsis: bool = True                 # "..." -> "…"
    quotes_style: str = "curly"                     # "straight" | "curly"
    dialogue_dash: str = "emdash"                   # "emdash" | "hyphen"
    number_range_dash: str = "endash"               # "endash" | "hyphen"
    smart_ptbr_punctuation: bool = True             # ajustes leves para PT-BR

    # Diversos
    normalize_bullets: bool = True                  # "-" ou "*" no início -> "•"
    preserve_markdown: bool = False                 # evita mexer em blocos markdown (código, headers)
    safe_mode: bool = True                          # evita transformações agressivas

default_options: Dict[str, FastFormatOptions] = {
    "padrao": FastFormatOptions()
}

def _to_curly_quotes(text: str) -> str:
    # Aspas duplas
    text = re.sub(r'(^|[\s(\[{<])"', r'\1“', text)   # abertura
    text = text.replace('"', '”')                    # o restante vira fechamento
    # Aspas simples (apostrofo vs aspas)
    # contrações: O'Neill -> O’Neill
    text = re.sub(r"(\w)'(\w)", r"\1’\2", text)
    # abertura simples
    text = re.sub(r"(^|[\s(\[{<])'", r"\1‘", text)
    # o restante vira fechamento simples
    text = text.replace("'", "’")
    return text

def _to_straight_quotes(text: str) -> str:
    # converte aspas tipográficas para retas
    replacements = {
        "“": '"', "”": '"',
        "‘": "'", "’": "'"
    }
    return "".join(replacements.get(ch, ch) for ch in text)

def _normalize_ellipsis(text: str) -> str:
    return re.sub(r'\.\.\.', '…', text)

def _denormalize_ellipsis(text: str) -> str:
    return text.replace('…', '...')

def _normalize_dialogue_dash(text: str, mode: str) -> str:
    lines = text.splitlines()
    out = []
    for ln in lines:
        # normaliza diálogos no início da linha
        if mode == "emdash":
            # "- " início de fala => "— "
            ln = re.sub(r'^[ \t]*-[ \t]+', '— ', ln)
            # "--" usado como emdash em alguns manuscritos
            ln = re.sub(r'^[ \t]*--[ \t]*', '— ', ln)
        else:
            # força hífen simples
            ln = re.sub(r'^[ \t]*—[ \t]*', '- ', ln)
            ln = re.sub(r'^[ \t]*--[ \t]*', '- ', ln)
        out.append(ln)
    return "\n".join(out)

def _normalize_number_ranges(text: str, dash: str) -> str:
    # "10-20", "10 - 20" -> "10–20" se endash
    if dash == "endash":
        return re.sub(r'(\d)\s*-\s*(\d)', r'\1–\2', text)
    else:
        # força hífen
        text = text.replace('–', '-')
        return re.sub(r'(\d)\s*–\s*(\d)', r'\1-\2', text)

def _normalize_bullets(text: str) -> str:
    lines = text.splitlines()
    out = []
    for ln in lines:
        ln2 = re.sub(r'^[ \t]*[-*][ \t]+', '• ', ln)
        out.append(ln2)
    return "\n".join(out)

def _normalize_spaces(text: str, trim_lines: bool, collapse_blanks: bool) -> str:
    lines = text.splitlines()
    norm = []
    for ln in lines:
        # substitui múltiplos espaços por 1 (preserva tabs)
        ln = re.sub(r' {2,}', ' ', ln)
        if trim_lines:
            ln = ln.strip()
        norm.append(ln)
    text = "\n".join(norm)
    if collapse_blanks:
        # 3+ linhas vazias => 1
        text = re.sub(r'\n{3,}', '\n\n', text, flags=re.MULTILINE)
    return text

def _smart_ptbr(text: str) -> str:
    # Ajustes leves:
    # Espaço antes de ? ! geralmente não; remove se houver
    text = re.sub(r'\s+([?!;:])', r'\1', text)
    # vírgula antes de “)” costuma ser ruim: ", )" -> ")"
    text = re.sub(r',\s+\)', ')', text)
    return text

def apply_fastformat(text: str, options: FastFormatOptions) -> str:
    original = text

    # 1) Ellipsis
    if options.normalize_ellipsis:
        text = _normalize_ellipsis(text)
    else:
        text = _denormalize_ellipsis(text)

    # 2) Quotes
    if options.quotes_style == "curly":
        text = _to_curly_quotes(text)
    else:
        text = _to_straight_quotes(text)

    # 3) Dialogue dash
    text = _normalize_dialogue_dash(text, options.dialogue_dash)

    # 4) Ranges
    text = _normalize_number_ranges(text, options.number_range_dash)

    # 5) Bullets
    if options.normalize_bullets:
        text = _normalize_bullets(text)

    # 6) PT-BR micro
    if options.smart_ptbr_punctuation:
        text = _smart_ptbr(text)

    # 7) Espaços
    if options.normalize_whitespace:
        text = _normalize_spaces(
            text,
            trim_lines=options.trim_line_spaces,
            collapse_blanks=options.collapse_blank_lines
        )

    if options.ensure_final_newline and not text.endswith("\n"):
        text += "\n"

    if options.safe_mode:
        # Evita fazer transformações muito agressivas encadeadas
        pass

    return text

def make_unified_diff(a: str, b: str, fromfile: str = "antes.txt", tofile: str = "depois.txt") -> str:
    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    diff = difflib.unified_diff(a_lines, b_lines, fromfile=fromfile, tofile=tofile, lineterm="")
    return "".join(diff)
