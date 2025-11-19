"""
Production Pipeline - Pipeline Completo de Produção Editorial Automatizada.

Este módulo integra todos os componentes de produção (layout, revisão,
materiais e capa) em um pipeline unificado e fácil de usar.

Autor: Manus AI
Versão: 1.0.0
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .layout_engine import LayoutEngine
from .proof_checker import ProofChecker
from .materials_generator import MaterialsGenerator
from .cover_designer import CoverDesigner


class ProductionPipeline:
    """Pipeline completo de produção editorial automatizada."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o pipeline de produção.
        
        Args:
            config: Dicionário de configuração com opções:
                - format: Formato da página (padrão: 'A5')
                - genre: Gênero do livro (padrão: 'academic')
                - language: Idioma (padrão: 'pt-BR')
                - use_ai: Usar IA para geração de conteúdo
                - openai_api_key: Chave API OpenAI
                - output_dir: Diretório base de saída
        """
        self.config = config or {}
        
        # Diretório de saída
        self.output_dir = Path(self.config.get('output_dir', './output'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar componentes
        self.layout_engine = LayoutEngine({
            'format': self.config.get('format', 'A5'),
            'genre': self.config.get('genre', 'academic')
        })
        
        self.proof_checker = ProofChecker({
            'language': self.config.get('language', 'pt-BR')
        })
        
        self.materials_generator = MaterialsGenerator({
            'use_ai': self.config.get('use_ai', False),
            'openai_api_key': self.config.get('openai_api_key')
        })
        
        self.cover_designer = CoverDesigner({
            'use_ai_images': self.config.get('use_ai', False),
            'openai_api_key': self.config.get('openai_api_key')
        })
    
    def process_book(self,
                    manuscript_path: str,
                    metadata: Dict,
                    steps: Optional[List[str]] = None) -> Dict:
        """
        Processa um livro completo através do pipeline.
        
        Args:
            manuscript_path: Caminho para o manuscrito
            metadata: Metadados do livro
            steps: Lista de etapas a executar. Se None, executa todas:
                   ['cover', 'layout', 'proof', 'materials']
                   
        Returns:
            Dicionário com resultados de cada etapa
        """
        print("=" * 70)
        print("🚀 INICIANDO PIPELINE DE PRODUÇÃO EDITORIAL")
        print("=" * 70)
        print(f"\n📚 Livro: {metadata.get('title', 'Sem título')}")
        print(f"✍️  Autor: {metadata.get('author', 'Sem autor')}")
        print(f"📐 Formato: {self.config.get('format', 'A5')}")
        print(f"📖 Gênero: {self.config.get('genre', 'academic')}")
        print()
        
        # Determinar etapas a executar
        if steps is None:
            steps = ['cover', 'layout', 'proof', 'materials']
        
        # Criar diretório de saída para este livro
        book_slug = self._slugify(metadata.get('title', 'livro'))
        book_output_dir = self.output_dir / book_slug
        book_output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'book_title': metadata.get('title'),
            'output_dir': str(book_output_dir),
            'timestamp': datetime.now().isoformat(),
            'steps_completed': []
        }
        
        # ETAPA 1: Design de Capa
        if 'cover' in steps:
            print("\n" + "=" * 70)
            print("ETAPA 1/4: DESIGN DE CAPA")
            print("=" * 70)
            
            try:
                cover_dir = book_output_dir / 'cover'
                cover_dir.mkdir(exist_ok=True)
                
                # Gerar 3 conceitos de capa
                concepts = self.cover_designer.generate_concepts(
                    metadata,
                    str(cover_dir),
                    num_concepts=3
                )
                
                results['cover'] = {
                    'concepts': concepts,
                    'status': 'success'
                }
                results['steps_completed'].append('cover')
                
            except Exception as e:
                print(f"❌ Erro no design de capa: {e}")
                results['cover'] = {'status': 'error', 'error': str(e)}
        
        # ETAPA 2: Diagramação
        if 'layout' in steps:
            print("\n" + "=" * 70)
            print("ETAPA 2/4: DIAGRAMAÇÃO")
            print("=" * 70)
            
            try:
                layout_dir = book_output_dir / 'layout'
                layout_dir.mkdir(exist_ok=True)
                
                # Usar primeiro conceito de capa se disponível
                cover_path = None
                if 'cover' in results and results['cover'].get('status') == 'success':
                    cover_path = results['cover']['concepts'][0]
                
                # Diagramar livro
                pdf_path = layout_dir / f"{book_slug}.pdf"
                layout_result = self.layout_engine.layout_book(
                    manuscript_path,
                    metadata,
                    str(pdf_path),
                    cover_path
                )
                
                # Exportar versão para impressão
                print_ready_path = layout_dir / f"{book_slug}_print_ready.pdf"
                self.layout_engine.export_print_ready(
                    str(pdf_path),
                    str(print_ready_path)
                )
                
                results['layout'] = {
                    'pdf': str(pdf_path),
                    'print_ready': str(print_ready_path),
                    'statistics': layout_result['statistics'],
                    'status': 'success'
                }
                results['steps_completed'].append('layout')
                
            except Exception as e:
                print(f"❌ Erro na diagramação: {e}")
                results['layout'] = {'status': 'error', 'error': str(e)}
        
        # ETAPA 3: Revisão de Provas
        if 'proof' in steps:
            print("\n" + "=" * 70)
            print("ETAPA 3/4: REVISÃO DE PROVAS")
            print("=" * 70)
            
            try:
                proof_dir = book_output_dir / 'proof'
                proof_dir.mkdir(exist_ok=True)
                
                # Revisar PDF se disponível, senão revisar manuscrito
                file_to_check = manuscript_path
                if 'layout' in results and results['layout'].get('status') == 'success':
                    file_to_check = results['layout']['pdf']
                
                # Executar revisão
                issues = self.proof_checker.check_all(file_to_check)
                
                # Gerar relatório
                report_path = proof_dir / "revision_report.md"
                self.proof_checker.generate_report(issues, str(report_path))
                
                results['proof'] = {
                    'issues_found': len(issues),
                    'report': str(report_path),
                    'status': 'success'
                }
                results['steps_completed'].append('proof')
                
            except Exception as e:
                print(f"❌ Erro na revisão: {e}")
                results['proof'] = {'status': 'error', 'error': str(e)}
        
        # ETAPA 4: Materiais Adicionais
        if 'materials' in steps:
            print("\n" + "=" * 70)
            print("ETAPA 4/4: MATERIAIS ADICIONAIS")
            print("=" * 70)
            
            try:
                materials_dir = book_output_dir / 'materials'
                materials_dir.mkdir(exist_ok=True)
                
                # Adicionar estatísticas ao metadata se disponível
                if 'layout' in results and results['layout'].get('status') == 'success':
                    stats = results['layout']['statistics']
                    metadata['pages'] = stats['estimated_pages']
                    metadata['word_count'] = stats['word_count']
                
                # Gerar materiais
                materials = self.materials_generator.generate_all(
                    metadata,
                    str(materials_dir)
                )
                
                results['materials'] = {
                    'files': materials,
                    'status': 'success'
                }
                results['steps_completed'].append('materials')
                
            except Exception as e:
                print(f"❌ Erro na geração de materiais: {e}")
                results['materials'] = {'status': 'error', 'error': str(e)}
        
        # Resumo final
        print("\n" + "=" * 70)
        print("✅ PIPELINE CONCLUÍDO")
        print("=" * 70)
        print(f"\n📂 Arquivos salvos em: {book_output_dir}")
        print(f"\n📊 Etapas concluídas: {len(results['steps_completed'])}/{len(steps)}")
        
        for step in steps:
            status = results.get(step, {}).get('status', 'not_run')
            icon = '✅' if status == 'success' else '❌' if status == 'error' else '⏭️'
            print(f"   {icon} {step.capitalize()}: {status}")
        
        # Gerar relatório final
        self._generate_final_report(results, book_output_dir)
        
        return results
    
    def _slugify(self, text: str) -> str:
        """Converte texto em slug para nome de arquivo."""
        import re
        import unicodedata
        
        # Normalizar unicode
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Converter para minúsculas e substituir espaços
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        
        return text[:50]  # Limitar tamanho
    
    def _generate_final_report(self, results: Dict, output_dir: Path):
        """Gera relatório final do pipeline."""
        
        report_path = output_dir / "production_report.md"
        
        report = f"""# Relatório de Produção Editorial

