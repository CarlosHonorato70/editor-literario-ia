@echo off
REM Script para iniciar a aplicação Streamlit no Windows
REM Editor Literário IA - Sistema Completo

echo ======================================
echo   Editor Literário IA - Versão 2.0
echo ======================================
echo.
echo Iniciando aplicação Streamlit...
echo.

REM Verifica se streamlit está instalado
where streamlit >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Streamlit não encontrado. Instalando dependências...
    pip install -r requirements.txt
)

REM Configuração de portas
if "%PORT%"=="" set PORT=8501

echo [*] Iniciando servidor em http://localhost:%PORT%
echo.
echo Opções disponíveis:
echo   1. app_completo.py - Interface completa com workflow de 14 fases
echo   2. app_editor.py   - Editor rápido e simples
echo.

REM Define qual app rodar (padrão: app_completo.py)
set APP_FILE=%1
if "%APP_FILE%"=="" set APP_FILE=app_completo.py

if not exist "%APP_FILE%" (
    echo [!] Arquivo '%APP_FILE%' não encontrado!
    echo [*] Usando app_completo.py como padrão...
    set APP_FILE=app_completo.py
)

echo [*] Iniciando: %APP_FILE%
echo.
echo Para parar o servidor: Ctrl+C
echo ======================================
echo.

REM Inicia o Streamlit
streamlit run "%APP_FILE%" ^
    --server.port=%PORT% ^
    --server.address=0.0.0.0 ^
    --server.headless=true ^
    --browser.gatherUsageStats=false ^
    --theme.primaryColor="#1f77b4" ^
    --theme.backgroundColor="#ffffff" ^
    --theme.secondaryBackgroundColor="#f0f2f6" ^
    --theme.textColor="#262730"
