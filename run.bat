@echo off
REM Script para iniciar o Editor Adapta ONE com interface Word-like

echo ================================================================
echo   📝 Adapta ONE - Editor Profissional com Interface Word-like
echo ================================================================
echo.

REM Check if Python is installed
py --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python não está instalado ou não está no PATH!
    echo.
    echo Por favor:
    echo 1. Baixe o Python em: https://www.python.org/downloads/
    echo 2. Durante a instalação, marque "Add Python to PATH"
    echo 3. Reinicie este script
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado
py --version
echo.

REM Check if streamlit is installed
py -m streamlit --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Streamlit não está instalado. Instalando dependências...
    echo.
    py -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ❌ Erro ao instalar dependências!
        echo.
        echo Tente manualmente:
        echo   py -m pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo ✅ Streamlit instalado
echo.
echo 🚀 Iniciando aplicativo...
echo.
echo 💡 Dicas:
echo    • O navegador abrirá automaticamente em http://localhost:8501
echo    • Para parar o servidor, pressione Ctrl+C
echo    • Use a aba '✍️ Editor Avançado' para edição com toolbar Word-like
echo.
echo ================================================================
echo.

REM Run streamlit
py -m streamlit run app_editor.py

if errorlevel 1 (
    echo.
    echo ❌ Erro ao executar o aplicativo!
    echo.
    echo Verifique:
    echo 1. Você está no diretório correto? (deve conter app_editor.py)
    echo 2. As dependências estão instaladas? Execute: py check_dependencies.py
    echo.
    echo Para mais ajuda, veja: GUIA_COMPLETO_WINDOWS.md
    echo.
    pause
)
