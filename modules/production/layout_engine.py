"""
Layout Engine - Motor de Diagramação Automatizada de Livros.

Este módulo implementa diagramação profissional automatizada usando HTML/CSS + WeasyPrint.
Suporta múltiplos formatos, gêneros e estilos de livros.

Autor: Manus AI
Versão: 1.0.0
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from jinja2 import Environment, FileSystemLoader, Template
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


class LayoutEngine:
    """Motor de diagramação automatizada de livros."""
    
    # Formatos de página suportados (largura x altura em mm)
    PAGE_FORMATS = {
        'A4': (210, 297),
        'A5': (148, 210),
        'B5': (176, 250),
        'US_LETTER': (216, 279),
        'US_TRADE': (152, 229),
        '6x9': (152, 229),  # Formato comum nos EUA
        'POCKET': (110, 178)  # Livro de bolso
    }
    
    # Margens por gênero (em mm: topo, externa, inferior, interna)
    MARGINS_BY_GENRE = {
        'academic': (25, 20, 25, 30),  # Margens amplas para notas
        'fiction': (20, 15, 20, 20),   # Margens menores
        'technical': (25, 20, 25, 25), # Espaço para código
        'poetry': (30, 25, 30, 25),    # Margens generosas
        'default': (22, 18, 22, 22)
    }
    
    # Tipografia por gênero
    TYPOGRAPHY_BY_GENRE = {
        'academic': {
            'body_font': 'Georgia, serif',
            'heading_font': 'Arial, sans-serif',
            'body_size': '11pt',
            'line_height': '1.5',
            'heading_scale': [2.0, 1.5, 1.25, 1.1, 1.0]
        },
        'fiction': {
            'body_font': 'Garamond, serif',
            'heading_font': 'Garamond, serif',
            'body_size': '12pt',
            'line_height': '1.6',
            'heading_scale': [2.2, 1.6, 1.3, 1.1, 1.0]
        },
        'technical': {
            'body_font': 'DejaVu Sans, sans-serif',
            'heading_font': 'DejaVu Sans, sans-serif',
            'body_size': '10pt',
            'line_height': '1.4',
            'heading_scale': [1.8, 1.4, 1.2, 1.05, 1.0],
            'code_font': 'DejaVu Sans Mono, monospace'
        },
        'poetry': {
            'body_font': 'Palatino, serif',
            'heading_font': 'Palatino, serif',
            'body_size': '11pt',
            'line_height': '1.8',
            'heading_scale': [2.0, 1.5, 1.2, 1.0, 1.0]
        }
    }
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o motor de diagramação.
        
        Args:
            config: Dicionário de configuração com opções:
                - format: Formato da página (padrão: 'A5')
                - genre: Gênero do livro (padrão: 'academic')
                - custom_css: CSS customizado adicional
                - template_dir: Diretório de templates customizados
        """
        self.config = config or {}
        self.format = self.config.get('format', 'A5')
        self.genre = self.config.get('genre', 'academic')
        
        # Configurar diretórios
        self.module_dir = Path(__file__).parent
        self.template_dir = Path(self.config.get(
            'template_dir',
            self.module_dir / 'templates' / 'layouts'
        ))
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False
        )
        
        # Configuração de fontes para WeasyPrint
        self.font_config = FontConfiguration()
        
    def layout_book(self, 
                    content_path: str,
                    metadata: Dict,
                    output_path: str,
                    cover_path: Optional[str] = None) -> Dict:
        """
        Diagrama um livro completo.
        
        Args:
            content_path: Caminho para o arquivo de conteúdo (MD, HTML, TXT)
            metadata: Metadados do livro (título, autor, etc.)
            output_path: Caminho para o PDF de saída
            cover_path: Caminho opcional para imagem de capa
            
        Returns:
            Dicionário com informações sobre o processo
        """
        print(f"📐 Iniciando diagramação de '{metadata.get('title', 'Livro')}'...")
        
        # 1. Carregar e processar conteúdo
        print("  📄 Processando conteúdo...")
        content = self._load_content(content_path)
        structured_content = self._structure_content(content, metadata)
        
        # 2. Gerar HTML
        print("  🔨 Gerando HTML...")
        html_content = self._generate_html(structured_content, metadata, cover_path)
        
        # 3. Gerar CSS
        print("  🎨 Aplicando estilos...")
        css_content = self._generate_css()
        
        # 4. Renderizar PDF
        print("  📦 Renderizando PDF...")
        self._render_pdf(html_content, css_content, output_path)
        
        # 5. Estatísticas
        stats = self._get_statistics(structured_content)
        
        print(f"  ✅ Diagramação concluída: {output_path}")
        print(f"     Páginas: ~{stats['estimated_pages']}")
        print(f"     Palavras: {stats['word_count']}")
        
        return {
            'output_path': output_path,
            'statistics': stats,
            'format': self.format,
            'genre': self.genre
        }
    
    def _load_content(self, content_path: str) -> str:
        """Carrega conteúdo do arquivo."""
        path = Path(content_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {content_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Converter Markdown para HTML se necessário
        if path.suffix.lower() in ['.md', '.markdown']:
            content = markdown.markdown(
                content,
                extensions=[
                    'extra',
                    'codehilite',
                    'toc',
                    'tables',
                    'fenced_code'
                ]
            )
        
        return content
    
    def _structure_content(self, content: str, metadata: Dict) -> Dict:
        """Estrutura o conteúdo em seções lógicas."""
        
        # Detectar estrutura de capítulos
        chapters = self._detect_chapters(content)
        
        # Extrair elementos especiais
        toc = self._generate_toc(chapters)
        
        return {
            'metadata': metadata,
            'chapters': chapters,
            'toc': toc,
            'has_cover': metadata.get('cover_path') is not None
        }
    
    def _detect_chapters(self, content: str) -> List[Dict]:
        """Detecta e extrai capítulos do conteúdo."""
        chapters = []
        
        # Padrões para detectar capítulos
        patterns = [
            r'<h1[^>]*>(.*?)</h1>',  # HTML h1
            r'^# (.+)$',              # Markdown h1
            r'CAPÍTULO \d+',          # Capítulo explícito
            r'PARTE \d+',             # Parte explícita
        ]
        
        # Dividir por h1 (principal indicador de capítulo)
        parts = re.split(r'(<h1[^>]*>.*?</h1>)', content, flags=re.DOTALL)
        
        current_chapter = None
        for i, part in enumerate(parts):
            if re.match(r'<h1[^>]*>.*?</h1>', part):
                # É um título de capítulo
                title = re.sub(r'<[^>]+>', '', part).strip()
                current_chapter = {
                    'title': title,
                    'content': '',
                    'number': len(chapters) + 1
                }
                chapters.append(current_chapter)
            elif current_chapter is not None:
                # É conteúdo do capítulo atual
                current_chapter['content'] += part
        
        # Se não encontrou capítulos, trata tudo como um único capítulo
        if not chapters:
            chapters = [{
                'title': 'Conteúdo',
                'content': content,
                'number': 1
            }]
        
        return chapters
    
    def _generate_toc(self, chapters: List[Dict]) -> str:
        """Gera sumário (table of contents)."""
        toc_html = '<nav id="toc" class="toc">\n'
        toc_html += '  <h1>Sumário</h1>\n'
        toc_html += '  <ul>\n'
        
        for chapter in chapters:
            toc_html += f'    <li><a href="#chapter-{chapter["number"]}">{chapter["title"]}</a></li>\n'
        
        toc_html += '  </ul>\n'
        toc_html += '</nav>\n'
        
        return toc_html
    
    def _generate_html(self, 
                       structured_content: Dict,
                       metadata: Dict,
                       cover_path: Optional[str]) -> str:
        """Gera HTML completo do livro."""
        
        # Template HTML base
        html_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="author" content="{{ metadata.author }}">
    <meta name="description" content="{{ metadata.get('description', '') }}">
    <title>{{ metadata.title }}</title>
</head>
<body>
    <!-- Capa -->
    {% if cover_path %}
    <section class="cover">
        <img src="{{ cover_path }}" alt="Capa">
    </section>
    {% endif %}
    
    <!-- Folha de rosto -->
    <section class="title-page">
        <h1 class="book-title">{{ metadata.title }}</h1>
        {% if metadata.get('subtitle') %}
        <h2 class="book-subtitle">{{ metadata.subtitle }}</h2>
        {% endif %}
        <p class="book-author">{{ metadata.author }}</p>
    </section>
    
    <!-- Ficha catalográfica -->
    {% if metadata.get('cataloging_data') %}
    <section class="cataloging">
        <div class="cataloging-box">
            {{ metadata.cataloging_data | safe }}
        </div>
    </section>
    {% endif %}
    
    <!-- Sumário -->
    {{ toc | safe }}
    
    <!-- Capítulos -->
    {% for chapter in chapters %}
    <section class="chapter" id="chapter-{{ chapter.number }}">
        <h1 class="chapter-title">{{ chapter.title }}</h1>
        <div class="chapter-content">
            {{ chapter.content | safe }}
        </div>
    </section>
    {% endfor %}
</body>
</html>
        """
        
        template = Template(html_template)
        
        html = template.render(
            metadata=metadata,
            cover_path=cover_path,
            toc=structured_content['toc'],
            chapters=structured_content['chapters']
        )
        
        return html
    
    def _generate_css(self) -> str:
        """Gera CSS para diagramação profissional."""
        
        # Obter configurações
        page_width, page_height = self.PAGE_FORMATS[self.format]
        margins = self.MARGINS_BY_GENRE.get(self.genre, self.MARGINS_BY_GENRE['default'])
        typo = self.TYPOGRAPHY_BY_GENRE.get(self.genre, self.TYPOGRAPHY_BY_GENRE['academic'])
        
        # Gerar CSS
        css = f"""
/* Configuração de página */
@page {{
    size: {page_width}mm {page_height}mm;
    margin-top: {margins[0]}mm;
    margin-right: {margins[1]}mm;
    margin-bottom: {margins[2]}mm;
    margin-left: {margins[3]}mm;
    
    @top-center {{
        content: string(chapter-title);
        font-size: 9pt;
        font-style: italic;
    }}
    
    @bottom-center {{
        content: counter(page);
        font-size: 10pt;
    }}
}}

/* Páginas especiais sem cabeçalho/rodapé */
@page :first {{
    @top-center {{ content: none; }}
    @bottom-center {{ content: none; }}
}}

@page cover {{
    margin: 0;
    @top-center {{ content: none; }}
    @bottom-center {{ content: none; }}
}}

/* Tipografia base */
body {{
    font-family: {typo['body_font']};
    font-size: {typo['body_size']};
    line-height: {typo['line_height']};
    text-align: justify;
    hyphens: auto;
    widows: 2;
    orphans: 2;
}}

/* Títulos */
h1, h2, h3, h4, h5, h6 {{
    font-family: {typo['heading_font']};
    font-weight: bold;
    page-break-after: avoid;
    page-break-inside: avoid;
}}

h1 {{ font-size: calc({typo['body_size']} * {typo['heading_scale'][0]}); margin-top: 0; }}
h2 {{ font-size: calc({typo['body_size']} * {typo['heading_scale'][1]}); }}
h3 {{ font-size: calc({typo['body_size']} * {typo['heading_scale'][2]}); }}
h4 {{ font-size: calc({typo['body_size']} * {typo['heading_scale'][3]}); }}
h5 {{ font-size: calc({typo['body_size']} * {typo['heading_scale'][4]}); }}

/* Parágrafos */
p {{
    margin: 0;
    text-indent: 1.5em;
}}

p:first-of-type,
h1 + p,
h2 + p,
h3 + p {{
    text-indent: 0;
}}

/* Citações */
blockquote {{
    margin: 1.5em 2em;
    padding-left: 1em;
    border-left: 3px solid #ccc;
    font-style: italic;
    page-break-inside: avoid;
}}

/* Listas */
ul, ol {{
    margin: 1em 0;
    padding-left: 2em;
}}

li {{
    margin: 0.5em 0;
}}

/* Tabelas */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1.5em 0;
    page-break-inside: avoid;
}}