**Livro:** {results.get('book_title', 'N/A')}  
**Data:** {results.get('timestamp', 'N/A')}  
**Diretório:** {results.get('output_dir', 'N/A')}

## Resumo

**Etapas concluídas:** {len(results.get('steps_completed', []))}

"""
        
        # Detalhes de cada etapa
        for step_name in ['cover', 'layout', 'proof', 'materials']:
            if step_name in results:
                step_data = results[step_name]
                status = step_data.get('status', 'unknown')
                icon = '✅' if status == 'success' else '❌'
                
                report += f"### {icon} {step_name.capitalize()}\n\n"
                report += f"**Status:** {status}\n\n"
                
                if status == 'success':
                    if step_name == 'cover':
                        report += f"**Conceitos gerados:** {len(step_data.get('concepts', []))}\n\n"
                        for i, concept in enumerate(step_data.get('concepts', []), 1):
                            report += f"- Conceito {i}: `{concept}`\n"
                        report += "\n"
                    
                    elif step_name == 'layout':
                        stats = step_data.get('statistics', {})
                        report += f"**Páginas:** {stats.get('estimated_pages', 'N/A')}\n"
                        report += f"**Palavras:** {stats.get('word_count', 'N/A')}\n"
                        report += f"**Capítulos:** {stats.get('chapter_count', 'N/A')}\n"
                        report += f"**PDF:** `{step_data.get('pdf', 'N/A')}`\n"
                        report += f"**Pronto para impressão:** `{step_data.get('print_ready', 'N/A')}`\n\n"
                    
                    elif step_name == 'proof':
                        report += f"**Problemas encontrados:** {step_data.get('issues_found', 0)}\n"
                        report += f"**Relatório:** `{step_data.get('report', 'N/A')}`\n\n"
                    
                    elif step_name == 'materials':
                        files = step_data.get('files', {})
                        report += f"**Materiais gerados:** {len(files)}\n\n"
                        for material_name, material_path in files.items():
                            report += f"- {material_name}: `{material_path}`\n"
                        report += "\n"
                
                elif status == 'error':
                    report += f"**Erro:** {step_data.get('error', 'Erro desconhecido')}\n\n"
        
        # Próximos passos
        report += """## Próximos Passos

