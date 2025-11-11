@echo off
REM Script de Diagnóstico - Editor Literário IA
REM Este script verifica se tudo está correto no seu ambiente

echo ==========================================
echo   DIAGNOSTICO - Editor Literario IA
echo ==========================================
echo.

echo [1] Verificando diretorio atual...
cd
echo.

echo [2] Verificando branch do Git...
git branch
echo.

echo [3] Verificando status do Git...
git status
echo.

echo [4] Listando arquivos Python (.py)...
dir /b *.py 2>nul
if errorlevel 1 (
    echo [!] ERRO: Nenhum arquivo .py encontrado!
    echo [*] Voce pode nao estar no diretorio correto.
) else (
    echo [OK] Arquivos Python encontrados!
)
echo.

echo [5] Procurando app_completo.py...
if exist app_completo.py (
    echo [OK] app_completo.py EXISTE
    dir app_completo.py
) else (
    echo [!] ERRO: app_completo.py NAO EXISTE
    echo [*] Voce precisa fazer git pull!
)
echo.

echo [6] Procurando run_app.bat...
if exist run_app.bat (
    echo [OK] run_app.bat EXISTE
    dir run_app.bat
) else (
    echo [!] ERRO: run_app.bat NAO EXISTE
    echo [*] Voce precisa fazer git pull!
)
echo.

echo [7] Verificando Python...
python --version 2>nul
if errorlevel 1 (
    echo [!] Python nao encontrado no PATH
) else (
    echo [OK] Python encontrado!
)
echo.

echo [8] Verificando Streamlit...
python -c "import streamlit; print('[OK] Streamlit versao:', streamlit.__version__)" 2>nul
if errorlevel 1 (
    echo [!] Streamlit nao instalado
    echo [*] Execute: pip install streamlit
)
echo.

echo ==========================================
echo   RESUMO DO DIAGNOSTICO
echo ==========================================
echo.

if exist app_completo.py (
    if exist run_app.bat (
        echo [OK] Todos os arquivos necessarios estao presentes!
        echo.
        echo Para executar, use:
        echo   run_app.bat
        echo.
        echo Ou:
        echo   streamlit run app_completo.py
    ) else (
        echo [!] FALTAM ARQUIVOS!
        echo.
        echo SOLUCAO:
        echo   git pull origin copilot/add-manuscript-preparation-system
    )
) else (
    echo [!] FALTAM ARQUIVOS!
    echo.
    echo SOLUCAO:
    echo   git pull origin copilot/add-manuscript-preparation-system
)

echo.
echo ==========================================
pause
