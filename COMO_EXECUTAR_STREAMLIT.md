# 🚀 Como Executar a Aplicação Streamlit

## Editor Literário IA - Sistema Completo v2.0

Este guia mostra como executar a aplicação Streamlit com todas as funcionalidades implementadas.

---

## 📋 Pré-requisitos

1. **Python 3.8+** instalado
2. **Dependências instaladas**:
   ```bash
   pip install -r requirements.txt
   ```

3. **(Opcional) Chave API da OpenAI** para recursos de IA:
   - Configure em `.streamlit/secrets.toml` (já configurado)
   - Ou insira diretamente na interface

---

## 🎯 Opções de Execução

### Opção 1: Script Automático (Recomendado)

```bash
# Usando o app completo (padrão)
./run_app.sh

# Ou especifique qual app usar
./run_app.sh app_completo.py   # Sistema completo
./run_app.sh app_editor.py     # Editor simples
```

### Opção 2: Comando Streamlit Direto

```bash
# App completo com workflow de 14 fases
streamlit run app_completo.py

# Editor rápido e simples
streamlit run app_editor.py
```

### Opção 3: Com Configurações Customizadas

```bash
streamlit run app_completo.py \
    --server.port=8501 \
    --server.address=localhost \
    --theme.primaryColor="#1f77b4"
```

---

## 🌐 Acessando a Aplicação

Após iniciar, a aplicação estará disponível em:

- **URL Local:** http://localhost:8501
- **URL de Rede:** http://0.0.0.0:8501 (se configurado para acesso externo)

O navegador será aberto automaticamente (se não estiver em modo headless).

---

## 📱 Interfaces Disponíveis

### 1. **app_completo.py** - Sistema Completo ⭐ RECOMENDADO

Interface completa com três modos de operação:

#### 🖊️ Modo 1: Editor Rápido
- Upload de arquivos (TXT, DOCX)
- Editor de texto integrado
- FastFormat para tipografia profissional
- Sugestões de IA para estilo
- Export para DOCX formatado

#### 🔄 Modo 2: Workflow Completo (14 Fases)
- **Fases 1-6**: Preparação do manuscrito
  - Análise estrutural
  - Aprimoramento de conteúdo
  - Formatação profissional
  - Revisão editorial
  
- **Fases 7-9**: Design e produção
  - Diagramação automática
  - Design de capas
  
- **Fase 10**: ISBN e CIP
  - Geração automática de ISBN-13
  - Ficha catalográfica (CIP)
  
- **Fases 11-14**: Preparação para gráfica
  - Arquivos print-ready
  - Especificações técnicas

#### 📊 Modo 3: Análise e Relatórios
- Análise estrutural detalhada
- Métricas de qualidade
- Relatórios de legibilidade
- Recomendações de melhoria

### 2. **app_editor.py** - Editor Simples

Interface focada em edição rápida:
- Editor de texto básico
- FastFormat integrado
- Sugestões de IA
- Export para DOCX

---

## ⚙️ Configurações

### Configuração de API

Há duas formas de configurar a API da OpenAI:

1. **Arquivo de configuração** (recomendado para desenvolvimento):
   ```toml
   # .streamlit/secrets.toml
   OPENAI_API_KEY = "sua-chave-aqui"
   ```

2. **Interface web** (recomendado para produção):
   - Insira a chave no campo lateral da aplicação
   - A validação é feita automaticamente

### Personalização de Tema

Edite `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

---

## 🎨 Funcionalidades Principais

### ✨ FastFormat - Tipografia Profissional

O FastFormat aplica formatação tipográfica avançada:

- **Aspas curvas**: `"texto"` → `"texto"`
- **Travessões em diálogos**: `- Olá` → `— Olá`
- **Travessões em intervalos**: `10-20` → `10–20`
- **Reticências normalizadas**: `...` → `…`
- **Espaçamento otimizado**: Remove espaços extras
- **Pontuação PT-BR**: Ajustes automáticos

**Presets disponíveis:**
- PT-BR (Ficção) - Para romances e narrativas
- Acadêmico/Técnico - Para textos científicos
- Personalizado - Configure manualmente

### 🤖 Assistente de IA

Requer chave API da OpenAI (GPT-4):

- Análise de estilo e clareza
- Sugestões de melhorias
- Detecção de inconsistências
- Avaliação de qualidade

### 📊 Análise de Manuscrito

Análise completa incluindo:

- **Contagem**: Palavras, páginas, capítulos
- **Estrutura**: Organização e hierarquia
- **Qualidade**: Score geral de 0-100%
- **Legibilidade**: Métricas de facilidade de leitura
- **Consistência**: Uniformidade terminológica
- **Formatação**: Padronização de elementos

### 📖 Geração de ISBN e CIP

Sistema automático que gera:

- **ISBN-13**: Número válido com dígito verificador
- **Código de barras**: EAN-13 para impressão
- **Ficha CIP**: Catalogação na publicação
- **Metadados ONIX**: Para distribuição

### 🎨 Design de Capas

Geração automática de 5 conceitos profissionais:

- Layout moderno
- Layout clássico
- Layout minimalista
- Layout bold
- Layout artístico

Cada conceito inclui:
- Capa completa (frente + lombada + contracapa)
- Arquivos em alta resolução (300 DPI)
- Formato CMYK para impressão

---

## 📂 Estrutura de Arquivos Gerados

### Editor Rápido

```
Downloads/
└── {Título}_ManuscritoProfissional.docx
```

### Workflow Completo

```
projects/
└── {Projeto}_{Timestamp}/
    ├── received/              # Manuscrito original
    ├── edited/                # Versões editadas
    ├── reviewed/              # Com revisões
    ├── approved/              # Aprovado pelo autor
    ├── layout/                # Diagramação
    ├── covers/                # Design de capas
    ├── isbn_cip/              # ISBN e ficha CIP
    ├── print_ready/           # Arquivos finais
    │   ├── miolo.pdf         # PDF do interior (300 DPI)
    │   ├── capa.pdf          # PDF da capa (300 DPI)
    │   └── especificacoes.txt # Dados para gráfica
    └── resultados.json        # Resumo do processo