1. **Revisar conceitos de capa** e escolher o preferido
2. **Verificar relatório de revisão** e corrigir problemas críticos
3. **Revisar PDF diagramado** para garantir qualidade
4. **Usar materiais gerados** para marketing e distribuição
5. **Enviar para impressão** o arquivo `*_print_ready.pdf`

---

*Relatório gerado automaticamente pelo Pipeline de Produção Editorial*
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Relatório completo salvo em: {report_path}")


# Função de conveniência
def process_book(manuscript_path: str,
                metadata: Dict,
                output_dir: str = './output',
                format: str = 'A5',
                genre: str = 'academic',
                use_ai: bool = False,
                openai_api_key: Optional[str] = None) -> Dict:
    """
    Função de conveniência para processar um livro completo.
    
    Args:
        manuscript_path: Caminho para o manuscrito
        metadata: Metadados do livro
        output_dir: Diretório de saída
        format: Formato da página
        genre: Gênero do livro
        use_ai: Usar IA para geração de conteúdo
        openai_api_key: Chave API OpenAI
        
    Returns:
        Dicionário com resultados do processamento
    """
    config = {
        'output_dir': output_dir,
        'format': format,
        'genre': genre,
        'use_ai': use_ai
    }
    
    # A chave de API deve ser tratada como um segredo e lida diretamente pelo componente
    # ou de variáveis de ambiente, não deve ser passada em dicionários de configuração.
    # O componente CoverDesigner/MaterialsGenerator deve ler de os.getenv("OPENAI_API_KEY")
    # ou de um objeto de configuração seguro.
    pass
    
    pipeline = ProductionPipeline(config)
    return pipeline.process_book(manuscript_path, metadata)
