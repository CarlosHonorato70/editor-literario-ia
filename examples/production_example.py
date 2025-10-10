"""
Exemplo de uso do módulo de Produção Editorial.

Este exemplo demonstra como usar o pipeline completo para processar
um livro desde o manuscrito até os arquivos prontos para publicação.
"""

from modules.production import ProductionPipeline

def main():
    print("=" * 70)
    print("EXEMPLO: Pipeline de Produção Editorial")
    print("=" * 70)
    print()
    
    # Configurar pipeline
    pipeline = ProductionPipeline({
        'format': 'A5',  # Formato do livro
        'genre': 'academic',  # Gênero
        'language': 'pt-BR',  # Idioma
        'output_dir': './output_exemplo',  # Diretório de saída
        'use_ai': False  # Usar IA (requer OpenAI API key)
    })
    
    # Metadados do livro
    metadata = {
        'title': 'Modelo VIP',
        'subtitle': 'Uma Nova Síntese em Psicoterapia',
        'author': 'Dr. Carlos Honorato',
        'author_bio': 'Psicólogo clínico com 20 anos de experiência em psicoterapia integrativa.',
        'genre': 'academic',
        'description': 'Este livro apresenta o Modelo VIP, uma abordagem inovadora que integra os pilares fundamentais da psicoterapia: Vínculo, Imagem e Palavra.',
        'isbn': '978-85-1234-567-8',
        'publisher': 'Editora Acadêmica',
        'publication_year': 2025,
        'target_audience': 'Psicólogos, terapeutas e estudantes de psicologia',
        'subject_code': '150',
        'price_amount': '89.90',
        'url': 'https://editora.com/modelo-vip',
        'press_contact_email': 'contato@editora.com',
        'press_contact_phone': '(11) 1234-5678'
    }
    
    # Processar livro completo
    print("Processando livro...")
    print()
    
    results = pipeline.process_book(
        manuscript_path='path/to/manuscript.md',  # Substitua pelo caminho real
        metadata=metadata,
        steps=['cover', 'layout', 'proof', 'materials']  # Todas as etapas
    )
    
    # Exibir resultados
    print()
    print("=" * 70)
    print("RESULTADOS")
    print("=" * 70)
    print()
    print(f"Livro: {results['book_title']}")
    print(f"Diretório: {results['output_dir']}")
    print(f"Etapas concluídas: {len(results['steps_completed'])}")
    print()
    
    # Detalhes por etapa
    if 'cover' in results:
        print("📐 CAPA:")
        if results['cover']['status'] == 'success':
            print(f"   ✅ {len(results['cover']['concepts'])} conceitos gerados")
        else:
            print(f"   ❌ Erro: {results['cover'].get('error')}")
        print()
    
    if 'layout' in results:
        print("📄 DIAGRAMAÇÃO:")
        if results['layout']['status'] == 'success':
            stats = results['layout']['statistics']
            print(f"   ✅ Páginas: {stats['estimated_pages']}")
            print(f"   ✅ Palavras: {stats['word_count']}")
            print(f"   ✅ PDF: {results['layout']['pdf']}")
        else:
            print(f"   ❌ Erro: {results['layout'].get('error')}")
        print()
    
    if 'proof' in results:
        print("🔍 REVISÃO:")
        if results['proof']['status'] == 'success':
            print(f"   ✅ Problemas encontrados: {results['proof']['issues_found']}")
            print(f"   ✅ Relatório: {results['proof']['report']}")
        else:
            print(f"   ❌ Erro: {results['proof'].get('error')}")
        print()
    
    if 'materials' in results:
        print("📦 MATERIAIS:")
        if results['materials']['status'] == 'success':
            files = results['materials']['files']
            print(f"   ✅ {len(files)} materiais gerados:")
            for name in files.keys():
                print(f"      - {name}")
        else:
            print(f"   ❌ Erro: {results['materials'].get('error')}")
        print()
    
    print("=" * 70)
    print("✅ PIPELINE CONCLUÍDO!")
    print("=" * 70)
    print()
    print(f"Verifique os arquivos em: {results['output_dir']}")
    print()


if __name__ == '__main__':
    main()
