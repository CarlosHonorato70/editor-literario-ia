"""
Módulo para extração de texto de diferentes tipos de arquivo.

Este módulo fornece funções para extrair texto de arquivos TXT, DOCX e PDF,
com tratamento de erros robusto e feedback claro.
"""

import io
from typing import Optional, Tuple

# Lazy imports to avoid loading heavy dependencies at module import time
# This prevents issues on systems where dependencies aren't fully installed
_docx_available = None
_pypdf2_available = None


class FileHandler:
    """Classe para gerenciar extração de texto de diferentes formatos de arquivo."""
    
    @staticmethod
    def extract_text_from_txt(file_content: bytes) -> str:
        """
        Extrai texto de arquivo TXT.
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            
        Returns:
            Texto extraído do arquivo
            
        Raises:
            ValueError: Se houver erro na decodificação
        """
        try:
            text = file_content.decode('utf-8')
            return text
        except UnicodeDecodeError:
            # Tenta com outras codificações comuns
            try:
                text = file_content.decode('latin-1')
                return text
            except Exception as e:
                raise ValueError(f"Erro ao decodificar arquivo TXT: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """
        Extrai texto de arquivo DOCX.
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            
        Returns:
            Texto extraído do arquivo (parágrafos separados por linha dupla)
            
        Raises:
            ValueError: Se houver erro na leitura do documento
            ImportError: Se python-docx não estiver instalado
        """
        try:
            from docx import Document
        except ImportError:
            raise ImportError(
                "python-docx não está instalado. "
                "Instale com: pip install python-docx"
            )
        
        try:
            doc = Document(io.BytesIO(file_content))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n\n".join(paragraphs)
            return text
        except Exception as e:
            raise ValueError(f"Erro ao ler arquivo DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """
        Extrai texto de arquivo PDF.
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            
        Returns:
            Texto extraído do arquivo (todas as páginas concatenadas)
            
        Raises:
            ValueError: Se houver erro na leitura do PDF
            ImportError: Se PyPDF2 não estiver instalado
        """
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            raise ImportError(
                "PyPDF2 não está instalado. "
                "Instale com: pip install PyPDF2"
            )
        
        try:
            pdf_reader = PdfReader(io.BytesIO(file_content))
            text_parts = []
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text.strip():
                    text_parts.append(page_text)
            
            text = "\n\n".join(text_parts)
            
            if not text.strip():
                raise ValueError("Não foi possível extrair texto do PDF. O arquivo pode estar vazio ou protegido.")
            
            return text
        except ImportError:
            raise
        except Exception as e:
            raise ValueError(f"Erro ao ler arquivo PDF: {str(e)}")
    
    @staticmethod
    def extract_text(file_content: bytes, filename: str) -> Tuple[str, Optional[str]]:
        """
        Extrai texto de um arquivo baseado em sua extensão.
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            filename: Nome do arquivo (usado para determinar o tipo)
            
        Returns:
            Tupla contendo:
            - Texto extraído (string vazia se houver erro)
            - Mensagem de erro (None se sucesso)
            
        Example:
            >>> text, error = FileHandler.extract_text(file_bytes, "documento.docx")
            >>> if error:
            ...     print(f"Erro: {error}")
            ... else:
            ...     print(f"Texto extraído: {text[:100]}")
        """
        filename_lower = filename.lower()
        
        try:
            if filename_lower.endswith('.txt'):
                text = FileHandler.extract_text_from_txt(file_content)
                return text, None
            
            elif filename_lower.endswith('.docx'):
                text = FileHandler.extract_text_from_docx(file_content)
                return text, None
            
            elif filename_lower.endswith('.pdf'):
                text = FileHandler.extract_text_from_pdf(file_content)
                return text, None
            
            else:
                return "", f"Tipo de arquivo não suportado: {filename}. Use .txt, .docx ou .pdf"
        
        except (ValueError, ImportError) as e:
            return "", str(e)
        except Exception as e:
            return "", f"Erro inesperado ao processar {filename}: {str(e)}"


# Funções auxiliares para compatibilidade
def extract_text_from_txt(file_content: bytes) -> str:
    """Extrai texto de arquivo TXT."""
    return FileHandler.extract_text_from_txt(file_content)


def extract_text_from_docx(file_content: bytes) -> str:
    """Extrai texto de arquivo DOCX."""
    return FileHandler.extract_text_from_docx(file_content)


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extrai texto de arquivo PDF."""
    return FileHandler.extract_text_from_pdf(file_content)


def extract_text(file_content: bytes, filename: str) -> Tuple[str, Optional[str]]:
    """Extrai texto de um arquivo baseado em sua extensão."""
    return FileHandler.extract_text(file_content, filename)
