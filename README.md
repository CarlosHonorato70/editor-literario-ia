> Este arquivo foi regenerado para refletir a estrutura atual do repositório e focar nas instruções essenciais.

# Editor Literário IA

O **Editor Literário IA** é um sistema automatizado para a preparação de manuscritos para publicação, utilizando Inteligência Artificial para análise, aprimoramento, formatação e geração de elementos complementares.

## 🚀 Instalação e Configuração

Para executar o projeto, siga os passos abaixo. É altamente recomendado o uso de um ambiente virtual.

### 1. Clonar o Repositório

```bash
git clone https://github.com/CarlosHonorato70/editor-literario-ia
cd editor-literario-ia
```

### 2. Configurar Ambiente Virtual e Dependências

```bash
# Criar e ativar o ambiente virtual (Exemplo para Linux/macOS)
python3 -m venv venv
source venv/bin/activate

# Instalar as dependências
pip install -r requirements.txt
```

Para **Windows (PowerShell)**, o comando de ativação é:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Configurar Chave de API

O sistema requer uma chave de API do OpenAI. Defina-a como uma variável de ambiente:

```bash
# Exemplo para Linux/macOS
export OPENAI_API_KEY="SUA_CHAVE_AQUI"

# Exemplo para Windows (PowerShell)
$env:OPENAI_API_KEY="SUA_CHAVE_AQUI"
```

## ▶️ Execução

O aplicativo pode ser executado em dois modos principais:

### 1. Interface Web (Streamlit)

Este é o modo recomendado para uma experiência de usuário completa.

```bash
streamlit run app_editor.py
```

O aplicativo será aberto automaticamente no seu navegador (geralmente em `http://localhost:8501`).

### 2. Linha de Comando (CLI)

O script principal (`main.py`) permite o processamento direto de arquivos.

#### Modo Interativo

Este modo guia o usuário através de um menu de opções.

```bash
python main.py --interactive
```

#### Modo Direto

Processe um arquivo diretamente, especificando a entrada e a saída.

```bash
python main.py caminho/para/seu/manuscrito.pdf -o saida_processada/
```

Os formatos de entrada suportados incluem: `.pdf`, `.docx`, `.md`, e `.txt`.
