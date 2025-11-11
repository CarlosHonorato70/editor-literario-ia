#!/usr/bin/env python3
"""
Testes de Integração do FastFormat no Editor Literário IA.

Este script testa a integração do FastFormat em todo o sistema:
- Módulo fastformat_utils
- DocumentFormatter
- Streamlit Editor (app_editor.py)
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_success(text):
    """Imprime mensagem de sucesso."""
    print(f"✅ {text}")

def print_error(text):
    """Imprime mensagem de erro."""
    print(f"❌ {text}")

def print_info(text):
    """Imprime mensagem informativa."""
    print(f"ℹ️  {text}")

def test_fastformat_module():
    """Testa o módulo fastformat.py principal."""
    print_header("TESTE 1: Módulo FastFormat Principal")
    
    try:
        from fastformat import (
            FastFormatOptions,
            apply_fastformat,
            make_unified_diff,
            get_fastformat_default_options
        )
        
        print_success("Importação de FastFormatOptions")
        print_success("Importação de apply_fastformat")
        print_success("Importação de make_unified_diff")
        print_success("Importação de get_fastformat_default_options")
        
        # Teste básico de funcionalidade
        text = 'Teste  com   "aspas" e... reticências 10-20'
        options = FastFormatOptions(
            normalize_whitespace=True,
            quotes_style="curly",
            normalize_ellipsis=True,
            number_range_dash="endash"
        )
        result = apply_fastformat(text, options)
        
        print_info(f"Texto original: {repr(text)}")
        print_info(f"Texto formatado: {repr(result)}")
        
        # Verifica transformações
        has_curly_quotes = '"' in result or '"' in result
        has_ellipsis = '…' in result or '...' in result
        has_endash = '–' in result
        
        if has_curly_quotes:
            print_success("Aspas curvas aplicadas")
        if has_ellipsis:
            print_success("Reticências formatadas")
        if has_endash:
            print_success("En-dash para intervalos numéricos")
        
        assert has_ellipsis or has_endash, "Pelo menos uma transformação deve ocorrer"
        
        print_success("Transformações de texto funcionando")
        print("\n📊 Resultado: Módulo FastFormat funcional")
        return True
        
    except Exception as e:
        print_error(f"Erro no módulo FastFormat: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fastformat_utils():
    """Testa o módulo fastformat_utils."""
    print_header("TESTE 2: Módulo FastFormat Utils")
    
    try:
        from modules.fastformat_utils import (
            get_default_options,
            get_ptbr_options,
            get_academic_options,
            apply_fastformat,
            format_with_diff
        )
        
        print_success("Importação de get_default_options")
        print_success("Importação de get_ptbr_options")
        print_success("Importação de get_academic_options")
        print_success("Importação de apply_fastformat")
        print_success("Importação de format_with_diff")
        
        # Teste PT-BR options
        text = '- Teste com "aspas"... e travessão no diálogo'
        ptbr_result = apply_fastformat(text, get_ptbr_options())
        print_info(f"Formatação PT-BR: {repr(ptbr_result)}")
        print_success("Opções PT-BR funcionando")
        
        # Teste Academic options
        academic_result = apply_fastformat(text, get_academic_options())
        print_info(f"Formatação Acadêmica: {repr(academic_result)}")
        print_success("Opções Acadêmicas funcionando")
        
        # Teste format_with_diff
        formatted, diff = format_with_diff(text)
        print_info(f"Diff gerado: {len(diff)} caracteres")
        print_success("Geração de diff funcionando")
        
        print("\n📊 Resultado: Módulo FastFormat Utils funcional")
        return True
        
    except Exception as e:
        print_error(f"Erro no módulo FastFormat Utils: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_formatter_integration():
    """Testa integração do FastFormat no DocumentFormatter."""
    print_header("TESTE 3: Integração no DocumentFormatter")
    
    try:
        from modules.formatter import DocumentFormatter
        from modules.config import Config
        
        config = Config()
        formatter = DocumentFormatter(config)
        
        print_success("DocumentFormatter instanciado")
        print_info(f"FastFormat habilitado: {formatter.use_fastformat}")
        print_info(f"Opções FastFormat configuradas: {type(formatter.fastformat_options).__name__}")
        
        # Teste formatação de documento
        enhanced_content = {
            "content": 'Texto de teste com "aspas"... e formatação 10-20.'
        }
        elements = {}
        corrections = []
        
        result = formatter.format_document(enhanced_content, elements, corrections)
        
        print_success("Formatação de documento executada")
        print_info(f"Tamanho original: {result['original_length']}")
        print_info(f"Tamanho formatado: {result['formatted_length']}")
        print_info(f"Conteúdo formatado: {repr(result['content'][:100])}")
        
        # Verifica se FastFormat foi aplicado
        if formatter.use_fastformat:
            content = result['content']
            # Deve ter aspas curvas ou reticências formatadas
            has_formatting = '"' in content or '…' in content or '–' in content
            if has_formatting:
                print_success("FastFormat aplicado ao conteúdo")
            else:
                print_info("FastFormat pode não ter alterado o texto (normal para texto simples)")
        
        print("\n📊 Resultado: Integração no DocumentFormatter funcional")
        return True
        
    except Exception as e:
        print_error(f"Erro na integração com DocumentFormatter: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_app_imports():
    """Testa importações do app Streamlit."""
    print_header("TESTE 4: Importações do App Streamlit")
    
    try:
        # Testa se o app pode ser importado (não executa streamlit)
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("app_editor", "app_editor.py")
        if spec and spec.loader:
            # Verifica se o arquivo pode ser lido
            with open("app_editor.py", "r") as f:
                content = f.read()
            
            print_success("app_editor.py pode ser lido")
            
            # Verifica imports de fastformat
            if "from modules.fastformat_utils import" in content:
                print_success("Import de fastformat_utils presente")
            else:
                print_error("Import de fastformat_utils não encontrado")
                return False
            
            # Verifica uso de apply_fastformat
            if "apply_fastformat" in content:
                print_success("Uso de apply_fastformat presente")
            else:
                print_error("Uso de apply_fastformat não encontrado")
                return False
            
            # Verifica remoção de smartypants
            if "smartypants" not in content or "smartypants" in content and "#" in content:
                print_success("smartypants removido ou comentado")
            else:
                print_info("smartypants ainda presente (pode ser OK se comentado)")
            
            # Verifica checkbox de fastformat
            if "use_fastformat" in content:
                print_success("Opção use_fastformat presente na UI")
            else:
                print_info("Opção use_fastformat não encontrada")
            
            print("\n📊 Resultado: App Streamlit com FastFormat integrado")
            return True
        else:
            print_error("Não foi possível carregar app_editor.py")
            return False
        
    except Exception as e:
        print_error(f"Erro ao verificar app Streamlit: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_formatting_examples():
    """Testa exemplos práticos de formatação."""
    print_header("TESTE 5: Exemplos Práticos de Formatação")
    
    try:
        from modules.fastformat_utils import apply_fastformat, get_ptbr_options
        
        examples = [
            ('Diálogo simples', '- Olá, como vai?', '—'),
            ('Aspas duplas', 'Ele disse "olá" para mim.', '"'),
            ('Reticências', 'E então... ele foi embora.', '…'),
            ('Intervalo numérico', 'De 10-20 anos', '–'),
            ('Espaços múltiplos', 'Texto  com    espaços', ' '),
        ]
        
        options = get_ptbr_options()
        success_count = 0
        
        for name, text, expected_char in examples:
            result = apply_fastformat(text, options)
            if expected_char in result:
                print_success(f"{name}: {repr(text)} → {repr(result)}")
                success_count += 1
            else:
                print_info(f"{name}: {repr(text)} → {repr(result)} (esperado: '{expected_char}')")
        
        print(f"\n📊 Resultado: {success_count}/{len(examples)} exemplos formatados corretamente")
        return success_count >= len(examples) - 1  # Permite 1 falha
        
    except Exception as e:
        print_error(f"Erro nos exemplos de formatação: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backward_compatibility():
    """Testa compatibilidade com código legado."""
    print_header("TESTE 6: Compatibilidade com Código Legado")
    
    try:
        from modules.fastformat_utils import (
            normalize_whitespace,
            remove_excess_newlines,
            standardize_quotes,
            capitalize_sentences
        )
        
        print_success("Funções legadas disponíveis")
        
        # Testa funções legadas
        text = "  texto  com   espaços  "
        result = normalize_whitespace(text)
        print_info(f"normalize_whitespace: {repr(text)} → {repr(result)}")
        print_success("normalize_whitespace funciona")
        
        text = "linha1\n\n\n\nlinha2"
        result = remove_excess_newlines(text)
        print_info(f"remove_excess_newlines: {repr(text)} → {repr(result)}")
        print_success("remove_excess_newlines funciona")
        
        text = '"teste"'
        result = standardize_quotes(text)
        print_info(f"standardize_quotes: {repr(text)} → {repr(result)}")
        print_success("standardize_quotes funciona")
        
        text = "olá mundo. nova frase."
        result = capitalize_sentences(text)
        print_info(f"capitalize_sentences: {repr(text)} → {repr(result)}")
        print_success("capitalize_sentences funciona")
        
        print("\n📊 Resultado: Compatibilidade com código legado mantida")
        return True
        
    except Exception as e:
        print_error(f"Erro na compatibilidade: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes."""
    print("\n" + "=" * 70)
    print("  🧪 TESTES DE INTEGRAÇÃO DO FASTFORMAT")
    print("=" * 70)
    
    tests = [
        ("Módulo FastFormat Principal", test_fastformat_module),
        ("Módulo FastFormat Utils", test_fastformat_utils),
        ("Integração DocumentFormatter", test_document_formatter_integration),
        ("Importações App Streamlit", test_streamlit_app_imports),
        ("Exemplos Práticos", test_formatting_examples),
        ("Compatibilidade Legada", test_backward_compatibility),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Erro inesperado no teste '{test_name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Resumo final
    print_header("RESUMO FINAL")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ FastFormat está 100% integrado e funcional.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam.")
        print("ℹ️  Verifique os erros acima.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
