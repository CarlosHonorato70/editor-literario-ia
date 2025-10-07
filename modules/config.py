"""
Módulo de Configuração do Sistema
Gerencia todas as configurações e parâmetros do sistema.
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class Config:
    """Classe de configuração principal do sistema."""
    
    # Configurações gerais
    project_name: str = "Manuscript Publisher"
    version: str = "2.0"
    log_level: str = "INFO"
    
    # Configurações de API
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 3000
    openai_temperature: float = 0.7
    
    # Configurações de processamento
    enable_ai_enhancement: bool = True
    enable_ai_review: bool = True
    enable_diagram_generation: bool = True
    parallel_processing: bool = False
    max_workers: int = 4
    
    # Configurações de formatação
    default_format: str = "A5"
    default_font: str = "Times New Roman"
    default_font_size: int = 12
    default_line_spacing: float = 1.5
    
    # Configurações de elementos
    generate_pre_textual: bool = True
    generate_post_textual: bool = True
    generate_glossary: bool = True
    generate_index: bool = True
    
    # Configurações de revisão
    check_grammar: bool = True
    check_style: bool = True
    check_consistency: bool = True
    check_references: bool = True
    
    # Configurações de exportação
    export_formats: List[str] = field(default_factory=lambda: ["md", "docx", "pdf"])
    include_metadata: bool = True
    include_diagrams: bool = True
    
    # Diretórios
    templates_dir: str = "templates"
    output_dir: str = "output"
    cache_dir: str = ".cache"
    
    def __post_init__(self):
        """Inicialização pós-criação."""
        # Carrega API key de variável de ambiente se não fornecida
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
    
    def to_dict(self) -> Dict:
        """Converte configuração para dicionário."""
        return {
            "project_name": self.project_name,
            "version": self.version,
            "log_level": self.log_level,
            "openai_model": self.openai_model,
            "openai_max_tokens": self.openai_max_tokens,
            "openai_temperature": self.openai_temperature,
            "enable_ai_enhancement": self.enable_ai_enhancement,
            "enable_ai_review": self.enable_ai_review,
            "enable_diagram_generation": self.enable_diagram_generation,
            "default_format": self.default_format,
            "default_font": self.default_font,
            "default_font_size": self.default_font_size,
            "export_formats": self.export_formats,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Config':
        """Cria configuração a partir de dicionário."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

def load_config(config_path: Optional[str] = None) -> Config:
    """
    Carrega configuração de arquivo YAML ou usa padrão.
    
    Args:
        config_path: Caminho para arquivo de configuração YAML
        
    Returns:
        Objeto Config configurado
    """
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        return Config.from_dict(config_data)
    else:
        # Tenta carregar configuração padrão
        default_config_path = Path(__file__).parent.parent / "configs" / "default.yaml"
        if default_config_path.exists():
            with open(default_config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            return Config.from_dict(config_data)
        else:
            # Retorna configuração padrão
            return Config()

def save_config(config: Config, output_path: str):
    """
    Salva configuração em arquivo YAML.
    
    Args:
        config: Objeto Config para salvar
        output_path: Caminho do arquivo de saída
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False, allow_unicode=True)

# Templates de configuração para diferentes tipos de manuscritos

ACADEMIC_CONFIG = Config(
    default_format="A4",
    default_font="Times New Roman",
    default_font_size=12,
    default_line_spacing=1.5,
    generate_glossary=True,
    generate_index=True,
    check_references=True,
)

FICTION_CONFIG = Config(
    default_format="6x9",
    default_font="Garamond",
    default_font_size=11,
    default_line_spacing=1.15,
    generate_glossary=False,
    generate_index=False,
    check_references=False,
)

TECHNICAL_CONFIG = Config(
    default_format="A4",
    default_font="Arial",
    default_font_size=11,
    default_line_spacing=1.3,
    generate_glossary=True,
    generate_index=True,
    enable_diagram_generation=True,
    check_references=True,
)

CONFIG_TEMPLATES = {
    "academic": ACADEMIC_CONFIG,
    "fiction": FICTION_CONFIG,
    "technical": TECHNICAL_CONFIG,
}
