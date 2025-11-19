# 🪟 Guia de Execução para Windows

## Editor Literário IA - Sistema Completo v2.0

Este guia é **específico para usuários Windows** que encontraram problemas ao executar os scripts bash.

---

## ⚠️ Problemas Comuns no Windows

### Erro: "'.' não é reconhecido como um comando interno"
**Causa:** Windows não reconhece scripts bash (`.sh`)  
**Solução:** Use o script `.bat` para Windows

### Erro: "File does not exist: app_completo.py"
**Causa:** Você está em um diretório diferente ou os arquivos não foram baixados  
**Solução:** Certifique-se de estar no diretório correto

---

## ✅ Solução Rápida para Windows

### Opção 1: Script Batch (Recomendado) ⭐

```cmd
run_app.bat
```

Ou especifique qual app executar:

```cmd
run_app.bat app_completo.py
run_app.bat app_editor.py
```

### Opção 2: Comando Direto do Streamlit

```cmd
streamlit run app_completo.py
```

### Opção 3: Com Python

```cmd
python -m streamlit run app_completo.py
```

---

## 📋 Passo a Passo Completo

### 1. Verifique se está no diretório correto

```cmd
cd "C:\Users\Carlos Honorato\OneDrive\Área de trabalho\Editor literário\editor-literario-ia"
```

### 2. Ative o ambiente virtual (se estiver usando)

```cmd
venv\Scripts\activate
```

Você verá `(venv)` no início da linha de comando.

### 3. Verifique se os arquivos existem

```cmd
dir *.py
```

Você deve ver:
- `app_completo.py` ✅
- `app_editor.py` ✅
- `main.py`
- etc.

**Se não vir esses arquivos:**

```cmd
git pull origin copilot/add-manuscript-preparation-system
```

### 4. Instale as dependências (se necessário)

```cmd
pip install -r requirements.txt
```

### 5. Execute a aplicação

**Método 1 - Script Batch:**
```cmd
run_app.bat
```

**Método 2 - Streamlit direto:**
```cmd
streamlit run app_completo.py
```

**Método 3 - Python module:**
```cmd
python -m streamlit run app_completo.py
```

### 6. Acesse no navegador

```
http://localhost:8501
```

O navegador deve abrir automaticamente. Se não abrir, copie e cole o endereço acima no seu navegador.

---

## 🔧 Solução de Problemas Específicos do Windows

### Problema: "streamlit não é reconhecido"

**Solução 1:** Certifique-se de que o ambiente virtual está ativado
```cmd
venv\Scripts\activate
```

**Solução 2:** Reinstale o Streamlit
```cmd
pip uninstall streamlit
pip install streamlit
```

**Solução 3:** Use Python -m
```cmd
python -m streamlit run app_completo.py
```

### Problema: "Porta 8501 já em uso"

**Solução:** Use outra porta
```cmd
streamlit run app_completo.py --server.port=8502
```

Ou com a variável de ambiente:
```cmd
set PORT=8502
run_app.bat
```

### Problema: "Módulo não encontrado"

**Solução:** Reinstale todas as dependências
```cmd
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Problema: "Erro ao carregar language_tool_python"

**Causa:** Falta o Java Runtime Environment  
**Solução:** Instale o Java

1. Baixe Java JRE: https://www.java.com/pt-BR/download/
2. Instale e reinicie o terminal
3. Verifique: `java -version`

### Problema: Caracteres especiais aparecem errados

**Solução:** Configure o encoding do terminal
```cmd
chcp 65001
```

Adicione isso ao início do seu `run_app.bat` se necessário.

---

## 📝 Comandos Úteis para Windows

### Verificar Python
```cmd
python --version
```

### Verificar pip
```cmd
pip --version
```

### Verificar Streamlit
```cmd
streamlit --version
```

### Listar pacotes instalados
```cmd
pip list
```

### Ver processos do Streamlit
```cmd
tasklist | findstr streamlit
```

### Matar processo do Streamlit (se travado)
```cmd
taskkill /F /IM streamlit.exe
```

---

## 🎯 Fluxo Completo para Primeira Execução

```cmd
REM 1. Navegue até o diretório
cd "C:\caminho\para\editor-literario-ia"

REM 2. Ative o ambiente virtual (se usar)
venv\Scripts\activate

REM 3. Atualize os arquivos do repositório
git pull origin copilot/add-manuscript-preparation-system

REM 4. Instale/atualize dependências
pip install -r requirements.txt

REM 5. Execute a aplicação
run_app.bat

REM Ou diretamente:
streamlit run app_completo.py
```

---

## 💡 Dicas Importantes para Windows

### 1. Use aspas em caminhos com espaços
```cmd
cd "C:\Users\Carlos Honorato\OneDrive\Área de trabalho\Editor literário\editor-literario-ia"
```

### 2. Barra invertida vs. barra normal
- Windows usa: `\` (backslash)
- Scripts bash usam: `/` (forward slash)
- No Windows cmd, use sempre `\`

### 3. Variáveis de ambiente
```cmd
REM Definir
set PORT=8502

