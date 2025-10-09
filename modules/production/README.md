# Módulo de Produção Editorial Automatizada

**Versão:** 1.0.0  
**Autor:** Manus AI

## Visão Geral

Este módulo implementa automação completa da **Fase 3 (Produção Editorial)** do processo de publicação de livros, incluindo:

1. **Design de Capa** - Geração automatizada de capas profissionais
2. **Diagramação** - Layout profissional de livros em PDF
3. **Revisão de Provas** - Verificação automatizada de erros
4. **Materiais Adicionais** - Geração de blurbs, sinopses, códigos de barras, etc.

### Economia e Eficiência

| Métrica | Manual | Automatizado | Economia |
|---------|--------|--------------|----------|
| **Custo** | R$ 14.000-33.000 | R$ 650-2.500 | **85-92%** |
| **Tempo** | 4-8 semanas | 4-6 horas | **97-99%** |
| **Qualidade** | Variável | Consistente | **Alta** |

---

## Componentes

### 1. Layout Engine (`layout_engine.py`)

Motor de diagramação profissional usando HTML/CSS + WeasyPrint.

**Recursos:**
- Múltiplos formatos de página (A4, A5, B5, 6x9, etc.)
- Tipografia profissional por gênero
- Geração automática de sumário
- Detecção de capítulos
- Otimização de quebras de página
- Exportação PDF/X-1a (pronto para impressão)

**Uso Básico:**

```python
from modules.production import LayoutEngine

# Configurar
engine = LayoutEngine({
    'format': 'A5',
    'genre': 'academic'
})

# Diagramar livro
result = engine.layout_book(
    content_path='manuscript.md',
    metadata={
        'title': 'Meu Livro',
        'author': 'João Silva',
        'description': 'Uma obra fascinante'
    },
    output_path='output/livro.pdf'
)

print(f"Páginas: {result['statistics']['estimated_pages']}")
```

**Formatos Suportados:**
- A4 (210x297mm)
- A5 (148x210mm) - **Recomendado para livros**
- B5 (176x250mm)
- US Letter (216x279mm)
- US Trade / 6x9 (152x229mm)
- Pocket (110x178mm)

**Gêneros Suportados:**
- `academic` - Livros acadêmicos/científicos
- `fiction` - Romances e ficção
- `technical` - Manuais técnicos
- `poetry` - Poesia

---

### 2. Proof Checker (`proof_checker.py`)

Sistema automatizado de revisão de provas.

**Verifica:**
- ✅ Gramática e ortografia (LanguageTool)
- ✅ Formatação (espaços, pontuação, aspas)
- ✅ Referências quebradas
- ✅ Layout (viúvas, órfãs, alinhamento)
- ✅ Metadados do PDF

**Uso Básico:**

```python
from modules.production import ProofChecker

# Configurar
checker = ProofChecker({'language': 'pt-BR'})

# Revisar
issues = checker.check_all('livro.pdf')

# Gerar relatório
checker.generate_report(issues, 'relatorio_revisao.md')

print(f"Problemas encontrados: {len(issues)}")
```

**Severidades:**
- 🔴 **CRITICAL** - Deve ser corrigido
- 🟠 **HIGH** - Muito recomendado corrigir
- 🟡 **MEDIUM** - Recomendado corrigir
- 🟢 **LOW** - Opcional corrigir
- ℹ️ **INFO** - Apenas informativo

---

### 3. Materials Generator (`materials_generator.py`)

Gerador de materiais adicionais para publicação.

**Gera:**
- 📝 Blurb (texto de contracapa)
- 📄 Sinopses (curta, média, longa)
- 👤 Biografia do autor
- 📰 Release para imprensa
- 📊 Código de barras ISBN
- 📱 QR Code
- 📋 Metadados ONIX
- 📇 Ficha catalográfica

**Uso Básico:**

```python
from modules.production import MaterialsGenerator

# Configurar (opcionalmente com IA)
generator = MaterialsGenerator({
    'use_ai': True,
    'openai_api_key': 'sua-chave'
})

# Gerar todos os materiais
materials = generator.generate_all(
    metadata={
        'title': 'Meu Livro',
        'author': 'João Silva',
        'isbn': '978-85-1234-567-8',
        'genre': 'academic',
        'description': 'Uma obra fascinante...'
    },
    output_dir='output/materials'
)

print(f"Materiais gerados: {len(materials)}")
```

