"""
Módulo de Produção Editorial Automatizada.

Este módulo implementa automação completa da Fase 3 (Produção Editorial),
incluindo design de capa, diagramação, revisão de provas e geração de
materiais adicionais.

Componentes:
- CoverDesigner: Design automatizado de capas
- LayoutEngine: Diagramação profissional de livros
- ProofChecker: Revisão automatizada de provas
- MaterialsGenerator: Geração de elementos adicionais
- ProductionPipeline: Pipeline completo de produção
"""

from .cover_designer import CoverDesigner
from .layout_engine import LayoutEngine
from .proof_checker import ProofChecker
from .materials_generator import MaterialsGenerator
from .pipeline import ProductionPipeline

__all__ = [
    'CoverDesigner',
    'LayoutEngine',
    'ProofChecker',
    'MaterialsGenerator',
    'ProductionPipeline'
]

__version__ = '1.0.0'
__author__ = 'Manus AI'
