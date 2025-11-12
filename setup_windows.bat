@echo off
REM Script de Configuração Inicial - Windows

echo ================================================================
echo   🔧 Configuração Inicial - Editor Literário IA
echo ================================================================
echo.

REM Check Python
echo [1/4] Verificando Python...
py --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo.
    echo Por favor:
    echo 1. Baixe em: https://www.python.org/downloads/
    echo 2. Durante instalação, marque "Add Python to PATH"
    echo 3. Reinicie este script
    echo.
    pause
    exit /b 1
)

py --version
echo ✅ Python instalado
echo.

REM Upgrade pip
echo [2/4] Atualizando pip...
py -m pip install --upgrade pip --quiet
echo ✅ pip atualizado
echo.

REM Install dependencies
echo [3/4] Instalando dependências...
echo     Isso pode levar alguns minutos...
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

echo.
echo ✅ Dependências instaladas
echo.

REM Run diagnostic
echo [4/4] Verificando instalação...
echo.
py check_dependencies.py

echo.
echo ================================================================
echo   ✅ CONFIGURAÇÃO COMPLETA!
echo ================================================================
echo.
echo Para iniciar o aplicativo:
echo   1. Clique duas vezes em "run.bat"
echo   OU
echo   2. Execute: py -m streamlit run app_editor.py
echo.
echo O navegador abrirá em: http://localhost:8501
echo.
echo 📚 Para mais informações:
echo    - GUIA_COMPLETO_WINDOWS.md
echo    - COMO_USAR.md
echo.
pause
