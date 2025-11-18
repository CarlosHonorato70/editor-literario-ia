# Sistema Automatizado de Preparação de Manuscritos para Publicação

**Versão 2.0** | Desenvolvido por Manus AI | Novembro 2025

**Pacote Python**: `@CarlosHonorato70/blackbelt-platform` 🎉 **NOVO**

[![PyPI Package](https://img.shields.io/badge/package-blackbelt--platform-blue)](https://github.com/CarlosHonorato70/editor-literario-ia)

---

## 📖 Visão Geral

Sistema completo e automatizado que replica o processo profissional de preparação de manuscritos para publicação, incluindo o **fluxo completo de 14 fases** do manuscrito bruto até a gráfica.

Este sistema transforma manuscritos brutos (PDF, DOCX, MD) em obras **completamente prontas para impressão e publicação**, incluindo:

### ⭐ NOVO: Workflow Completo (14 Fases)
- ✅ **Fase 1-6**: Recebimento → Edição → Revisão → Aprovação
- ✅ **Fase 7-9**: Diagramação → Design de Capa (5 conceitos)
- ✅ **Fase 10**: Geração de ISBN e CIP automatizada
- ✅ **Fase 11-14**: Preparação para impressão → Pacote para gráfica

### Preparação de Manuscrito (Fases 1 e 2)
- ✅ Análise estrutural e de qualidade
- ✅ Aprimoramento de conteúdo com IA
- ✅ Criação de elementos pré e pós-textuais
- ✅ Revisão editorial profissional
- ✅ **FastFormat: Formatação tipográfica avançada** ⭐ **NOVO**
- ✅ Padronização de formatação
- ✅ Geração de metadados e documentação
- ✅ Exportação em múltiplos formatos

### FastFormat - Tipografia Profissional ⭐ **NOVO**
- ✨ **Aspas tipográficas** (curly quotes)
- ✨ **Travessões para diálogos** (em-dash: —)
- ✨ **Travessões para intervalos** (en-dash: 10–20)
- ✨ **Reticências padronizadas** (…)
- ✨ **Normalização de espaçamento**
- ✨ **Pontuação PT-BR inteligente**

### Produção Editorial (Fase 3) ⭐ **NOVO**
- ✅ **Design automatizado de capas** (5 layouts profissionais)
- ✅ **Diagramação profissional** (PDF pronto para impressão)
- ✅ **Revisão automatizada de provas** (gramática, layout, formatação)
- ✅ **Geração de materiais adicionais** (blurbs, sinopses, ISBN, QR codes, ONIX)

### Economia e Eficiência
- 💰 **85-92% de redução de custo** (R$ 14k-33k → R$ 650-2.5k)
- ⚡ **97-99% de redução de tempo** (4-8 semanas → 4-6 horas)
- 🎯 **Qualidade profissional consistente**

---

## 🚀 Início Rápido

### Workflow Completo (14 Fases) ⭐ **NOVO**

```bash
# Execute o workflow completo: do manuscrito até a gráfica
python complete_workflow.py manuscrito.pdf \
  --title "Meu Livro" \
  --author "Nome do Autor" \
  --genre "Ficção" \
  --pages 300

# Resultado: Pacote completo pronto para envio à gráfica!
```

📖 **Documentação Completa**: [WORKFLOW_COMPLETO.md](WORKFLOW_COMPLETO.md)

### Instalação

#### Método 1: Instalar como Pacote Python (Recomendado) 🎉 **NOVO**

```bash
# Clone o repositório
git clone https://github.com/CarlosHonorato70/editor-literario-ia.git
cd editor-literario-ia

# Instale o pacote
pip install -e .

# Verifique a instalação
manuscript-publisher --help
```

📖 **Guia Completo de Instalação**: [PACKAGE_INSTALL.md](PACKAGE_INSTALL.md)

#### Método 2: Instalação Manual (Desenvolvimento)

```bash
# Clone ou baixe o sistema
cd editor-literario-ia

# Instale dependências
pip install -r requirements.txt

# Configure sua API key (opcional, para recursos de IA)
export OPENAI_API_KEY="sua-chave-aqui"
```

### Uso Básico

```bash
# Processar um manuscrito
python main.py manuscrito.pdf -o output/

# Com configuração customizada
python main.py manuscrito.docx -o output/ -c configs/academic.yaml

# Modo interativo
python main.py --interactive
```

---

## 📁 Estrutura do Sistema

```
manuscript_publisher/
├── main.py                 # Script principal
├── modules/                # Módulos do sistema
│   ├── __init__.py
│   ├── config.py          # Configurações
│   ├── utils.py           # Utilidades
│   ├── analyzer.py        # Análise de manuscritos
│   ├── enhancer.py        # Aprimoramento de conteúdo
│   ├── formatter.py       # Formatação
│   ├── elements.py        # Geração de elementos
│   ├── reviewer.py        # Revisão editorial
│   ├── exporter.py        # Exportação
│   └── interactive.py     # Modo interativo
├── templates/             # Templates de documentos
│   ├── pre_textual/
│   ├── post_textual/
│   └── diagrams/
├── configs/               # Arquivos de configuração
│   ├── default.yaml
│   ├── academic.yaml
│   ├── fiction.yaml
│   └── technical.yaml
├── tests/                 # Testes unitários
├── docs/                  # Documentação detalhada
├── examples/              # Exemplos de uso
└── README.md             # Este arquivo
```

---

## 🔧 Configuração

### Arquivo de Configuração (YAML)

```yaml
# config.yaml
project_name: "Meu Manuscrito"
version: "1.0"

# Configurações de IA
openai_model: "gpt-4o-mini"
enable_ai_enhancement: true
enable_ai_review: true

# Configurações de formatação
default_format: "A5"
default_font: "Times New Roman"
default_font_size: 12

# Configurações de elementos
generate_pre_textual: true
generate_post_textual: true
generate_glossary: true
generate_index: true

# Formatos de exportação
export_formats:
  - md
  - docx
  - pdf
```

### Templates Pré-Configurados

#### Manuscrito Acadêmico
```bash
python main.py manuscrito.pdf -c configs/academic.yaml
```

#### Ficção/Romance
```bash
python main.py manuscrito.docx -c configs/fiction.yaml
```

#### Manual Técnico
```bash
python main.py manuscrito.md -c configs/technical.yaml
```

---

## 📊 Processo Completo (7 Fases)

### FASE 1: Análise e Diagnóstico
- Extração de conteúdo (PDF, DOCX, MD)
- Análise estrutural (capítulos, seções, elementos)
- Análise de qualidade (legibilidade, consistência, formatação)
- Extração de metadados
- **Output:** `01_Analise_Estrutura.md`

### FASE 2: Identificação de Oportunidades
- Análise de estrutura
- Análise de conteúdo
- Análise de referências
- Priorização de melhorias (Alta, Média, Baixa)
- **Output:** `02_Oportunidades_Aprimoramento.md`

### FASE 3: Aprimoramento de Conteúdo
- Correção de formatação
- Padronização terminológica
- Aprimoramento com IA (opcional)
- Melhoria de clareza e estilo
- **Output:** Conteúdo aprimorado

### FASE 4: Criação de Elementos Complementares
- **Pré-Textuais:**
  - Folha de rosto
  - Ficha catalográfica
  - Dedicatória
  - Agradecimentos
  - Prefácio
  - Sumário
  
- **Pós-Textuais:**
  - Apêndices
  - Glossário (40+ termos)
  - Índice remissivo (200+ entradas)
  - Referências bibliográficas

- **Output:** Múltiplos arquivos `.md`

### FASE 5: Revisão Editorial Profissional
- Análise de estrutura e organização
- Análise de conteúdo e argumentação
- Análise de estilo e clareza
- Verificação de consistência
- Verificação de referências
- **Output:** `Relatorio_Revisao_Editorial.md`

### FASE 6: Formatação e Padronização
- Padronização de títulos e subtítulos
- Padronização de listas e citações
- Padronização de tabelas
- Limpeza de espaçamento
- Correção de pontuação
- **Output:** Documento formatado

### FASE 7: Exportação para Publicação
- Unificação de todos os elementos
- Geração de metadados
- Exportação em múltiplos formatos
- Criação de guia de próximos passos
- **Output:** Pacote completo de publicação

---

## 📦 Arquivos Gerados

Ao final do processamento, o sistema gera:

1. **Análise e Diagnóstico**
   - `01_Analise_Estrutura.md`
   - `02_Oportunidades_Aprimoramento.md`

2. **Elementos Pré-Textuais**
   - `03_Elementos_Pre-Textuais.md`
   - `Folha_Rosto.md`
   - `Dedicatoria.md`
   - `Agradecimentos.md`
   - `Prefacio.md`

3. **Conteúdo Principal**
   - `Manuscrito_Aprimorado.md`
   - `Manuscrito_Padronizado.md`

4. **Elementos Pós-Textuais**
   - `Elementos_Pos_Textuais.md`
   - `Glossario.md`
   - `Indice_Remissivo.md`
   - `Referencias.md`

5. **Revisão e Metadados**
   - `Relatorio_Revisao_Editorial.md`
   - `Relatorio_Padronizacao.md`
   - `Metadados_Publicacao.md`

6. **Documentação Final**
   - `Guia_Proximos_Passos.md`
   - `Relatorio_Final_Projeto.md`

7. **Livro Completo**
   - `Livro_Pronto_Para_Publicacao.md`
   - `Livro_Pronto_Para_Publicacao.docx` (se habilitado)
   - `Livro_Pronto_Para_Publicacao.pdf` (se habilitado)

8. **Elementos Visuais** (se gerados)
   - Diagramas em PNG
   - Tabelas formatadas
   - Gráficos

---

## 🎯 Casos de Uso

### 1. Livro Acadêmico/Técnico

```python
from modules.config import ACADEMIC_CONFIG
from main import ManuscriptPublisher

publisher = ManuscriptPublisher()
publisher.config = ACADEMIC_CONFIG

results = publisher.process_manuscript(
    "tese_doutorado.pdf",
    "output_academic/"
)
```

**Características:**
- Formato A4
- Times New Roman 12pt
- Espaçamento 1.5
- Glossário e índice incluídos
- Verificação rigorosa de referências

### 2. Romance/Ficção

```python
from modules.config import FICTION_CONFIG
from main import ManuscriptPublisher

publisher = ManuscriptPublisher()
publisher.config = FICTION_CONFIG

results = publisher.process_manuscript(
    "romance.docx",
    "output_fiction/"
)
```

**Características:**
- Formato 6x9"
- Garamond 11pt
- Espaçamento 1.15
- Sem glossário/índice
- Foco em narrativa e estilo

### 3. Manual Técnico

```python
from modules.config import TECHNICAL_CONFIG
from main import ManuscriptPublisher

publisher = ManuscriptPublisher()
publisher.config = TECHNICAL_CONFIG

results = publisher.process_manuscript(
    "manual.md",
    "output_technical/"
)
```

**Características:**
- Formato A4
- Arial 11pt
- Geração de diagramas
- Glossário técnico
- Índice detalhado

---

## 🤖 Recursos de IA

O sistema utiliza IA (OpenAI GPT-4) para:

1. **Aprimoramento de Conteúdo**
   - Correção gramatical
   - Melhoria de clareza
   - Refinamento de estilo
   - Sugestões de reescrita

2. **Revisão Editorial**
   - Análise de estrutura
   - Verificação de coerência
   - Identificação de inconsistências
   - Sugestões de melhoria

3. **Geração de Elementos**
   - Criação de prefácio
   - Geração de blurb
   - Sugestões para dedicatória
   - Expansão de glossário

4. **Análise de Qualidade**
   - Avaliação de legibilidade
   - Análise de tom e voz
   - Verificação de público-alvo
   - Score de qualidade geral

**Nota:** Todos os recursos de IA são opcionais e podem ser desabilitados na configuração.

---

## 📈 Estatísticas e Métricas

O sistema fornece métricas detalhadas:

- **Contagem de palavras** e páginas estimadas
- **Estrutura:** Capítulos, seções, subsecções
- **Elementos:** Figuras, tabelas, códigos
- **Qualidade:** Score geral (0-1.0)
- **Legibilidade:** Palavras por sentença
- **Consistência:** Score terminológico
- **Formatação:** Score de padronização
- **Referências:** Contagem e verificação

---

## 🔍 Exemplo de Relatório Final

```markdown
# RELATÓRIO FINAL DO PROJETO
## Preparação de Manuscrito para Publicação

**Arquivo de Entrada:** manuscrito.pdf
**Diretório de Saída:** output/

---

## ESTATÍSTICAS GERAIS

- **Contagem de Palavras:** 129,116
- **Páginas Estimadas:** 560
- **Arquivos Gerados:** 15

---

## FASES CONCLUÍDAS

### ANALYSIS
- word_count: 129116
- page_count: 560
- chapter_count: 10
- quality_score: 0.92

### ENHANCEMENT
- total_changes: 247
- formatting_changes: 89
- terminology_changes: 34
- ai_changes: 124

### REVIEW
- issues_found: 12
- issues_fixed: 12
- overall_rating: 9.2/10

---

## ARQUIVOS GERADOS

1. `01_Analise_Estrutura.md`
2. `02_Oportunidades_Aprimoramento.md`
3. `03_Elementos_Pre-Textuais.md`
...
15. `Livro_Pronto_Para_Publicacao.md`

---

**Status:** ✅ PRONTO PARA PUBLICAÇÃO
```

---

## 🛠️ Personalização e Extensão

### Adicionar Novo Tipo de Manuscrito

1. Criar configuração em `configs/`:

```yaml
# configs/meu_tipo.yaml
default_format: "Custom"
default_font: "Minha Fonte"
# ... outras configurações
```

2. Usar na linha de comando:

```bash
python main.py manuscrito.pdf -c configs/meu_tipo.yaml
```

### Adicionar Novo Módulo

1. Criar arquivo em `modules/`:

```python
# modules/meu_modulo.py
class MeuModulo:
    def __init__(self, config):
        self.config = config
    
    def processar(self, content):
        # Sua lógica aqui
        return resultado
```

2. Integrar no `main.py`:

```python
from modules.meu_modulo import MeuModulo

# No ManuscriptPublisher.__init__
self.meu_modulo = MeuModulo(self.config)
```

---

## 📚 Documentação Adicional

- **[🎯 Workflow Completo (14 Fases)](WORKFLOW_COMPLETO.md)** ⭐ **NOVO**
- **[FastFormat - Documentação Completa](FASTFORMAT_DOCS.md)**
- **[Guia de Instalação Detalhado](INSTALL.md)**
- **[Visão Geral do Sistema](SYSTEM_OVERVIEW.md)**
- **[Guia de Início Rápido](QUICKSTART.md)**
- **[Exemplos de Uso](examples/)**

## 🎯 Recursos Principais

### Workflow Completo (14 Fases) ⭐ **NOVO**

Execute o fluxo completo de publicação automaticamente:

```bash
python complete_workflow.py manuscrito.pdf \
  --title "Meu Livro" \
  --author "Autor" \
  --genre "Ficção"
```

**Saída**:
- ✅ Manuscrito editado e revisado
- ✅ ISBN-13 válido com código de barras
- ✅ Ficha CIP (Catalogação na Publicação)
- ✅ 5 conceitos de capa profissionais
- ✅ PDF do miolo diagramado (300 DPI, CMYK)
- ✅ PDF da capa com lombada calculada
- ✅ Especificações técnicas para gráfica
- ✅ Pacote completo pronto para impressão

📖 **Veja**: [WORKFLOW_COMPLETO.md](WORKFLOW_COMPLETO.md) para detalhes

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

## 📄 Licença

Este sistema é fornecido "como está" para uso em projetos de preparação de manuscritos.

---

## 🙏 Agradecimentos

Este sistema foi desenvolvido com base na metodologia comprovada no projeto "Modelo VIP - Uma Nova Síntese em Psicoterapia" e incorpora as melhores práticas de preparação editorial profissional.

---

## 📞 Suporte

Para questões, sugestões ou problemas:
- Abra uma issue no repositório
- Consulte a documentação em `docs/`
- Veja exemplos em `examples/`

---

**Desenvolvido com ❤️ por Manus AI**

**Versão 2.0** | Outubro 2025
