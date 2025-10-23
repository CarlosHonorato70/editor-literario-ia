"""
Módulo Analisador de Manuscritos
Realiza análise completa da estrutura e conteúdo do manuscrito.
"""

import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

from .config import Config
from .utils import count_words, estimate_pages, print_info, print_warning

class ManuscriptAnalyzer:
    """Analisa manuscritos e identifica estrutura e oportunidades de melhoria."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, file_path: str) -> Dict:
        """
        Analisa um manuscrito completo.
        
        Args:
            file_path: Caminho do arquivo do manuscrito
            
        Returns:
            Dicionário com resultados da análise
        """
        print_info("Iniciando análise do manuscrito...")
        
        # Extrai conteúdo baseado no tipo de arquivo
        content = self._extract_content(file_path)
        
        # Análise estrutural
        structure = self._analyze_structure(content)
        
        # Análise de conteúdo
        content_analysis = self._analyze_content(content)
        
        # Análise de qualidade
        quality = self._analyze_quality(content)
        
        # Metadados
        metadata = self._extract_metadata(content, file_path)
        
        result = {
            "file_path": file_path,
            "content": content,
            "structure": structure,
            "content_analysis": content_analysis,
            "quality": quality,
            "metadata": metadata,
            "word_count": count_words(content),
            "page_count": estimate_pages(count_words(content))
        }
        
        print_info(f"Análise concluída: {result['word_count']} palavras, ~{result['page_count']} páginas")
        
        return result
    
    def _extract_content(self, file_path: str) -> str:
        """Extrai conteúdo do arquivo baseado no tipo."""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.md':
            return self._extract_from_markdown(file_path)
        elif file_ext == '.docx':
            return self._extract_from_docx(file_path)
        elif file_ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Formato de arquivo não suportado: {file_ext}")
    
    def _extract_from_markdown(self, file_path: str) -> str:
        """Extrai conteúdo de arquivo Markdown."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extrai conteúdo de arquivo DOCX."""
        try:
            from docx import Document
            doc = Document(file_path)
            return '\n\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
        except ImportError:
            print_warning("Biblioteca python-docx não instalada. Instale com: pip install python-docx")
            return ""
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extrai conteúdo de arquivo PDF."""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = []
                for page in pdf_reader.pages:
                    text.append(page.extract_text())
                return '\n\n'.join(text)
        except ImportError:
            print_warning("Biblioteca PyPDF2 não instalada. Instale com: pip install PyPDF2")
            return ""
    
    def _analyze_structure(self, content: str) -> Dict:
        """Analisa a estrutura do manuscrito."""
        # Identifica capítulos
        chapters = self._find_chapters(content)
        
        # Identifica seções
        sections = self._find_sections(content)
        
        # Identifica elementos especiais
        figures = len(re.findall(r'!\[.*?\]\(.*?\)', content))  # Imagens em Markdown
        tables = len(re.findall(r'\|.*\|', content))  # Tabelas
        code_blocks = len(re.findall(r'```.*?```', content, re.DOTALL))
        
        return {
            "chapters": chapters,
            "sections": sections,
            "chapter_count": len(chapters),
            "section_count": len(sections),
            "figure_count": figures,
            "table_count": tables,
            "code_block_count": code_blocks
        }
    
    def _find_chapters(self, content: str) -> List[Dict]:
        """Encontra capítulos no manuscrito."""
        chapters = []
        
        # Padrões para identificar capítulos
        patterns = [
            r'^#\s+(.+)$',  # Markdown H1
            r'^CAPÍTULO\s+\d+[:\s]+(.+)$',  # CAPÍTULO 1: Título
            r'^Capítulo\s+\d+[:\s]+(.+)$',  # Capítulo 1: Título
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                chapters.append({
                    "title": match.group(1).strip(),
                    "position": match.start(),
                    "level": 1
                })
        
        # Remove duplicatas e ordena por posição
        chapters = sorted(chapters, key=lambda x: x['position'])
        unique_chapters = []
        seen_positions = set()
        
        for chapter in chapters:
            if chapter['position'] not in seen_positions:
                unique_chapters.append(chapter)
                seen_positions.add(chapter['position'])
        
        return unique_chapters
    
    def _find_sections(self, content: str) -> List[Dict]:
        """Encontra seções no manuscrito."""
        sections = []
        
        # Padrões para identificar seções
        patterns = [
            (r'^##\s+(.+)$', 2),  # Markdown H2
            (r'^###\s+(.+)$', 3),  # Markdown H3
        ]
        
        for pattern, level in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                sections.append({
                    "title": match.group(1).strip(),
                    "position": match.start(),
                    "level": level
                })
        
        return sorted(sections, key=lambda x: x['position'])
    
    def _analyze_content(self, content: str) -> Dict:
        """Analisa o conteúdo do manuscrito."""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Análise de parágrafos
        para_lengths = [len(p.split()) for p in paragraphs]
        avg_para_length = sum(para_lengths) / len(para_lengths) if para_lengths else 0
        
        # Análise de sentenças
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        sent_lengths = [len(s.split()) for s in sentences]
        avg_sent_length = sum(sent_lengths) / len(sent_lengths) if sent_lengths else 0
        
        # Identifica casos clínicos (para manuscritos acadêmicos)
        clinical_cases = self._find_clinical_cases(content)
        
        # Identifica referências
        references = self._find_references(content)
        
        return {
            "paragraph_count": len(paragraphs),
            "avg_paragraph_length": round(avg_para_length, 1),
            "sentence_count": len(sentences),
            "avg_sentence_length": round(avg_sent_length, 1),
            "clinical_cases": clinical_cases,
            "reference_count": len(references)
        }
    
    def _find_clinical_cases(self, content: str) -> List[Dict]:
        """Encontra casos clínicos no manuscrito."""
        cases = []
        
        patterns = [
            r'Caso Clínico\s*\d*[:\s]+',
            r'Caso\s+\d+[:\s]+',
            r'Paciente[:\s]+',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                cases.append({
                    "position": match.start(),
                    "marker": match.group(0)
                })
        
        return cases
    
    def _find_references(self, content: str) -> List[str]:
        """Encontra referências bibliográficas."""
        references = []
        
        # Procura por seção de referências
        ref_section_match = re.search(
            r'(REFERÊNCIAS|BIBLIOGRAFIA|REFERENCES).*$',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if ref_section_match:
            ref_text = ref_section_match.group(0)
            # Divide em linhas e filtra referências
            ref_lines = [line.strip() for line in ref_text.split('\n') if line.strip()]
            references = [line for line in ref_lines if self._is_reference_line(line)]
        
        return references
    
    def _is_reference_line(self, line: str) -> bool:
        """Verifica se uma linha parece ser uma referência."""
        # Heurística simples: linha contém ano entre parênteses e ponto final
        return bool(re.search(r'\(\d{4}\)', line) and line.endswith('.'))
    
    def _analyze_quality(self, content: str) -> Dict:
        """Analisa qualidade do manuscrito."""
        # Análise de legibilidade (Flesch Reading Ease simplificado)
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        sentences = [s for s in sentences if s.strip()]
        
        avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
        
        # Análise de consistência terminológica
        term_consistency = self._check_term_consistency(content)
        
        # Análise de formatação
        formatting = self._check_formatting(content)
        
        return {
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "term_consistency": term_consistency,
            "formatting": formatting,
            "overall_score": self._calculate_quality_score(avg_words_per_sentence, term_consistency, formatting)
        }
    
    def _check_term_consistency(self, content: str) -> Dict:
        """Verifica consistência terminológica."""
        # Procura por termos que podem ter variações
        common_terms = {
            "Teoria da Emoção Construída": ["TCE", "teoria da emoção construída"],
            "Modelo VIP": ["VIP", "modelo VIP"],
        }
        
        inconsistencies = []
        for full_term, variations in common_terms.items():
            full_count = len(re.findall(re.escape(full_term), content, re.IGNORECASE))
            var_counts = {var: len(re.findall(re.escape(var), content, re.IGNORECASE)) for var in variations}
            
            if full_count > 10 and any(count > 5 for count in var_counts.values()):
                inconsistencies.append({
                    "term": full_term,
                    "full_count": full_count,
                    "variations": var_counts
                })
        
        return {
            "inconsistencies": inconsistencies,
            "score": 1.0 if not inconsistencies else 0.7
        }
    
    def _check_formatting(self, content: str) -> Dict:
        """Verifica qualidade da formatação."""
        issues = []
        
        # Verifica espaçamento excessivo
        if re.search(r'\n{4,}', content):
            issues.append("Espaçamento excessivo entre parágrafos")
        
        # Verifica pontuação inconsistente
        if re.search(r'\s+[.,;:]', content):
            issues.append("Espaços antes de pontuação")
        
        # Verifica aspas inconsistentes
        if re.search(r'["""]', content) and re.search(r'["\']', content):
            issues.append("Uso inconsistente de aspas")
        
        return {
            "issues": issues,
            "score": 1.0 if not issues else max(0.5, 1.0 - len(issues) * 0.1)
        }
    
    def _calculate_quality_score(self, avg_words_per_sentence: float, term_consistency: Dict, formatting: Dict) -> float:
        """Calcula score geral de qualidade."""
        # Score de legibilidade (ideal: 15-25 palavras por sentença)
        readability_score = 1.0 if 15 <= avg_words_per_sentence <= 25 else 0.7
        
        # Média ponderada
        overall = (
            readability_score * 0.3 +
            term_consistency["score"] * 0.4 +
            formatting["score"] * 0.3
        )
        
        return round(overall, 2)
    
    def _extract_metadata(self, content: str, file_path: str) -> Dict:
        """Extrai metadados do manuscrito."""
        # Tenta extrair título (primeira linha H1 ou primeira linha)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else Path(file_path).stem
        
        # Tenta extrair autor
        author_match = re.search(r'(?:autor|author)[:\s]+(.+)$', content, re.MULTILINE | re.IGNORECASE)
        author = author_match.group(1).strip() if author_match else "Autor Desconhecido"
        
        return {
            "title": title,
            "author": author,
            "file_name": Path(file_path).name,
            "file_size": Path(file_path).stat().st_size if Path(file_path).exists() else 0
        }
    
    def identify_opportunities(self, analysis_result: Dict) -> Dict:
        """
        Identifica oportunidades de aprimoramento baseado na análise.
        
        Args:
            analysis_result: Resultado da análise do manuscrito
            
        Returns:
            Dicionário com oportunidades identificadas
        """
        opportunities = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": []
        }
        
        # Análise de estrutura
        if analysis_result["structure"]["chapter_count"] == 0:
            opportunities["high_priority"].append({
                "category": "structure",
                "issue": "Nenhum capítulo identificado",
                "suggestion": "Adicionar marcadores de capítulo (# Capítulo 1, etc.)"
            })
        
        # Análise de conteúdo
        if analysis_result["content_analysis"]["reference_count"] == 0:
            opportunities["medium_priority"].append({
                "category": "references",
                "issue": "Nenhuma referência bibliográfica encontrada",
                "suggestion": "Adicionar seção de referências bibliográficas"
            })
        
        # Análise de qualidade
        quality = analysis_result["quality"]
        if quality["overall_score"] < 0.7:
            opportunities["high_priority"].append({
                "category": "quality",
                "issue": f"Score de qualidade baixo ({quality['overall_score']})",
                "suggestion": "Revisar formatação, consistência terminológica e legibilidade"
            })
        
        # Análise de formatação
        if quality["formatting"]["issues"]:
            opportunities["medium_priority"].append({
                "category": "formatting",
                "issue": "Problemas de formatação detectados",
                "suggestion": f"Corrigir: {', '.join(quality['formatting']['issues'])}"
            })
        
        return opportunities
    
    def save_analysis(self, analysis_result: Dict, output_path: str):
        """
        Salva análise em arquivo Markdown.
        Alias para save_report para compatibilidade.
        """
        self.save_report(analysis_result, Path(output_path))
    
    def save_report(self, analysis_result: Dict, output_path: Path):
        """Salva relatório de análise em arquivo Markdown."""
        lines = [
            "# RELATÓRIO DE ANÁLISE DO MANUSCRITO",
            "",
            f"**Arquivo:** {analysis_result['file_path']}",
            f"**Título:** {analysis_result['metadata']['title']}",
            f"**Autor:** {analysis_result['metadata']['author']}",
            "",
            "---",
            "",
            "## ESTATÍSTICAS GERAIS",
            "",
            f"- **Palavras:** {analysis_result['word_count']:,}",
            f"- **Páginas Estimadas:** {analysis_result['page_count']}",
            f"- **Parágrafos:** {analysis_result['content_analysis']['paragraph_count']}",
            f"- **Sentenças:** {analysis_result['content_analysis']['sentence_count']}",
            "",
            "## ESTRUTURA",
            "",
            f"- **Capítulos:** {analysis_result['structure']['chapter_count']}",
            f"- **Seções:** {analysis_result['structure']['section_count']}",
            f"- **Figuras:** {analysis_result['structure']['figure_count']}",
            f"- **Tabelas:** {analysis_result['structure']['table_count']}",
            "",
            "## QUALIDADE",
            "",
            f"- **Score Geral:** {analysis_result['quality']['overall_score']}/1.0",
            f"- **Média de Palavras por Sentença:** {analysis_result['quality']['avg_words_per_sentence']}",
            f"- **Consistência Terminológica:** {analysis_result['quality']['term_consistency']['score']}/1.0",
            f"- **Formatação:** {analysis_result['quality']['formatting']['score']}/1.0",
            ""
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def save_opportunities_report(self, opportunities: Dict, output_path: Path):
        """Salva relatório de oportunidades em arquivo Markdown."""
        lines = [
            "# OPORTUNIDADES DE APRIMORAMENTO",
            "",
            "## PRIORIDADE ALTA",
            ""
        ]
        
        for opp in opportunities["high_priority"]:
            lines.append(f"### {opp['category'].upper()}")
            lines.append(f"- **Problema:** {opp['issue']}")
            lines.append(f"- **Sugestão:** {opp['suggestion']}")
            lines.append("")
        
        lines.extend([
            "## PRIORIDADE MÉDIA",
            ""
        ])
        
        for opp in opportunities["medium_priority"]:
            lines.append(f"### {opp['category'].upper()}")
            lines.append(f"- **Problema:** {opp['issue']}")
            lines.append(f"- **Sugestão:** {opp['suggestion']}")
            lines.append("")
        
        lines.extend([
            "## PRIORIDADE BAIXA",
            ""
        ])
        
        for opp in opportunities["low_priority"]:
            lines.append(f"### {opp['category'].upper()}")
            lines.append(f"- **Problema:** {opp['issue']}")
            lines.append(f"- **Sugestão:** {opp['suggestion']}")
            lines.append("")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
