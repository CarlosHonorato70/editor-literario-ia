# Guia de Instalação - Manuscript Publisher

## Requisitos do Sistema

### Sistema Operacional
- Linux (Ubuntu 20.04+, Debian 10+)
- macOS (10.14+)
- Windows (10+)

### Python
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Espaço em Disco
- Mínimo: 500 MB
- Recomendado: 2 GB (para cache e arquivos temporários)

---

## Instalação Rápida

### 1. Clone ou Baixe o Sistema

```bash
# Se você tem o sistema em um repositório Git
git clone https://github.com/seu-usuario/manuscript-publisher.git
cd manuscript-publisher

# OU baixe e extraia o arquivo ZIP
unzip manuscript-publisher.zip
cd manuscript-publisher
```

### 2. Crie um Ambiente Virtual (Recomendado)

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure a API Key (Opcional, para recursos de IA)

```bash
# Linux/macOS
export OPENAI_API_KEY="sua-chave-aqui"

# Windows
set OPENAI_API_KEY=sua-chave-aqui
```

### 5. Teste a Instalação

```bash
python main.py --help
```

Se você ver a ajuda do sistema, a instalação foi bem-sucedida!

---

## Instalação Detalhada

### Passo 1: Verificar Python

```bash
python3 --version
```

Deve mostrar Python 3.8 ou superior. Se não tiver Python instalado:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS (com Homebrew):**
```bash
brew install python3
```

**Windows:**
Baixe e instale de https://www.python.org/downloads/

### Passo 2: Instalar Dependências do Sistema

Algumas bibliotecas Python requerem dependências do sistema.

**Ubuntu/Debian:**
```bash
sudo apt install -y \
    python3-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info
```

**macOS:**
```bash
brew install cairo pango gdk-pixbuf libffi
```

**Windows:**
Não são necessárias dependências adicionais se usar pip.

### Passo 3: Criar Ambiente Virtual

```bash
python3 -m venv venv
```

Ativar o ambiente virtual:

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

Você verá `(venv)` no início do prompt quando ativado.

### Passo 4: Instalar Dependências Python

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
```

Se houver erros:

**Erro com weasyprint:**
```bash
# Instale sem weasyprint (exportação PDF será desabilitada)
pip install -r requirements.txt --no-deps
pip install pyyaml PyPDF2 python-docx markdown openai tiktoken tqdm colorama
```

**Erro com python-docx:**
```bash
pip install --upgrade setuptools wheel
pip install python-docx
```

### Passo 5: Configurar API Key (para recursos de IA)

#### Opção A: Variável de Ambiente

**Linux/macOS (temporário):**
```bash
export OPENAI_API_KEY="sua-chave-aqui"
```

**Linux/macOS (permanente):**
```bash
echo 'export OPENAI_API_KEY="sua-chave-aqui"' >> ~/.bashrc
source ~/.bashrc
```

**Windows (temporário):**
```bash
set OPENAI_API_KEY=sua-chave-aqui
```

**Windows (permanente):**
1. Painel de Controle → Sistema → Configurações Avançadas
2. Variáveis de Ambiente
3. Nova variável de sistema: `OPENAI_API_KEY` = `sua-chave-aqui`

#### Opção B: Arquivo de Configuração

Edite `configs/default.yaml`:

```yaml
openai_api_key: "sua-chave-aqui"
```

⚠️ **Aviso:** Não compartilhe este arquivo se contiver sua chave API!

### Passo 6: Testar Instalação

```bash
# Teste básico
python main.py --help

# Teste com arquivo de exemplo (se disponível)
python main.py examples/sample.pdf -o output_test/
```

---

## Instalação de Recursos Opcionais

### Exportação para PDF

#### Método 1: WeasyPrint (Linux/macOS)

```bash
pip install weasyprint
```

#### Método 2: ReportLab (Multiplataforma)

```bash
pip install reportlab
```

#### Método 3: docx2pdf (Windows)

```bash
pip install docx2pdf
```

### Geração de Diagramas

```bash
# Instale Graphviz (sistema)
# Ubuntu/Debian
sudo apt install graphviz

# macOS
brew install graphviz

# Windows
# Baixe de https://graphviz.org/download/

# Instale biblioteca Python
pip install graphviz
```

### Análise Avançada de Texto

```bash
pip install textstat spacy
python -m spacy download pt_core_news_sm
```

---

## Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'modules'"

**Causa:** Executando de diretório errado.

**Solução:**
```bash
cd manuscript-publisher
python main.py --help
```

### Erro: "ImportError: cannot import name 'Config'"

**Causa:** Dependências não instaladas.

**Solução:**
```bash
pip install -r requirements.txt
```

### Erro: "Permission denied"

**Causa:** Arquivo main.py não é executável.

**Solução:**
```bash
chmod +x main.py
```

### Erro: "OpenAI API key not found"

**Causa:** API key não configurada (apenas afeta recursos de IA).

**Solução:**
```bash
export OPENAI_API_KEY="sua-chave-aqui"
```

OU desabilite IA em `configs/default.yaml`:
```yaml
enable_ai_enhancement: false
enable_ai_review: false
```

### Erro ao exportar PDF

**Causa:** Dependências de PDF não instaladas.

**Solução:**
```bash
pip install weasyprint
# OU
pip install reportlab
```

Se persistir, desabilite exportação PDF em `configs/default.yaml`:
```yaml
export_formats:
  - md
  - docx
  # - pdf
```

---

## Verificação da Instalação

Execute este script para verificar todos os componentes:

```bash
python -c "
import sys
print(f'Python: {sys.version}')

try:
    import yaml
    print('✓ PyYAML instalado')
except:
    print('✗ PyYAML não encontrado')

try:
    import PyPDF2
    print('✓ PyPDF2 instalado')
except:
    print('✗ PyPDF2 não encontrado')

try:
    import docx
    print('✓ python-docx instalado')
except:
    print('✗ python-docx não encontrado')

try:
    import openai
    print('✓ OpenAI instalado')
except:
    print('✗ OpenAI não encontrado')

try:
    import weasyprint
    print('✓ WeasyPrint instalado (PDF)')
except:
    print('⚠ WeasyPrint não encontrado (exportação PDF desabilitada)')

print('\nInstalação verificada!')
"
```

---

## Desinstalação

```bash
# Desativar ambiente virtual
deactivate

# Remover ambiente virtual
rm -rf venv

# Remover sistema (se desejar)
cd ..
rm -rf manuscript-publisher
```

---

## Próximos Passos

Após instalação bem-sucedida:

1. **Leia o README.md** para entender o sistema
2. **Explore os exemplos** em `examples/`
3. **Teste com um manuscrito** simples
4. **Configure** conforme suas necessidades

---

## Suporte

Se encontrar problemas:

1. Verifique a seção de Solução de Problemas acima
2. Consulte a documentação em `docs/`
3. Abra uma issue no repositório GitHub
4. Entre em contato com o suporte

---

**Desenvolvido por Manus AI** | Versão 2.0 | Outubro 2025
