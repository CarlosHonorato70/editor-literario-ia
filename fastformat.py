# fastformat.py
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
import re
import difflib

@dataclass
class FastFormatOptions:
    # Espaços e quebras
    normalize_whitespace: bool = True               # espaços duplicados -> simples
    trim_line_spaces: bool = True                   # remove espaços à direita/esquerda de cada linha
    collapse_blank_lines: bool = True               # múltiplas linhas em branco -> 1
    ensure_final_newline: bool = True               # garante quebra de linha no final

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

def get_fastformat_default_options() -> FastFormatOptions:
    return FastFormatOptions()


def _to_curly_quotes(text: str, pt_br_style: bool = True) -> str:
    # Aspas duplas
    # Abertura em pt-BR (com base em contexto)
    text = re.sub(r'(^|[\s(\[{<])(")', r'\1“', text)
    # Fechamento em pt-BR
    text = re.sub(r'(")([\s).\]}>]|$)', r'”\2', text) # Ajustado para fechar aspas duplas de forma mais robusta

    # Aspas simples (apostrofo vs aspas)
    text = re.sub(r"(\w)'(\w)", r"\1’\2", text) # Contração
    text = re.sub(r"(^|[\s(\[{<])(')(\s)", r"\1‘\3", text) # Abertura simples
    text = text.sub(r"([^\s])(')", r"\1’", text) # Fechamento simples se não for abertura e não for contração

    # Correção para apostrofo inicial em palavras (ex: 's algo)
    text = re.sub(r"(\s|^)'(\w)", r"\1‘\2", text)
    
    # Garantir que aspas restantes sejam fechadas como '”' ou '’'
    text = text.replace('"', '”')
    text = text.replace("'", "’")
    return text


def _to_straight_quotes(text: str) -> str:
    # Converte aspas tipográficas para retas
    replacements = {
        "“": '"', "”": '"',
        "‘": "'", "’": "'"
    }
    return "".join(replacements.get(ch, ch) for ch in text)

def _normalize_ellipsis(text: str) -> str:
    # Substitui múltiplas ocorrências de '.' por '…'
    text = re.sub(r'\.{3,}', '…', text)
    # Garante um espaço antes e depois, a menos que esteja no fim de frase ou precedido por espaço
    text = re.sub(r'([^\s])…', r'\1 …', text) # Ex: palavra…palavra -> palavra …palavra
    text = re.sub(r'…([^\s])', r'… \1', text) # Ex: palavra…palavra -> palavra… palavra
    text = re.sub(r'\s…\s', ' … ', text) # Normaliza espaços ao redor
    return text

def _denormalize_ellipsis(text: str) -> str:
    # Converte '…' de volta para '...'
    return text.replace('…', '...')

def _normalize_dialogue_dash(text: str, mode: str) -> str:
    lines = text.splitlines()
    out = []
    for ln in lines:
        # Apenas afeta o início da linha ou após um parágrafo vazio para diálogos
        if mode == "emdash":
            ln = re.sub(r'^[ \t]*[-]{1,2}[ \t]+', '— ', ln)
        else: # hyphen
            ln = re.sub(r'^[ \t]*[—]{1,2}[ \t]+', '- ', ln)
        out.append(ln)
    return "\n".join(out)

def _normalize_number_ranges(text: str, dash_type: str) -> str:
    # "10-20", "10 - 20" -> "10–20" se endash
    if dash_type == "endash":
        # Encontra padrões como "1-2", "1 - 2", "1 -- 2" e converte para "1–2"
        return re.sub(r'(\d+)\s*[-]{1,2}\s*(\d+)', r'\1–\2', text)
    else: # hyphen
        # Converte qualquer en/em-dash em contexto de range para hífen
        return re.sub(r'(\d+)\s*[–—]{1,2}\s*(\d+)', r'\1-\2', text)

def _normalize_bullets(text: str) -> str:
    lines = text.splitlines()
    out = []
    for ln in lines:
        ln = re.sub(r'^[ \t]*[-*][ \t]+', '• ', ln)
        out.append(ln)
    return "\n".join(out)

def _normalize_spaces_and_newlines(text: str, trim_lines: bool, collapse_blanks: bool, ensure_final: bool) -> str:
    # Remove múltiplos espaços para um único espaço
    text = re.sub(r' {2,}', ' ', text)

    lines = text.splitlines()
    norm_lines = []
    for ln in lines:
        if trim_lines:
            ln = ln.strip()
        norm_lines.append(ln)
    text = "\n".join(norm_lines)

    if collapse_blanks:
        # Reduz múltiplas linhas vazias para no máximo uma linha vazia
        text = re.sub(r'\n{3,}', '\n\n', text)
    
    if ensure_final and not text.endswith("\n") and text.strip():
        text += "\n"
        
    return text

def _smart_ptbr_punctuation(text: str) -> str:
    # Remove espaço antes de pontuação de fechamento (geralmente não usado em PT-BR)
    text = re.sub(r'\s+([,.;:?!])', r'\1', text)
    # Garante um espaço após pontuação de fechamento, se seguido por caractere que não seja pontuação
    text = re.sub(r'([,.;:?!])([^\s,.?!])', r'\1 \2', text)
    # Normaliza espaços ao redor de parênteses/colchetes
    text = re.sub(r'\s*\(\s*', ' (', text)
    text = re.sub(r'\s*\)\s*', ') ', text)
    text = re.sub(r'\s*\[\s*', ' [', text)
    text = re.sub(r'\s*\]\s*', '] ', text)
    # Remove espaço duplicado que possa ter surgido
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def apply_fastformat(text: str, options: FastFormatOptions) -> str:
    if not isinstance(text, str):
        return text # Garante que estamos trabalhando com string
    
    current_text = text

    if options.normalize_ellipsis:
        current_text = _normalize_ellipsis(current_text)
    else:
        current_text = _denormalize_ellipsis(current_text) # Desfaz se a opção for desligada

    if options.quotes_style == "curly":
        current_text = _to_curly_quotes(current_text)
    else:
        current_text = _to_straight_quotes(current_text)

    current_text = _normalize_dialogue_dash(current_text, options.dialogue_dash)
    current_text = _normalize_number_ranges(current_text, options.number_range_dash)

    if options.normalize_bullets:
        current_text = _normalize_bullets(current_text)

    if options.smart_ptbr_punctuation:
        current_text = _smart_ptbr_punctuation(current_text)

    if options.normalize_whitespace:
        current_text = _normalize_spaces_and_newlines(
            current_text,
            trim_lines=options.trim_line_spaces,
            collapse_blanks=options.collapse_blank_lines,
            ensure_final=options.ensure_final_newline
        )
    
    if options.safe_mode:
        # Implementar regras de segurança adicionais aqui, se necessário.
        # Por enquanto, as regras acima já são relativamente seguras.
        pass

    return current_text


def make_unified_diff(a: str, b: str, fromfile: str = "antes.txt", tofile: str = "depois.txt") -> str:
    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    diff = difflib.unified_diff(a_lines, b_lines, fromfile=fromfile, tofile=tofile, lineterm="")
    return "".join(diff)