th, td {{
    border: 1px solid #ddd;
    padding: 0.5em;
    text-align: left;
}}

th {{
    background-color: #f5f5f5;
    font-weight: bold;
}}

/* Código */
code {{
    font-family: {typo.get('code_font', 'monospace')};
    font-size: 0.9em;
    background-color: #f5f5f5;
    padding: 0.2em 0.4em;
    border-radius: 3px;
}}

pre {{
    background-color: #f5f5f5;
    padding: 1em;
    overflow-x: auto;
    page-break-inside: avoid;
}}

pre code {{
    background-color: transparent;
    padding: 0;
}}

/* Imagens */
img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
}}

/* Capa */
.cover {{
    page: cover;
    text-align: center;
}}

.cover img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
}}

/* Folha de rosto */
.title-page {{
    page-break-after: always;
    text-align: center;
    padding-top: 30%;
}}

.book-title {{
    font-size: 2.5em;
    margin-bottom: 0.5em;
}}

.book-subtitle {{
    font-size: 1.5em;
    font-weight: normal;
    margin-bottom: 2em;
}}

.book-author {{
    font-size: 1.2em;
    margin-top: 3em;
}}

/* Ficha catalográfica */
.cataloging {{
    page-break-after: always;
    padding-top: 60%;
}}

.cataloging-box {{
    border: 1px solid #000;
    padding: 1em;
    font-size: 0.9em;
    line-height: 1.3;
}}

