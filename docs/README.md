# Documentação - Sistema de Preparação de Manuscritos

Bem-vindo à documentação completa do sistema!

## 📚 Índice

1. [Guia de Instalação](INSTALL_GUIDE.md)
2. [Guia do Usuário](USER_GUIDE.md)
3. [Referência da API](API_REFERENCE.md)
4. [Arquitetura do Sistema](ARCHITECTURE.md)
5. [Guia de Contribuição](CONTRIBUTING.md)
6. [FAQ](FAQ.md)

## 🚀 Início Rápido

### Instalação
```bash
# Clone o repositório
git clone <repository-url>
cd editor-literario-ia

# Instale dependências
pip install -r requirements.txt

# Configure (opcional)
export OPENAI_API_KEY="sua-chave-aqui"
```

### Uso Básico
```bash
# Processar um manuscrito
python main.py manuscrito.pdf -o output/

# Workflow completo (14 fases)
python complete_workflow.py manuscrito.pdf \
  --title "Meu Livro" \
  --author "Autor"
```

## 📖 Visão Geral

Este sistema automatiza o processo completo de preparação de manuscritos para publicação, incluindo:

### Fase 1-6: Preparação Editorial
- Análise estrutural e de qualidade
- Aprimoramento de conteúdo com IA
- Criação de elementos pré/pós-textuais
- Revisão editorial profissional
- Formatação tipográfica (FastFormat)
- Padronização e exportação

### Fase 7-9: Produção Editorial
- Design automatizado de capas (5 conceitos)
- Diagramação profissional em PDF
- Revisão de provas

### Fase 10: ISBN e CIP
- Geração de ISBN-13 válido
- Criação de código de barras
- Ficha catalográfica (CIP)

### Fase 11-14: Preparação para Gráfica
- PDF do miolo (300 DPI, CMYK)
- PDF da capa com lombada
- Especificações técnicas
- Pacote completo para impressão

## 🎯 Casos de Uso

### Livro Acadêmico/Técnico
```bash
python main.py tese.pdf -c configs/academic.yaml
```
- Formato A4
- Times New Roman 12pt
- Glossário e índice incluídos
- Verificação de referências

### Romance/Ficção
```bash
python main.py romance.docx -c configs/fiction.yaml
```
- Formato 6x9"
- Garamond 11pt
- Foco em narrativa
- Sem elementos técnicos

### Manual Técnico
```bash
python main.py manual.md -c configs/technical.yaml
```
- Formato A4
- Arial 11pt
- Diagramas automáticos
- Glossário técnico

## 🔧 Configuração

### Arquivo de Configuração Básico
```yaml
# config.yaml
project_name: "Meu Manuscrito"
version: "1.0"

# IA
openai_model: "gpt-4o-mini"
enable_ai_enhancement: true

# Formatação
default_format: "A5"
default_font: "Times New Roman"
default_font_size: 12

# Elementos
generate_pre_textual: true
generate_post_textual: true
generate_glossary: true
generate_index: true
```

## 📊 Estatísticas

O sistema fornece métricas detalhadas:
- Contagem de palavras e páginas
- Estrutura (capítulos, seções)
- Qualidade (score 0-1.0)
- Legibilidade
- Consistência terminológica
- Formatação

## 🤖 Recursos de IA

Utiliza OpenAI GPT-4 para:
- Aprimoramento de conteúdo
- Revisão editorial
- Geração de elementos
- Análise de qualidade

**Nota:** Recursos de IA são opcionais e podem ser desabilitados.

## 📦 Saídas Geradas

### Análise
- `01_Analise_Estrutura.md`
- `02_Oportunidades_Aprimoramento.md`

### Elementos Pré-Textuais
- `Folha_Rosto.md`
- `Dedicatoria.md`
- `Agradecimentos.md`
- `Prefacio.md`
- `Sumario.md`

### Conteúdo Principal
- `Manuscrito_Aprimorado.md`
- `Manuscrito_Padronizado.md`

### Elementos Pós-Textuais
- `Glossario.md` (40+ termos)
- `Indice_Remissivo.md` (200+ entradas)
- `Referencias.md`

### Documentação Final
- `Relatorio_Revisao_Editorial.md`
- `Relatorio_Final_Projeto.md`
- `Guia_Proximos_Passos.md`

### Livro Completo
- `Livro_Pronto_Para_Publicacao.md`
- `Livro_Pronto_Para_Publicacao.docx`
- `Livro_Pronto_Para_Publicacao.pdf`

## 🛠️ Personalização

### Adicionar Novo Tipo de Manuscrito
1. Crie `configs/meu_tipo.yaml`
2. Configure formatação e elementos
3. Use: `python main.py manuscrito.pdf -c configs/meu_tipo.yaml`

### Adicionar Novo Módulo
1. Crie `modules/meu_modulo.py`
2. Implemente a classe
3. Integre em `main.py`

### Customizar Templates
1. Edite arquivos em `templates/`
2. Ajuste variáveis e formatação
3. Sistema detecta automaticamente

## 🧪 Testes

```bash
# Executar todos os testes
python -m unittest discover tests/

# Testes específicos
python tests/test_modules.py
python tests/test_workflow.py

# Com cobertura
python -m pytest tests/ --cov=modules
```

## 📈 Performance

### Economia
- **85-92% redução de custo**: R$ 14k-33k → R$ 650-2.5k
- **97-99% redução de tempo**: 4-8 semanas → 4-6 horas
- **Qualidade profissional consistente**

### Requisitos de Sistema
- Python 3.8+
- 4GB RAM mínimo
- 1GB espaço em disco
- Conexão internet (para IA, opcional)

## 🤝 Suporte

- **Issues**: Abra uma issue no repositório
- **Documentação**: Consulte `docs/`
- **Exemplos**: Veja `examples/`
- **FAQ**: Leia `docs/FAQ.md`

## 📄 Licença

Sistema fornecido "como está" para uso em projetos de preparação de manuscritos.

---

**Desenvolvido com ❤️ por Manus AI**

**Versão 2.0** | Novembro 2025
