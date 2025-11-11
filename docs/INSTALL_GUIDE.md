# Guia de Instalação

## Requisitos do Sistema

### Requisitos Mínimos
- **Python**: 3.8 ou superior
- **RAM**: 4GB
- **Espaço em Disco**: 1GB
- **Sistema Operacional**: Windows, Linux, macOS

### Requisitos Recomendados
- **Python**: 3.10 ou superior
- **RAM**: 8GB ou mais
- **Espaço em Disco**: 2GB ou mais
- **Conexão Internet**: Para recursos de IA (opcional)

## Instalação

### 1. Instalar Python

#### Windows
```bash
# Baixe o instalador em python.org
# Execute e marque "Add Python to PATH"
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip
```

#### macOS
```bash
# Instale Homebrew primeiro (brew.sh)
brew install python3
```

### 2. Clonar o Repositório

```bash
git clone <repository-url>
cd editor-literario-ia
```

### 3. Criar Ambiente Virtual (Recomendado)

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 4. Instalar Dependências

```bash
# Instalar todas as dependências
pip install -r requirements.txt
```

#### Dependências Principais
- **streamlit**: Interface web
- **python-docx**: Processamento de DOCX
- **PyPDF2**: Processamento de PDF
- **pyyaml**: Arquivos de configuração
- **openai**: IA (opcional)
- **language-tool-python**: Gramática e ortografia
- **Pillow**: Processamento de imagens
- **WeasyPrint**: Geração de PDF profissional
- **python-barcode**: Códigos de barras (ISBN)
- **qrcode**: QR codes
- **reportlab**: PDFs avançados

### 5. Configurar API de IA (Opcional)

Se deseja usar recursos de IA:

```bash
# Linux/macOS
export OPENAI_API_KEY="sua-chave-aqui"

# Windows
set OPENAI_API_KEY=sua-chave-aqui

# Ou crie um arquivo .env
echo "OPENAI_API_KEY=sua-chave-aqui" > .env
```

Para obter uma chave:
1. Acesse https://platform.openai.com/
2. Crie uma conta ou faça login
3. Vá em API Keys
4. Crie uma nova chave

### 6. Verificar Instalação

```bash
# Testar instalação
python main.py --help

# Deve mostrar a ajuda do sistema
```

## Dependências Adicionais

### WeasyPrint (Linux)

WeasyPrint requer bibliotecas adicionais no Linux:

```bash
# Ubuntu/Debian
sudo apt install python3-dev python3-pip python3-setuptools python3-wheel \
  python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# Fedora
sudo dnf install python3-devel python3-pip python3-setuptools python3-wheel \
  cairo pango gdk-pixbuf2
```

### LanguageTool

Para correção gramatical offline:

```bash
# Instalar Java (requerido)
sudo apt install default-jre  # Linux
brew install java  # macOS

# O LanguageTool será baixado automaticamente no primeiro uso
```

## Resolução de Problemas

### Erro: "pip: command not found"
```bash
# Linux/macOS
python3 -m ensurepip --default-pip

# Windows
python -m ensurepip --default-pip
```

### Erro: "WeasyPrint não funciona"
```bash
# Instale dependências do sistema (veja seção acima)
# Depois reinstale
pip uninstall weasyprint
pip install weasyprint
```

### Erro: "ModuleNotFoundError"
```bash
# Reinstale dependências
pip install -r requirements.txt --upgrade
```

### Erro: "Permission denied"
```bash
# Use --user
pip install -r requirements.txt --user

# Ou use ambiente virtual (recomendado)
```

## Instalação em Ambientes Específicos

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

```bash
# Build
docker build -t editor-literario .

# Run
docker run -v $(pwd)/output:/app/output editor-literario
```

### Google Colab

```python
# Em uma célula do Colab
!git clone <repository-url>
%cd editor-literario-ia
!pip install -r requirements.txt
```

### Servidor Linux sem GUI

```bash
# Instalar dependências sem GUI
pip install -r requirements.txt

# Desabilitar interface gráfica em configs
# Edite configs/default.yaml:
# enable_gui: false
```

## Atualização

### Atualizar Sistema

```bash
# Atualizar código
git pull origin main

# Atualizar dependências
pip install -r requirements.txt --upgrade
```

### Atualizar Apenas Dependências

```bash
pip install -r requirements.txt --upgrade
```

## Desinstalação

```bash
# Se usando ambiente virtual
deactivate
cd ..
rm -rf editor-literario-ia/

# Se instalado globalmente
pip uninstall -r requirements.txt -y
```

## Próximos Passos

Após a instalação:

1. Leia o [Guia do Usuário](USER_GUIDE.md)
2. Veja [Exemplos de Uso](../examples/)
3. Experimente o [Quickstart](../QUICKSTART.md)
4. Configure seu [arquivo de config](../configs/)

## Suporte

Se encontrar problemas:
- Verifique [FAQ](FAQ.md)
- Abra uma issue no GitHub
- Consulte a documentação completa
