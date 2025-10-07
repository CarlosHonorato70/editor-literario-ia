"""
Módulo de Modo Interativo
Interface interativa para o sistema de preparação de manuscritos.
"""

import os
from pathlib import Path
from typing import Optional
import logging

from .config import Config, CONFIG_TEMPLATES, save_config
from .utils import print_banner, print_info, print_success, print_error, Colors

class InteractiveMode:
    """Modo interativo com menu para o sistema."""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Executa modo interativo."""
        print_banner("MODO INTERATIVO - MANUSCRIPT PUBLISHER")
        
        while True:
            self._show_main_menu()
            choice = input(f"\n{Colors.OKCYAN}Escolha uma opção: {Colors.ENDC}").strip()
            
            if choice == '1':
                self._process_manuscript_interactive()
            elif choice == '2':
                self._configure_settings()
            elif choice == '3':
                self._view_templates()
            elif choice == '4':
                self._show_help()
            elif choice == '5':
                print_success("Encerrando sistema. Até logo!")
                break
            else:
                print_error("Opção inválida. Tente novamente.")
    
    def _show_main_menu(self):
        """Mostra menu principal."""
        print(f"\n{Colors.HEADER}{Colors.BOLD}═══ MENU PRINCIPAL ═══{Colors.ENDC}\n")
        print(f"{Colors.OKBLUE}1.{Colors.ENDC} Processar Manuscrito")
        print(f"{Colors.OKBLUE}2.{Colors.ENDC} Configurar Sistema")
        print(f"{Colors.OKBLUE}3.{Colors.ENDC} Ver Templates Disponíveis")
        print(f"{Colors.OKBLUE}4.{Colors.ENDC} Ajuda")
        print(f"{Colors.OKBLUE}5.{Colors.ENDC} Sair")
    
    def _process_manuscript_interactive(self):
        """Processa manuscrito em modo interativo."""
        print(f"\n{Colors.HEADER}═══ PROCESSAR MANUSCRITO ═══{Colors.ENDC}\n")
        
        # Solicita arquivo de entrada
        input_file = input(f"{Colors.OKCYAN}Caminho do manuscrito: {Colors.ENDC}").strip()
        
        if not os.path.exists(input_file):
            print_error(f"Arquivo não encontrado: {input_file}")
            return
        
        # Solicita diretório de saída
        output_dir = input(f"{Colors.OKCYAN}Diretório de saída (Enter para 'output/'): {Colors.ENDC}").strip()
        if not output_dir:
            output_dir = "output"
        
        # Pergunta sobre template
        use_template = input(f"{Colors.OKCYAN}Usar template pré-configurado? (s/n): {Colors.ENDC}").strip().lower()
        
        if use_template == 's':
            print("\nTemplates disponíveis:")
            print("1. Acadêmico")
            print("2. Ficção")
            print("3. Técnico")
            
            template_choice = input(f"{Colors.OKCYAN}Escolha o template (1-3): {Colors.ENDC}").strip()
            
            template_map = {
                '1': 'academic',
                '2': 'fiction',
                '3': 'technical'
            }
            
            if template_choice in template_map:
                self.config = CONFIG_TEMPLATES[template_map[template_choice]]
                print_success(f"Template '{template_map[template_choice]}' carregado!")
        
        # Confirma processamento
        print(f"\n{Colors.WARNING}Resumo:{Colors.ENDC}")
        print(f"  Arquivo: {input_file}")
        print(f"  Saída: {output_dir}")
        print(f"  Formato: {self.config.default_format}")
        print(f"  IA habilitada: {'Sim' if self.config.enable_ai_enhancement else 'Não'}")
        
        confirm = input(f"\n{Colors.OKCYAN}Confirmar processamento? (s/n): {Colors.ENDC}").strip().lower()
        
        if confirm == 's':
            print_info("Iniciando processamento...")
            
            # Importa e executa processamento
            from ..main import ManuscriptPublisher
            
            publisher = ManuscriptPublisher()
            publisher.config = self.config
            
            try:
                results = publisher.process_manuscript(input_file, output_dir)
                
                if "error" not in results:
                    print_success("\n✅ Processamento concluído com sucesso!")
                    print(f"\n📁 Arquivos gerados: {len(results['files_generated'])}")
                    print(f"📊 Localização: {output_dir}/")
                else:
                    print_error(f"\n❌ Erro: {results['error']}")
            
            except Exception as e:
                print_error(f"Erro durante processamento: {e}")
        else:
            print_info("Processamento cancelado.")
    
    def _configure_settings(self):
        """Configura opções do sistema."""
        print(f"\n{Colors.HEADER}═══ CONFIGURAÇÕES ═══{Colors.ENDC}\n")
        
        print("1. Habilitar/Desabilitar IA")
        print("2. Configurar Formato Padrão")
        print("3. Configurar Fonte")
        print("4. Configurar Formatos de Exportação")
        print("5. Salvar Configuração Atual")
        print("6. Voltar")
        
        choice = input(f"\n{Colors.OKCYAN}Escolha: {Colors.ENDC}").strip()
        
        if choice == '1':
            self.config.enable_ai_enhancement = not self.config.enable_ai_enhancement
            status = "habilitada" if self.config.enable_ai_enhancement else "desabilitada"
            print_success(f"IA {status}!")
        
        elif choice == '2':
            formats = ["A4", "A5", "6x9", "Letter"]
            print("\nFormatos disponíveis:")
            for i, fmt in enumerate(formats, 1):
                print(f"{i}. {fmt}")
            
            fmt_choice = input(f"{Colors.OKCYAN}Escolha (1-{len(formats)}): {Colors.ENDC}").strip()
            try:
                idx = int(fmt_choice) - 1
                if 0 <= idx < len(formats):
                    self.config.default_format = formats[idx]
                    print_success(f"Formato definido: {formats[idx]}")
            except:
                print_error("Opção inválida.")
        
        elif choice == '3':
            fonts = ["Times New Roman", "Arial", "Garamond", "Georgia"]
            print("\nFontes disponíveis:")
            for i, font in enumerate(fonts, 1):
                print(f"{i}. {font}")
            
            font_choice = input(f"{Colors.OKCYAN}Escolha (1-{len(fonts)}): {Colors.ENDC}").strip()
            try:
                idx = int(font_choice) - 1
                if 0 <= idx < len(fonts):
                    self.config.default_font = fonts[idx]
                    print_success(f"Fonte definida: {fonts[idx]}")
            except:
                print_error("Opção inválida.")
        
        elif choice == '4':
            print("\nFormatos de exportação atuais:", ", ".join(self.config.export_formats))
            print("\nFormatos disponíveis: md, docx, pdf")
            
            new_formats = input(f"{Colors.OKCYAN}Digite formatos separados por vírgula: {Colors.ENDC}").strip()
            formats_list = [f.strip() for f in new_formats.split(',')]
            
            valid_formats = [f for f in formats_list if f in ['md', 'docx', 'pdf']]
            if valid_formats:
                self.config.export_formats = valid_formats
                print_success(f"Formatos definidos: {', '.join(valid_formats)}")
            else:
                print_error("Nenhum formato válido especificado.")
        
        elif choice == '5':
            filename = input(f"{Colors.OKCYAN}Nome do arquivo de configuração: {Colors.ENDC}").strip()
            if not filename.endswith('.yaml'):
                filename += '.yaml'
            
            save_config(self.config, f"configs/{filename}")
            print_success(f"Configuração salva em configs/{filename}")
        
        elif choice == '6':
            return
    
    def _view_templates(self):
        """Mostra templates disponíveis."""
        print(f"\n{Colors.HEADER}═══ TEMPLATES DISPONÍVEIS ═══{Colors.ENDC}\n")
        
        templates_info = {
            "academic": {
                "nome": "Acadêmico/Científico",
                "formato": "A4",
                "fonte": "Times New Roman 12pt",
                "características": "Glossário, índice, referências rigorosas"
            },
            "fiction": {
                "nome": "Ficção/Romance",
                "formato": "6x9\"",
                "fonte": "Garamond 11pt",
                "características": "Foco em narrativa, sem elementos acadêmicos"
            },
            "technical": {
                "nome": "Manual Técnico",
                "formato": "A4",
                "fonte": "Arial 11pt",
                "características": "Diagramas, glossário técnico, índice detalhado"
            }
        }
        
        for key, info in templates_info.items():
            print(f"{Colors.OKBLUE}{Colors.BOLD}{info['nome']}{Colors.ENDC}")
            print(f"  Formato: {info['formato']}")
            print(f"  Fonte: {info['fonte']}")
            print(f"  Características: {info['características']}")
            print()
    
    def _show_help(self):
        """Mostra ajuda."""
        print(f"\n{Colors.HEADER}═══ AJUDA ═══{Colors.ENDC}\n")
        
        help_text = """
SOBRE O SISTEMA:
  Sistema automatizado para preparação de manuscritos para publicação.
  Realiza análise, aprimoramento, formatação e geração de elementos
  complementares de forma profissional.

FORMATOS SUPORTADOS:
  - PDF (.pdf)
  - Word (.docx)
  - Markdown (.md)
  - Texto (.txt)

PROCESSO COMPLETO (7 FASES):
  1. Análise e Diagnóstico
  2. Identificação de Oportunidades
  3. Aprimoramento de Conteúdo
  4. Criação de Elementos Complementares
  5. Revisão Editorial Profissional
  6. Formatação e Padronização
  7. Exportação para Publicação

RECURSOS DE IA:
  - Aprimoramento de texto
  - Revisão editorial
  - Geração de elementos
  - Análise de qualidade

DOCUMENTAÇÃO COMPLETA:
  Consulte README.md para informações detalhadas.

SUPORTE:
  - GitHub: [URL do repositório]
  - Email: [email de suporte]
        """
        
        print(help_text)
        
        input(f"\n{Colors.OKCYAN}Pressione Enter para continuar...{Colors.ENDC}")
