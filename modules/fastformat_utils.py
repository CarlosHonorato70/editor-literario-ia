"""
FastFormat utilities module for the literary editor.
This module provides a wrapper around the comprehensive fastformat.py
with additional helper functions for common formatting tasks.
"""

import re
import sys
from pathlib import Path

# Import the comprehensive fastformat module
from fastformat import (
    FastFormatOptions,
    apply_fastformat as _apply_fastformat_core,
    make_unified_diff,
    get_fastformat_default_options
)


def get_default_options() -> FastFormatOptions:
    """
    Get default FastFormat options optimized for literary text.
    
    Returns:
        FastFormatOptions configured for literary editing
    """
    return get_fastformat_default_options()


def get_ptbr_options() -> FastFormatOptions:
    """
    Get FastFormat options optimized for Brazilian Portuguese literary text.
    
    Returns:
        FastFormatOptions configured for PT-BR
    """
    options = FastFormatOptions(
        normalize_whitespace=True,
        trim_line_spaces=True,
        collapse_blank_lines=True,
        ensure_final_newline=True,
        normalize_ellipsis=True,
        quotes_style="curly",
        dialogue_dash="emdash",
        number_range_dash="endash",
        smart_ptbr_punctuation=True,
        normalize_bullets=True,
        preserve_markdown=False,
        safe_mode=True
    )
    return options


def get_academic_options() -> FastFormatOptions:
    """
    Get FastFormat options for academic text.
    
    Returns:
        FastFormatOptions configured for academic writing
    """
    options = FastFormatOptions(
        normalize_whitespace=True,
        trim_line_spaces=True,
        collapse_blank_lines=True,
        ensure_final_newline=True,
        normalize_ellipsis=True,
        quotes_style="curly",
        dialogue_dash="hyphen",
        number_range_dash="endash",
        smart_ptbr_punctuation=True,
        normalize_bullets=False,  # Preserve academic list formatting
        preserve_markdown=True,   # Preserve markdown in academic text
        safe_mode=True
    )
    return options


def apply_fastformat(text: str, options: FastFormatOptions = None) -> str:
    """
    Apply FastFormat formatting to text.
    
    This is the main entry point for applying fastformat transformations.
    Uses comprehensive fastformat.py implementation with configurable options.
    
    Args:
        text: Text to format
        options: FastFormatOptions to use. If None, uses PT-BR defaults.
        
    Returns:
        Formatted text
    """
    if not isinstance(text, str) or not text:
        return text
    
    if options is None:
        options = get_ptbr_options()
    
    return _apply_fastformat_core(text, options)


def format_with_diff(text: str, options: FastFormatOptions = None) -> tuple:
    """
    Apply FastFormat and return both formatted text and diff.
    
    Args:
        text: Text to format
        options: FastFormatOptions to use. If None, uses PT-BR defaults.
        
    Returns:
        Tuple of (formatted_text, unified_diff)
    """
    if not isinstance(text, str) or not text:
        return text, ""
    
    formatted = apply_fastformat(text, options)
    diff = make_unified_diff(text, formatted)
    
    return formatted, diff


# Legacy helper functions for backward compatibility
def normalize_whitespace(text: str) -> str:
    """
    Remove múltiplos espaços, espaços em branco no início/fim e espaços antes de pontuação.
    
    Note: This is a legacy function. Use apply_fastformat() for comprehensive formatting.
    """
    text = re.sub(r' {2,}', ' ', text).strip()
    text = re.sub(r'\s([.,!?;:])', r'\1', text)
    return text


def remove_excess_newlines(text: str) -> str:
    """
    Remove quebras de linha consecutivas em excesso, deixando no máximo duas.
    
    Note: This is a legacy function. Use apply_fastformat() for comprehensive formatting.
    """
    return re.sub(r'\n{3,}', '\n\n', text)


def standardize_quotes(text: str) -> str:
    """
    Converte aspas retas para aspas tipográficas (curvas).
    
    Note: This is a legacy function. Use apply_fastformat() for comprehensive formatting.
    """
    text = re.sub(r'"([^"]*)"', r'"\1"', text)
    text = re.sub(r"'([^']*)'", r"'\1'", text)
    return text


def capitalize_sentences(text: str) -> str:
    """
    Capitaliza a primeira letra de cada frase.
    
    Note: This function is preserved for specific use cases.
    """
    sentences = re.split(r'([.!?]\s*)', text)
    capitalized_sentences_parts = []
    
    for i in range(0, len(sentences), 2):
        sentence_part = sentences[i].strip()
        if sentence_part:
            capitalized_sentences_parts.append(sentence_part[0].upper() + sentence_part[1:])
        if i + 1 < len(sentences):
            capitalized_sentences_parts.append(sentences[i+1])
            
    return "".join(capitalized_sentences_parts).strip()