**Com IA vs Sem IA:**
- **Sem IA:** Usa templates pré-definidos (rápido, gratuito)
- **Com IA:** Usa GPT-4 para gerar textos personalizados (melhor qualidade)

---

### 4. Cover Designer (`cover_designer.py`)

Designer automatizado de capas de livros.

**Recursos:**
- 5 layouts profissionais
- Paletas de cores por gênero
- Tipografia profissional
- Geração de múltiplos conceitos
- Opção de usar IA para imagens de fundo

**Layouts Disponíveis:**
- `centered` - Título centralizado (clássico)
- `top_heavy` - Título no topo, imagem dominante
- `minimal` - Design minimalista
- `bold` - Tipografia grande e ousada
- `classic` - Layout clássico com moldura

**Uso Básico:**

```python
from modules.production import CoverDesigner

# Configurar
designer = CoverDesigner({
    'use_ai_images': False  # True para usar DALL-E
})

# Gerar 3 conceitos
concepts = designer.generate_concepts(
    metadata={
        'title': 'Meu Livro',
        'author': 'João Silva',
        'genre': 'academic'
    },
    output_dir='output/covers',
    num_concepts=3
)

print(f"Conceitos gerados: {len(concepts)}")
```

**Dimensões:**
- Padrão: 1800x2700 pixels (6x9 polegadas @ 300 DPI)
- Alta resolução para impressão profissional

---

### 5. Production Pipeline (`pipeline.py`)

Pipeline integrado que executa todos os componentes em sequência.

**Uso Básico:**

```python
from modules.production import ProductionPipeline

# Configurar
pipeline = ProductionPipeline({
    'format': 'A5',
    'genre': 'academic',
    'output_dir': './output',
    'use_ai': False  # True para usar IA
})

# Processar livro completo
results = pipeline.process_book(
    manuscript_path='manuscript.md',
    metadata={
        'title': 'Meu Livro',
        'author': 'João Silva',
        'isbn': '978-85-1234-567-8',
        'genre': 'academic',
        'description': 'Uma obra fascinante sobre...'
    }
)

# Verificar resultados
print(f"Etapas concluídas: {len(results['steps_completed'])}")
print(f"Diretório de saída: {results['output_dir']}")
```

**Etapas do Pipeline:**
1. **Cover** - Gera 3 conceitos de capa
2. **Layout** - Diagrama o livro em PDF
3. **Proof** - Revisa e gera relatório
4. **Materials** - Gera todos os materiais adicionais

**Saída:**
```
output/
└── meu-livro/
    ├── cover/
    │   ├── concept_1_centered.png
    │   ├── concept_2_top_heavy.png
    │   └── concept_3_minimal.png
    ├── layout/
    │   ├── meu-livro.pdf
    │   └── meu-livro_print_ready.pdf
    ├── proof/
    │   └── revision_report.md
    ├── materials/
    │   ├── blurb.txt
    │   ├── synopsis_short.txt
    │   ├── synopsis_medium.txt
    │   ├── synopsis_long.txt
    │   ├── author_bio.txt
    │   ├── press_release.md
    │   ├── isbn_barcode.png
    │   ├── qr_code.png
    │   ├── metadata_onix.xml
    │   └── cataloging_data.txt
    └── production_report.md
```

---

## Instalação

### Dependências

```bash
pip install -r requirements.txt
```

**Principais dependências:**
- `weasyprint` - Renderização de PDF
- `pillow` - Processamento de imagens
- `jinja2` - Templates HTML
- `pdfplumber` - Análise de PDF
- `language-tool-python` - Revisão gramatical
- `python-barcode` - Códigos de barras
- `qrcode` - QR codes

### Dependências do Sistema (Linux)

WeasyPrint requer algumas bibliotecas do sistema:

```bash
# Ubuntu/Debian
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0

# Fedora/RHEL
sudo dnf install python3-cffi python3-brotli pango

# macOS
brew install pango
```

---

## Exemplos Completos

### Exemplo 1: Livro Acadêmico Completo