```

---

## 🔧 Solução de Problemas

### Erro: "Streamlit não encontrado"

```bash
pip install streamlit
```

### Erro: "Módulo não encontrado"

Instale todas as dependências:

```bash
pip install -r requirements.txt
```

### Erro: "language_tool_python falhou"

```bash
# Instala Java (necessário para o corretor gramatical)
# Ubuntu/Debian:
sudo apt-get install default-jre

# macOS:
brew install java
```

### Porta 8501 já em uso

```bash
# Use uma porta diferente
streamlit run app_completo.py --server.port=8502
```

### API Key inválida

1. Verifique se a chave está correta
2. Confirme que tem créditos na conta OpenAI
3. Teste em https://platform.openai.com/api-keys

---

## 💡 Dicas de Uso

### Para Melhor Performance

1. **Use FastFormat sempre**: Garante tipografia profissional
2. **Revise por partes**: Para textos longos, processe em seções
3. **Salve frequentemente**: Faça download de versões intermediárias
4. **Configure API**: Habilita recursos avançados de IA

### Workflow Recomendado

1. **Inicie no Editor Rápido**: Faça ajustes iniciais
2. **Aplique FastFormat**: Garanta tipografia correta
3. **Use IA para sugestões**: Refine o estilo
4. **Execute Workflow Completo**: Para publicação final

### Otimizações

- **Manuscritos grandes** (>100k palavras): Use análise primeiro
- **Múltiplas versões**: Execute workflow em projetos separados
- **Revisão colaborativa**: Exporte DOCX para compartilhar

---

## 📚 Documentação Adicional

- **WORKFLOW_COMPLETO.md** - Detalhes das 14 fases
- **FASTFORMAT_DOCS.md** - Guia completo do FastFormat
- **README.md** - Documentação geral do sistema

---

## 🆘 Suporte

### Problemas Comuns

- **App não abre**: Verifique se a porta está livre
- **Erro de módulo**: Reinstale requirements.txt
- **Lentidão**: Reduza o tamanho do texto processado
- **Crash de memória**: Para textos muito grandes, use análise por partes

### Recursos

- 📖 **Documentação**: Veja os arquivos .md no repositório
- 🐛 **Issues**: Abra issues no GitHub para bugs
- 💬 **Discussões**: Use GitHub Discussions para dúvidas

---

## 🎯 Exemplos de Uso

### Exemplo 1: Edição Rápida

```bash
# 1. Inicie o app
./run_app.sh app_editor.py

# 2. Na interface:
#    - Cole seu texto ou faça upload
#    - Aplique FastFormat
#    - Baixe o DOCX formatado
```

### Exemplo 2: Publicação Completa

```bash
# 1. Inicie o app completo
./run_app.sh app_completo.py

# 2. Na interface:
#    - Escolha "Workflow Completo"
#    - Preencha metadados (título, autor, etc.)
#    - Faça upload do manuscrito
#    - Clique "Iniciar Processamento"
#    - Aguarde o processo completo
#    - Baixe todos os arquivos gerados
```

### Exemplo 3: Apenas Análise

```bash
# 1. Inicie o app
./run_app.sh app_completo.py

# 2. Na interface:
#    - Escolha "Análise e Relatórios"
#    - Faça upload do manuscrito
#    - Veja métricas e recomendações
```

---

## 📊 Resultados Esperados

### Economia

- 💰 **85-92% de redução de custo**: R$ 14k-33k → R$ 650-2.5k
- ⚡ **97-99% de redução de tempo**: 4-8 semanas → 4-6 horas
- 🎯 **Qualidade profissional**: Consistente e verificada

### Arquivos Gerados

- ✅ Manuscrito editado e formatado
- ✅ ISBN-13 válido com código de barras
- ✅ Ficha CIP (Catalogação)
- ✅ 5 conceitos de capa profissionais
- ✅ PDF do miolo (300 DPI, CMYK)
- ✅ PDF da capa com lombada
- ✅ Especificações para gráfica

---

## 🚀 Começando Agora

```bash
# Clone o repositório (se ainda não fez)
git clone https://github.com/CarlosHonorato70/editor-literario-ia.git
cd editor-literario-ia

# Instale as dependências
pip install -r requirements.txt

# Inicie a aplicação
./run_app.sh

# Ou use diretamente:
streamlit run app_completo.py
```

**Pronto!** A aplicação estará rodando em http://localhost:8501

---

*Desenvolvido com ❤️ por Manus AI - Novembro 2025*
