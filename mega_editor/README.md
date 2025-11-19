# 📚 MEGA EDITOR - Dashboard Unificado

## Visão Geral

O **MEGA EDITOR** é um dashboard unificado que integra todas as funcionalidades do Editor Literário IA em uma interface única e profissional.

## 🎯 Acesso Único

Execute o MEGA EDITOR com um único comando:

```bash
streamlit run mega_editor/app.py
```

Ou no Windows:
```powershell
py -m streamlit run mega_editor/app.py
```

## 🚀 Funcionalidades Integradas

### 1. Dashboard Principal (🏠 Início)
- Visão geral de todas as funcionalidades
- Estatísticas do projeto em tempo real
- Acesso rápido aos recursos principais
- Projetos recentes

### 2. Editores Múltiplos (✍️ Editores)
- **Editor Simples**: Texto puro com upload de arquivos
- **Editor Quill**: WYSIWYG com formatação rica
- **Editor Ace**: Editor de código profissional
- **Sincronização**: Sincronize conteúdo entre editores

### 3. Workflow de 14 Fases (🔄 Workflow)
- Configuração inicial e metadados
- Importação e revisão ortográfica
- Análise estrutural
- Edição de conteúdo
- Formatação tipográfica (FastFormat)
- Revisão de estilo
- Sugestões de IA
- Validação de consistência
- Pré-visualização
- Elementos pré/pós-textuais
- Exportação multi-formato
- Publicação e distribuição

### 4. Produção Gráfica (🎨 Produção)
- Design de capa
- Layout profissional
- Materiais de marketing
- Arquivos print-ready

### 5. Análise de Manuscrito (📊 Análise)
- Contagem de palavras e caracteres
- Análise de legibilidade
- Complexidade do texto
- Estatísticas detalhadas

### 6. Exportação (🚀 Exportação)
- DOCX (Microsoft Word)
- PDF (impressão e digital)
- EPUB (e-books)
- HTML (web)
- Markdown
- TXT (texto puro)

### 7. Configurações (⚙️ Configurações)
- Configurações gerais do sistema
- Personalização do editor
- Configuração de IA (OpenAI)
- Preferências de exportação

## 📋 Requisitos

```bash
pip install streamlit
pip install streamlit-quill
pip install streamlit-ace
pip install python-docx
pip install beautifulsoup4
pip install openai
```

Ou instale todas as dependências:
```bash
pip install -r requirements.txt
```

## 🎨 Interface

O MEGA EDITOR oferece:
- ✅ **Interface Moderna**: Design limpo e profissional
- ✅ **Navegação Intuitiva**: Tabs organizadas por função
- ✅ **Sidebar Informativa**: Estatísticas e controles rápidos
- ✅ **Responsivo**: Funciona em qualquer tamanho de tela
- ✅ **Tema Customizável**: Adaptável às suas preferências

## 📊 Painel de Controle (Sidebar)

O painel lateral oferece:
- Nome e informações do projeto atual
- Estatísticas em tempo real (palavras, caracteres)
- Barra de progresso do workflow
- Ações rápidas (Salvar, Carregar, Resetar)
- Links úteis

## 🔄 Fluxo de Trabalho Recomendado

1. **Início**: Crie um novo manuscrito ou importe um arquivo
2. **Edição**: Use o editor de sua preferência
3. **Workflow**: Siga as 14 fases para publicação profissional
4. **Análise**: Revise estatísticas e qualidade do texto
5. **Produção**: Gere materiais gráficos (opcional)
6. **Exportação**: Gere os arquivos finais em múltiplos formatos
7. **Configurações**: Ajuste preferências conforme necessário

## 🎯 Vantagens do MEGA EDITOR

- ✅ **Acesso Unificado**: Todas as ferramentas em um só lugar
- ✅ **Sincronização**: Trabalhe com múltiplos editores simultaneamente
- ✅ **Workflow Guiado**: 14 fases profissionais
- ✅ **Multiplataforma**: Suporte para KDP, Apple Books, Google Play, Kobo
- ✅ **Produção Completa**: Da escrita à publicação
- ✅ **Interface Profissional**: Design moderno e intuitivo
- ✅ **Salvamento Inteligente**: Persistência automática de estado
- ✅ **Extensível**: Fácil adicionar novos recursos

## 🛠️ Estrutura

```
mega_editor/
├── app.py              # Aplicação principal
├── README.md           # Esta documentação
└── __init__.py         # Módulo Python
```

## 📝 Notas

- Todos os dados são armazenados em `st.session_state`
- A sincronização entre editores é manual (botões específicos)
- O workflow de 14 fases é independente dos editores
- A exportação usa os módulos existentes do projeto
- As configurações são aplicadas em tempo real

## 🆘 Suporte

Para problemas ou sugestões:
- GitHub Issues: https://github.com/CarlosHonorato70/editor-literario-ia/issues
- Documentação: Consulte os arquivos MD na raiz do projeto

## 📜 Licença

Este projeto faz parte do Editor Literário IA.
