@echo off
REM Quick Start - Instala streamlit-quill e executa o app

echo ================================================================
echo   🚀 Quick Start - Editor Literário IA
echo ================================================================
echo.

echo [1/2] Instalando streamlit-quill (Editor Avançado)...
py -m pip install streamlit-quill --quiet

if errorlevel 1 (
    echo ❌ Erro ao instalar streamlit-quill!
    echo.
    echo Tente:
    echo   py -m pip install streamlit-quill
    echo.
    pause
    exit /b 1
)

echo ✅ streamlit-quill instalado
echo.

echo [2/2] Iniciando aplicativo...
echo.
echo 💡 O navegador abrirá em: http://localhost:8501
echo 💡 Para parar: Pressione Ctrl+C
echo.
echo ================================================================
echo.

py -m streamlit run app_editor.py

if errorlevel 1 (
    echo.
    echo ❌ Erro ao executar!
    echo.
    echo Verifique:
    echo 1. Executou o diagnóstico: py check_dependencies.py
    echo 2. Instalou dependências: py -m pip install -r requirements.txt
    echo.
    pause
)
