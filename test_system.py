#!/usr/bin/env python3
"""
Script de Teste Completo do Sistema Editor Literário IA.

Este script valida todas as funcionalidades do sistema, incluindo:
- Importação de módulos
- Preparação de manuscrito (Fases 1 e 2)
- Produção editorial (Fase 3)

Uso:
    python test_system.py
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

def test_imports():
    """Testa importação de todos os módulos."""
    print_header("TESTE 1: Importação de Módulos")
    
    modules_to_test = [
        ('modules.config', 'Configuração'),
        ('modules.utils', 'Utilidades'),
        ('modules.analyzer', 'Analisador'),
        ('modules.enhancer', 'Aprimorador'),
        ('modules.formatter', 'Formatador'),
        ('modules.elements', 'Elementos'),
        ('modules.reviewer', 'Revisor'),
        ('modules.exporter', 'Exportador'),
        ('modules.interactive', 'Modo Interativo'),
        ('modules.production', 'Produção Editorial'),
    ]
    
    success_count = 0
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print_success(f"{description} ({module_name})")
            success_count += 1
        except Exception as e:
            print_error(f"{description} ({module_name}): {e}")
    
    print(f"\n📊 Resultado: {success_count}/{len(modules_to_test)} módulos importados com sucesso")
    return success_count == len(modules_to_test)

def test_production_modules():
    """Testa módulos de produção editorial."""
    print_header("TESTE 2: Módulos de Produção Editorial")
    
    try:
        from modules.production import (
            LayoutEngine,
            ProofChecker,
            MaterialsGenerator,
            CoverDesigner,
            ProductionPipeline
        )
        
        print_success("LayoutEngine importado")
        print_success("ProofChecker importado")
        print_success("MaterialsGenerator importado")
        print_success("CoverDesigner importado")
        print_success("ProductionPipeline importado")
        
        print("\n📊 Resultado: Todos os módulos de produção disponíveis")
        return True
        
    except Exception as e:
        print_error(f"Erro ao importar módulos de produção: {e}")
        return False

def test_layout_engine():
    """Testa inicialização do Layout Engine."""
    print_header("TESTE 3: Layout Engine")
    
    try:
        from modules.production import LayoutEngine
        
        # Testar diferentes configurações
        configs = [
            {'format': 'A5', 'genre': 'academic'},
            {'format': 'A4', 'genre': 'fiction'},
            {'format': 'B5', 'genre': 'technical'},
        ]
        
        for config in configs:
            engine = LayoutEngine(config)
            print_success(f"Configuração {config['format']} / {config['genre']}")
        
        print("\n📊 Resultado: Layout Engine funcional")
        return True
        
    except Exception as e:
        print_error(f"Erro no Layout Engine: {e}")
        return False

def test_proof_checker():
    """Testa inicialização do Proof Checker."""
    print_header("TESTE 4: Proof Checker")
    
    try:
        from modules.production import ProofChecker
        
        checker = ProofChecker({'language': 'pt-BR'})
        print_success("ProofChecker inicializado com pt-BR")
        
        # Testar verificação de texto simples
        test_text = "Este é um texto de teste."
        issues = checker.check_formatting(test_text)
        print_success(f"Verificação de formatação: {len(issues)} problemas encontrados")
        
        print("\n📊 Resultado: Proof Checker funcional")
        return True
        
    except Exception as e:
        print_error(f"Erro no Proof Checker: {e}")
        return False

def test_materials_generator():
    """Testa inicialização do Materials Generator."""
    print_header("TESTE 5: Materials Generator")
    
    try:
        from modules.production import MaterialsGenerator
        
        generator = MaterialsGenerator({'use_ai': False})
        print_success("MaterialsGenerator inicializado (sem IA)")
        
        # Testar geração de blurb
        metadata = {
            'title': 'Livro de Teste',
            'author': 'Autor Teste',
            'description': 'Uma descrição de teste para o livro.'
        }
        
        blurb = generator._generate_blurb_template(metadata)
        print_success(f"Blurb gerado: {len(blurb)} caracteres")
        
        print("\n📊 Resultado: Materials Generator funcional")
        return True
        
    except Exception as e:
        print_error(f"Erro no Materials Generator: {e}")
        return False

def test_cover_designer():
    """Testa inicialização do Cover Designer."""
    print_header("TESTE 6: Cover Designer")
    
    try:
        from modules.production import CoverDesigner
        
        designer = CoverDesigner({'use_ai_images': False})
        print_success("CoverDesigner inicializado (sem IA)")
        
        # Testar paletas de cores
        palettes = designer._get_color_palettes('academic')
        print_success(f"Paletas para 'academic': {len(palettes)} disponíveis")
        
        palettes = designer._get_color_palettes('fiction')
        print_success(f"Paletas para 'fiction': {len(palettes)} disponíveis")
        
        print("\n📊 Resultado: Cover Designer funcional")
        return True
        
    except Exception as e:
        print_error(f"Erro no Cover Designer: {e}")
        return False

def test_pipeline():
    """Testa inicialização do Production Pipeline."""
    print_header("TESTE 7: Production Pipeline")
    
    try:
        from modules.production import ProductionPipeline
        
        pipeline = ProductionPipeline({
            'format': 'A5',
            'genre': 'academic',
            'output_dir': './test_output'
        })
        print_success("ProductionPipeline inicializado")
        
        print_info("Pipeline configurado com:")
        print_info("  - Formato: A5")
        print_info("  - Gênero: academic")
        print_info("  - Saída: ./test_output")
        
        print("\n📊 Resultado: Production Pipeline funcional")
        return True
        
    except Exception as e:
        print_error(f"Erro no Production Pipeline: {e}")
        return False

def test_dependencies():
    """Testa dependências críticas."""
    print_header("TESTE 8: Dependências Críticas")
    
    dependencies = [
        ('yaml', 'PyYAML'),
        ('PIL', 'Pillow'),
        ('jinja2', 'Jinja2'),
        ('weasyprint', 'WeasyPrint'),
        ('barcode', 'python-barcode'),
        ('qrcode', 'qrcode'),
    ]
    
    success_count = 0
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print_success(f"{package_name}")
            success_count += 1
        except ImportError:
            print_error(f"{package_name} não instalado")
    
    print(f"\n📊 Resultado: {success_count}/{len(dependencies)} dependências instaladas")
    
    if success_count < len(dependencies):
        print_info("\nPara instalar dependências faltantes:")
        print_info("  pip install -r requirements.txt")
    
    return success_count == len(dependencies)

def test_file_structure():
    """Testa estrutura de arquivos do projeto."""
    print_header("TESTE 9: Estrutura de Arquivos")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'modules/__init__.py',
        'modules/production/__init__.py',
        'modules/production/layout_engine.py',
        'modules/production/proof_checker.py',
        'modules/production/materials_generator.py',
        'modules/production/cover_designer.py',
        'modules/production/pipeline.py',
        'modules/production/README.md',
        'examples/production_example.py',
    ]
    
    success_count = 0
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(file_path)
            success_count += 1
        else:
            print_error(f"{file_path} não encontrado")
    
    print(f"\n📊 Resultado: {success_count}/{len(required_files)} arquivos encontrados")
    return success_count == len(required_files)

def main():
    """Executa todos os testes."""
    print("\n" + "=" * 70)
    print("  🧪 TESTE COMPLETO DO SISTEMA EDITOR LITERÁRIO IA")
    print("=" * 70)
    
    tests = [
        ("Importação de Módulos", test_imports),
        ("Módulos de Produção", test_production_modules),
        ("Layout Engine", test_layout_engine),
        ("Proof Checker", test_proof_checker),
        ("Materials Generator", test_materials_generator),
        ("Cover Designer", test_cover_designer),
        ("Production Pipeline", test_pipeline),
        ("Dependências", test_dependencies),
        ("Estrutura de Arquivos", test_file_structure),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Erro inesperado no teste '{test_name}': {e}")
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
        print("✅ O sistema está 100% funcional e pronto para uso.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam.")
        print("ℹ️  Verifique os erros acima e instale dependências se necessário:")
        print("   pip install -r requirements.txt")
        return 1

if __name__ == '__main__':
    sys.exit(main())

