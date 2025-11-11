@echo off
REM Script para iniciar o Editor Adapta ONE com interface Word-like

echo ================================================================
echo   📝 Adapta ONE - Editor Profissional com Interface Word-like
echo ================================================================
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
streamlit run app_editor.py
