"""
Proof Checker - Sistema de Revisão Automatizada de Provas.

Este módulo implementa verificação automatizada de erros tipográficos,
formatação, layout e referências cruzadas em PDFs e documentos.

Autor: Manus AI
Versão: 1.0.0
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import PyPDF2
    import pdfplumber
except ImportError:
    PyPDF2 = None
    pdfplumber = None

try:
    import language_tool_python
except ImportError:
    language_tool_python = None


class IssueSeverity(Enum):
    """Severidade de problemas encontrados."""
    CRITICAL = "critical"  # Deve ser corrigido
    HIGH = "high"         # Muito recomendado corrigir
    MEDIUM = "medium"     # Recomendado corrigir
    LOW = "low"          # Opcional corrigir
    INFO = "info"        # Apenas informativo


@dataclass
class Issue:
    """Representa um problema encontrado."""
    category: str
    severity: IssueSeverity
    description: str
    location: str
    suggestion: Optional[str] = None
    page: Optional[int] = None


class ProofChecker:
    """Sistema automatizado de revisão de provas."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o revisor de provas.
        
        Args:
            config: Dicionário de configuração com opções:
                - language: Idioma para verificação (padrão: 'pt-BR')
                - check_grammar: Ativar verificação gramatical
                - check_formatting: Ativar verificação de formatação
                - check_layout: Ativar verificação de layout
                - check_references: Ativar verificação de referências
        """
        self.config = config or {}
        self.language = self.config.get('language', 'pt-BR')
        
        # Configurar verificações ativas
        self.check_grammar = self.config.get('check_grammar', True)
        self.check_formatting = self.config.get('check_formatting', True)
        self.check_layout = self.config.get('check_layout', True)
        self.check_references = self.config.get('check_references', True)
        
        # Inicializar ferramenta gramatical se disponível
        self.grammar_tool = None
        if self.check_grammar and language_tool_python:
            try:
                self.grammar_tool = language_tool_python.LanguageTool(self.language)
            except Exception as e:
                print(f"⚠️  Não foi possível inicializar verificador gramatical: {e}")
    
    def check_all(self, file_path: str) -> List[Issue]:
        """
        Executa todas as verificações em um arquivo.
        
        Args:
            file_path: Caminho para o arquivo (PDF, MD, TXT)
            
        Returns:
            Lista de problemas encontrados
        """
        print(f"🔍 Iniciando revisão de provas de '{file_path}'...")
        
        issues = []
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Determinar tipo de arquivo e executar verificações apropriadas
        if path.suffix.lower() == '.pdf':
            issues.extend(self._check_pdf(file_path))
        else:
            # Arquivo de texto (MD, TXT, HTML)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            issues.extend(self._check_text(content))
        
        # Ordenar por severidade
        issues.sort(key=lambda x: list(IssueSeverity).index(x.severity))
        
        print(f"  ✅ Revisão concluída: {len(issues)} problemas encontrados")
        self._print_summary(issues)
        
        return issues
    
    def _check_pdf(self, pdf_path: str) -> List[Issue]:
        """Verifica problemas em PDF."""
        issues = []
        
        if not PyPDF2 or not pdfplumber:
            issues.append(Issue(
                category="system",
                severity=IssueSeverity.INFO,
                description="Bibliotecas PDF não instaladas. Instale PyPDF2 e pdfplumber.",
                location="sistema"
            ))
            return issues
        
        # Extrair texto e verificar
        print("  📄 Extraindo texto do PDF...")
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    page_issues = self._check_text(text, page_num)
                    issues.extend(page_issues)
                
                # Verificar layout da página
                if self.check_layout:
                    layout_issues = self._check_page_layout(page, page_num)
                    issues.extend(layout_issues)
        
        # Verificar metadados e estrutura do PDF
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            
            # Verificar número de páginas
            num_pages = len(pdf_reader.pages)
            issues.append(Issue(
                category="info",
                severity=IssueSeverity.INFO,
                description=f"Total de páginas: {num_pages}",
                location="documento"
            ))
            
            # Verificar metadados
            metadata = pdf_reader.metadata
            if metadata:
                if not metadata.get('/Title'):
                    issues.append(Issue(
                        category="metadata",
                        severity=IssueSeverity.LOW,
                        description="Título não definido nos metadados do PDF",
                        location="metadados",
                        suggestion="Adicionar título nos metadados"
                    ))
                if not metadata.get('/Author'):
                    issues.append(Issue(
                        category="metadata",
                        severity=IssueSeverity.LOW,
                        description="Autor não definido nos metadados do PDF",
                        location="metadados",
                        suggestion="Adicionar autor nos metadados"
                    ))
        
        return issues
    
    def _check_text(self, text: str, page_num: Optional[int] = None) -> List[Issue]:
        """Verifica problemas em texto."""
        issues = []
        location = f"página {page_num}" if page_num else "documento"
        
        # 1. Verificação gramatical
        if self.check_grammar and self.grammar_tool:
            grammar_issues = self._check_grammar_text(text, location)
            issues.extend(grammar_issues)
        
        # 2. Verificação de formatação
        if self.check_formatting:
            formatting_issues = self._check_formatting_text(text, location)
            issues.extend(formatting_issues)
        
        # 3. Verificação de referências
        if self.check_references:
            reference_issues = self._check_references_text(text, location)
            issues.extend(reference_issues)
        
        return issues
    
    def _check_grammar_text(self, text: str, location: str) -> List[Issue]:
        """Verifica gramática e ortografia."""
        issues = []
        
        try:
            matches = self.grammar_tool.check(text)
            
            # Limitar a 50 problemas por página para não sobrecarregar
            for match in matches[:50]:
                issues.append(Issue(
                    category="grammar",
                    severity=self._map_grammar_severity(match.ruleIssueType),
                    description=match.message,
                    location=location,
                    suggestion=", ".join(match.replacements[:3]) if match.replacements else None
                ))
        except Exception as e:
            print(f"  ⚠️  Erro na verificação gramatical: {e}")
        
        return issues
    
    def _check_formatting_text(self, text: str, location: str) -> List[Issue]:
        """Verifica problemas de formatação."""
        issues = []
        
        # Espaços múltiplos
        if re.search(r'  +', text):
            issues.append(Issue(
                category="formatting",
                severity=IssueSeverity.MEDIUM,
                description="Espaços múltiplos encontrados",
                location=location,
                suggestion="Substituir por espaço único"
            ))
        
        # Espaços antes de pontuação
        if re.search(r' [.,;:!?]', text):
            issues.append(Issue(
                category="formatting",
                severity=IssueSeverity.MEDIUM,
                description="Espaço antes de pontuação",
                location=location,
                suggestion="Remover espaço antes de pontuação"
            ))
        
        # Falta de espaço após pontuação
        if re.search(r'[.,;:!?][A-Za-zÀ-ÿ]', text):
            issues.append(Issue(
                category="formatting",
                severity=IssueSeverity.MEDIUM,
                description="Falta espaço após pontuação",
                location=location,
                suggestion="Adicionar espaço após pontuação"
            ))
        
        # Linhas muito longas (mais de 100 caracteres sem quebra)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if len(line) > 100 and ' ' not in line[-50:]:
                issues.append(Issue(
                    category="formatting",
                    severity=IssueSeverity.LOW,
                    description=f"Linha {i+1} muito longa sem quebras",
                    location=location,
                    suggestion="Verificar quebra de linha"
                ))
        
        # Aspas inconsistentes
        single_quotes = text.count("'")
        double_quotes = text.count('"')
        if single_quotes % 2 != 0:
            issues.append(Issue(
                category="formatting",
                severity=IssueSeverity.HIGH,
                description="Aspas simples desbalanceadas",
                location=location,
                suggestion="Verificar fechamento de aspas"
            ))
        if double_quotes % 2 != 0:
            issues.append(Issue(
                category="formatting",
                severity=IssueSeverity.HIGH,
                description="Aspas duplas desbalanceadas",
                location=location,
                suggestion="Verificar fechamento de aspas"
            ))
        
        # Parênteses desbalanceados
        if text.count('(') != text.count(')'):
            issues.append(Issue(
                category="formatting",
                severity=IssueSeverity.HIGH,
                description="Parênteses desbalanceados",
                location=location,
                suggestion="Verificar fechamento de parênteses"
            ))
        
        return issues
    
    def _check_references_text(self, text: str, location: str) -> List[Issue]:
        """Verifica referências e citações."""
        issues = []
        
        # Detectar citações (Autor, Ano)
        citations = re.findall(r'\([A-ZÀ-Ý][a-zà-ÿ]+(?:\s+et\s+al\.)?,\s*\d{4}\)', text)
        
        # Detectar referências quebradas [?]
        broken_refs = re.findall(r'\[\?\]', text)
        if broken_refs:
            issues.append(Issue(
                category="references",
                severity=IssueSeverity.CRITICAL,
                description=f"{len(broken_refs)} referência(s) quebrada(s) encontrada(s)",
                location=location,
                suggestion="Verificar e corrigir referências"
            ))
        
        # Detectar URLs quebradas
        broken_urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+\s+[^\s<>"{}|\\^`\[\]]+', text)
        if broken_urls:
            issues.append(Issue(
                category="references",
                severity=IssueSeverity.MEDIUM,
                description="Possível URL quebrada em múltiplas linhas",
                location=location,
                suggestion="Verificar URLs"
            ))
        
        return issues
    
    def _check_page_layout(self, page, page_num: int) -> List[Issue]:
        """Verifica problemas de layout em uma página PDF."""
        issues = []
        location = f"página {page_num}"
        
        # Extrair palavras com posições
        words = page.extract_words()
        
        if not words:
            issues.append(Issue(
                category="layout",
                severity=IssueSeverity.HIGH,
                description="Página vazia ou sem texto extraível",
                location=location
            ))
            return issues
        
        # Verificar viúvas (linha única no topo da página)
        first_line_words = [w for w in words if w['top'] < 100]
        if len(first_line_words) < 5:
            issues.append(Issue(
                category="layout",
                severity=IssueSeverity.MEDIUM,
                description="Possível viúva (linha isolada no topo)",
                location=location,
                suggestion="Ajustar quebra de página anterior"
            ))
        
        # Verificar órfãs (linha única no final da página)
        page_height = page.height
        last_line_words = [w for w in words if w['bottom'] > page_height - 100]
        if len(last_line_words) < 5:
            issues.append(Issue(
                category="layout",
                severity=IssueSeverity.MEDIUM,
                description="Possível órfã (linha isolada no final)",
                location=location,
                suggestion="Ajustar quebra de página"
            ))
        
        # Verificar alinhamento inconsistente
        x_positions = [w['x0'] for w in words]
        unique_x = set(round(x, 1) for x in x_positions)
        if len(unique_x) > 20:
            issues.append(Issue(
                category="layout",
                severity=IssueSeverity.LOW,
                description="Alinhamento possivelmente inconsistente",
                location=location
            ))
        
        return issues
    
    def _map_grammar_severity(self, issue_type: str) -> IssueSeverity:
        """Mapeia tipo de problema gramatical para severidade."""
        if issue_type in ['misspelling', 'typographical']:
            return IssueSeverity.HIGH
        elif issue_type in ['grammar', 'syntax']:
            return IssueSeverity.MEDIUM
        elif issue_type in ['style', 'register']:
            return IssueSeverity.LOW
        else:
            return IssueSeverity.INFO
    
    def _print_summary(self, issues: List[Issue]):
        """Imprime resumo dos problemas encontrados."""
        if not issues:
            print("  🎉 Nenhum problema encontrado!")
            return
        
        # Contar por severidade
        by_severity = {}
        for issue in issues:
            severity = issue.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        print("\n  📊 Resumo:")
        severity_icons = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢',
            'info': 'ℹ️'
        }
        
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = by_severity.get(severity, 0)
            if count > 0:
                icon = severity_icons[severity]
                print(f"     {icon} {severity.capitalize()}: {count}")
    
    def generate_report(self, issues: List[Issue], output_path: str):
        """
        Gera relatório detalhado dos problemas encontrados.
        
        Args:
            issues: Lista de problemas
            output_path: Caminho para o arquivo de relatório (MD ou TXT)
        """
        print(f"  📝 Gerando relatório em '{output_path}'...")
        
        report = "# Relatório de Revisão de Provas\n\n"
        report += f"**Total de problemas encontrados:** {len(issues)}\n\n"
        
        # Agrupar por categoria
        by_category = {}
        for issue in issues:
            if issue.category not in by_category:
                by_category[issue.category] = []
            by_category[issue.category].append(issue)
        
        # Gerar seções por categoria
        for category, category_issues in sorted(by_category.items()):
            report += f"## {category.capitalize()}\n\n"
            report += f"**{len(category_issues)} problema(s) encontrado(s)**\n\n"
            
            for issue in category_issues:
                severity_emoji = {
                    IssueSeverity.CRITICAL: "🔴",
                    IssueSeverity.HIGH: "🟠",
                    IssueSeverity.MEDIUM: "🟡",
                    IssueSeverity.LOW: "🟢",
                    IssueSeverity.INFO: "ℹ️"
                }
                
                report += f"### {severity_emoji[issue.severity]} {issue.description}\n\n"
                report += f"- **Localização:** {issue.location}\n"
                report += f"- **Severidade:** {issue.severity.value}\n"
                if issue.suggestion:
                    report += f"- **Sugestão:** {issue.suggestion}\n"
                report += "\n"
        
        # Salvar relatório
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"  ✅ Relatório salvo em '{output_path}'")


# Função de conveniência
def check_proof(file_path: str, 
                output_report: Optional[str] = None,
                language: str = 'pt-BR') -> List[Issue]:
    """
    Função de conveniência para revisar provas.
    
    Args:
        file_path: Caminho para o arquivo a ser revisado
        output_report: Caminho opcional para salvar relatório
        language: Idioma para verificação (padrão: 'pt-BR')
        
    Returns:
        Lista de problemas encontrados
    """
    checker = ProofChecker({'language': language})
    issues = checker.check_all(file_path)
    
    if output_report:
        checker.generate_report(issues, output_report)
    
    return issues
