"""
Blackbelt Platform - Sistema Automatizado de Preparação de Manuscritos para Publicação
Versão 2.0

Desenvolvido por Manus AI e Carlos Honorato
"""

__version__ = "2.0.0"
__author__ = "Carlos Honorato & Manus AI"

# Import main classes for easier access
from .main import ManuscriptPublisher

__all__ = [
    "ManuscriptPublisher",
    "__version__",
    "__author__",
]
