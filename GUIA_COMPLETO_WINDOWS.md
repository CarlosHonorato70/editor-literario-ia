# Guia Completo para Windows - Editor Literário IA

## 🪟 Configuração Inicial no Windows

### Passo 1: Verificar Instalação do Python

Abra o PowerShell e teste:

```powershell
py --version
```

**Saída esperada:** `Python 3.x.x`

Se aparecer erro, [baixe o Python aqui](https://www.python.org/downloads/)

### Passo 2: Navegar até o Diretório Correto

⚠️ **IMPORTANTE:** Você precisa estar no diretório correto!

Veja o que você tem no diretório atual:
```powershell
dir
```

**Se você NÃO vir os arquivos:**
- `check_dependencies.py`
- `run.bat`
- `app_editor.py`

**Então você está no diretório errado!**

#### Opção A: Baixar os Arquivos Atualizados

1. Vá para: https://github.com/CarlosHonorato70/editor-literario-ia
2. Clique em "Code" → "Download ZIP"
3. Extraia o ZIP
4. Abra PowerShell nessa pasta

#### Opção B: Usar Git (se você tem Git instalado)

```powershell
cd "C:\Users\Carlos Honorato\OneDrive\Área de trabalho\Editor literário"
git clone https://github.com/CarlosHonorato70/editor-literario-ia.git
cd editor-literario-ia
```

### Passo 3: Instalar Dependências

⚠️ **Use `py -m pip` no Windows, não apenas `pip`**

```powershell
# Atualizar pip primeiro
py -m pip install --upgrade pip

# Instalar todas as dependências
py -m pip install -r requirements.txt
```

**Isso vai instalar:**
- streamlit
- streamlit-quill (Editor Avançado)
- E todas as outras dependências

### Passo 4: Verificar Instalação

Execute o script de diagnóstico:

```powershell
py check_dependencies.py
```

**Você deve ver:**
```
============================================================
  Diagnóstico de Dependências - Adapta ONE
============================================================

✅ streamlit                 - Framework da interface
✅ streamlit_quill           - Editor Avançado (Word-like)
✅ docx                      - Processamento de documentos DOCX
...
```

**Se aparecer ❌ (faltando):**
```powershell
py -m pip install -r requirements.txt
```

### Passo 5: Executar o Aplicativo

#### Opção 1: Usar o Script Automático (Recomendado)

Basta clicar duas vezes em:
```
run.bat
```

Ou no PowerShell:
```powershell
.\run.bat
```

#### Opção 2: Comando Manual

```powershell
py -m streamlit run app_editor.py
```

**O navegador abrirá automaticamente em:** `http://localhost:8501`

## 🔧 Solução de Problemas Comuns no Windows

### Erro: "python não é reconhecido"

**Problema:** Você está usando `python` mas deve usar `py`

**Solução:**
```powershell
# ❌ NÃO funciona no Windows
python check_dependencies.py
pip install -r requirements.txt

# ✅ USE ISTO no Windows
py check_dependencies.py
py -m pip install -r requirements.txt
```

### Erro: "pip não é reconhecido"

**Problema:** `pip` não está no PATH

**Solução:** Use `py -m pip` em vez de apenas `pip`
```powershell
# ❌ NÃO funciona
pip install -r requirements.txt

# ✅ USE ISTO
py -m pip install -r requirements.txt
```

### Erro: "streamlit não é reconhecido"

**Problema:** streamlit não foi instalado ou não está no PATH

**Solução:**
```powershell
# 1. Instalar streamlit
py -m pip install streamlit

# 2. Executar com py -m
py -m streamlit run app_editor.py
```

### Erro: "can't open file ... No such file or directory"

**Problema:** Você está no diretório errado

**Solução:**
```powershell
# Ver onde você está
pwd

# Ver o que tem na pasta
dir

# Se não vir app_editor.py, vá para o diretório certo
cd "caminho\correto\editor-literario-ia"
```

### Erro: "check_dependencies.py não encontrado"

**Problema:** O arquivo não existe no seu diretório

**Você tem duas opções:**

#### Opção 1: Baixar a versão atualizada

1. Vá para: https://github.com/CarlosHonorato70/editor-literario-ia
2. Navegue até o branch `copilot/integrate-word-interface`
3. Baixe os arquivos atualizados

#### Opção 2: Criar o arquivo manualmente

Crie um arquivo chamado `check_dependencies.py` com este conteúdo:

```python
#!/usr/bin/env python3
"""
Script de Diagnóstico - Verifica se todas as dependências estão instaladas
"""

import sys
import importlib

print("="*60)
print("  Diagnóstico de Dependências - Adapta ONE")
print("="*60)
print()

# Lista de dependências críticas
dependencies = [
    ("streamlit", "Framework da interface", True),
    ("streamlit_quill", "Editor Avançado (Word-like)", True),
    ("docx", "Processamento de documentos DOCX", True),
    ("PyPDF2", "Processamento de documentos PDF", False),
    ("openai", "Sugestões de IA (opcional)", False),
    ("language_tool_python", "Revisão gramatical", False),
]

missing_critical = []
missing_optional = []

for module_name, description, is_critical in dependencies:
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name:25} - {description}")
    except ImportError:
        print(f"❌ {module_name:25} - {description} [FALTANDO]")
        if is_critical:
            missing_critical.append(module_name)
        else:
            missing_optional.append(module_name)

print()
print("="*60)

if missing_critical:
    print("⚠️  ATENÇÃO: Dependências críticas faltando!")
    print()
    print("Para instalar:")
    print()
    print("  py -m pip install -r requirements.txt")
    print()
elif missing_optional:
    print("✅ Todas as dependências críticas estão instaladas!")
    print()
    print("Para instalar todas:")
    print("  py -m pip install -r requirements.txt")
    print()
else:
    print("✅ Todas as dependências estão instaladas!")
    print()
    print("Execute: py -m streamlit run app_editor.py")
    print()

print("="*60)
```

Salve como `check_dependencies.py` no mesmo diretório de `app_editor.py`

## 📋 Checklist Completo

Marque cada item conforme completa:

- [ ] Python instalado (testar com `py --version`)
- [ ] No diretório correto (ver `app_editor.py` com `dir`)
- [ ] Dependências instaladas (`py -m pip install -r requirements.txt`)
- [ ] Diagnóstico passou (`py check_dependencies.py`)
- [ ] App rodando (`py -m streamlit run app_editor.py` ou `.\run.bat`)
- [ ] Navegador abriu em `http://localhost:8501`

## 🚀 Início Rápido (Resumo)

Para quem já tem tudo configurado:

```powershell
# 1. Ir para o diretório
cd "C:\caminho\para\editor-literario-ia"

# 2. Instalar (primeira vez)
py -m pip install -r requirements.txt

# 3. Executar
.\run.bat

# OU
py -m streamlit run app_editor.py
```

## 📞 Ainda com Problemas?

Se ainda não funcionar, envie estas informações:

```powershell
# 1. Versão do Python
py --version

# 2. Onde você está
pwd

# 3. O que tem na pasta
dir

# 4. Diagnóstico
py check_dependencies.py
```

---

**Desenvolvido com ❤️ por Manus AI**

**Versão 2.0** | Novembro 2025
