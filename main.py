#!/usr/bin/env python3
"""
Sistema Automatizado de Preparação de Manuscritos para Publicação
Versão 2.0

Desenvolvido por Manus AI - Outubro 2025
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Optional

# Importa módulos do sistema
from modules.config import Config, load_config
from modules.utils import (
    print_banner, print_info, print_success, print_error,
    ProgressTracker, setup_logging
)
from modules.analyzer import ManuscriptAnalyzer
from modules.enhancer import ContentEnhancer
from modules.formatter import DocumentFormatter
from modules.elements import ElementsGenerator
from modules.reviewer import EditorialReviewer
from modules.exporter import PublicationExporter

class ManuscriptPublisher:
    """Sistema principal de preparação de manuscritos."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Inicializa o sistema.
        
        Args:
            config: Configuração customizada (opcional)
        """
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        
        # Inicializa módulos
        self.analyzer = ManuscriptAnalyzer(self.config)
        self.enhancer = ContentEnhancer(self.config)
        self.formatter = DocumentFormatter(self.config)
        self.elements_generator = ElementsGenerator(self.config)
        self.reviewer = EditorialReviewer(self.config)
        self.exporter = PublicationExporter(self.config)
    
    def process_manuscript(self, input_path: str, output_path: str) -> Dict:
        """
        Processa manuscrito completo.
        
        Args:
            input_path: Caminho do manuscrito de entrada
            output_path: Diretório de saída
            
        Returns:
            Dicionário com resultados do processamento
        """
        try:
            # Cria diretório de saída
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Inicia rastreamento de progresso
            tracker = ProgressTracker()
            
            print_banner(f"PROCESSANDO: {Path(input_path).name}")
            
            # FASE 1: Análise
            print_info("FASE 1/7: Análise e Diagnóstico")
            tracker.start_phase("ANALYSIS")
            
            analysis_result = self.analyzer.analyze(input_path)
            
            if "error" in analysis_result:
                print_error(f"Erro na análise: {analysis_result['error']}")
                return {"error": analysis_result["error"]}
            
            # Salva análise
            analysis_path = output_dir / "01_Analise_Estrutura.md"
            self.analyzer.save_report(analysis_result, analysis_path)
            
            tracker.end_phase("ANALYSIS", {
                "word_count": analysis_result["word_count"],
                "page_count": analysis_result["page_count"],
                "chapter_count": len(analysis_result["structure"]["chapters"]),
                "quality_score": analysis_result["quality"]["overall_score"]
            })
            
            # FASE 2: Identificação de Oportunidades
            print_info("FASE 2/7: Identificação de Oportunidades")
            tracker.start_phase("OPPORTUNITIES")
            
            opportunities = self._identify_opportunities(analysis_result)
            opportunities_path = output_dir / "02_Oportunidades_Aprimoramento.md"
            self._save_opportunities(opportunities, str(opportunities_path))
            
            tracker.end_phase("OPPORTUNITIES", {
                "total_opportunities": len(opportunities["high_priority"]) + 
                                     len(opportunities["medium_priority"]) + 
                                     len(opportunities["low_priority"])
            })
            
            # FASE 3: Aprimoramento
            print_info("FASE 3/7: Aprimoramento de Conteúdo")
            tracker.start_phase("ENHANCEMENT")
            
            enhanced_content = self.enhancer.enhance(
                analysis_result["content"],
                analysis_result["metadata"],
                opportunities
            )
            
            tracker.end_phase("ENHANCEMENT", {
                "total_changes": enhanced_content.get("total_changes", 0),
                "formatting_changes": enhanced_content.get("formatting_changes", 0),
                "terminology_changes": enhanced_content.get("terminology_changes", 0),
                "ai_changes": enhanced_content.get("ai_changes", 0)
            })
            
            # FASE 4: Elementos Complementares
            print_info("FASE 4/7: Criação de Elementos Complementares")
            tracker.start_phase("ELEMENTS")
            
            elements = self.elements_generator.generate_all(
                enhanced_content,
                analysis_result["metadata"]
            )
            
            # Salva elementos individuais
            for element_name, element_content in elements["files"].items():
                element_path = output_dir / f"{element_name}.md"
                with open(element_path, 'w', encoding='utf-8') as f:
                    f.write(element_content)
            
            tracker.end_phase("ELEMENTS", {
                "pre_textual_count": elements["statistics"]["pre_textual_count"],
                "post_textual_count": elements["statistics"]["post_textual_count"]
            })
            
            # FASE 5: Revisão Editorial
            print_info("FASE 5/7: Revisão Editorial Profissional")
            tracker.start_phase("REVIEW")
            
            review_result = self.reviewer.review(
                enhanced_content,
                elements,
                analysis_result["metadata"]
            )
            
            # Salva relatório de revisão
            review_path = output_dir / "Relatorio_Revisao_Editorial.md"
            self.reviewer.save_report(review_result, str(review_path))
            
            tracker.end_phase("REVIEW", {
                "issues_found": review_result["statistics"]["total_issues"],
                "critical_issues": review_result["statistics"]["critical_issues"],
                "overall_rating": review_result["overall_rating"]
            })
            
            # FASE 6: Formatação
            print_info("FASE 6/7: Formatação e Padronização")
            tracker.start_phase("FORMATTING")
            
            formatted_doc = self.formatter.format_document(
                enhanced_content,
                elements,
                review_result["corrections"]
            )
            
            tracker.end_phase("FORMATTING", {
                "corrections_applied": formatted_doc["statistics"]["corrections_applied"],
                "headings_formatted": formatted_doc["statistics"]["headings_formatted"]
            })
            
            # FASE 7: Exportação
            print_info("FASE 7/7: Exportação para Publicação")
            tracker.start_phase("EXPORT")
            
            export_result = self.exporter.export_all(
                formatted_doc,
                elements,
                analysis_result["metadata"],
                output_dir
            )
            
            tracker.end_phase("EXPORT", {
                "files_generated": len(export_result["files"]),
                "formats": ", ".join(export_result["formats"])
            })
            
            # Finaliza
            print_success("\n✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
            
            # Mostra resumo
            self._print_summary(tracker, export_result, output_dir)
            
            return {
                "success": True,
                "files_generated": export_result["files"],
                "output_directory": str(output_dir),
                "statistics": tracker.get_summary()
            }
            
        except Exception as e:
            self.logger.error(f"Erro durante processamento: {e}", exc_info=True)
            print_error(f"Erro: {e}")
            return {"error": str(e)}
    
    def _identify_opportunities(self, analysis_result: Dict) -> Dict:
        """Identifica oportunidades de aprimoramento."""
        opportunities = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": []
        }
        
        quality = analysis_result["quality"]
        
        # Verifica qualidade geral
        if quality["overall_score"] < 0.7:
            opportunities["high_priority"].append({
                "category": "quality",
                "description": "Qualidade geral abaixo do ideal",
                "action": "Revisão abrangente necessária"
            })
        
        # Verifica legibilidade (baseado em palavras por sentença)
        if quality.get("avg_words_per_sentence", 0) > 25:
            opportunities["medium_priority"].append({
                "category": "readability",
                "description": "Legibilidade pode ser melhorada (sentenças muito longas)",
                "action": "Simplificar sentenças e parágrafos"
            })
        
        # Verifica consistência
        term_consistency = quality.get("term_consistency", {})
        if term_consistency.get("score", 1.0) < 0.7:
            opportunities["medium_priority"].append({
                "category": "consistency",
                "description": "Inconsistências terminológicas",
                "action": "Padronizar termos e formatação"
            })
        
        return opportunities
    
    def _save_opportunities(self, opportunities: Dict, output_path: str):
        """Salva relatório de oportunidades."""
        lines = [
            "# OPORTUNIDADES DE APRIMORAMENTO",
            "",
            "---",
            "",
            "## PRIORIDADE ALTA",
            ""
        ]
        
        for opp in opportunities["high_priority"]:
            lines.append(f"### {opp['category'].upper()}")
            lines.append(f"**Descrição:** {opp['description']}")
            lines.append(f"**Ação:** {opp['action']}")
            lines.append("")
        
        if not opportunities["high_priority"]:
            lines.append("*Nenhuma oportunidade de alta prioridade identificada.*")
            lines.append("")
        
        lines.extend(["---", "", "## PRIORIDADE MÉDIA", ""])
        
        for opp in opportunities["medium_priority"]:
            lines.append(f"### {opp['category'].upper()}")
            lines.append(f"**Descrição:** {opp['description']}")
            lines.append(f"**Ação:** {opp['action']}")
            lines.append("")
        
        if not opportunities["medium_priority"]:
            lines.append("*Nenhuma oportunidade de média prioridade identificada.*")
            lines.append("")
        
        lines.extend(["---", ""])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def _print_summary(self, tracker: ProgressTracker, export_result: Dict, output_dir: Path):
        """Imprime resumo do processamento."""
        print("\n" + "="*60)
        print("RESUMO DO PROCESSAMENTO")
        print("="*60)
        
        summary = tracker.get_summary()
        phases = summary.get('phases', {})
        
        print(f"\n📊 Estatísticas:")
        if 'ANALYSIS' in phases and 'metrics' in phases['ANALYSIS']:
            metrics = phases['ANALYSIS']['metrics']
            print(f"  • Palavras processadas: {metrics.get('word_count', 0):,}")
            print(f"  • Páginas estimadas: {metrics.get('page_count', 0)}")
            print(f"  • Capítulos: {metrics.get('chapter_count', 0)}")
            print(f"  • Qualidade inicial: {metrics.get('quality_score', 0):.1f}/1.0")
        
        if 'REVIEW' in phases and 'metrics' in phases['REVIEW']:
            review_metrics = phases['REVIEW']['metrics']
            print(f"  • Avaliação final: {review_metrics.get('overall_rating', 0)}/10.0")
        
        print(f"\n📁 Arquivos gerados: {len(export_result.get('files', []))}")
        print(f"📂 Localização: {output_dir}/")
        
        print(f"\n⏱️  Tempo total: {summary.get('total_time', 0):.1f}s")
        
        print("\n" + "="*60)

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Sistema Automatizado de Preparação de Manuscritos para Publicação",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py manuscrito.pdf -o output/
  python main.py manuscrito.docx -o output/ -c configs/academic.yaml
  python main.py --interactive
        """
    )
    
    parser.add_argument(
        "input",
        nargs="?",
        help="Arquivo de entrada (PDF, DOCX, MD)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="output",
        help="Diretório de saída (padrão: output/)"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="Arquivo de configuração YAML"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Modo interativo"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Modo verbose (mais detalhes)"
    )
    
    args = parser.parse_args()
    
    # Configura logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    
    # Modo interativo
    if args.interactive:
        from modules.interactive import InteractiveMode
        interactive = InteractiveMode()
        interactive.run()
        return
    
    # Modo linha de comando
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    # Carrega configuração
    if args.config:
        config = load_config(args.config)
    else:
        config = Config()
    
    # Processa manuscrito
    publisher = ManuscriptPublisher(config)
    results = publisher.process_manuscript(args.input, args.output)
    
    # Retorna código de saída apropriado
    if "error" in results:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
