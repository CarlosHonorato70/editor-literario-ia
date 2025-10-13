# 🚀 Quick Start - Editor Literário IA

Guia rápido para começar a usar o sistema em 5 minutos.

---

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- 500 MB de espaço em disco

---

## ⚡ Instalação Rápida

### 1. Clone o repositório

```bash
git clone https://github.com/CarlosHonorato70/editor-literario-ia.git
cd editor-literario-ia
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Teste o sistema

```bash
python test_system.py
```

Se todos os testes passarem, você está pronto! ✅

---

## 🎯 Uso Básico

### Preparar um Manuscrito (Fases 1 e 2)

```bash
python main.py seu_manuscrito.pdf -o output/
```

Isso vai:
- ✅ Analisar o manuscrito
- ✅ Aprimorar o conteúdo
- ✅ Criar elementos pré/pós-textuais
- ✅ Revisar editorialmente
- ✅ Padronizar formatação
- ✅ Gerar metadados

### Produzir um Livro Completo (Fase 3)

```python
from modules.production import ProductionPipeline

# Configurar
pipeline = ProductionPipeline({
    'format': 'A5',
    'genre': 'academic',
    'output_dir': './output'
})

# Processar
results = pipeline.process_book(
    manuscript_path='manuscrito.md',
    metadata={
        'title': 'Meu Livro',
        'author': 'Seu Nome',
        'isbn': '978-85-1234-567-8',
        'genre': 'academic',
        'description': 'Uma descrição fascinante...'
    }
)
```

Isso vai gerar:
- 📐 **3 conceitos de capa** profissionais
- 📄 **PDF diagramado** pronto para impressão
- 🔍 **Relatório de revisão** detalhado
- 📦 **10+ materiais** (blurbs, sinopses, ISBN, QR code, etc.)

---

## 📚 Exemplos Prontos

### Exemplo 1: Livro Acadêmico

```bash
python examples/production_example.py
```

### Exemplo 2: Apenas Diagramação

```python
from modules.production import layout_book

result = layout_book(
    content_path='manuscrito.md',
    metadata={'title': 'Meu Livro', 'author': 'Seu Nome'},
    output_path='livro.pdf',
    format='A5',
    genre='academic'
)
```

### Exemplo 3: Apenas Design de Capa

```python
from modules.production import design_cover

cover_path = design_cover(
    metadata={'title': 'Meu Livro', 'author': 'Seu Nome'},
    output_path='capa.png',
    layout='bold'
)
```

---

## 🔧 Configuração

### Usar IA (Opcional)

Para usar recursos de IA (GPT-4 para textos, DALL-E para imagens):

```bash
export OPENAI_API_KEY="sua-chave-aqui"
```

Depois, configure `use_ai=True`:

```python
pipeline = ProductionPipeline({
    'use_ai': True,
    'openai_api_key': os.getenv('OPENAI_API_KEY')
})
```

### Customizar Formato

Formatos disponíveis:
- `A4` - 210x297mm
- `A5` - 148x210mm (recomendado)
- `B5` - 176x250mm
- `US Letter` - 216x279mm
- `6x9` - 152x229mm
- `Pocket` - 110x178mm

### Customizar Gênero

Gêneros disponíveis:
- `academic` - Livros acadêmicos/científicos
- `fiction` - Romances e ficção
- `technical` - Manuais técnicos
- `poetry` - Poesia

---

## 📂 Estrutura de Saída

Após processar um livro, você terá:

```
output/
└── nome-do-livro/
    ├── cover/
    │   ├── concept_1_centered.png
    │   ├── concept_2_top_heavy.png
    │   └── concept_3_minimal.png
    ├── layout/
    │   ├── nome-do-livro.pdf
    │   └── nome-do-livro_print_ready.pdf  ← Envie para impressão
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
    └── production_report.md  ← Leia primeiro
```

---

## 💡 Dicas

### 1. Comece Simples

Primeiro teste com um manuscrito pequeno (10-20 páginas) para entender o fluxo.

### 2. Revise o Relatório

Sempre leia `production_report.md` para ver o que foi gerado e identificar problemas.

### 3. Escolha a Melhor Capa

O sistema gera 3 conceitos. Escolha o que mais combina com seu livro.

### 4. Corrija Problemas Críticos

Verifique `proof/revision_report.md` e corrija problemas marcados como CRITICAL.

### 5. Use o PDF Print-Ready

Para impressão profissional, use sempre o arquivo `*_print_ready.pdf`.

---

## 🆘 Problemas Comuns

### Erro: "Module not found"

```bash
pip install -r requirements.txt
```

### Erro: "WeasyPrint not working"

No Ubuntu/Debian:
```bash
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0
```

No macOS:
```bash
brew install pango
```

### Erro: "OpenAI API key not found"

Configure a variável de ambiente:
```bash
export OPENAI_API_KEY="sua-chave"
```

Ou passe diretamente no código:
```python
pipeline = ProductionPipeline({
    'openai_api_key': 'sua-chave-aqui'
})
```

---

## 📖 Documentação Completa

- **README principal:** `README.md`
- **Módulo de produção:** `modules/production/README.md`
- **Instalação detalhada:** `INSTALL.md`
- **Visão do sistema:** `SYSTEM_OVERVIEW.md`

---

## 🎯 Próximos Passos

1. ✅ Teste com seu manuscrito
2. ✅ Revise os resultados
3. ✅ Ajuste metadados conforme necessário
4. ✅ Escolha a melhor capa
5. ✅ Envie `*_print_ready.pdf` para impressão
6. ✅ Use materiais gerados para marketing

---

## 💬 Suporte

- **Issues:** https://github.com/CarlosHonorato70/editor-literario-ia/issues
- **Documentação:** `modules/production/README.md`
- **Exemplos:** `examples/`

---

## 🎉 Pronto!

Você está pronto para transformar manuscritos em livros profissionais!

**Tempo estimado:** 4-6 horas por livro  
**Custo estimado:** R$ 650-2.500 (vs. R$ 14k-33k manual)  
**Qualidade:** Profissional e consistente

**Boa sorte com sua publicação!** 📚✨

