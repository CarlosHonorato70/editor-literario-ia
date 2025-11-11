"""
ISBN and CIP Generator - Gerador de ISBN e Ficha Catalográfica

Este módulo gerencia a geração de ISBN e CIP (Catalogação na Publicação)
para obras literárias, seguindo os padrões brasileiros.

Autor: Manus AI
Versão: 1.0
"""

import re
import barcode
from barcode.writer import ImageWriter
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class ISBNCIPGenerator:
    """Gerador de ISBN e CIP para publicações."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o gerador.
        
        Args:
            config: Configurações opcionais
        """
        self.config = config or {}
        self.publisher_prefix = self.config.get('publisher_prefix', '85')
    
    def generate_isbn(self, book_id: str = None) -> str:
        """
        Gera um ISBN-13 válido.
        
        Args:
            book_id: Identificador único do livro
            
        Returns:
            ISBN no formato 978-85-XXXXX-XX-X
        """
        # Em produção, isso viria de um sistema de registro oficial
        # Aqui geramos um exemplo para demonstração
        
        if book_id:
            # Usa hash do book_id para gerar números consistentes
            hash_val = abs(hash(book_id))
            publisher_code = str(hash_val % 100000).zfill(5)
            title_code = str((hash_val // 100000) % 100).zfill(2)
        else:
            # Gera aleatoriamente para demonstração
            import random
            publisher_code = str(random.randint(10000, 99999))
            title_code = str(random.randint(10, 99))
        
        # Formato: 978 (prefixo GS1) - 85 (Brasil) - XXXXX (editora) - XX (título) - X (check)
        isbn_without_check = f"978{self.publisher_prefix}{publisher_code}{title_code}"
        
        # Calcula dígito verificador
        check_digit = self._calculate_isbn_check_digit(isbn_without_check)
        
        # Formata com hífens
        isbn = f"978-{self.publisher_prefix}-{publisher_code}-{title_code}-{check_digit}"
        
        return isbn
    
    def _calculate_isbn_check_digit(self, isbn_12: str) -> str:
        """Calcula o dígito verificador do ISBN-13."""
        # Remove hífens se houver
        isbn_12 = isbn_12.replace('-', '')
        
        # Algoritmo ISBN-13
        total = 0
        for i, digit in enumerate(isbn_12):
            weight = 1 if i % 2 == 0 else 3
            total += int(digit) * weight
        
        check = (10 - (total % 10)) % 10
        return str(check)
    
    def validate_isbn(self, isbn: str) -> bool:
        """Valida um ISBN-13."""
        # Remove hífens e espaços
        isbn_clean = re.sub(r'[-\s]', '', isbn)
        
        # Verifica comprimento
        if len(isbn_clean) != 13:
            return False
        
        # Verifica se são todos dígitos
        if not isbn_clean.isdigit():
            return False
        
        # Verifica dígito verificador
        check_digit = self._calculate_isbn_check_digit(isbn_clean[:12])
        
        return check_digit == isbn_clean[12]
    
    def generate_barcode(self, isbn: str, output_path: str) -> str:
        """
        Gera código de barras do ISBN.
        
        Args:
            isbn: ISBN no formato 978-85-XXXXX-XX-X
            output_path: Caminho para salvar a imagem
            
        Returns:
            Caminho do arquivo gerado
        """
        # Remove hífens do ISBN
        isbn_clean = isbn.replace('-', '')
        
        # Gera código de barras EAN-13
        ean = barcode.get_barcode_class('ean13')
        code = ean(isbn_clean, writer=ImageWriter())
        
        # Salva imagem
        output_file = Path(output_path).with_suffix('')
        filename = code.save(str(output_file))
        
        print(f"✅ Código de barras ISBN gerado: {filename}")
        
        return filename
    
    def generate_cip(self, metadata: Dict) -> str:
        """
        Gera ficha CIP (Catalogação na Publicação).
        
        Args:
            metadata: Dicionário com metadados do livro:
                - author: Nome do autor
                - title: Título do livro
                - subtitle: Subtítulo (opcional)
                - edition: Edição (ex: "1. ed.")
                - city: Cidade de publicação
                - publisher: Nome da editora
                - year: Ano de publicação
                - pages: Número de páginas
                - isbn: ISBN do livro
                - subjects: Lista de assuntos/categorias
                - cdd: Código CDD (Classificação Decimal de Dewey)
                
        Returns:
            Texto formatado da ficha CIP
        """
        # Extrai informações
        author = metadata.get('author', 'Autor Desconhecido')
        title = metadata.get('title', 'Sem Título')
        subtitle = metadata.get('subtitle', '')
        edition = metadata.get('edition', '1. ed.')
        city = metadata.get('city', 'São Paulo')
        publisher = metadata.get('publisher', 'Editora')
        year = metadata.get('year', datetime.now().year)
        pages = metadata.get('pages', 0)
        isbn = metadata.get('isbn', 'Sem ISBN')
        subjects = metadata.get('subjects', ['Literatura Brasileira'])
        cdd = metadata.get('cdd', '869')
        
        # Separa sobrenome do autor (último nome)
        author_parts = author.strip().split()
        if len(author_parts) > 1:
            surname = author_parts[-1]
            given_names = ' '.join(author_parts[:-1])
            author_formatted = f"{surname}, {given_names}"
        else:
            author_formatted = author
        
        # Constrói a ficha CIP
        cip_lines = []
        cip_lines.append("Dados Internacionais de Catalogação na Publicação (CIP)")
        cip_lines.append("(Câmara Brasileira do Livro, SP, Brasil)")
        cip_lines.append("")
        
        # Entrada principal (autor)
        cip_lines.append(author_formatted)
        
        # Título e subtítulo
        title_line = f"    {title}"
        if subtitle:
            title_line += f" : {subtitle}"
        title_line += f" / {author}. — {edition} —"
        cip_lines.append(title_line)
        
        # Imprenta (cidade, editora, ano)
        cip_lines.append(f"    {city} : {publisher}, {year}.")
        
        # Descrição física
        if pages > 0:
            cip_lines.append(f"    {pages} p. ; 23 cm")
        cip_lines.append("")
        
        # ISBN
        cip_lines.append(f"    ISBN {isbn.replace('-', '')}")
        cip_lines.append("")
        
        # Assuntos
        for i, subject in enumerate(subjects, 1):
            cip_lines.append(f"    {i}. {subject}. I. Título.")
        cip_lines.append("")
        
        # CDD
        cip_lines.append(f"                                        CDD: {cdd}")
        cip_lines.append("")
        
        # Índice para catálogo sistemático
        if subjects:
            cip_lines.append("Índices para catálogo sistemático:")
            for i, subject in enumerate(subjects, 1):
                cip_lines.append(f"{i}. {subject}  {cdd}")
        
        cip_text = "\n".join(cip_lines)
        
        return cip_text
    
    def generate_cip_box(self, metadata: Dict) -> str:
        """
        Gera ficha CIP formatada em caixa (para inserir no livro).
        
        Returns:
            Texto CIP formatado com bordas
        """
        cip_text = self.generate_cip(metadata)
        
        # Adiciona bordas
        lines = cip_text.split('\n')
        max_length = max(len(line) for line in lines)
        
        boxed_cip = []
        boxed_cip.append('┌' + '─' * (max_length + 2) + '┐')
        
        for line in lines:
            padding = ' ' * (max_length - len(line))
            boxed_cip.append(f'│ {line}{padding} │')
        
        boxed_cip.append('└' + '─' * (max_length + 2) + '┘')
        
        return '\n'.join(boxed_cip)
    
    def get_cdd_code(self, genre: str) -> str:
        """
        Retorna código CDD (Classificação Decimal de Dewey) baseado no gênero.
        
        Args:
            genre: Gênero literário
            
        Returns:
            Código CDD correspondente
        """
        cdd_mapping = {
            'ficção': '869.3',
            'romance': '869.3',
            'conto': '869.3',
            'poesia': '869.1',
            'teatro': '869.2',
            'crônica': '869.4',
            'ensaio': '869.4',
            'biografia': '920',
            'autobiografia': '920',
            'memórias': '920',
            'história': '900',
            'filosofia': '100',
            'psicologia': '150',
            'religião': '200',
            'ciências sociais': '300',
            'linguagem': '400',
            'ciências naturais': '500',
            'tecnologia': '600',
            'artes': '700',
            'literatura': '800',
            'geografia': '910',
            'auto-ajuda': '158',
            'negócios': '650',
            'culinária': '641',
            'infantil': '028.5',
            'juvenil': '028.5',
        }
        
        genre_lower = genre.lower()
        return cdd_mapping.get(genre_lower, '869')  # Default para literatura brasileira
    
    def generate_legal_page(self, metadata: Dict) -> str:
        """
        Gera a página de direitos autorais (verso da folha de rosto).
        
        Args:
            metadata: Metadados do livro
            
        Returns:
            Texto formatado da página legal
        """
        title = metadata.get('title', 'Sem Título')
        author = metadata.get('author', 'Autor')
        year = metadata.get('year', datetime.now().year)
        publisher = metadata.get('publisher', 'Editora')
        publisher_address = metadata.get('publisher_address', 'São Paulo, SP')
        publisher_website = metadata.get('publisher_website', 'www.editora.com.br')
        publisher_email = metadata.get('publisher_email', 'contato@editora.com.br')
        isbn = metadata.get('isbn', '')
        edition = metadata.get('edition', '1. ed.')
        
        legal_text = f"""
{title}
© {year} {author}
© {year} {publisher}

Todos os direitos reservados. Nenhuma parte deste livro pode ser reproduzida
ou transmitida por qualquer forma e/ou quaisquer meios (eletrônico ou mecânico,
incluindo fotocópia e gravação) ou arquivada em qualquer sistema ou banco de
dados sem permissão escrita da editora.

{edition}

ISBN {isbn}

{publisher}
{publisher_address}
Site: {publisher_website}
E-mail: {publisher_email}

{self.generate_cip(metadata)}

Impresso no Brasil
Printed in Brazil
"""
        
        return legal_text.strip()


def main():
    """Função de teste."""
    generator = ISBNCIPGenerator()
    
    # Testa geração de ISBN
    isbn = generator.generate_isbn('exemplo-livro-001')
    print(f"ISBN gerado: {isbn}")
    print(f"ISBN válido: {generator.validate_isbn(isbn)}")
    
    # Testa geração de CIP
    metadata = {
        'author': 'João Silva Santos',
        'title': 'O Caminho das Estrelas',
        'subtitle': 'Uma jornada pela ficção científica',
        'edition': '1. ed.',
        'city': 'São Paulo',
        'publisher': 'Editora Exemplo',
        'year': 2025,
        'pages': 320,
        'isbn': isbn,
        'subjects': ['Ficção científica brasileira', 'Literatura brasileira'],
        'cdd': '869.3'
    }
    
    print("\n" + "="*70)
    print("FICHA CIP:")
    print("="*70)
    print(generator.generate_cip_box(metadata))
    
    print("\n" + "="*70)
    print("PÁGINA LEGAL:")
    print("="*70)
    print(generator.generate_legal_page(metadata))


if __name__ == '__main__':
    main()