/* Sumário */
.toc {{
    page-break-after: always;
}}

.toc h1 {{
    text-align: center;
    margin-bottom: 2em;
}}

.toc ul {{
    list-style: none;
    padding: 0;
}}

.toc li {{
    margin: 0.8em 0;
}}

.toc a {{
    text-decoration: none;
    color: #000;
}}

.toc a::after {{
    content: leader('.') target-counter(attr(href), page);
}}

/* Capítulos */
.chapter {{
    page-break-before: always;
}}

.chapter-title {{
    string-set: chapter-title content();
    text-align: center;
    margin-bottom: 2em;
    page-break-after: avoid;
}}

.chapter-content {{
    text-align: justify;
}}

/* Notas de rodapé */
.footnote {{
    font-size: 0.9em;
    float: footnote;
}}

/* Links */
a {{
    color: #000;
    text-decoration: underline;
}}

/* Quebras de página */
.page-break {{
    page-break-after: always;
}}

.no-break {{
    page-break-inside: avoid;
}}
        """
        
        # Adicionar CSS customizado se fornecido
        if 'custom_css' in self.config:
            css += f"\n\n/* CSS Customizado */\n{self.config['custom_css']}"
        
        return css
    
    def _render_pdf(self, html_content: str, css_content: str, output_path: str):
        """Renderiza HTML+CSS em PDF usando WeasyPrint."""
        
        # Criar objeto HTML
        html = HTML(string=html_content, base_url=str(self.template_dir))
        
        # Criar objeto CSS
        css = CSS(string=css_content, font_config=self.font_config)
        
        # Renderizar PDF
        html.write_pdf(
            output_path,
            stylesheets=[css],
            font_config=self.font_config
        )
    
    def _get_statistics(self, structured_content: Dict) -> Dict:
        """Calcula estatísticas do livro."""
        
        # Contar palavras
        total_words = 0
        for chapter in structured_content['chapters']:
            # Remover tags HTML
            text = re.sub(r'<[^>]+>', '', chapter['content'])
            words = len(text.split())
            total_words += words
        
        # Estimar páginas (aproximadamente 250-300 palavras por página)
        words_per_page = 275
        estimated_pages = max(1, round(total_words / words_per_page))
        
        return {
            'word_count': total_words,
            'chapter_count': len(structured_content['chapters']),
            'estimated_pages': estimated_pages
        }
    
    def export_print_ready(self, 
                          pdf_path: str,
                          output_path: str,
                          bleed: float = 3.0) -> str:
        """
        Exporta PDF pronto para impressão com sangria e marcas de corte.
        
        Args:
            pdf_path: Caminho do PDF de entrada
            output_path: Caminho do PDF de saída
            bleed: Sangria em mm (padrão: 3mm)
            
        Returns:
            Caminho do PDF exportado
        """
        # TODO: Implementar adição de sangria e marcas de corte
        # Requer PyPDF2 ou similar para manipulação de PDF
        
        print(f"  📦 Exportando PDF pronto para impressão...")
        print(f"     Sangria: {bleed}mm")
        print(f"     Saída: {output_path}")
        
        # Por enquanto, apenas copia o arquivo
        import shutil
        shutil.copy(pdf_path, output_path)
        
        return output_path


# Função de conveniência
def layout_book(content_path: str,
                metadata: Dict,
                output_path: str,
                format: str = 'A5',
                genre: str = 'academic',
                cover_path: Optional[str] = None) -> Dict:
    """
    Função de conveniência para diagramar um livro.
    
    Args:
        content_path: Caminho para o arquivo de conteúdo
        metadata: Metadados do livro
        output_path: Caminho para o PDF de saída
        format: Formato da página (padrão: 'A5')
        genre: Gênero do livro (padrão: 'academic')
        cover_path: Caminho opcional para imagem de capa
        
    Returns:
        Dicionário com informações sobre o processo
    """
    engine = LayoutEngine({'format': format, 'genre': genre})
    return engine.layout_book(content_path, metadata, output_path, cover_path)
