"""
Materials Generator - Gerador de Materiais Adicionais para Publicação.

Este módulo gera automaticamente elementos adicionais necessários para
publicação: blurbs, sinopses, biografias, códigos de barras, metadados, etc.

Autor: Manus AI
Versão: 1.0.0
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

try:
    import barcode
    from barcode.writer import ImageWriter
except ImportError:
    barcode = None

try:
    import qrcode
except ImportError:
    qrcode = None


class MaterialsGenerator:
    """Gerador de materiais adicionais para publicação."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o gerador de materiais.
        
        Args:
            config: Dicionário de configuração com opções:
                - openai_api_key: Chave API OpenAI para geração de texto
                - use_ai: Usar IA para geração de texto (padrão: False)
        """
        self.config = config or {}
        self.use_ai = self.config.get('use_ai', False)
        
        # Configurar OpenAI se disponível
        if self.use_ai and 'openai_api_key' in self.config:
            try:
                import openai
                self.openai = openai
                self.openai.api_key = self.config['openai_api_key']
            except ImportError:
                print("⚠️  OpenAI não instalado. Geração com IA desativada.")
                self.use_ai = False
    
    def generate_all(self, metadata: Dict, output_dir: str) -> Dict[str, str]:
        """
        Gera todos os materiais adicionais.
        
        Args:
            metadata: Metadados do livro
            output_dir: Diretório para salvar os materiais
            
        Returns:
            Dicionário com caminhos dos arquivos gerados
        """
        print("📦 Gerando materiais adicionais...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated = {}
        
        # 1. Blurb (texto de contracapa)
        if 'blurb' not in metadata:
            print("  ✍️  Gerando blurb...")
            blurb = self.generate_blurb(metadata)
            blurb_path = output_path / "blurb.txt"
            with open(blurb_path, 'w', encoding='utf-8') as f:
                f.write(blurb)
            generated['blurb'] = str(blurb_path)
        
        # 2. Sinopses (curta, média, longa)
        print("  ✍️  Gerando sinopses...")
        for length in ['short', 'medium', 'long']:
            synopsis = self.generate_synopsis(metadata, length)
            synopsis_path = output_path / f"synopsis_{length}.txt"
            with open(synopsis_path, 'w', encoding='utf-8') as f:
                f.write(synopsis)
            generated[f'synopsis_{length}'] = str(synopsis_path)
        
        # 3. Biografia do autor
        if metadata.get('author_bio'):
            print("  ✍️  Gerando biografia do autor...")
            bio = self.generate_author_bio(metadata)
            bio_path = output_path / "author_bio.txt"
            with open(bio_path, 'w', encoding='utf-8') as f:
                f.write(bio)
            generated['author_bio'] = str(bio_path)
        
        # 4. Release para imprensa
        print("  ✍️  Gerando release para imprensa...")
        press_release = self.generate_press_release(metadata)
        release_path = output_path / "press_release.md"
        with open(release_path, 'w', encoding='utf-8') as f:
            f.write(press_release)
        generated['press_release'] = str(release_path)
        
        # 5. Código de barras ISBN
        if metadata.get('isbn'):
            print("  📊 Gerando código de barras ISBN...")
            barcode_path = self.generate_isbn_barcode(
                metadata['isbn'],
                str(output_path / "isbn_barcode")
            )
            if barcode_path:
                generated['isbn_barcode'] = barcode_path
        
        # 6. QR Code (link do livro)
        if metadata.get('url'):
            print("  📱 Gerando QR Code...")
            qr_path = self.generate_qr_code(
                metadata['url'],
                str(output_path / "qr_code.png")
            )
            if qr_path:
                generated['qr_code'] = qr_path
        
        # 7. Metadados ONIX
        print("  📋 Gerando metadados ONIX...")
        onix = self.generate_onix(metadata)
        onix_path = output_path / "metadata_onix.xml"
        with open(onix_path, 'w', encoding='utf-8') as f:
            f.write(onix)
        generated['onix'] = str(onix_path)
        
        # 8. Ficha catalográfica
        print("  📇 Gerando ficha catalográfica...")
        cataloging = self.generate_cataloging_data(metadata)
        cataloging_path = output_path / "cataloging_data.txt"
        with open(cataloging_path, 'w', encoding='utf-8') as f:
            f.write(cataloging)
        generated['cataloging'] = str(cataloging_path)
        
        print(f"  ✅ {len(generated)} materiais gerados em '{output_dir}'")
        
        return generated
    
    def generate_blurb(self, metadata: Dict) -> str:
        """Gera texto de contracapa (blurb)."""
        
        if self.use_ai:
            return self._generate_blurb_ai(metadata)
        else:
            return self._generate_blurb_template(metadata)
    
    def _generate_blurb_template(self, metadata: Dict) -> str:
        """Gera blurb usando template."""
        
        title = metadata.get('title', 'Este livro')
        author = metadata.get('author', 'o autor')
        description = metadata.get('description', 'uma obra fascinante')
        
        blurb = f""""{title}" é {description}.

