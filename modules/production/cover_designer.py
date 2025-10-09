"""
Cover Designer - Designer Automatizado de Capas de Livros.

Este módulo implementa design automatizado de capas usando IA generativa
e composição tipográfica profissional.

Autor: Manus AI
Versão: 1.0.0
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests
from io import BytesIO


class CoverDesigner:
    """Designer automatizado de capas de livros."""
    
    # Paletas de cores por gênero
    COLOR_PALETTES = {
        'academic': [
            {'primary': '#1a365d', 'secondary': '#2c5282', 'accent': '#4299e1', 'text': '#ffffff'},
            {'primary': '#2d3748', 'secondary': '#4a5568', 'accent': '#718096', 'text': '#ffffff'},
            {'primary': '#742a2a', 'secondary': '#9b2c2c', 'accent': '#c53030', 'text': '#ffffff'},
        ],
        'fiction': [
            {'primary': '#1a202c', 'secondary': '#2d3748', 'accent': '#e53e3e', 'text': '#ffffff'},
            {'primary': '#2c5282', 'secondary': '#2b6cb0', 'accent': '#4299e1', 'text': '#ffffff'},
            {'primary': '#553c9a', 'secondary': '#6b46c1', 'accent': '#9f7aea', 'text': '#ffffff'},
        ],
        'technical': [
            {'primary': '#1a365d', 'secondary': '#2c5282', 'accent': '#63b3ed', 'text': '#ffffff'},
            {'primary': '#234e52', 'secondary': '#285e61', 'accent': '#38b2ac', 'text': '#ffffff'},
            {'primary': '#2d3748', 'secondary': '#4a5568', 'accent': '#a0aec0', 'text': '#ffffff'},
        ],
        'poetry': [
            {'primary': '#553c9a', 'secondary': '#6b46c1', 'accent': '#d6bcfa', 'text': '#ffffff'},
            {'primary': '#702459', 'secondary': '#97266d', 'accent': '#ed64a6', 'text': '#ffffff'},
            {'primary': '#2c5282', 'secondary': '#2b6cb0', 'accent': '#90cdf4', 'text': '#ffffff'},
        ]
    }
    
    # Layouts de capa
    LAYOUTS = {
        'centered': 'Título centralizado, autor embaixo',
        'top_heavy': 'Título no topo, imagem dominante',
        'minimal': 'Design minimalista com muito espaço em branco',
        'bold': 'Tipografia grande e ousada',
        'classic': 'Layout clássico e elegante'
    }
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o designer de capas.
        
        Args:
            config: Dicionário de configuração com opções:
                - openai_api_key: Chave API OpenAI para geração de imagens
                - use_ai_images: Usar IA para gerar imagens (padrão: False)
                - fonts_dir: Diretório de fontes customizadas
        """
        self.config = config or {}
        self.use_ai_images = self.config.get('use_ai_images', False)
        
        # Configurar OpenAI se disponível
        if self.use_ai_images and 'openai_api_key' in self.config:
            try:
                import openai
                self.openai = openai
                self.openai.api_key = self.config['openai_api_key']
            except ImportError:
                print("⚠️  OpenAI não instalado. Geração de imagens com IA desativada.")
                self.use_ai_images = False
        
        # Diretório de fontes
        self.fonts_dir = Path(self.config.get('fonts_dir', '/usr/share/fonts'))
    
    def design_cover(self,
                    metadata: Dict,
                    output_path: str,
                    layout: str = 'centered',
                    palette_index: int = 0) -> str:
        """
        Cria design de capa completo.
        
        Args:
            metadata: Metadados do livro (título, autor, gênero, etc.)
            output_path: Caminho para salvar a capa
            layout: Tipo de layout ('centered', 'top_heavy', 'minimal', 'bold', 'classic')
            palette_index: Índice da paleta de cores (0-2)
            
        Returns:
            Caminho do arquivo gerado
        """
        print(f"🎨 Criando design de capa para '{metadata.get('title', 'Livro')}'...")
        
        # 1. Obter dimensões (formato padrão 6x9 polegadas, 300 DPI)
        width, height = 1800, 2700  # pixels
        
        # 2. Selecionar paleta de cores
        genre = metadata.get('genre', 'academic')
        palettes = self.COLOR_PALETTES.get(genre, self.COLOR_PALETTES['academic'])
        palette = palettes[palette_index % len(palettes)]
        
        # 3. Criar imagem base
        cover = Image.new('RGB', (width, height), palette['primary'])
        draw = ImageDraw.Draw(cover)
        
        # 4. Adicionar imagem de fundo (se usar IA ou fornecida)
        if self.use_ai_images:
            background = self._generate_background_ai(metadata, (width, height))
            if background:
                cover.paste(background, (0, 0))
                # Adicionar overlay semi-transparente para legibilidade
                overlay = Image.new('RGBA', (width, height), (*self._hex_to_rgb(palette['primary']), 180))
                cover = Image.alpha_composite(cover.convert('RGBA'), overlay).convert('RGB')
                draw = ImageDraw.Draw(cover)
        
        # 5. Aplicar layout específico
        if layout == 'centered':
            self._layout_centered(draw, metadata, palette, (width, height))
        elif layout == 'top_heavy':
            self._layout_top_heavy(draw, metadata, palette, (width, height))
        elif layout == 'minimal':
            self._layout_minimal(draw, metadata, palette, (width, height))
        elif layout == 'bold':
            self._layout_bold(draw, metadata, palette, (width, height))
        else:  # classic
            self._layout_classic(draw, metadata, palette, (width, height))
        
        # 6. Salvar
        cover.save(output_path, 'PNG', dpi=(300, 300), quality=95)
        
        print(f"  ✅ Capa criada: {output_path}")
        
        return output_path
    
    def generate_concepts(self,
                         metadata: Dict,
                         output_dir: str,
                         num_concepts: int = 3) -> List[str]:
        """
        Gera múltiplos conceitos de capa para escolha.
        
        Args:
            metadata: Metadados do livro
            output_dir: Diretório para salvar os conceitos
            num_concepts: Número de conceitos a gerar
            
        Returns:
            Lista de caminhos dos arquivos gerados
        """
        print(f"🎨 Gerando {num_concepts} conceitos de capa...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        concepts = []
        layouts = list(self.LAYOUTS.keys())
        
        for i in range(num_concepts):
            layout = layouts[i % len(layouts)]
            palette_index = i % 3
            
            concept_path = output_path / f"concept_{i+1}_{layout}.png"
            self.design_cover(metadata, str(concept_path), layout, palette_index)
            concepts.append(str(concept_path))
        
        print(f"  ✅ {len(concepts)} conceitos gerados")
        
        return concepts
    
    def _generate_background_ai(self, metadata: Dict, size: Tuple[int, int]) -> Optional[Image.Image]:
        """Gera imagem de fundo usando IA."""
        
        if not self.use_ai_images:
            return None
        
        # Criar prompt baseado em metadados
        title = metadata.get('title', '')
        genre = metadata.get('genre', 'academic')
        description = metadata.get('description', '')
        
        prompt = f"""Abstract professional book cover background for "{title}", {genre} genre.
Style: elegant, modern, minimalist. Colors: deep blues and grays.
No text, no people, just abstract shapes and patterns."""
        
        try:
            print("  🤖 Gerando imagem de fundo com IA...")
            response = self.openai.Image.create(
                prompt=prompt,
                n=1,
                size=f"{size[0]}x{size[1]}" if size[0] <= 1024 else "1024x1024"
            )
            
            image_url = response['data'][0]['url']
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            
            # Redimensionar se necessário
            if img.size != size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            return img
        except Exception as e:
            print(f"  ⚠️  Erro ao gerar imagem com IA: {e}")
            return None
    
    def _layout_centered(self, draw: ImageDraw.Draw, metadata: Dict, 
                        palette: Dict, size: Tuple[int, int]):
        """Layout com título centralizado."""
        width, height = size
        
        # Título
        title = metadata.get('title', 'Título')
        title_font = self._get_font(100, bold=True)
        
        # Calcular posição centralizada
        bbox = draw.textbbox((0, 0), title, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2 - 200
        
        # Desenhar título com sombra
        shadow_offset = 5
        draw.text((x + shadow_offset, y + shadow_offset), title, 
                 font=title_font, fill='#000000')
        draw.text((x, y), title, font=title_font, fill=palette['text'])
        
        # Subtítulo (se houver)
        if metadata.get('subtitle'):
            subtitle = metadata.get('subtitle')
            subtitle_font = self._get_font(50)
            bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y += 150
            draw.text((x, y), subtitle, font=subtitle_font, fill=palette['accent'])
        
        # Autor
        author = metadata.get('author', 'Autor')
        author_font = self._get_font(60)
        bbox = draw.textbbox((0, 0), author, font=author_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = height - 300
        draw.text((x, y), author, font=author_font, fill=palette['text'])
    
    def _layout_top_heavy(self, draw: ImageDraw.Draw, metadata: Dict,
                         palette: Dict, size: Tuple[int, int]):
        """Layout com título no topo."""
        width, height = size
        
        # Título no topo
        title = metadata.get('title', 'Título')
        title_font = self._get_font(90, bold=True)
        
        x = 100
        y = 200
        
        # Quebrar título em múltiplas linhas se necessário
        words = title.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=title_font)
            if bbox[2] - bbox[0] < width - 200:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Desenhar cada linha
        for line in lines:
            draw.text((x, y), line, font=title_font, fill=palette['text'])
            y += 120
        
        # Autor no rodapé
        author = metadata.get('author', 'Autor')
        author_font = self._get_font(60)
        y = height - 250
        draw.text((x, y), author, font=author_font, fill=palette['accent'])
    
    def _layout_minimal(self, draw: ImageDraw.Draw, metadata: Dict,
                       palette: Dict, size: Tuple[int, int]):
        """Layout minimalista."""
        width, height = size
        
        # Muito espaço em branco, tipografia pequena
        title = metadata.get('title', 'Título')
        title_font = self._get_font(70, bold=True)
        
        x = 150
        y = height // 2 - 100
        
        draw.text((x, y), title, font=title_font, fill=palette['text'])
        
        # Linha decorativa
        line_y = y + 100
        draw.line([(x, line_y), (x + 400, line_y)], 
                 fill=palette['accent'], width=3)
        
        # Autor
        author = metadata.get('author', 'Autor')
        author_font = self._get_font(40)
        y = line_y + 50
        draw.text((x, y), author, font=author_font, fill=palette['text'])
    
    def _layout_bold(self, draw: ImageDraw.Draw, metadata: Dict,
                    palette: Dict, size: Tuple[int, int]):
        """Layout com tipografia ousada."""
        width, height = size
        
        # Título muito grande
        title = metadata.get('title', 'Título')
        title_font = self._get_font(120, bold=True)
        
        x = 100
        y = 400
        
        # Título em múltiplas linhas
        words = title.split()
        for word in words:
            draw.text((x, y), word, font=title_font, fill=palette['text'])
            y += 150
        
        # Autor
        author = metadata.get('author', 'Autor')
        author_font = self._get_font(50)
        y = height - 300
        draw.text((x, y), author, font=author_font, fill=palette['accent'])
    
    def _layout_classic(self, draw: ImageDraw.Draw, metadata: Dict,
                       palette: Dict, size: Tuple[int, int]):
        """Layout clássico e elegante."""
        width, height = size
        
        # Moldura decorativa
        margin = 100
        draw.rectangle([margin, margin, width-margin, height-margin],
                      outline=palette['accent'], width=5)
        
        # Título centralizado
        title = metadata.get('title', 'Título')
        title_font = self._get_font(80, bold=True)
        
        bbox = draw.textbbox((0, 0), title, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = height // 2 - 100
        
        draw.text((x, y), title, font=title_font, fill=palette['text'])
        
        # Autor
        author = metadata.get('author', 'Autor')
        author_font = self._get_font(50)
        bbox = draw.textbbox((0, 0), author, font=author_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = height - 400
        draw.text((x, y), author, font=author_font, fill=palette['text'])
    
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Obtém fonte com tamanho especificado."""
        
        # Tentar fontes comuns
        font_names = [
            'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf',
            'LiberationSans-Bold.ttf' if bold else 'LiberationSans-Regular.ttf',
            'Arial-Bold.ttf' if bold else 'Arial.ttf',
        ]
        
        for font_name in font_names:
            try:
                font_path = self.fonts_dir / 'truetype' / 'dejavu' / font_name
                if font_path.exists():
                    return ImageFont.truetype(str(font_path), size)
            except:
                pass
        
        # Fallback para fonte padrão
        try:
            return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)
        except:
            return ImageFont.load_default()
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Converte cor hexadecimal para RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


# Função de conveniência
def design_cover(metadata: Dict,
                output_path: str,
                layout: str = 'centered',
                use_ai: bool = False,
                openai_api_key: Optional[str] = None) -> str:
    """
    Função de conveniência para criar capa.
    
    Args:
        metadata: Metadados do livro
        output_path: Caminho de saída
        layout: Tipo de layout
        use_ai: Usar IA para gerar imagens
        openai_api_key: Chave API OpenAI (se use_ai=True)
        
    Returns:
        Caminho do arquivo gerado
    """
    config = {'use_ai_images': use_ai}
    if openai_api_key:
        config['openai_api_key'] = openai_api_key
    
    designer = CoverDesigner(config)
    return designer.design_cover(metadata, output_path, layout)
