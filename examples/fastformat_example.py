#!/usr/bin/env python3
"""
Exemplo de uso do FastFormat no Editor Literário IA.

Este script demonstra como usar o FastFormat para formatar texto
com tipografia profissional.
"""

from modules.fastformat_utils import (
    apply_fastformat,
    get_ptbr_options,
    get_academic_options,
    format_with_diff
)

def print_separator():
    print("\n" + "=" * 70 + "\n")

def exemplo_basico():
    """Exemplo básico de uso do FastFormat."""
    print_separator()
    print("📝 EXEMPLO 1: Uso Básico")
    print_separator()
    
    texto_original = '''
    Texto com "aspas retas"... e varios  espacos.
    - Este é um dialogo
    - Outro dialogo
    E um intervalo: 10-20 anos.
    '''
    
    print("Texto Original:")
    print(texto_original)
    
    # Aplica FastFormat com opções PT-BR
    texto_formatado = apply_fastformat(texto_original, get_ptbr_options())
    
    print("\nTexto Formatado:")
    print(texto_formatado)

def exemplo_comparacao():
    """Compara presets PT-BR vs Acadêmico."""
    print_separator()
    print("🔄 EXEMPLO 2: Comparação de Presets")
    print_separator()
    
    texto = '- Dialogo com "aspas"... e intervalos 10-20.'
    
    print("Texto Original:")
    print(repr(texto))
    
    # PT-BR (Ficção)
    ptbr = apply_fastformat(texto, get_ptbr_options())
    print("\nPreset PT-BR (Ficção):")
    print(repr(ptbr))
    
    # Acadêmico
    academic = apply_fastformat(texto, get_academic_options())
    print("\nPreset Acadêmico:")
    print(repr(academic))
    
    print("\n📊 Diferenças:")
    print("- PT-BR usa EM-DASH (—) para diálogos")
    print("- Acadêmico usa HÍFEN (-) para diálogos")
    print("- Ambos usam EN-DASH (–) para intervalos")

def exemplo_com_diff():
    """Mostra diff das mudanças."""
    print_separator()
    print("📊 EXEMPLO 3: Visualizar Mudanças (Diff)")
    print_separator()
    
    texto = '''
    "Citacao com aspas retas"
    - Dialogo 1
    - Dialogo 2
    Reticencias... e espacos  extras.
    Intervalo: 10-20 anos.
    '''
    
    # Aplica FastFormat e gera diff
    texto_formatado, diff = format_with_diff(texto, get_ptbr_options())
    
    print("Unified Diff das Mudanças:")
    print(diff)

def exemplo_literatura():
    """Exemplo com texto literário real."""
    print_separator()
    print("📚 EXEMPLO 4: Texto Literário")
    print_separator()
    
    texto = '''
    - Onde você estava? - perguntou ela.
    - Por ai... - respondeu vagamente. - Fazendo umas coisas.
    Ela suspirou. Entre 20-30 minutos, ele sempre desaparecia assim.
    "Sera que posso confiar nele?" pensou.
    '''
    
    print("Antes da Formatação:")
    print(texto)
    
    texto_formatado = apply_fastformat(texto, get_ptbr_options())
    
    print("\nDepois da Formatação:")
    print(texto_formatado)
    
    print("\n✨ Melhorias Aplicadas:")
    print("- Travessões (—) nos diálogos")
    print('- Aspas tipográficas ("texto")')
    print("- Reticências padronizadas (…)")
    print("- En-dash para intervalos (20–30)")
    print("- Espaçamento normalizado")

def exemplo_customizado():
    """Exemplo com opções customizadas."""
    print_separator()
    print("⚙️ EXEMPLO 5: Opções Customizadas")
    print_separator()
    
    from fastformat import FastFormatOptions
    
    # Cria opções customizadas
    opcoes = FastFormatOptions(
        normalize_whitespace=True,
        quotes_style="straight",  # Mantém aspas retas
        dialogue_dash="hyphen",   # Usa hífen para diálogos
        normalize_ellipsis=True,  # Mas normaliza reticências
        number_range_dash="endash"  # E usa en-dash para intervalos
    )
    
    texto = '- Dialogo com "aspas"... e 10-20 anos.'
    
    print("Texto Original:")
    print(repr(texto))
    
    formatado = apply_fastformat(texto, opcoes)
    
    print("\nCom Opções Customizadas:")
    print(repr(formatado))
    print("\n📝 Configurações:")
    print("- Aspas: RETAS (straight)")
    print("- Diálogos: HÍFEN (-)")
    print("- Reticências: NORMALIZADAS (…)")
    print("- Intervalos: EN-DASH (–)")

def main():
    """Executa todos os exemplos."""
    print("\n" + "=" * 70)
    print("  ✨ EXEMPLOS DE USO DO FASTFORMAT")
    print("  Editor Literário IA")
    print("=" * 70)
    
    exemplos = [
        exemplo_basico,
        exemplo_comparacao,
        exemplo_com_diff,
        exemplo_literatura,
        exemplo_customizado
    ]
    
    for exemplo in exemplos:
        try:
            exemplo()
        except Exception as e:
            print(f"\n❌ Erro no exemplo: {e}")
            import traceback
            traceback.print_exc()
    
    print_separator()
    print("✅ Todos os exemplos executados!")
    print("\n📚 Para mais informações, consulte: FASTFORMAT_DOCS.md")
    print_separator()

if __name__ == '__main__':
    main()