Escrito por {author}, este livro oferece uma perspectiva única e aprofundada sobre o tema, combinando rigor acadêmico com clareza e acessibilidade.

Ideal para profissionais, estudantes e todos aqueles interessados em expandir seus conhecimentos na área.

Uma leitura essencial que certamente enriquecerá sua compreensão e prática."""
        
        return blurb
    
    def _generate_blurb_ai(self, metadata: Dict) -> str:
        """Gera blurb usando IA."""
        
        prompt = f"""Escreva um blurb atraente (texto de contracapa) para o livro:

Título: {metadata.get('title')}
Autor: {metadata.get('author')}
Gênero: {metadata.get('genre', 'acadêmico')}
Descrição: {metadata.get('description', 'N/A')}
Público-alvo: {metadata.get('target_audience', 'profissionais e estudantes')}

O blurb deve ter 100-150 palavras, ser persuasivo e destacar os principais benefícios do livro."""
        
        try:
            response = self.openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um copywriter especializado em textos de contracapa de livros."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  ⚠️  Erro ao gerar blurb com IA: {e}")
            return self._generate_blurb_template(metadata)
    
    def generate_synopsis(self, metadata: Dict, length: str = 'medium') -> str:
        """
        Gera sinopse do livro.
        
        Args:
            metadata: Metadados do livro
            length: Tamanho da sinopse ('short', 'medium', 'long')
            
        Returns:
            Texto da sinopse
        """
        word_counts = {
            'short': (50, 100),
            'medium': (150, 250),
            'long': (300, 500)
        }
        
        min_words, max_words = word_counts.get(length, (150, 250))
        
        if self.use_ai:
            return self._generate_synopsis_ai(metadata, min_words, max_words)
        else:
            return self._generate_synopsis_template(metadata, length)
    
    def _generate_synopsis_template(self, metadata: Dict, length: str) -> str:
        """Gera sinopse usando template."""
        
        title = metadata.get('title', 'Este livro')
        author = metadata.get('author', 'o autor')
        description = metadata.get('description', 'uma obra importante')
        
        if length == 'short':
            synopsis = f"{title}, de {author}, apresenta {description}."
        elif length == 'medium':
            synopsis = f"""{title}

Escrito por {author}, este livro apresenta {description}.

A obra aborda de forma abrangente os principais aspectos do tema, oferecendo insights valiosos para profissionais e estudantes da área."""
        else:  # long
            synopsis = f"""{title}

Autor: {author}

{description}

Este livro representa uma contribuição significativa para a área, combinando fundamentação teórica sólida com aplicações práticas relevantes. O autor apresenta uma análise aprofundada e atualizada, incorporando as mais recentes descobertas e tendências.

A obra é estruturada de forma didática, facilitando a compreensão mesmo de conceitos complexos. Cada capítulo inclui exemplos práticos, estudos de caso e exercícios que auxiliam na consolidação do aprendizado.

Destinado a profissionais, pesquisadores e estudantes, este livro é uma referência essencial para todos aqueles que buscam aprofundar seus conhecimentos e aprimorar sua prática na área."""
        
        return synopsis
    
    def _generate_synopsis_ai(self, metadata: Dict, min_words: int, max_words: int) -> str:
        """Gera sinopse usando IA."""
        
        prompt = f"""Escreva uma sinopse profissional para o livro:

Título: {metadata.get('title')}
Autor: {metadata.get('author')}
Gênero: {metadata.get('genre', 'acadêmico')}
Descrição: {metadata.get('description', 'N/A')}

