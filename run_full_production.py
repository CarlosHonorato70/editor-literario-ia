import sys
import os
from pathlib import Path
from typing import Dict

# Adicionar o diretório raiz do projeto ao path para importar módulos
sys.path.append(str(Path(__file__).parent))

from modules.production.pipeline import process_book
from modules.utils import print_info, print_success, print_error

def run_production_example():
    """Executa o pipeline de produção completo com metadados de exemplo."""
    
    # --- 1. Configuração ---
    
    # O manuscrito de exemplo está no diretório raiz
    manuscript_path = "manuscrito_exemplo.md"
    
    # O diretório de saída será criado dentro do projeto
    output_dir = "output_producao_final"
    
    # Metadados do livro (essenciais para a capa e materiais)
    metadata: Dict = {
        "title": "O Segredo da Máquina do Tempo",
        "subtitle": "Crônicas do Crononauta",
        "author": "Elias Chronos",
        "genre": "fiction",
        "description": "Uma aventura épica sobre um relojoeiro que constrói uma máquina do tempo e descobre que a história é mais frágil do que ele imaginava.",
        "blurb": "O cheiro de ozônio e metal enferrujado era a primeira coisa que atingia qualquer um que ousasse entrar no laboratório de Elias. Ele não era um cientista no sentido tradicional, mas um artesão da cronologia, um relojoeiro do impossível. Agora, ele deve usar sua invenção para corrigir um paradoxo que ameaça apagar o próprio tecido da realidade. Uma jornada emocionante através da história, onde a única coisa mais difícil do que viajar no tempo é convencer um editor de que você o fez.",
        "isbn": "978-65-80000-00-1" # ISBN de exemplo
    }
    
    # --- 2. Execução do Pipeline ---
    
    print_info(f"Iniciando o pipeline de produção para: {metadata['title']}")
    print_info(f"Verifique se a variável de ambiente OPENAI_API_KEY está configurada.")
    
    try:
        # O pipeline completo inclui: Capa, Diagramação, Revisão de Provas e Materiais Adicionais
        results = process_book(
            manuscript_path=manuscript_path,
            metadata=metadata,
            output_dir=output_dir,
            format='6x9', # Formato comum para ficção
            genre='fiction',
            use_ai=True, # Usar IA para gerar imagens de capa e materiais
            # A chave de API será lida automaticamente da variável de ambiente OPENAI_API_KEY
        )
        
        # --- 3. Verificação dos Resultados ---
        
        if results.get('error'):
            print_error(f"O pipeline falhou: {results['error']}")
            return
        
        print_success("\n✅ Processamento completo concluído com sucesso!")
        
        # Detalhes da Capa
        cover_results = results.get('cover', {})
        if cover_results.get('status') == 'success':
            print_info(f"\n🎨 Capas Completas Geradas ({len(cover_results.get('concepts', []))} conceitos):")
            for i, path in enumerate(cover_results['concepts'], 1):
                print(f"   - Conceito {i}: {path}")
        
        # Detalhes da Diagramação (Pronto para Impressão)
        layout_results = results.get('layout', {})
        if layout_results.get('status') == 'success':
            print_info("\n📦 Arquivos de Impressão:")
            print(f"   - PDF Final: {layout_results['pdf']}")
            print(f"   - PDF Pronto para Gráfica (Print Ready): {layout_results['print_ready']}")
            print(f"   - Páginas Estimadas: {layout_results['statistics']['estimated_pages']}")
            
        print_info(f"\nTodos os arquivos estão no diretório: {Path(output_dir) / Path(metadata['title']).stem.lower().replace(' ', '-')}")
        
    except RuntimeError as e:
        # Captura erros de dependência (como a falta de PyPDF2 ou python-docx)
        print_error(f"\n❌ Erro de Configuração/Dependência: {e}")
    except Exception as e:
        print_error(f"\n❌ Erro Inesperado durante a execução: {e}")

if __name__ == "__main__":
    run_production_example()
