# PowerShell - Comandos Corretos

## 🔧 Diferenças Importantes

### Executar Múltiplos Comandos

**❌ Bash/Linux (NÃO funciona no PowerShell):**
```bash
comando1 && comando2
```

**✅ PowerShell:**
```powershell
# Opção 1: Ponto-e-vírgula
comando1; comando2

# Opção 2: Linha por linha
comando1
comando2

# Opção 3: If de sucesso
comando1
if ($?) { comando2 }
```

### Exemplo Específico para o Projeto

**❌ NÃO funciona:**
```powershell
py -m pip install -r requirements.txt && py -m streamlit run app_editor.py
```

**✅ USE:**
```powershell
# Opção 1: Dois comandos separados
py -m pip install -r requirements.txt
py -m streamlit run app_editor.py

# Opção 2: Ponto-e-vírgula
py -m pip install -r requirements.txt; py -m streamlit run app_editor.py

# Opção 3: Usar o script automático (MELHOR!)
.\quick_start.bat
```

## 🚀 Solução Rápida para Você

Baseado no diagnóstico que você rodou, **apenas `streamlit-quill` está faltando**.

### Comandos na Ordem:

```powershell
# 1. Instalar streamlit-quill (a única dependência faltando)
py -m pip install streamlit-quill

# 2. Executar o aplicativo
py -m streamlit run app_editor.py
```

### Ou use o Script Rápido:

```powershell
# Este script instala streamlit-quill e executa o app automaticamente
.\quick_start.bat
```

## 📋 Checklist do Seu Diagnóstico

Conforme o resultado do seu `py check_dependencies.py`:

- [x] ✅ streamlit - Instalado
- [ ] ❌ streamlit_quill - **FALTANDO** ← Precisa instalar!
- [x] ✅ docx - Instalado
- [x] ✅ PyPDF2 - Instalado  
- [x] ✅ openai - Instalado
- [x] ✅ language_tool_python - Instalado
- [x] ✅ PIL - Instalado
- [x] ✅ markdown - Instalado

**Conclusão:** Você só precisa instalar `streamlit-quill`!

## 🎯 Próximos Passos

```powershell
# Passo 1: Instalar a dependência faltando
py -m pip install streamlit-quill

# Passo 2: Executar o app
py -m streamlit run app_editor.py
```

**Pronto!** O navegador abrirá automaticamente em `http://localhost:8501`

## ⚠️ Avisos do WeasyPrint

O aviso que apareceu sobre WeasyPrint é normal e não impede o uso do app:

```
WeasyPrint could not import some external libraries...
```

**Isto é OK!** WeasyPrint é opcional e usado apenas para geração avançada de PDF. O Editor Avançado (Word-like) funciona perfeitamente sem ele.

## 📞 Ainda com Dúvidas?

Se depois de instalar `streamlit-quill` ainda houver problema:

```powershell
# Verificar diagnóstico novamente
py check_dependencies.py

# Reinstalar tudo (se necessário)
py -m pip install -r requirements.txt

# Executar
py -m streamlit run app_editor.py
```

---

**Dica:** Sempre que o PowerShell reclamar de `&&`, lembre-se de usar `;` ou executar linha por linha!
