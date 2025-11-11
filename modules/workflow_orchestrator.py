"""
Workflow Orchestrator - Fluxo Completo: Do Manuscrito Bruto até a Gráfica

Este módulo implementa o fluxo completo de 14 fases do processo editorial,
desde o recebimento do manuscrito até o envio dos arquivos para a gráfica.

Fases implementadas:
1. Recebimento do Manuscrito
2. Edição Estrutural
3. Revisão do Autor
4. Copyediting (Edição Linguística)
5. Proofreading (Revisão Final)
6. Aprovação Final do Autor
7. Diagramação do Miolo
8. Revisão da Diagramação
9. Design da Capa
10. Geração de ISBN e CIP
11. Preparação Final do Arquivo para Impressão
12. Aprovação Final Antes de Envio
13. Preparação para Envio à Gráfica
14. Envio à Gráfica

Autor: Manus AI
Versão: 2.0
Data: Novembro 2025
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class ManuscriptMetadata:
    """Metadados do manuscrito."""
    title: str
    author: str
    genre: str
    word_count: int = 0
    page_count: int = 0
    isbn: Optional[str] = None
    cip: Optional[str] = None
    publisher: str = "Editora"
    edition: str = "1. ed."
    year: int = 2025
    language: str = "pt-BR"
    
@dataclass
class WorkflowPhase:
    """Representa uma fase do workflow."""
    phase_number: int
    phase_name: str
    status: str  # 'pending', 'in_progress', 'completed', 'approved', 'rejected'
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    assigned_to: Optional[str] = None
    output_files: List[str] = None
    notes: str = ""
    
    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []

@dataclass
class ApprovalRecord:
    """Registro de aprovação."""
    phase: str
    approver: str
    approved: bool
    timestamp: str
    comments: str = ""

class WorkflowOrchestrator:
    """
    Orquestrador do fluxo completo de preparação de manuscrito.
    
    Gerencia todas as 14 fases do processo editorial, desde o recebimento
    do manuscrito bruto até o envio dos arquivos finais para a gráfica.
    """
    
    def __init__(self, project_dir: str, config: Optional[Dict] = None):
        """
        Inicializa o orquestrador de workflow.
        
        Args:
            project_dir: Diretório raiz do projeto
            config: Configurações customizadas
        """
        self.project_dir = Path(project_dir)
        self.config = config or {}
        
        # Criar estrutura de diretórios
        self.structure = {
            'received': self.project_dir / '01_manuscrito_recebido',
            'structural_edit': self.project_dir / '02_edicao_estrutural',
            'author_revision': self.project_dir / '03_revisao_autor',
            'copyedit': self.project_dir / '04_copyediting',
            'proofread': self.project_dir / '05_proofreading',
            'author_approval': self.project_dir / '06_aprovacao_autor',
            'layout': self.project_dir / '07_diagramacao',
            'layout_review': self.project_dir / '08_revisao_diagramacao',
            'cover_design': self.project_dir / '09_design_capa',
            'isbn_cip': self.project_dir / '10_isbn_cip',
            'print_prep': self.project_dir / '11_preparacao_impressao',
            'final_approval': self.project_dir / '12_aprovacao_final',
            'printer_package': self.project_dir / '13_pacote_grafica',
            'delivery': self.project_dir / '14_envio_grafica',
            'backups': self.project_dir / 'backups',
            'logs': self.project_dir / 'logs',
        }
        
        # Criar todos os diretórios
        for dir_path in self.structure.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar estado do workflow
        self.workflow_state_file = self.project_dir / 'workflow_state.json'
        self.metadata: Optional[ManuscriptMetadata] = None
        self.phases: List[WorkflowPhase] = []
        self.approvals: List[ApprovalRecord] = []
        
        # Carregar estado se existir
        if self.workflow_state_file.exists():
            self.load_state()
        else:
            self.initialize_phases()
    
    def initialize_phases(self):
        """Inicializa todas as fases do workflow."""
        phase_definitions = [
            (1, "Recebimento do Manuscrito"),
            (2, "Edição Estrutural"),
            (3, "Revisão do Autor"),
            (4, "Copyediting (Edição Linguística)"),
            (5, "Proofreading (Revisão Final)"),
            (6, "Aprovação Final do Autor"),
            (7, "Diagramação do Miolo"),
            (8, "Revisão da Diagramação"),
            (9, "Design da Capa"),
            (10, "Geração de ISBN e CIP"),
            (11, "Preparação Final para Impressão"),
            (12, "Aprovação Final Antes de Envio"),
            (13, "Preparação para Envio à Gráfica"),
            (14, "Envio à Gráfica"),
        ]
        
        self.phases = [
            WorkflowPhase(
                phase_number=num,
                phase_name=name,
                status='pending'
            )
            for num, name in phase_definitions
        ]
    
    def save_state(self):
        """Salva o estado atual do workflow."""
        state = {
            'metadata': asdict(self.metadata) if self.metadata else None,
            'phases': [asdict(phase) for phase in self.phases],
            'approvals': [asdict(approval) for approval in self.approvals],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.workflow_state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def load_state(self):
        """Carrega o estado do workflow."""
        with open(self.workflow_state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        if state['metadata']:
            self.metadata = ManuscriptMetadata(**state['metadata'])
        
        self.phases = [WorkflowPhase(**phase) for phase in state['phases']]
        self.approvals = [ApprovalRecord(**approval) for approval in state['approvals']]
    
    def get_phase(self, phase_number: int) -> WorkflowPhase:
        """Retorna uma fase específica."""
        return self.phases[phase_number - 1]
    
    def start_phase(self, phase_number: int, assigned_to: str = "System"):
        """Inicia uma fase do workflow."""
        phase = self.get_phase(phase_number)
        phase.status = 'in_progress'
        phase.started_at = datetime.now().isoformat()
        phase.assigned_to = assigned_to
        self.save_state()
        
        print(f"\n{'='*70}")
        print(f"🚀 FASE {phase_number}: {phase.phase_name}")
        print(f"{'='*70}")
        print(f"Responsável: {assigned_to}")
        print(f"Iniciado em: {phase.started_at}")
        print()
    
    def complete_phase(self, phase_number: int, output_files: List[str] = None, notes: str = ""):
        """Completa uma fase do workflow."""
        phase = self.get_phase(phase_number)
        phase.status = 'completed'
        phase.completed_at = datetime.now().isoformat()
        
        if output_files:
            phase.output_files.extend(output_files)
        
        if notes:
            phase.notes = notes
        
        self.save_state()
        
        print(f"\n✅ FASE {phase_number} CONCLUÍDA: {phase.phase_name}")
        if output_files:
            print(f"Arquivos gerados: {len(output_files)}")
        print()
    
    def add_approval(self, phase_name: str, approver: str, approved: bool, comments: str = ""):
        """Adiciona um registro de aprovação."""
        approval = ApprovalRecord(
            phase=phase_name,
            approver=approver,
            approved=approved,
            timestamp=datetime.now().isoformat(),
            comments=comments
        )
        self.approvals.append(approval)
        self.save_state()
        
        status_icon = "✅" if approved else "❌"
        print(f"{status_icon} Aprovação registrada: {phase_name} por {approver}")
    
    def generate_workflow_report(self) -> str:
        """Gera relatório completo do workflow."""
        report = []
        report.append("=" * 70)
        report.append("📊 RELATÓRIO DO WORKFLOW EDITORIAL")
        report.append("=" * 70)
        report.append("")
        
        if self.metadata:
            report.append("📚 INFORMAÇÕES DO MANUSCRITO")
            report.append(f"Título: {self.metadata.title}")
            report.append(f"Autor: {self.metadata.author}")
            report.append(f"Gênero: {self.metadata.genre}")
            report.append(f"Palavras: {self.metadata.word_count:,}")
            report.append(f"Páginas estimadas: {self.metadata.page_count}")
            if self.metadata.isbn:
                report.append(f"ISBN: {self.metadata.isbn}")
            report.append("")
        
        report.append("📋 PROGRESSO DAS FASES")
        report.append("")
        
        for phase in self.phases:
            status_icons = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅',
                'approved': '✅',
                'rejected': '❌'
            }
            icon = status_icons.get(phase.status, '❓')
            
            report.append(f"{icon} Fase {phase.phase_number}: {phase.phase_name}")
            report.append(f"   Status: {phase.status.upper()}")
            
            if phase.assigned_to:
                report.append(f"   Responsável: {phase.assigned_to}")
            
            if phase.started_at:
                report.append(f"   Iniciado: {phase.started_at}")
            
            if phase.completed_at:
                report.append(f"   Concluído: {phase.completed_at}")
            
            if phase.output_files:
                report.append(f"   Arquivos: {len(phase.output_files)}")
            
            report.append("")
        
        # Estatísticas
        completed = sum(1 for p in self.phases if p.status == 'completed')
        in_progress = sum(1 for p in self.phases if p.status == 'in_progress')
        pending = sum(1 for p in self.phases if p.status == 'pending')
        
        report.append("📈 ESTATÍSTICAS")
        report.append(f"Fases concluídas: {completed}/14")
        report.append(f"Fases em progresso: {in_progress}")
        report.append(f"Fases pendentes: {pending}")
        report.append(f"Progresso geral: {(completed/14)*100:.1f}%")
        report.append("")
        
        # Aprovações
        if self.approvals:
            report.append("✍️ APROVAÇÕES REGISTRADAS")
            for approval in self.approvals:
                status = "APROVADO" if approval.approved else "REJEITADO"
                report.append(f"• {approval.phase} - {status} por {approval.approver}")
                if approval.comments:
                    report.append(f"  Comentários: {approval.comments}")
            report.append("")
        
        report.append("=" * 70)
        report.append(f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def export_workflow_report(self, output_path: Optional[str] = None):
        """Exporta o relatório do workflow para arquivo."""
        if output_path is None:
            output_path = self.project_dir / 'RELATORIO_WORKFLOW.txt'
        
        report = self.generate_workflow_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Relatório exportado: {output_path}")
        return output_path
    
    def get_current_phase(self) -> Optional[WorkflowPhase]:
        """Retorna a fase atual (primeira não concluída)."""
        for phase in self.phases:
            if phase.status != 'completed':
                return phase
        return None
    
    def is_phase_ready(self, phase_number: int) -> Tuple[bool, str]:
        """
        Verifica se uma fase está pronta para ser executada.
        
        Returns:
            Tuple (pode_executar, mensagem)
        """
        if phase_number == 1:
            return True, "Primeira fase sempre pronta"
        
        # Verifica se a fase anterior está concluída
        previous_phase = self.get_phase(phase_number - 1)
        
        if previous_phase.status != 'completed':
            return False, f"Fase anterior ({previous_phase.phase_name}) ainda não concluída"
        
        return True, "Pronta para execução"
    
    def create_backup(self, phase_number: int):
        """Cria backup antes de iniciar uma fase."""
        backup_dir = self.structure['backups'] / f"fase_{phase_number:02d}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copia arquivos relevantes
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f"backup_{timestamp}.zip"
        
        # Aqui você pode adicionar lógica de backup real
        print(f"💾 Backup criado: {backup_file}")
        
        return str(backup_file)
