#!/bin/bash
# Script para iniciar a aplicação Streamlit
# Editor Literário IA - Sistema Completo

echo "======================================"
echo "  Editor Literário IA - Versão 2.0  "
echo "======================================"
echo ""
echo "Iniciando aplicação Streamlit..."
echo ""

# Verifica se streamlit está instalado
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit não encontrado. Instalando dependências..."
    pip install -r requirements.txt
fi

# Configuração de portas
PORT=${PORT:-8501}

echo "🚀 Iniciando servidor em http://localhost:$PORT"
echo ""
echo "Opções disponíveis:"
echo "  1. app_completo.py - Interface completa com workflow de 14 fases"
echo "  2. app_editor.py   - Editor rápido e simples"
echo ""

# Pergunta qual app rodar (padrão: app_completo.py)
APP_FILE="${1:-app_completo.py}"

if [ ! -f "$APP_FILE" ]; then
    echo "❌ Arquivo '$APP_FILE' não encontrado!"
    echo "Usando app_completo.py como padrão..."
    APP_FILE="app_completo.py"
fi

echo "📚 Iniciando: $APP_FILE"
echo ""
echo "Para parar o servidor: Ctrl+C"
echo "======================================"
echo ""

# Inicia o Streamlit
streamlit run "$APP_FILE" \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --theme.primaryColor="#1f77b4" \
    --theme.backgroundColor="#ffffff" \
    --theme.secondaryBackgroundColor="#f0f2f6" \
    --theme.textColor="#262730"