A sinopse deve ter entre {min_words} e {max_words} palavras e apresentar claramente o conteúdo e os benefícios do livro."""
        
        try:
            response = self.openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um especialista em sinopses de livros acadêmicos e profissionais."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_words * 2,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  ⚠️  Erro ao gerar sinopse com IA: {e}")
            return self._generate_synopsis_template(metadata, 'medium')
    
    def generate_author_bio(self, metadata: Dict) -> str:
        """Gera biografia do autor."""
        
        author = metadata.get('author', 'Autor')
        author_bio = metadata.get('author_bio', '')
        
        if author_bio:
            return f"""**Sobre o Autor**

{author_bio}"""
        else:
            return f"""**Sobre o Autor**

{author} é autor de {metadata.get('title', 'esta obra')}, trazendo sua experiência e conhecimento para enriquecer a compreensão dos leitores sobre o tema."""
    
    def generate_press_release(self, metadata: Dict) -> str:
        """Gera release para imprensa."""
        
        today = datetime.now().strftime("%d de %B de %Y")
        
        release = f"""# RELEASE PARA IMPRENSA

**Para divulgação imediata**  
**Data:** {today}

## {metadata.get('title', 'Novo Livro')}

### {metadata.get('subtitle', '')}

**Autor:** {metadata.get('author', 'N/A')}  
**Editora:** {metadata.get('publisher', 'N/A')}  
**Páginas:** {metadata.get('pages', 'N/A')}  
**ISBN:** {metadata.get('isbn', 'N/A')}  
**Preço:** {metadata.get('price', 'N/A')}  
**Lançamento:** {metadata.get('release_date', 'Em breve')}

### Sobre o Livro

{metadata.get('description', 'Descrição não disponível.')}

### Público-Alvo

{metadata.get('target_audience', 'Profissionais e estudantes da área.')}

### Sobre o Autor

{metadata.get('author_bio', f'{metadata.get("author")} é especialista na área.')}

### Informações para Imprensa

Para mais informações, entrevistas ou cópias de revisão, entre em contato:

**Email:** {metadata.get('press_contact_email', 'contato@editora.com')}  
**Telefone:** {metadata.get('press_contact_phone', '(XX) XXXX-XXXX')}

---

*Fim do Release*
"""
        
        return release
    
    def generate_isbn_barcode(self, isbn: str, output_path: str) -> Optional[str]:
        """
        Gera código de barras ISBN.
        
        Args:
            isbn: Número ISBN (com ou sem hífens)
            output_path: Caminho de saída (sem extensão)
            
        Returns:
            Caminho do arquivo gerado ou None se falhar
        """
        if not barcode:
            print("  ⚠️  Biblioteca 'python-barcode' não instalada")
            return None
        
        # Limpar ISBN (remover hífens)
        isbn_clean = isbn.replace('-', '').replace(' ', '')
        
        try:
            # Determinar tipo de código de barras
            if len(isbn_clean) == 13:
                barcode_class = barcode.get_barcode_class('ean13')
            elif len(isbn_clean) == 10:
                barcode_class = barcode.get_barcode_class('isbn10')
            else:
                print(f"  ⚠️  ISBN inválido: {isbn}")
                return None
            
            # Gerar código de barras
            isbn_barcode = barcode_class(isbn_clean, writer=ImageWriter())
            filename = isbn_barcode.save(output_path)
            
            return filename
        except Exception as e:
            print(f"  ⚠️  Erro ao gerar código de barras: {e}")
            return None
    
    def generate_qr_code(self, url: str, output_path: str) -> Optional[str]:
        """
        Gera QR Code.
        
        Args:
            url: URL para o QR Code
            output_path: Caminho do arquivo de saída
            
        Returns:
            Caminho do arquivo gerado ou None se falhar
        """
        if not qrcode:
            print("  ⚠️  Biblioteca 'qrcode' não instalada")
            return None
        
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(output_path)
            
            return output_path
        except Exception as e:
            print(f"  ⚠️  Erro ao gerar QR Code: {e}")
            return None
    
    def generate_onix(self, metadata: Dict) -> str:
        """Gera arquivo ONIX (padrão da indústria editorial)."""
        
        onix = f"""<?xml version="1.0" encoding="UTF-8"?>
