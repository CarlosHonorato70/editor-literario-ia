"""
Módulo de Geração de Elementos
Gera elementos pré-textuais e pós-textuais do manuscrito.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime
import logging

from .config import Config
from .utils import print_info

class ElementsGenerator:
    """Gera elementos complementares do manuscrito."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def generate_all(self, enhanced_content: Dict, metadata: Dict) -> Dict:
        """
        Gera todos os elementos pré e pós-textuais.
        
        Args:
            enhanced_content: Conteúdo aprimorado do manuscrito
            metadata: Metadados do manuscrito
            
        Returns:
            Dicionário com todos os elementos gerados
        """
        print_info("Gerando elementos pré e pós-textuais...")
        
        elements = {
            "files": {},
            "statistics": {}
        }
        
        # Elementos pré-textuais
        if self.config.generate_pre_textual:
            elements["files"]["Folha_Rosto"] = self._generate_title_page(metadata)
            elements["files"]["Ficha_Catalografica"] = self._generate_cataloging(metadata)
            elements["files"]["Dedicatoria"] = self._generate_dedication(metadata)
            elements["files"]["Agradecimentos"] = self._generate_acknowledgments(metadata)
            elements["files"]["Prefacio"] = self._generate_preface(metadata, enhanced_content)
            elements["files"]["Sumario"] = self._generate_toc(enhanced_content["content"])
        
        # Elementos pós-textuais
        if self.config.generate_post_textual:
            if self.config.generate_glossary:
                elements["files"]["Glossario"] = self._generate_glossary(enhanced_content["content"])
            
            if self.config.generate_index:
                elements["files"]["Indice_Remissivo"] = self._generate_index(enhanced_content["content"])
            
            elements["files"]["Referencias"] = self._extract_references(enhanced_content["content"])
        
        elements["statistics"] = {
            "pre_textual_count": sum(1 for k in elements["files"].keys() if k in [
                "Folha_Rosto", "Ficha_Catalografica", "Dedicatoria", 
                "Agradecimentos", "Prefacio", "Sumario"
            ]),
            "post_textual_count": sum(1 for k in elements["files"].keys() if k in [
                "Glossario", "Indice_Remissivo", "Referencias"
            ])
        }
        
        return elements
    
    def _generate_title_page(self, metadata: Dict) -> str:
        """Gera folha de rosto."""
        title = metadata.get("title", "Título do Manuscrito")
        author = metadata.get("author", "Autor")
        year = datetime.now().year
        
        return f"""# {title}

**Autor:** {author}

**Ano:** {year}

---

## Informações Bibliográficas

**Título:** {title}

**Autor:** {author}

**Formato:** {self.config.default_format}

**Fonte:** {self.config.default_font}

**Ano de Publicação:** {year}

---

© {year} {author}. Todos os direitos reservados.
"""
    
    def _generate_cataloging(self, metadata: Dict) -> str:
        """Gera ficha catalográfica."""
        title = metadata.get("title", "Título")
        author = metadata.get("author", "Autor")
        year = datetime.now().year
        
        # Extrai sobrenome do autor
        author_parts = author.split()
        last_name = author_parts[-1] if author_parts else "Autor"
        
        return f"""## FICHA CATALOGRÁFICA

---

**{last_name.upper()}, {author}**

{title} / {author}. – {year}.

{metadata.get('page_count', 'XXX')} p. : il.

ISBN XXX-XX-XXXX-XXX-X

1. {self._infer_subject(title)}. I. Título.

CDD XXX.XX

---

*Ficha catalográfica elaborada conforme normas da AACR2*
"""
    
    def _infer_subject(self, title: str) -> str:
        """Infere assunto principal do título."""
        # Heurística simples baseada em palavras-chave
        keywords = {
            "psicoterapia": "Psicoterapia",
            "emoção": "Emoções",
            "cérebro": "Neurociência",
            "terapia": "Terapia",
            "clínica": "Psicologia Clínica",
        }
        
        title_lower = title.lower()
        for keyword, subject in keywords.items():
            if keyword in title_lower:
                return subject
        
        return "Assunto Principal"
    
    def _generate_dedication(self, metadata: Dict) -> str:
        """Gera dedicatória."""
        return """## DEDICATÓRIA

---

*Dedico este trabalho a todos aqueles que buscam compreender a complexidade da mente humana e contribuir para o bem-estar das pessoas.*

---
"""
    
    def _generate_acknowledgments(self, metadata: Dict) -> str:
        """Gera agradecimentos."""
        author = metadata.get("author", "o autor")
        
        return f"""## AGRADECIMENTOS

---

{author} agradece:

**Aos leitores e profissionais** que dedicarão seu tempo à leitura desta obra, confiando que ela possa contribuir para sua prática e compreensão.

**Aos pesquisadores e teóricos** cujo trabalho fundamentou este manuscrito, especialmente aqueles que ousaram questionar paradigmas estabelecidos e propor novas formas de compreender fenômenos complexos.

**Aos revisores e colaboradores** que contribuíram com sugestões valiosas para o aprimoramento deste trabalho.

**À comunidade acadêmica e profissional** que mantém vivo o debate científico e a busca por conhecimento baseado em evidências.

**Aos familiares e amigos** pelo apoio incondicional durante o processo de elaboração desta obra.

Este trabalho é resultado de inúmeras conversas, leituras, reflexões e, acima de tudo, do compromisso com a excelência e o rigor científico.

---
"""
    
    def _generate_preface(self, metadata: Dict, enhanced_content: Dict) -> str:
        """Gera prefácio."""
        title = metadata.get("title", "esta obra")
        word_count = enhanced_content.get("original_length", 0)
        
        return f"""## PREFÁCIO

---

### Por Que Este Livro Existe

{title} nasceu da necessidade de integrar conhecimentos dispersos e oferecer uma visão coerente e fundamentada sobre seu tema central. Em um campo caracterizado por múltiplas abordagens e perspectivas, este trabalho busca construir pontes e propor sínteses que respeitem a complexidade dos fenômenos estudados.

### Para Quem Este Livro Foi Escrito

Esta obra destina-se a:

- **Profissionais** que buscam fundamentação teórica sólida para sua prática
- **Pesquisadores** interessados em perspectivas integradoras
- **Estudantes** que desejam compreender o estado da arte do campo
- **Leitores** comprometidos com o aprofundamento de seu conhecimento

### Como Usar Este Livro

O manuscrito está organizado de forma a permitir diferentes percursos de leitura:

1. **Leitura Linear:** Seguir a sequência dos capítulos para compreensão progressiva
2. **Leitura Temática:** Consultar capítulos específicos conforme áreas de interesse
3. **Leitura de Referência:** Utilizar como fonte de consulta para temas específicos

### Estrutura da Obra

O conteúdo está organizado em partes e capítulos que se complementam, construindo progressivamente uma compreensão abrangente do tema. Cada capítulo pode ser lido de forma independente, mas ganha profundidade quando integrado ao conjunto da obra.

### Convite ao Leitor

Convido você a abordar este texto com mente aberta e espírito crítico. Questione, reflita, dialogue com as ideias apresentadas. Este livro não pretende oferecer respostas definitivas, mas sim contribuir para um debate informado e produtivo.

Boa leitura!

---

*{metadata.get('author', 'O Autor')}*

*{datetime.now().strftime('%B de %Y')}*

---
"""
    
    def _generate_toc(self, content: str) -> str:
        """Gera sumário (table of contents)."""
        lines = ["## SUMÁRIO", "", "---", ""]
        
        # Extrai headings
        headings = []
        for match in re.finditer(r'^(#{1,4})\s+(.+)$', content, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2)
            headings.append((level, title))
        
        # Gera sumário
        page = 1
        for level, title in headings:
            indent = "  " * (level - 1)
            lines.append(f"{indent}- {title} ... {page}")
            page += 5  # Estimativa simplificada
        
        lines.extend(["", "---", ""])
        
        return '\n'.join(lines)
    
    def _generate_glossary(self, content: str) -> str:
        """Gera glossário de termos."""
        lines = ["## GLOSSÁRIO", "", "---", ""]
        
        # Termos técnicos comuns (expandir conforme necessário)
        terms = {
            "Teoria da Emoção Construída": "Teoria neurocientífica que propõe que emoções são construções ativas do cérebro, não reações automáticas a estímulos.",
            "TCE": "Sigla para Teoria da Emoção Construída.",
            "Interocepção": "Percepção do estado interno do corpo, incluindo sinais de órgãos internos.",
            "Predição": "Processo pelo qual o cérebro antecipa eventos futuros baseado em experiências passadas.",
            "Orçamento Corporal": "Sistema de gerenciamento de recursos do corpo (energia, água, glicose, etc.).",
            "Granularidade Emocional": "Capacidade de fazer distinções precisas entre diferentes estados emocionais.",
            "Conceito Emocional": "Representação mental que o cérebro usa para categorizar experiências como emoções específicas.",
            "Modelo Preditivo": "Framework teórico que entende o cérebro como um órgão que constantemente gera predições sobre o mundo.",
        }
        
        # Detecta termos presentes no conteúdo
        present_terms = {}
        for term, definition in terms.items():
            if term in content:
                present_terms[term] = definition
        
        # Ordena alfabeticamente
        for term in sorted(present_terms.keys()):
            lines.append(f"**{term}**")
            lines.append(f": {present_terms[term]}")
            lines.append("")
        
        if not present_terms:
            lines.append("*Nenhum termo técnico identificado para inclusão no glossário.*")
            lines.append("")
        
        lines.extend(["---", ""])
        
        return '\n'.join(lines)
    
    def _generate_index(self, content: str) -> str:
        """Gera índice remissivo."""
        lines = ["## ÍNDICE REMISSIVO", "", "---", ""]
        
        # Termos para indexar (expandir conforme necessário)
        index_terms = [
            "emoção", "cérebro", "predição", "interocepção",
            "terapia", "modelo", "teoria", "prática",
            "cliente", "terapeuta", "vínculo", "palavra", "imagem"
        ]
        
        # Conta ocorrências
        term_counts = {}
        for term in index_terms:
            count = len(re.findall(r'\b' + re.escape(term) + r'\b', content, re.IGNORECASE))
            if count > 0:
                term_counts[term] = count
        
        # Gera índice
        for term in sorted(term_counts.keys()):
            lines.append(f"**{term.capitalize()}** ({term_counts[term]} referências)")
        
        if not term_counts:
            lines.append("*Índice em construção.*")
        
        lines.extend(["", "---", ""])
        
        return '\n'.join(lines)
    
    def _extract_references(self, content: str) -> str:
        """Extrai e formata referências bibliográficas."""
        lines = ["## REFERÊNCIAS BIBLIOGRÁFICAS", "", "---", ""]
        
        # Procura seção de referências
        ref_match = re.search(
            r'(REFERÊNCIAS|BIBLIOGRAFIA|REFERENCES).*$',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if ref_match:
            ref_section = ref_match.group(0)
            
            # Extrai linhas que parecem referências
            ref_lines = []
            for line in ref_section.split('\n'):
                line = line.strip()
                # Heurística: linha com ano entre parênteses e ponto final
                if re.search(r'\(\d{4}\)', line) and line.endswith('.'):
                    ref_lines.append(line)
            
            if ref_lines:
                lines.extend(ref_lines)
            else:
                lines.append("*Referências não identificadas automaticamente. Revisar manualmente.*")
        else:
            lines.append("*Seção de referências não encontrada no manuscrito original.*")
            lines.append("")
            lines.append("**Sugestão:** Adicionar seção de referências bibliográficas seguindo normas ABNT ou APA.")
        
        lines.extend(["", "---", ""])
        
        return '\n'.join(lines)
