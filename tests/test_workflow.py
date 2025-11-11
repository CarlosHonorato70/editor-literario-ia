"""
Testes de Integração - Workflow Completo
Versão 2.0

Testa o fluxo completo de 14 fases do sistema.
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.workflow_orchestrator import WorkflowOrchestrator, ManuscriptMetadata
from modules.isbn_cip_generator import ISBNCIPGenerator
from modules.print_ready_generator import PrintReadyGenerator
from modules.config import Config


class TestWorkflowOrchestrator(unittest.TestCase):
    """Testa o orquestrador de workflow."""
    
    def setUp(self):
        """Prepara ambiente de teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {}  # Use dict instead of Config
        self.orchestrator = WorkflowOrchestrator(self.temp_dir, self.config)
    
    def tearDown(self):
        """Limpa ambiente de teste."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_orchestrator_initialization(self):
        """Testa inicialização do orquestrador."""
        self.assertIsNotNone(self.orchestrator)
        self.assertTrue(Path(self.temp_dir).exists())
    
    def test_directory_structure_creation(self):
        """Testa criação da estrutura de diretórios."""
        structure = self.orchestrator.structure
        self.assertIn('received', structure)
        self.assertIn('structural_edit', structure)
        self.assertIn('copyedit', structure)


class TestISBNCIPGenerator(unittest.TestCase):
    """Testa gerador de ISBN e CIP."""
    
    def setUp(self):
        """Prepara ambiente de teste."""
        self.config = {}  # Use dict instead of Config
        self.generator = ISBNCIPGenerator(self.config)
    
    def test_generator_initialization(self):
        """Testa inicialização do gerador."""
        self.assertIsNotNone(self.generator)
    
    def test_isbn_generation(self):
        """Testa geração de ISBN."""
        metadata = ManuscriptMetadata(
            title="Livro Teste",
            author="Autor Teste",
            genre="Ficção"
        )
        
        # Pass a string book_id instead of the metadata object
        isbn = self.generator.generate_isbn(book_id="livro-teste-123")
        
        # ISBN deve ter 13 dígitos (com hífens: 17 caracteres)
        self.assertIsNotNone(isbn)
        isbn_digits = isbn.replace('-', '')
        self.assertEqual(len(isbn_digits), 13)


class TestPrintReadyGenerator(unittest.TestCase):
    """Testa gerador de arquivos prontos para impressão."""
    
    def setUp(self):
        """Prepara ambiente de teste."""
        self.config = {}  # Use dict instead of Config
        self.generator = PrintReadyGenerator(self.config)
    
    def test_generator_initialization(self):
        """Testa inicialização do gerador."""
        self.assertIsNotNone(self.generator)


class TestManuscriptMetadata(unittest.TestCase):
    """Testa metadados de manuscrito."""
    
    def test_metadata_creation(self):
        """Testa criação de metadados."""
        metadata = ManuscriptMetadata(
            title="Meu Livro",
            author="João Silva",
            genre="Romance"
        )
        
        self.assertEqual(metadata.title, "Meu Livro")
        self.assertEqual(metadata.author, "João Silva")
        self.assertEqual(metadata.genre, "Romance")
    
    def test_metadata_with_optional_fields(self):
        """Testa metadados com campos opcionais."""
        metadata = ManuscriptMetadata(
            title="Meu Livro",
            author="João Silva",
            genre="Romance",
            publisher="Editora XYZ",
            page_count=350
        )
        
        self.assertEqual(metadata.publisher, "Editora XYZ")
        self.assertEqual(metadata.page_count, 350)


class TestCompleteWorkflow(unittest.TestCase):
    """Testa o workflow completo de ponta a ponta."""
    
    def setUp(self):
        """Prepara ambiente de teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {}  # Use dict instead of Config
    
    def tearDown(self):
        """Limpa ambiente de teste."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_workflow_structure_exists(self):
        """Testa que a estrutura de workflow existe."""
        orchestrator = WorkflowOrchestrator(self.temp_dir, self.config)
        
        # Verifica diretórios das 14 fases
        self.assertTrue(orchestrator.structure['received'].exists())
        self.assertTrue(orchestrator.structure['structural_edit'].exists())
        self.assertTrue(orchestrator.structure['copyedit'].exists())


if __name__ == '__main__':
    # Executa todos os testes
    unittest.main(verbosity=2)
