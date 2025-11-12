"""
Módulo de Aprimoramento de Conteúdo
Realiza melhorias no conteúdo do manuscrito usando IA e regras.
"""

import re
import time
from typing import Dict, List, Tuple
import logging

from .config import Config
from .utils import print_info, print_warning, ProgressTracker

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class ContentEnhancer:
    """Aprimora conteúdo do manuscrito."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        if OPENAI_AVAILABLE and config.openai_api_key and config.enable_ai_enhancement:
            self.client = OpenAI(api_key=config.openai_api_key)
            self.ai_enabled = True
        else:
            self.client = None
            self.ai_enabled = False
    
    def enhance(self, content: str, opportunities: Dict, metadata: Dict) -> Dict:
        """Aprimora o conteúdo do manuscrito."""
        print_info("Iniciando aprimoramento de conteúdo...")
        
        enhanced_content = content
        changes = []
        
        # Aprimoramento de formatação
        enhanced_content, format_changes = self._enhance_formatting(enhanced_content)
        changes.extend(format_changes)
        
        # Aprimoramento de consistência terminológica
        enhanced_content, term_changes = self._enhance_terminology(enhanced_content)
        changes.extend(term_changes)
        
        # Aprimoramento com IA (se habilitado)
        ai_changes = []
        if self.ai_enabled:
            enhanced_content, ai_changes = self._enhance_with_ai(enhanced_content, metadata)
            changes.extend(ai_changes)
        
        return {
            "content": enhanced_content,
            "original_length": len(content),
            "enhanced_length": len(enhanced_content),
            "changes": changes,
            "statistics": {
                "total_changes": len(changes),
                "formatting_changes": len(format_changes),
                "terminology_changes": len(term_changes),
                "ai_changes": len(ai_changes)
            }
        }
    
    def _enhance_formatting(self, content: str) -> Tuple[str, List[Dict]]:
        """Aprimora formatação do conteúdo."""
        changes = []
        enhanced = content
        
        # Remove espaços em branco excessivos
        original = enhanced
        enhanced = re.sub(r'\n{4,}', '\n\n\n', enhanced)
        if enhanced != original:
            changes.append({"type": "formatting", "description": "Removido espaçamento excessivo"})
        
        # Corrige espaços antes de pontuação
        original = enhanced
        enhanced = re.sub(r'\s+([.,;:!?])', r'\1', enhanced)
        if enhanced != original:
            changes.append({"type": "formatting", "description": "Corrigidos espaços antes de pontuação"})
        
        return enhanced, changes
    
    def _enhance_terminology(self, content: str) -> Tuple[str, List[Dict]]:
        """Aprimora consistência terminológica."""
        changes = []
        enhanced = content
        
        # Padronização de termos
        term_replacements = {
            r'Teoria da Emoção Construída(?! \(TCE\))': 'Teoria da Emoção Construída (TCE)',
        }
        
        for pattern, replacement in term_replacements.items():
            if re.search(pattern, enhanced):
                enhanced = re.sub(pattern, replacement, enhanced, count=1)
                changes.append({"type": "terminology", "description": f"Padronizado: {replacement}"})
        
        return enhanced, changes
    
    def _enhance_with_ai(self, content: str, metadata: Dict) -> Tuple[str, List[Dict]]:
        """Aprimora conteúdo usando IA."""
        changes = []
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        sample_paragraphs = paragraphs[:5]  # Amostra reduzida
        
        print_info(f"Aprimorando {len(sample_paragraphs)} parágrafos com IA...")
        
        enhanced_paragraphs = []
        for para in sample_paragraphs:
            if len(para.split()) < 10:
                enhanced_paragraphs.append(para)
                continue
            
            try:
                enhanced_para = self._enhance_paragraph_ai(para)
                enhanced_paragraphs.append(enhanced_para)
                if enhanced_para != para:
                    changes.append({"type": "ai", "description": "Parágrafo aprimorado"})
            except:
                enhanced_paragraphs.append(para)
            
            time.sleep(0.5)
        
        enhanced_content = '\n\n'.join(enhanced_paragraphs + paragraphs[len(sample_paragraphs):])
        return enhanced_content, changes
    
    def _enhance_paragraph_ai(self, paragraph: str) -> str:
        """Aprimora um parágrafo usando IA."""
        if not self.client:
            return paragraph
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": "Você é um editor. Aprimore o parágrafo mantendo o significado."},
                    {"role": "user", "content": paragraph}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except:
            return paragraph


# Exportar função standalone para compatibilidade
def enhance_content(text: str, focus: str = "overall", use_ai: bool = False) -> str:
    """
    Função standalone para aprimorar conteúdo.
    
    Args:
        text: Texto a ser aprimorado
        focus: Foco do aprimoramento (overall, dialogue, description, transitions)
        use_ai: Se True, usa IA para aprimoramento
    
    Returns:
        Texto aprimorado
    """
    enhancer = ContentEnhancer()
    return enhancer.enhance(text, focus=focus, use_ai=use_ai)