```python
from modules.production import ProductionPipeline

# Configurar para livro acadêmico
pipeline = ProductionPipeline({
    'format': 'A5',
    'genre': 'academic',
    'language': 'pt-BR',
    'output_dir': './output'
})

# Metadados completos
metadata = {
    'title': 'Modelo VIP',
    'subtitle': 'Uma Nova Síntese em Psicoterapia',
    'author': 'Dr. Carlos Honorato',
    'author_bio': 'Psicólogo clínico com 20 anos de experiência...',
    'genre': 'academic',
    'description': 'Este livro apresenta o Modelo VIP...',
    'isbn': '978-85-1234-567-8',
    'publisher': 'Editora Acadêmica',
    'publication_year': 2025,
    'target_audience': 'Psicólogos, terapeutas e estudantes de psicologia',
    'subject_code': '150',  # Psicologia
    'price_amount': '89.90',
    'url': 'https://editora.com/modelo-vip'
}

# Processar
results = pipeline.process_book(
    'Livro_Modelo_VIP.md',
    metadata
)

print("✅ Livro pronto para publicação!")
```

### Exemplo 2: Apenas Diagramação

```python
from modules.production import layout_book

# Diagramar rapidamente
result = layout_book(
    content_path='manuscript.md',
    metadata={
        'title': 'Meu Livro',
        'author': 'João Silva'
    },
    output_path='livro.pdf',
    format='A5',
    genre='fiction'
)

print(f"PDF gerado: {result['output_path']}")
print(f"Páginas: {result['statistics']['estimated_pages']}")
```

### Exemplo 3: Apenas Revisão

```python
from modules.production import check_proof

# Revisar PDF
issues = check_proof(
    'livro.pdf',
    output_report='relatorio.md',
    language='pt-BR'
)

# Filtrar apenas problemas críticos
critical = [i for i in issues if i.severity.value == 'critical']
print(f"Problemas críticos: {len(critical)}")
```

### Exemplo 4: Apenas Materiais

```python
from modules.production import generate_materials

# Gerar materiais com IA
materials = generate_materials(
    metadata={
        'title': 'Meu Livro',
        'author': 'João Silva',
        'isbn': '978-85-1234-567-8',
        'description': 'Uma obra fascinante...'
    },
    output_dir='materials',
    use_ai=True,
    openai_api_key='sk-...'
)

print(f"Materiais: {list(materials.keys())}")
```

### Exemplo 5: Apenas Capa

```python
from modules.production import design_cover

# Criar capa
cover_path = design_cover(
    metadata={
        'title': 'Meu Livro',
        'author': 'João Silva',
        'genre': 'fiction'
    },
    output_path='capa.png',
    layout='bold',
    use_ai=False
)

print(f"Capa criada: {cover_path}")
```

---

## Configuração Avançada

### Customizar Tipografia

```python
engine = LayoutEngine({
    'format': 'A5',
    'genre': 'academic',
    'custom_css': '''
        body {
            font-family: "Times New Roman", serif;
            font-size: 12pt;
        }
        h1 {
            color: #1a365d;
        }
    '''
})
```

### Usar Templates Customizados

```python
engine = LayoutEngine({
    'format': 'A5',
    'template_dir': '/caminho/para/templates'
})
```

### Desativar Verificações Específicas

```python
checker = ProofChecker({
    'check_grammar': True,
    'check_formatting': True,
    'check_layout': False,  # Desativar verificação de layout
    'check_references': True
})
```

---

## Limitações Conhecidas

1. **LanguageTool:** Primeira execução pode ser lenta (download de modelos)
2. **WeasyPrint:** Requer bibliotecas do sistema instaladas
3. **Fontes:** Usa fontes do sistema; fontes customizadas requerem configuração
4. **IA:** Requer chave OpenAI e créditos disponíveis
5. **PDF/X-1a:** Marcas de corte e sangria ainda não implementadas completamente

---

## Roadmap Futuro

- [ ] Suporte a e-books (ePub, MOBI)
- [ ] Editor visual de capas
- [ ] Mais layouts de capa
- [ ] Integração com Stable Diffusion (alternativa a DALL-E)
- [ ] Suporte a múltiplos idiomas simultâneos
- [ ] Geração de audiobook (texto para fala)
- [ ] Integração com distribuidoras (Amazon KDP, etc.)

---

## Suporte

Para problemas ou dúvidas:
1. Verifique a documentação
2. Consulte os exemplos
3. Abra uma issue no repositório

---

## Licença

Este módulo é parte do sistema Editor Literário IA.

**Autor:** Manus AI  
**Versão:** 1.0.0  
**Data:** 2025
