#!/usr/bin/env python3
"""
Script de Diagnóstico - Verifica se todas as dependências estão instaladas
"""

import sys
import importlib

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

for module_name, description, is_critical in dependencies:
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name:25} - {description}")
    except ImportError:
        print(f"❌ {module_name:25} - {description} [FALTANDO]")
        if is_critical:
            missing_critical.append(module_name)
        else:
            missing_optional.append(module_name)

print()
print("="*60)

if missing_critical:
    print("⚠️  ATENÇÃO: Dependências críticas faltando!")
    print()
    print("Para instalar as dependências críticas:")
    print()
    print("  pip install " + " ".join(missing_critical))
    print()
    print("Ou reinstale todas as dependências:")
    print()
    print("  pip install -r requirements.txt")
    print()
    sys.exit(1)
elif missing_optional:
    print("✅ Todas as dependências críticas estão instaladas!")
    print()
    print("⚠️  Algumas dependências opcionais estão faltando:")
    for module in missing_optional:
        print(f"   - {module}")
    print()
    print("Para instalar todas as dependências:")
    print()
    print("  pip install -r requirements.txt")
    print()
else:
    print("✅ Todas as dependências estão instaladas!")
    print()
    print("🚀 Você está pronto para usar o Adapta ONE!")
    print()
    print("Execute: streamlit run app_editor.py")
    print()

print("="*60)
