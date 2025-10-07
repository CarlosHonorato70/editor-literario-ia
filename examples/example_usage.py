#!/usr/bin/env python3
"""
Exemplos de Uso do Sistema de Preparação de Manuscritos
"""

import sys
sys.path.insert(0, '..')

from modules.config import Config, CONFIG_TEMPLATES
from main import ManuscriptPublisher

# =============================================================================
# EXEMPLO 1: Uso Básico
# =============================================================================

def example_basic():
    """Exemplo básico de processamento."""
    print("="*60)
    print("EXEMPLO 1: Uso Básico")
    print("="*60)
    
    publisher = ManuscriptPublisher()
    
    results = publisher.process_manuscript(
        input_path="sample_manuscript.pdf",
        output_path="output_basic/"
    )
    
    if "error" not in results:
        print(f"\n✅ Sucesso! Arquivos em: {results['output_directory']}")
    else:
        print(f"\n❌ Erro: {results['error']}")

# =============================================================================
# EXEMPLO 2: Livro Acadêmico
# =============================================================================

def example_academic():
    """Exemplo para livro acadêmico."""
    print("\n" + "="*60)
    print("EXEMPLO 2: Livro Acadêmico")
    print("="*60)
    
    # Usa template acadêmico
    config = CONFIG_TEMPLATES['academic']
    
    publisher = ManuscriptPublisher(config)
    
    results = publisher.process_manuscript(
        input_path="academic_thesis.pdf",
        output_path="output_academic/"
    )
    
    if "error" not in results:
        print(f"\n✅ Livro acadêmico processado!")
        print(f"📁 Localização: {results['output_directory']}")
        print(f"📊 Arquivos gerados: {len(results['files_generated'])}")

# =============================================================================
# EXEMPLO 3: Romance/Ficção
# =============================================================================

def example_fiction():
    """Exemplo para romance/ficção."""
    print("\n" + "="*60)
    print("EXEMPLO 3: Romance/Ficção")
    print("="*60)
    
    # Usa template de ficção
    config = CONFIG_TEMPLATES['fiction']
    
    publisher = ManuscriptPublisher(config)
    
    results = publisher.process_manuscript(
        input_path="novel.docx",
        output_path="output_fiction/"
    )
    
    if "error" not in results:
        print(f"\n✅ Romance processado!")

# =============================================================================
# EXEMPLO 4: Configuração Customizada
# =============================================================================

def example_custom_config():
    """Exemplo com configuração customizada."""
    print("\n" + "="*60)
    print("EXEMPLO 4: Configuração Customizada")
    print("="*60)
    
    # Cria configuração customizada
    config = Config()
    config.default_format = "A4"
    config.default_font = "Arial"
    config.default_font_size = 11
    config.enable_ai_enhancement = True
    config.generate_glossary = True
    config.export_formats = ["md", "docx", "pdf"]
    
    publisher = ManuscriptPublisher(config)
    
    results = publisher.process_manuscript(
        input_path="custom_manuscript.pdf",
        output_path="output_custom/"
    )
    
    if "error" not in results:
        print(f"\n✅ Manuscrito customizado processado!")

# =============================================================================
# EXEMPLO 5: Processamento em Lote
# =============================================================================

def example_batch_processing():
    """Exemplo de processamento em lote."""
    print("\n" + "="*60)
    print("EXEMPLO 5: Processamento em Lote")
    print("="*60)
    
    manuscripts = [
        ("manuscript1.pdf", "output1/"),
        ("manuscript2.docx", "output2/"),
        ("manuscript3.md", "output3/")
    ]
    
    publisher = ManuscriptPublisher()
    
    for input_file, output_dir in manuscripts:
        print(f"\nProcessando: {input_file}")
        
        results = publisher.process_manuscript(input_file, output_dir)
        
        if "error" not in results:
            print(f"✅ {input_file} → {output_dir}")
        else:
            print(f"❌ {input_file}: {results['error']}")

# =============================================================================
# EXEMPLO 6: Apenas Análise (sem processamento completo)
# =============================================================================

def example_analysis_only():
    """Exemplo de apenas análise."""
    print("\n" + "="*60)
    print("EXEMPLO 6: Apenas Análise")
    print("="*60)
    
    from modules.analyzer import ManuscriptAnalyzer
    
    config = Config()
    analyzer = ManuscriptAnalyzer(config)
    
    analysis = analyzer.analyze("manuscript.pdf")
    
    if "error" not in analysis:
        print(f"\n📊 Análise Completa:")
        print(f"  • Palavras: {analysis['metadata']['word_count']:,}")
        print(f"  • Páginas: {analysis['metadata']['page_count']}")
        print(f"  • Capítulos: {len(analysis['structure']['chapters'])}")
        print(f"  • Qualidade: {analysis['quality']['overall_score']:.2f}/1.0")
        
        # Salva análise
        analyzer.save_analysis(analysis, "analysis_report.md")
        print(f"\n✅ Relatório salvo em: analysis_report.md")

