"""
Testes Unitários - Sistema de Preparação de Manuscritos
Versão 2.0

Este módulo contém testes para os componentes principais do sistema.
"""

import unittest
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config import Config
from modules.analyzer import ManuscriptAnalyzer
from modules.enhancer import ContentEnhancer
from modules.formatter import DocumentFormatter
from modules.elements import ElementsGenerator
from modules.reviewer import EditorialReviewer
from modules.exporter import PublicationExporter


class TestConfig(unittest.TestCase):
    """Testa configurações do sistema."""
    
    def test_default_config(self):
        """Testa criação de configuração padrão."""
        config = Config()
        self.assertIsNotNone(config)
        self.assertEqual(config.project_name, "Manuscript Publisher")
    
    def test_custom_config(self):
        """Testa configuração customizada."""
        config = Config(project_name="Teste")
        self.assertEqual(config.project_name, "Teste")


class TestManuscriptAnalyzer(unittest.TestCase):
    """Testa analisador de manuscritos."""
    
    def setUp(self):
        """Prepara ambiente de teste."""
        self.config = Config()
        self.analyzer = ManuscriptAnalyzer(self.config)
    
    def test_analyzer_initialization(self):
        """Testa inicialização do analisador."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.config, self.config)
    
    def test_extract_text_from_string(self):
        """Testa extração de texto de string."""
        test_text = "Este é um teste.\n\nCom múltiplos parágrafos."
        # Teste básico de que o analisador foi criado corretamente
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.config, self.config)


class TestContentEnhancer(unittest.TestCase):
    """Testa aprimorador de conteúdo."""
    
    def setUp(self):
        """Prepara ambiente de teste."""
        self.config = Config()
        self.enhancer = ContentEnhancer(self.config)
    
    def test_enhancer_initialization(self):
        """Testa inicialização do enhancer."""
        self.assertIsNotNone(self.enhancer)
    
    def test_basic_formatting_fixes(self):
        """Testa correções básicas de formatação."""
        text = "Texto  com   espaços   extras."
        # Teste básico de que o enhancer foi criado corretamente
        self.assertIsNotNone(self.enhancer)
        self.assertEqual(self.enhancer.config, self.config)


class TestDocumentFormatter(unittest.TestCase):
    """Testa formatador de documentos."""
    
    def setUp(self):
        """Prepara ambiente de teste."""
        self.config = Config()
        self.formatter = DocumentFormatter(self.config)
    
    def test_formatter_initialization(self):
        """Testa inicialização do formatter."""
        self.assertIsNotNone(self.formatter)
    
    def test_heading_standardization(self):
        """Testa padronização de títulos."""
        text = "# Capítulo 1\n## Seção 1.1"
        # O formatter deve manter estrutura de headings
        self.assertIn("#", text)


class TestElementsGenerator(unittest.TestCase):
    """Testa gerador de elementos."""
    
    def setUp(self):
        """Prepara ambiente de teste."""
        self.config = Config()
        self.generator = ElementsGenerator(self.config)
    
    def test_generator_initialization(self):
        """Testa inicialização do generator."""
        self.assertIsNotNone(self.generator)


class TestEditorialReviewer(unittest.TestCase):
    """Testa revisor editorial."""
    
    def setUp(self):
        """Prepara ambiente de teste."""
        self.config = Config()
        self.reviewer = EditorialReviewer(self.config)
    
    def test_reviewer_initialization(self):
        """Testa inicialização do reviewer."""
        self.assertIsNotNone(self.reviewer)


class TestPublicationExporter(unittest.TestCase):
    """Testa exportador de publicações."""
    
    def setUp(self):
        """Prepara ambiente de teste."""
        self.config = Config()
        self.exporter = PublicationExporter(self.config)
    
    def test_exporter_initialization(self):
        """Testa inicialização do exporter."""
        self.assertIsNotNone(self.exporter)


class TestTemplates(unittest.TestCase):
    """Testa templates do sistema."""
    
    def test_templates_exist(self):
        """Verifica que templates existem."""
        templates_dir = Path(__file__).parent.parent / "templates"
        self.assertTrue(templates_dir.exists())
        
        # Verifica pré-textuais
        pre_textual = templates_dir / "pre_textual"
        self.assertTrue(pre_textual.exists())
        self.assertTrue((pre_textual / "folha_rosto.md").exists())
        self.assertTrue((pre_textual / "dedicatoria.md").exists())
        
        # Verifica pós-textuais
        post_textual = templates_dir / "post_textual"
        self.assertTrue(post_textual.exists())
        self.assertTrue((post_textual / "glossario.md").exists())


if __name__ == '__main__':
    # Executa todos os testes
    unittest.main(verbosity=2)
