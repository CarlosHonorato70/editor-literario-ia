import re

def normalize_whitespace(text: str) -> str:
    """
    Remove múltiplos espaços, espaços em branco no início/fim e espaços antes de pontuação.
    """
    text = re.sub(r'\s+', ' ', text).strip()  # Múltiplos espaços para um, e remove no início/fim
    text = re.sub(r'\s([.,!?;:])', r'\1', text) # Remove espaço antes de pontuação
    return text

def remove_excess_newlines(text: str) -> str:
    """
    Remove quebras de linha consecutivas em excesso, deixando no máximo duas.
    """
    return re.sub(r'\n{3,}', '\n\n', text)

def standardize_quotes(text: str) -> str:
    """
    Converte aspas retas para aspas tipográficas (curvas).
    """
    # Replace double quotes
    text = re.sub(r'"([^"]*)"', r'“\1”', text)
    # Replace single quotes
    text = re.sub(r"'([^']*)'", r'‘\1’', text)
    return text

def capitalize_sentences(text: str) -> str:
    """
    Capitaliza a primeira letra de cada frase.
    """
    # Divide o texto em frases, mantendo os delimitadores
    sentences = re.split(r'([.!?]\s*)', text)
    capitalized_sentences_parts = []
    
    for i in range(0, len(sentences), 2):
        sentence_part = sentences[i].strip()
        if sentence_part:
            capitalized_sentences_parts.append(sentence_part[0].upper() + sentence_part[1:])
        if i + 1 < len(sentences): # Adiciona o delimitador de volta
            capitalized_sentences_parts.append(sentences[i+1])
            
    return "".join(capitalized_sentences_parts).strip()


def apply_fastformat(text: str) -> str:
    """
    Aplica todas as regras de formatação do FastFormat ao texto fornecido.
    """
    if not isinstance(text, str) or not text:
        return text # Retorna o texto original se não for string ou estiver vazio

    text = normalize_whitespace(text)
    text = remove_excess_newlines(text)
    text = standardize_quotes(text)
    # Aplica capitalize_sentences por último para garantir que os outros passos não interfiram
    text = capitalize_sentences(text) 
    
    return text