# =============================================================================
# EXEMPLO 7: Configuração via Arquivo YAML
# =============================================================================

def example_yaml_config():
    """Exemplo usando arquivo de configuração YAML."""
    print("\n" + "="*60)
    print("EXEMPLO 7: Configuração via YAML")
    print("="*60)
    
    from modules.config import load_config
    
    # Carrega configuração de arquivo
    config = load_config("../configs/academic.yaml")
    
    # Modifica algumas opções
    config.enable_ai_enhancement = True
    config.export_formats = ["md", "pdf"]
    
    publisher = ManuscriptPublisher(config)
    
    results = publisher.process_manuscript(
        input_path="manuscript.pdf",
        output_path="output_yaml/"
    )
    
    if "error" not in results:
        print(f"\n✅ Processado com config YAML!")

# =============================================================================
# EXEMPLO 8: Tratamento de Erros
# =============================================================================

def example_error_handling():
    """Exemplo de tratamento de erros."""
    print("\n" + "="*60)
    print("EXEMPLO 8: Tratamento de Erros")
    print("="*60)
    
    publisher = ManuscriptPublisher()
    
    try:
        results = publisher.process_manuscript(
            input_path="nonexistent_file.pdf",
            output_path="output/"
        )
        
        if "error" in results:
            print(f"❌ Erro capturado: {results['error']}")
            
            # Tenta com arquivo alternativo
            print("\nTentando arquivo alternativo...")
            results = publisher.process_manuscript(
                input_path="backup_manuscript.pdf",
                output_path="output/"
            )
            
            if "error" not in results:
                print("✅ Sucesso com arquivo alternativo!")
    
    except Exception as e:
        print(f"❌ Exceção: {e}")

# =============================================================================
# EXEMPLO 9: Exportação Seletiva
# =============================================================================

def example_selective_export():
    """Exemplo de exportação seletiva de formatos."""
    print("\n" + "="*60)
    print("EXEMPLO 9: Exportação Seletiva")
    print("="*60)
    
    # Apenas Markdown
    config = Config()
    config.export_formats = ["md"]
    
    publisher = ManuscriptPublisher(config)
    results = publisher.process_manuscript("manuscript.pdf", "output_md/")
    
    # Apenas DOCX
    config.export_formats = ["docx"]
    publisher = ManuscriptPublisher(config)
    results = publisher.process_manuscript("manuscript.pdf", "output_docx/")
    
    # Todos os formatos
    config.export_formats = ["md", "docx", "pdf"]
    publisher = ManuscriptPublisher(config)
    results = publisher.process_manuscript("manuscript.pdf", "output_all/")
    
    print("✅ Exportações seletivas concluídas!")

# =============================================================================
# EXEMPLO 10: Integração com Pipeline
# =============================================================================

def example_pipeline_integration():
    """Exemplo de integração em pipeline."""
    print("\n" + "="*60)
    print("EXEMPLO 10: Integração com Pipeline")
    print("="*60)
    
    def preprocessing(input_file):
        """Pré-processamento customizado."""
        print(f"  → Pré-processando: {input_file}")
        # Adicione lógica de pré-processamento aqui
        return input_file
    
    def postprocessing(results):
        """Pós-processamento customizado."""
        print(f"  → Pós-processando resultados")
        # Adicione lógica de pós-processamento aqui
        return results
    
    # Pipeline completo
    input_file = "manuscript.pdf"
    
    # 1. Pré-processamento
    processed_input = preprocessing(input_file)
    
    # 2. Processamento principal
    publisher = ManuscriptPublisher()
    results = publisher.process_manuscript(processed_input, "output_pipeline/")
    
    # 3. Pós-processamento
    if "error" not in results:
        final_results = postprocessing(results)
        print("✅ Pipeline completo executado!")

# =============================================================================
# EXECUTAR EXEMPLOS
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("EXEMPLOS DE USO - MANUSCRIPT PUBLISHER")
    print("="*60)
    
    # Descomente o exemplo que deseja executar:
    
    # example_basic()
    # example_academic()
    # example_fiction()
    # example_custom_config()
    # example_batch_processing()
    example_analysis_only()
    # example_yaml_config()
    # example_error_handling()
    # example_selective_export()
    # example_pipeline_integration()
    
    print("\n" + "="*60)
    print("Exemplos concluídos!")
    print("="*60)
