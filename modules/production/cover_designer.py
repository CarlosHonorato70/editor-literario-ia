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
        # Largura da capa (6in) + Largura da lombada (estimada) + Largura da contracapa (6in)
        # Altura (9in)
        # 6in * 300dpi = 1800px
        # 9in * 300dpi = 2700px
        
        # Largura da lombada (estimativa baseada em 300 páginas, 0.75in)
        # A estimativa real deve vir do LayoutEngine, mas para o conceito, usamos um valor fixo.
        spine_width_px = 225 # 0.75in * 300dpi
        
        cover_width = 1800
        cover_height = 2700
        
        width = cover_width * 2 + spine_width_px # Capa + Lombada + Contracapa
        height = cover_height # Altura da capa
        
        # 2. Selecionar paleta de cores
        
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
        # O layout agora é aplicado à capa e contracapa separadamente, e a lombada.
        
        # Posições
        back_cover_x = 0
        spine_x = cover_width
        front_cover_x = cover_width + spine_width_px
        
        # Capa (Front Cover)
        self._layout_front_cover(draw, metadata, palette, (cover_width, cover_height), front_cover_x)
        
        # Contracapa (Back Cover)
        self._layout_back_cover(draw, metadata, palette, (cover_width, cover_height), back_cover_x)
        
        # Lombada (Spine)
        self._layout_spine(draw, metadata, palette, (spine_width_px, cover_height), spine_x)
        
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
        
        # O tamanho da imagem deve ser a capa completa (capa + lombada + contracapa)
        # O modelo DALL-E 3 suporta até 1792x1024 ou 1024x1792.
        # Usaremos 1792x1024 como base e faremos o upscale/crop.
        
        prompt = f"""Abstract professional book cover background for the full wrap-around cover (front, spine, and back) of the book titled "{title}", {genre} genre.
Style: elegant, modern, minimalist. Colors: deep blues and grays.
No text, no people, just abstract shapes and patterns. The image must be a single horizontal composition."""
        
        try:
            print("  🤖 Gerando imagem de fundo com IA...")
            # Usar o maior tamanho horizontal suportado
            response = self.openai.Image.create(
                prompt=prompt,
                n=1,
                size="1792x1024" # Tamanho máximo horizontal para DALL-E 3
            )
            
            image_url = response['data'][0]['url']
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            
            # Redimensionar para o tamanho da capa completa (size)
            # O tamanho gerado é 1792x1024. O tamanho alvo é (cover_width*2 + spine_width_px) x cover_height
            # Vamos redimensionar para a altura correta e cortar/esticar a largura.
            
            # Calcular a proporção de redimensionamento pela altura
            target_height = size[1]
            current_height = img.size[1]
            
            scale_factor = target_height / current_height
            
            # Novo tamanho mantendo a proporção da altura
            new_width = int(img.size[0] * scale_factor)
            new_height = target_height
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Se a largura ainda for menor que a largura alvo, esticar ou preencher (por simplicidade, esticar)
            if new_width < size[0]:
                 img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Se a largura for maior, cortar o centro (não ideal, mas necessário)
            elif new_width > size[0]:
                left = (new_width - size[0]) // 2
                right = left + size[0]
                img = img.crop((left, 0, right, size[1]))
            
            return img
        except Exception as e:
            print(f"  ⚠️  Erro ao gerar imagem com IA: {e}")
            return None
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Quebra o texto em linhas para caber na largura máxima."""
        lines = []
        words = text.split()
        current_line = []
        
        # Obter o objeto ImageDraw.Draw para calcular o tamanho do texto
        # Como não temos o objeto draw aqui, vamos usar uma estimativa ou
        # passar o draw como argumento. Por simplicidade, vamos usar uma
        # função auxiliar que simula o cálculo.
        
        # Nota: O código original tinha uma dependência de 'draw' que não estava
        # definida no escopo de _wrap_text. Corrigindo para usar a função
        # de cálculo de tamanho de texto da PIL de forma independente.
        
        # Usando uma função auxiliar para simular o cálculo de largura do texto
        def get_text_width(text_to_check, font_to_check):
            # Cria uma imagem temporária para o cálculo
            temp_img = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), text_to_check, font=font_to_check)
            return bbox[2] - bbox[0]
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            text_width = get_text_width(test_line, font)
            
            if text_width < max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
    
    def _layout_front_cover(self, draw: ImageDraw.Draw, metadata: Dict, 
                            palette: Dict, size: Tuple[int, int], offset_x: int):
        """Layout da Capa (Front Cover)."""
        width, height = size
        
        # Título
        title = metadata.get('title', 'Título')
        title_font = self._get_font(100, bold=True)
        
        # Calcular posição centralizada na capa
        bbox = draw.textbbox((0, 0), title, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = offset_x + (width - text_width) // 2
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
            x = offset_x + (width - text_width) // 2
            y += 150
            draw.text((x, y), subtitle, font=subtitle_font, fill=palette['accent'])
        
        # Autor
        author = metadata.get('author', 'Autor')
        author_font = self._get_font(60)
        bbox = draw.textbbox((0, 0), author, font=author_font)
        text_width = bbox[2] - bbox[0]
        x = offset_x + (width - text_width) // 2
        y = height - 300
        draw.text((x, y), author, font=author_font, fill=palette['text'])
    
    def _layout_back_cover(self, draw: ImageDraw.Draw, metadata: Dict, 
                           palette: Dict, size: Tuple[int, int], offset_x: int):
        """Layout da Contracapa (Back Cover)."""
        width, height = size
        
        # Blurb/Sinopse
        blurb = metadata.get('blurb', 'Sinopse do livro. Este texto deve ser gerado pelo MaterialsGenerator.')
        blurb_font = self._get_font(40)
        
        x = offset_x + 100
        y = 300
        max_width = width - 200
        
        # Quebrar texto
        lines = self._wrap_text(blurb, blurb_font, max_width)
        
        for line in lines:
            draw.text((x, y), line, font=blurb_font, fill=palette['text'])
            y += 60
            
        # ISBN/Código de Barras (simulado)
        isbn = metadata.get('isbn', '978-1234567890')
        isbn_font = self._get_font(30)
        
        x_isbn = offset_x + (width - 400) // 2
        y_isbn = height - 200
        
        draw.rectangle([x_isbn, y_isbn - 50, x_isbn + 400, y_isbn], fill='#ffffff', outline='#000000')
        draw.text((x_isbn + 10, y_isbn - 45), f"ISBN {isbn}", font=isbn_font, fill='#000000')
        
    def _layout_spine(self, draw: ImageDraw.Draw, metadata: Dict, 
                      palette: Dict, size: Tuple[int, int], offset_x: int):
        """Layout da Lombada (Spine)."""
        width, height = size
        
        # Título (rotacionado)
        title = metadata.get('title', 'Título')
        title_font = self._get_font(60, bold=True)
        
        # Criar imagem temporária para texto rotacionado
        temp_img = Image.new('RGB', (height, width), palette['primary'])
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Posição centralizada na lombada
        # Usando textlength para compatibilidade
        text_w        # Posição centralizada na lombada
        # Usar textbbox para obter dimensões corretas
        bbox = temp_draw.textbbox((0, 0), title, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (height - text_width) // 2
        y = (width - text_height) // 2
        
        temp_draw.text((x, y), title, font=title_font, fill=palette['text'])
        
        # Rotacionar e colar na lombada
        rotated_text = temp_img.rotate(90, expand=1)
        
        # Colar na posição correta
        draw.bitmap((offset_x, 0), rotated_text, fill=palette['text'])
        
        # Autor (rotacionado)
        author = metadata.get('author', 'Autor')
        author_font = self._get_font(40)
        
        temp_img_author = Image.new('RGB', (height, width), palette['primary'])
        temp_draw_author = ImageDraw.Draw(temp_img_author)
        
        bbox_a = temp_draw_author.textbbox((0, 0), author, font=author_font)
        text_width_a = bbox_a[2] - bbox_a[0]
        text_height_a = bbox_a[3] - bbox_a[1]
        
        x_a = (height - text_width_a) // 2
        y_a = (width - text_height_a) // 2
        
        temp_draw_author.text((x_a, y_a), author, font=author_font, fill=palette['accent'])
        
        rotated_author = temp_img_author.rotate(90, expand=1)
        
        # Colar na posição correta (abaixo do título)
        draw.bitmap((offset_x, height - 200), rotated_author, fill=palette['accent'])  
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
