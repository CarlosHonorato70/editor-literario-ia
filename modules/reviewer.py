"""
Módulo de Revisão Editorial
Realiza revisão editorial profissional do manuscrito.
"""

import re
from typing import Dict, List, Tuple
import logging

from .config import Config
from .utils import print_info, count_words

class EditorialReviewer:
    """Realiza revisão editorial completa."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def review(self, enhanced_content: Dict, elements: Dict, metadata: Dict) -> Dict:
        """
        Realiza revisão editorial completa.
        
        Args:
            enhanced_content: Conteúdo aprimorado
            elements: Elementos pré e pós-textuais
            metadata: Metadados do manuscrito
            
        Returns:
            Resultado da revisão com correções e avaliação
        """
        print_info("Iniciando revisão editorial profissional...")
        
        content = enhanced_content["content"]
        
        # Diferentes dimensões de revisão
        structure_review = self._review_structure(content)
        content_review = self._review_content(content)
        style_review = self._review_style(content)
        consistency_review = self._review_consistency(content)
        references_review = self._review_references(content)
        technical_review = self._review_technical_aspects(content, elements)
        
        # Calcula avaliação geral
        overall_rating = self._calculate_overall_rating([
            structure_review,
            content_review,
            style_review,
            consistency_review,
            references_review,
            technical_review
        ])
        
        # Compila correções
        corrections = []
        corrections.extend(structure_review.get("corrections", []))
        corrections.extend(content_review.get("corrections", []))
        corrections.extend(style_review.get("corrections", []))
        corrections.extend(consistency_review.get("corrections", []))
        
        return {
            "structure": structure_review,
            "content": content_review,
            "style": style_review,
            "consistency": consistency_review,
            "references": references_review,
            "technical": technical_review,
            "overall_rating": overall_rating,
            "corrections": corrections,
            "statistics": {
                "total_issues": sum(len(r.get("issues", [])) for r in [
                    structure_review, content_review, style_review,
                    consistency_review, references_review, technical_review
                ]),
                "critical_issues": sum(len([i for i in r.get("issues", []) if i.get("severity") == "critical"]) for r in [
                    structure_review, content_review, style_review,
                    consistency_review, references_review, technical_review
                ]),
                "corrections_suggested": len(corrections)
            }
        }
    
    def _review_structure(self, content: str) -> Dict:
        """Revisa estrutura do manuscrito."""
        issues = []
        score = 10.0
        
        # Verifica presença de capítulos
        chapters = re.findall(r'^#\s+.+$', content, re.MULTILINE)
        if len(chapters) == 0:
            issues.append({
                "severity": "high",
                "category": "structure",
                "description": "Nenhum capítulo identificado (usar # para títulos de capítulo)"
            })
            score -= 2.0
        
        # Verifica hierarquia de headings
        headings = re.findall(r'^(#{1,6})\s+', content, re.MULTILINE)
        if headings:
            levels = [len(h) for h in headings]
            # Verifica se há saltos na hierarquia (ex: # direto para ###)
            for i in range(len(levels) - 1):
                if levels[i+1] - levels[i] > 1:
                    issues.append({
                        "severity": "medium",
                        "category": "structure",
                        "description": f"Salto na hierarquia de títulos detectado (nível {levels[i]} para {levels[i+1]})"
                    })
                    score -= 0.5
                    break
        
        # Verifica balanceamento de seções
        if len(chapters) > 0:
            # Calcula tamanho médio de capítulos
            chapter_positions = [m.start() for m in re.finditer(r'^#\s+.+$', content, re.MULTILINE)]
            chapter_positions.append(len(content))
            
            chapter_sizes = []
            for i in range(len(chapter_positions) - 1):
                size = chapter_positions[i+1] - chapter_positions[i]
                chapter_sizes.append(size)
            
            if chapter_sizes:
                avg_size = sum(chapter_sizes) / len(chapter_sizes)
                # Verifica se algum capítulo é muito menor que a média
                for i, size in enumerate(chapter_sizes):
                    if size < avg_size * 0.3:
                        issues.append({
                            "severity": "low",
                            "category": "structure",
                            "description": f"Capítulo {i+1} significativamente menor que os demais"
                        })
                        score -= 0.3
        
        return {
            "score": max(0, score),
            "issues": issues,
            "corrections": []
        }
    
    def _review_content(self, content: str) -> Dict:
        """Revisa qualidade do conteúdo."""
        issues = []
        score = 10.0
        
        # Verifica densidade de parágrafos
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
        
        if paragraphs:
            para_lengths = [len(p.split()) for p in paragraphs]
            avg_para_length = sum(para_lengths) / len(para_lengths)
            
            # Parágrafos ideais: 50-150 palavras
            if avg_para_length < 30:
                issues.append({
                    "severity": "medium",
                    "category": "content",
                    "description": f"Parágrafos muito curtos em média ({avg_para_length:.0f} palavras)"
                })
                score -= 1.0
            elif avg_para_length > 200:
                issues.append({
                    "severity": "medium",
                    "category": "content",
                    "description": f"Parágrafos muito longos em média ({avg_para_length:.0f} palavras)"
                })
                score -= 1.0
        
        # Verifica presença de exemplos/casos
        example_markers = ['exemplo', 'caso', 'por exemplo', 'como ilustração']
        example_count = sum(content.lower().count(marker) for marker in example_markers)
        
        if example_count < 3:
            issues.append({
                "severity": "low",
                "category": "content",
                "description": "Poucos exemplos ou casos ilustrativos identificados"
            })
            score -= 0.5
        
        return {
            "score": max(0, score),
            "issues": issues,
            "corrections": []
        }
    
    def _review_style(self, content: str) -> Dict:
        """Revisa estilo de escrita."""
        issues = []
        corrections = []
        score = 10.0
        
        # Verifica voz passiva excessiva
        passive_patterns = [
            r'\bfoi\s+\w+ado\b',
            r'\bforam\s+\w+ados\b',
            r'\bsão\s+\w+ados\b',
        ]
        
        passive_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in passive_patterns)
        total_sentences = len(re.split(r'[.!?]+', content))
        
        if total_sentences > 0:
            passive_ratio = passive_count / total_sentences
            if passive_ratio > 0.3:
                issues.append({
                    "severity": "medium",
                    "category": "style",
                    "description": f"Uso excessivo de voz passiva ({passive_ratio*100:.0f}% das sentenças)"
                })
                score -= 1.5
        
        # Verifica repetição de palavras
        words = re.findall(r'\b\w{4,}\b', content.lower())
        if words:
            from collections import Counter
            word_freq = Counter(words)
            # Palavras muito frequentes (exceto artigos, preposições comuns)
            common_words = {'para', 'como', 'mais', 'sobre', 'pela', 'pelo', 'pela', 'este', 'esta', 'esse', 'essa'}
            overused = [(w, c) for w, c in word_freq.most_common(20) if w not in common_words and c > len(words) * 0.02]
            
            if overused:
                issues.append({
                    "severity": "low",
                    "category": "style",
                    "description": f"Palavras potencialmente repetitivas: {', '.join([w for w, c in overused[:5]])}"
                })
                score -= 0.5
        
        # Verifica sentenças muito longas
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        long_sentences = [s for s in sentences if len(s.split()) > 40]
        
        if len(long_sentences) > len(sentences) * 0.2:
            issues.append({
                "severity": "medium",
                "category": "style",
                "description": f"{len(long_sentences)} sentenças muito longas (>40 palavras)"
            })
            score -= 1.0
        
        return {
            "score": max(0, score),
            "issues": issues,
            "corrections": corrections
        }
    
    def _review_consistency(self, content: str) -> Dict:
        """Revisa consistência terminológica e formatação."""
        issues = []
        corrections = []
        score = 10.0
        
        # Verifica consistência de termos técnicos
        term_variations = {
            "Teoria da Emoção Construída": ["teoria da emoção construída", "TCE"],
            "Modelo VIP": ["modelo VIP", "VIP"],
        }
        
        for main_term, variations in term_variations.items():
            main_count = content.count(main_term)
            var_counts = {v: content.count(v) for v in variations}
            
            # Se há uso inconsistente
            if main_count > 5 and any(count > main_count * 0.5 for count in var_counts.values()):
                issues.append({
                    "severity": "low",
                    "category": "consistency",
                    "description": f"Uso inconsistente de '{main_term}' e suas variações"
                })
                score -= 0.5
        
        # Verifica consistência de formatação de listas
        list_markers = re.findall(r'^[\s]*([*\-+])\s', content, re.MULTILINE)
        if list_markers:
            from collections import Counter
            marker_counts = Counter(list_markers)
            if len(marker_counts) > 1:
                issues.append({
                    "severity": "low",
                    "category": "consistency",
                    "description": "Uso inconsistente de marcadores de lista (*, -, +)"
                })
                score -= 0.3
        
        return {
            "score": max(0, score),
            "issues": issues,
            "corrections": corrections
        }
    
    def _review_references(self, content: str) -> Dict:
        """Revisa referências bibliográficas."""
        issues = []
        score = 10.0
        
        # Procura seção de referências
        ref_section = re.search(r'(REFERÊNCIAS|BIBLIOGRAFIA|REFERENCES)', content, re.IGNORECASE)
        
        if not ref_section:
            issues.append({
                "severity": "high",
                "category": "references",
                "description": "Seção de referências bibliográficas não encontrada"
            })
            score -= 3.0
        else:
            # Extrai referências
            ref_text = content[ref_section.start():]
            ref_lines = [line.strip() for line in ref_text.split('\n') if line.strip()]
            
            # Conta referências (heurística: linhas com ano entre parênteses)
            references = [line for line in ref_lines if re.search(r'\(\d{4}\)', line)]
            
            if len(references) == 0:
                issues.append({
                    "severity": "medium",
                    "category": "references",
                    "description": "Nenhuma referência identificada na seção de referências"
                })
                score -= 2.0
            elif len(references) < 10:
                issues.append({
                    "severity": "low",
                    "category": "references",
                    "description": f"Poucas referências identificadas ({len(references)})"
                })
                score -= 0.5
        
        return {
            "score": max(0, score),
            "issues": issues,
            "corrections": []
        }
    
    def _review_technical_aspects(self, content: str, elements: Dict) -> Dict:
        """Revisa aspectos técnicos."""
        issues = []
        score = 10.0
        
        # Verifica presença de elementos essenciais
        required_elements = ["Sumario", "Referencias"]
        missing_elements = [elem for elem in required_elements if elem not in elements.get("files", {})]
        
        if missing_elements:
            issues.append({
                "severity": "medium",
                "category": "technical",
                "description": f"Elementos faltantes: {', '.join(missing_elements)}"
            })
            score -= 1.0 * len(missing_elements)
        
        # Verifica formatação Markdown
        # Headings sem espaço após #
        bad_headings = re.findall(r'^#{1,6}[^\s]', content, re.MULTILINE)
        if bad_headings:
            issues.append({
                "severity": "low",
                "category": "technical",
                "description": f"{len(bad_headings)} títulos com formatação incorreta (falta espaço após #)"
            })
            score -= 0.5
        
        return {
            "score": max(0, score),
            "issues": issues,
            "corrections": []
        }
    
    def _calculate_overall_rating(self, reviews: List[Dict]) -> float:
        """Calcula avaliação geral."""
        scores = [r.get("score", 0) for r in reviews]
        if not scores:
            return 0.0
        
        avg_score = sum(scores) / len(scores)
        return round(avg_score, 1)
    
    def save_report(self, review_result: Dict, output_path: str):
        """Salva relatório de revisão editorial."""
        lines = [
            "# RELATÓRIO DE REVISÃO EDITORIAL",
            "",
            f"**Avaliação Geral:** {review_result['overall_rating']}/10.0",
            "",
            "---",
            "",
            "## RESUMO EXECUTIVO",
            "",
            f"- **Total de Questões Identificadas:** {review_result['statistics']['total_issues']}",
            f"- **Questões Críticas:** {review_result['statistics']['critical_issues']}",
            f"- **Correções Sugeridas:** {review_result['statistics']['corrections_suggested']}",
            "",
            "---",
            ""
        ]
        
        # Adiciona cada dimensão de revisão
        dimensions = [
            ("ESTRUTURA", "structure"),
            ("CONTEÚDO", "content"),
            ("ESTILO", "style"),
            ("CONSISTÊNCIA", "consistency"),
            ("REFERÊNCIAS", "references"),
            ("ASPECTOS TÉCNICOS", "technical")
        ]
        
        for title, key in dimensions:
            review_data = review_result.get(key, {})
            lines.append(f"## {title}")
            lines.append("")
            lines.append(f"**Score:** {review_data.get('score', 0)}/10.0")
            lines.append("")
            
            issues = review_data.get("issues", [])
            if issues:
                lines.append("### Questões Identificadas:")
                lines.append("")
                for issue in issues:
                    severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(issue.get("severity", "low"), "⚪")
                    lines.append(f"{severity_icon} **{issue.get('severity', 'low').upper()}:** {issue.get('description', '')}")
                lines.append("")
            else:
                lines.append("*Nenhuma questão identificada.*")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Adiciona recomendações
        lines.extend([
            "## RECOMENDAÇÕES",
            "",
            "### Prioridade Alta",
            ""
        ])
        
        high_priority_issues = [
            issue for review in [review_result.get(dim[1], {}) for dim in dimensions]
            for issue in review.get("issues", [])
            if issue.get("severity") in ["critical", "high"]
        ]
        
        if high_priority_issues:
            for issue in high_priority_issues:
                lines.append(f"- {issue.get('description', '')}")
        else:
            lines.append("*Nenhuma questão de alta prioridade.*")
        
        lines.extend(["", "---", ""])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
