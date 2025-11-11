"""
Módulo de Utilidades
Funções auxiliares usadas em todo o sistema.
"""

import logging
import sys
import time
from typing import Any, Callable, Optional
from pathlib import Path
import hashlib

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configura o sistema de logging.
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Logger configurado
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('manuscript_publisher.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger('ManuscriptPublisher')

def print_banner(title: str):
    """Imprime banner decorativo."""
    width = 70
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("=" * width)
    print(f"{title:^{width}}")
    print("=" * width)
    print(f"{Colors.ENDC}\n")

def print_progress(phase: str, description: str, success: bool = False):
    """
    Imprime progresso de uma fase.
    
    Args:
        phase: Nome da fase (ex: "FASE 1/7")
        description: Descrição da fase
        success: Se True, usa cor de sucesso
    """
    color = Colors.OKGREEN if success else Colors.OKCYAN
    symbol = "✅" if success else "⏳"
    
    print(f"\n{color}{Colors.BOLD}{symbol} {phase}: {description}{Colors.ENDC}")
    print(f"{color}{'─' * 70}{Colors.ENDC}\n")

def print_error(message: str):
    """Imprime mensagem de erro."""
    print(f"{Colors.FAIL}{Colors.BOLD}❌ ERRO: {message}{Colors.ENDC}")

def print_warning(message: str):
    """Imprime mensagem de aviso."""
    print(f"{Colors.WARNING}⚠️  AVISO: {message}{Colors.ENDC}")

def print_success(message: str):
    """Imprime mensagem de sucesso."""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_info(message: str):
    """Imprime mensagem informativa."""
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")

def measure_time(func: Callable) -> Callable:
    """
    Decorator para medir tempo de execução de função.
    
    Args:
        func: Função a ser medida
        
    Returns:
        Função decorada
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        func_name = func.__name__
        print_info(f"{func_name} concluída em {duration:.2f}s")
        
        return result
    
    return wrapper

def calculate_file_hash(file_path: str) -> str:
    """
    Calcula hash MD5 de um arquivo.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        Hash MD5 em hexadecimal
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def ensure_dir(directory: str) -> Path:
    """
    Garante que um diretório existe, criando se necessário.
    
    Args:
        directory: Caminho do diretório
        
    Returns:
        Path object do diretório
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path

def count_words(text: str) -> int:
    """
    Conta palavras em um texto.
    
    Args:
        text: Texto para contar
        
    Returns:
        Número de palavras
    """
    return len(text.split())

def estimate_pages(word_count: int, words_per_page: int = 250) -> int:
    """
    Estima número de páginas baseado em contagem de palavras.
    
    Args:
        word_count: Número de palavras
        words_per_page: Palavras por página (padrão: 250)
        
    Returns:
        Número estimado de páginas
    """
    return max(1, round(word_count / words_per_page))

def format_file_size(size_bytes: int) -> str:
    """
    Formata tamanho de arquivo em formato legível.
    
    Args:
        size_bytes: Tamanho em bytes
        
    Returns:
        String formatada (ex: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Trunca texto se exceder comprimento máximo.
    
    Args:
        text: Texto para truncar
        max_length: Comprimento máximo
        suffix: Sufixo para adicionar se truncado
        
    Returns:
        Texto truncado
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """
    Cria barra de progresso ASCII.
    
    Args:
        current: Valor atual
        total: Valor total
        width: Largura da barra
        
    Returns:
        String da barra de progresso
    """
    if total == 0:
        return "[" + "=" * width + "]"
    
    progress = current / total
    filled = int(width * progress)
    bar = "=" * filled + "-" * (width - filled)
    percentage = progress * 100
    
    return f"[{bar}] {percentage:.1f}% ({current}/{total})"

def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nome de arquivo removendo caracteres inválidos.
    
    Args:
        filename: Nome do arquivo original
        
    Returns:
        Nome do arquivo sanitizado
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def read_file_safe(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
    """
    Lê arquivo de forma segura, tratando erros.
    
    Args:
        file_path: Caminho do arquivo
        encoding: Codificação do arquivo
        
    Returns:
        Conteúdo do arquivo ou None se erro
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print_error(f"Erro ao ler arquivo {file_path}: {e}")
        return None

def write_file_safe(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    Escreve arquivo de forma segura, tratando erros.
    
    Args:
        file_path: Caminho do arquivo
        content: Conteúdo a escrever
        encoding: Codificação do arquivo
        
    Returns:
        True se sucesso, False se erro
    """
    try:
        ensure_dir(Path(file_path).parent)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print_error(f"Erro ao escrever arquivo {file_path}: {e}")
        return False

class ProgressTracker:
    """Classe para rastrear progresso de operações longas."""
    
    def __init__(self, total: int = 7, description: str = "Processando"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.phases = {}
        self.current_phase = None
    
    def start_phase(self, phase_name: str):
        """Inicia uma nova fase."""
        self.current_phase = phase_name
        self.phases[phase_name] = {
            'start_time': time.time(),
            'status': 'in_progress'
        }
    
    def end_phase(self, phase_name: str, metrics: dict = None):
        """Finaliza uma fase."""
        if phase_name in self.phases:
            self.phases[phase_name]['end_time'] = time.time()
            self.phases[phase_name]['status'] = 'completed'
            if metrics:
                self.phases[phase_name]['metrics'] = metrics
        self.current += 1
        self._print_progress()
    
    def update(self, increment: int = 1):
        """Atualiza progresso."""
        self.current += increment
        self._print_progress()
    
    def _print_progress(self):
        """Imprime barra de progresso."""
        elapsed = time.time() - self.start_time
        progress_bar = create_progress_bar(self.current, self.total)
        
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f"ETA: {eta:.0f}s"
        else:
            eta_str = "ETA: --"
        
        print(f"\r{self.description}: {progress_bar} {eta_str}", end='', flush=True)
        
        if self.current >= self.total:
            print()  # Nova linha ao completar
    
    def finish(self):
        """Finaliza progresso."""
        self.current = self.total
        self._print_progress()
        duration = time.time() - self.start_time
        print_success(f"{self.description} concluído em {duration:.2f}s")
    
    def get_summary(self) -> dict:
        """Retorna sumário do progresso."""
        return {
            'total_time': time.time() - self.start_time,
            'phases': self.phases,
            'completed': self.current,
            'total': self.total
        }
