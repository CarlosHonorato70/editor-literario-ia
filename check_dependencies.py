#!/usr/bin/env python3
"""
Script de Diagnóstico - Verifica se todas as dependências estão instaladas
"""

import sys
import importlib
import warnings

# Suprimir warnings durante import
warnings.filterwarnings("ignore")

print("="*60)
print("  Diagnóstico de Dependências - Adapta ONE")
print("="*60)
print()

# Lista de dependências críticas
dependencies = [
    ("streamlit", "Framework da interface", True),
    ("streamlit_quill", "Editor Avançado (Word-like)", True),
    ("docx", "Processamento de documentos DOCX", True),
    ("PyPDF2", "Processamento de documentos PDF", False),
    ("openai", "Sugestões de IA (opcional)", False),
    ("language_tool_python", "Revisão gramatical", False),
    ("PIL", "Processamento de imagens", False),
    ("markdown", "Conversão de Markdown", False),
    ("weasyprint", "Geração de PDF", False),
    ("barcode", "Geração de códigos de barras", False),
    ("qrcode", "Geração de QR codes", False),
    ("reportlab", "Criação de PDFs", False),
]

missing_critical = []
missing_optional = []
has_warnings = []

for module_name, description, is_critical in dependencies:
    try:
        # Redirecionar stderr temporariamente para suprimir warnings
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            importlib.import_module(module_name)
        
        # Capturar warnings se houver
        stderr_output = f.getvalue()
        if stderr_output and "could not import" in stderr_output.lower():
            has_warnings.append((module_name, description))
            
        print(f"✅ {module_name:25} - {description}")
    except ImportError:
        print(f"❌ {module_name:25} - {description} [FALTANDO]")
        if is_critical:
            missing_critical.append(module_name)
        else:
            missing_optional.append(module_name)
    except Exception as e:
        # Capturar outros erros
        print(f"⚠️  {module_name:25} - {description} [ERRO: {type(e).__name__}]")
        if is_critical:
            missing_critical.append(module_name)

print()
print("="*60)

if missing_critical:
    print("⚠️  ATENÇÃO: Dependências críticas faltando!")
    print()
    print("Para instalar (Windows):")
    print()
    print("  py -m pip install " + " ".join(missing_critical))
    print()
    print("Ou reinstale todas as dependências:")
    print()
    print("  py -m pip install -r requirements.txt")
    print()
    print("="*60)
    sys.exit(1)
elif missing_optional:
    print("✅ Todas as dependências críticas estão instaladas!")
    print()
    if has_warnings:
        print("⚠️  Alguns módulos têm avisos (mas funcionam):")
        for module, desc in has_warnings:
            print(f"   - {module} ({desc})")
        print()
    print("⚠️  Algumas dependências opcionais estão faltando:")
    for module in missing_optional:
        print(f"   - {module}")
    print()
    print("Para instalar todas (Windows):")
    print()
    print("  py -m pip install -r requirements.txt")
    print()
    print("="*60)
else:
    print("✅ Todas as dependências estão instaladas!")
    print()
    if has_warnings:
        print("⚠️  Alguns módulos têm avisos (mas funcionam):")
        for module, desc in has_warnings:
            print(f"   - {module} ({desc})")
        print()
    print("🚀 Você está pronto para usar o Adapta ONE!")
    print()
    print("Execute (Windows):")
    print()
    print("  py -m streamlit run app_editor.py")
    print()
    print("Ou clique duas vezes em: run.bat")
    print()
    print("="*60)