REM Ver
echo %PORT%
```

### 4. Limpar a tela
```cmd
cls
```

### 5. Ver conteúdo de arquivo
```cmd
type requirements.txt
```

---

## 📂 Estrutura de Diretórios no Windows

```
C:\Users\Carlos Honorato\OneDrive\Área de trabalho\Editor literário\editor-literario-ia\
│
├── venv\                      # Ambiente virtual (se usar)
│   └── Scripts\
│       ├── activate.bat       # Ativar ambiente
│       └── streamlit.exe      # Executável do Streamlit
│
├── app_completo.py            # ✅ App principal
├── app_editor.py              # ✅ Editor simples
├── run_app.bat                # ✅ Script Windows
├── run_app.sh                 # Script bash (não funciona no Windows)
├── requirements.txt           # Dependências
└── modules\                   # Módulos do sistema
```

---

## 🚀 Execução Rápida (Copie e Cole)

### Para usuários com ambiente virtual:

```cmd
cd "C:\Users\Carlos Honorato\OneDrive\Área de trabalho\Editor literário\editor-literario-ia"
venv\Scripts\activate
run_app.bat
```

### Para usuários sem ambiente virtual:

```cmd
cd "C:\Users\Carlos Honorato\OneDrive\Área de trabalho\Editor literário\editor-literario-ia"
streamlit run app_completo.py
```

---

## ⚡ Atalhos do Windows

### Criar um atalho na área de trabalho:

1. Clique com botão direito na área de trabalho
2. Novo → Atalho
3. Digite o caminho:
   ```
   cmd /k "cd /d C:\Users\Carlos Honorato\OneDrive\Área de trabalho\Editor literário\editor-literario-ia && venv\Scripts\activate && run_app.bat"
   ```
4. Nomeie: "Editor Literário IA"
5. Clique duas vezes no atalho para iniciar

### Criar um arquivo .bat na área de trabalho:

Crie `Iniciar_Editor.bat` com:

```batch
@echo off
cd /d "C:\Users\Carlos Honorato\OneDrive\Área de trabalho\Editor literário\editor-literario-ia"
call venv\Scripts\activate
call run_app.bat
pause
```

---

## 📊 Comandos de Diagnóstico

Se algo não funcionar, execute estes comandos e envie a saída:

```cmd
REM Versões
python --version
pip --version
streamlit --version

REM Diretório atual
cd

REM Arquivos presentes
dir *.py

REM Pacotes instalados
pip list | findstr streamlit

REM Status do Git
git status
git branch

REM Testar imports
python -c "import streamlit; print('Streamlit OK')"
python -c "from modules.fastformat_utils import apply_fastformat; print('Modules OK')"
```

---

## 🆘 Ainda com Problemas?

### Opção 1: Reset Completo

```cmd
REM 1. Desative e remova o ambiente virtual
deactivate
rmdir /s /q venv

REM 2. Crie novo ambiente
python -m venv venv

REM 3. Ative
venv\Scripts\activate

REM 4. Instale tudo
pip install --upgrade pip
pip install -r requirements.txt

REM 5. Execute
run_app.bat
```

### Opção 2: Use o editor simples primeiro

```cmd
streamlit run app_editor.py
```

Se o `app_editor.py` funcionar, o `app_completo.py` também funcionará.

### Opção 3: Python direto

```cmd
python -c "import streamlit.web.cli as stcli; import sys; sys.argv = ['streamlit', 'run', 'app_completo.py']; stcli.main()"
```

---

## 📞 Informações de Suporte

**Sistema:** Editor Literário IA v2.0  
**Plataforma:** Windows 10/11  
**Python:** 3.8 ou superior  
**Status:** ✅ Testado e funcional

---

## ✅ Checklist de Validação

Antes de pedir ajuda, verifique:

- [ ] Estou no diretório correto? (`cd` mostra o caminho certo)
- [ ] Os arquivos existem? (`dir *.py` mostra app_completo.py)
- [ ] Python funciona? (`python --version` mostra 3.8+)
- [ ] Pip funciona? (`pip --version`)
- [ ] Ambiente virtual ativado? (vejo `(venv)` no prompt)
- [ ] Dependências instaladas? (`pip list | findstr streamlit`)
- [ ] Java instalado? (`java -version`) - se usar corretor gramatical
- [ ] Usei o comando correto? (`run_app.bat` ou `streamlit run app_completo.py`)

---

## 🎉 Sucesso!

Se você conseguiu executar, verá:

```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Abra:** http://localhost:8501

---

## 📚 Documentação Adicional

- **INICIO_RAPIDO.md** - Guia geral de uso
- **COMO_EXECUTAR_STREAMLIT.md** - Detalhes técnicos
- **README.md** - Visão geral do sistema

---

**🪟 Guia específico para Windows**  
*Desenvolvido com ❤️ por Manus AI - Novembro 2025*