<ONIXMessage release="3.0">
  <Header>
    <Sender>
      <SenderName>{metadata.get('publisher', 'Editora')}</SenderName>
    </Sender>
    <SentDateTime>{datetime.now().strftime('%Y%m%dT%H%M%S')}</SentDateTime>
  </Header>
  
  <Product>
    <RecordReference>{metadata.get('isbn', 'N/A')}</RecordReference>
    <NotificationType>03</NotificationType>
    <ProductIdentifier>
      <ProductIDType>15</ProductIDType>
      <IDValue>{metadata.get('isbn', 'N/A')}</IDValue>
    </ProductIdentifier>
    
    <DescriptiveDetail>
      <ProductComposition>00</ProductComposition>
      <ProductForm>BB</ProductForm>
      
      <TitleDetail>
        <TitleType>01</TitleType>
        <TitleElement>
          <TitleElementLevel>01</TitleElementLevel>
          <TitleText>{metadata.get('title', 'N/A')}</TitleText>
          <Subtitle>{metadata.get('subtitle', '')}</Subtitle>
        </TitleElement>
      </TitleDetail>
      
      <Contributor>
        <SequenceNumber>1</SequenceNumber>
        <ContributorRole>A01</ContributorRole>
        <PersonName>{metadata.get('author', 'N/A')}</PersonName>
      </Contributor>
      
      <Language>
        <LanguageRole>01</LanguageRole>
        <LanguageCode>por</LanguageCode>
      </Language>
      
      <Extent>
        <ExtentType>00</ExtentType>
        <ExtentValue>{metadata.get('pages', '0')}</ExtentValue>
        <ExtentUnit>03</ExtentUnit>
      </Extent>
      
      <Subject>
        <SubjectSchemeIdentifier>10</SubjectSchemeIdentifier>
        <SubjectCode>{metadata.get('subject_code', '')}</SubjectCode>
      </Subject>
    </DescriptiveDetail>
    
    <CollateralDetail>
      <TextContent>
        <TextType>03</TextType>
        <Text>{metadata.get('description', 'N/A')}</Text>
      </TextContent>
    </CollateralDetail>
    
    <PublishingDetail>
      <Publisher>
        <PublishingRole>01</PublishingRole>
        <PublisherName>{metadata.get('publisher', 'N/A')}</PublisherName>
      </Publisher>
      <PublishingDate>
        <PublishingDateRole>01</PublishingDateRole>
        <Date>{metadata.get('publication_date', datetime.now().strftime('%Y%m%d'))}</Date>
      </PublishingDate>
    </PublishingDetail>
    
    <ProductSupply>
      <SupplyDetail>
        <ProductAvailability>20</ProductAvailability>
        <Price>
          <PriceType>02</PriceType>
          <PriceAmount>{metadata.get('price_amount', '0.00')}</PriceAmount>
          <CurrencyCode>BRL</CurrencyCode>
        </Price>
      </SupplyDetail>
    </ProductSupply>
  </Product>
</ONIXMessage>"""
        
        return onix
    
    def generate_cataloging_data(self, metadata: Dict) -> str:
        """Gera ficha catalográfica."""
        
        author = metadata.get('author', 'Autor, Nome')
        title = metadata.get('title', 'Título do Livro')
        subtitle = metadata.get('subtitle', '')
        publisher = metadata.get('publisher', 'Editora')
        year = metadata.get('publication_year', datetime.now().year)
        pages = metadata.get('pages', 'XXX')
        isbn = metadata.get('isbn', 'XXX-XX-XXXXX-XX-X')
        
        cataloging = f"""Dados Internacionais de Catalogação na Publicação (CIP)
(Câmara Brasileira do Livro, SP, Brasil)

{author}
    {title} {': ' + subtitle if subtitle else ''} / {author}. -- 
    São Paulo : {publisher}, {year}.
    {pages} p.

    ISBN {isbn}

    1. [Assunto principal] 2. [Assunto secundário] I. Título.

                                                CDD-XXX.XX
                                                CDU-XXX.XX

Índices para catálogo sistemático:

1. [Descrição do índice] : [Área de conhecimento]  XXX.XX"""
        
        return cataloging


# Função de conveniência
def generate_materials(metadata: Dict, 
                      output_dir: str,
                      use_ai: bool = False,
                      openai_api_key: Optional[str] = None) -> Dict[str, str]:
    """
    Função de conveniência para gerar materiais.
    
    Args:
        metadata: Metadados do livro
        output_dir: Diretório de saída
        use_ai: Usar IA para geração de texto
        openai_api_key: Chave API OpenAI (se use_ai=True)
        
    Returns:
        Dicionário com caminhos dos arquivos gerados
    """
    config = {'use_ai': use_ai}
    if openai_api_key:
        config['openai_api_key'] = openai_api_key
    
    generator = MaterialsGenerator(config)
    return generator.generate_all(metadata, output_dir)
