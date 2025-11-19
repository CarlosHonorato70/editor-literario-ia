# 📸 Guia Visual - Como Executar o App

## Passo 1: Abrir Terminal

### Windows
- Pressione `Win + R`
- Digite `cmd` e pressione Enter
- OU abra o PowerShell

### Mac/Linux
- Pressione `Cmd + Space` (Mac) ou `Ctrl + Alt + T` (Linux)
- Digite `terminal` e pressione Enter

## Passo 2: Navegar até a Pasta do Projeto

```bash
# Exemplo (ajuste para o seu caminho):
cd C:\projetos\editor-literario-ia         # Windows
cd ~/projetos/editor-literario-ia          # Mac/Linux
```

## Passo 3: Verificar Dependências ⭐ **IMPORTANTE**

### Opção 1: Usar Script de Diagnóstico (Recomendado)

```bash
python check_dependencies.py
```

**O que você verá:**
```
============================================================
  Diagnóstico de Dependências - Adapta ONE
============================================================

✅ streamlit                 - Framework da interface
✅ streamlit_quill           - Editor Avançado (Word-like)
✅ docx                      - Processamento de documentos DOCX
...

============================================================
✅ Todas as dependências estão instaladas!

🚀 Você está pronto para usar o Adapta ONE!

Execute: streamlit run app_editor.py

============================================================
```

**Se alguma dependência estiver faltando:**
```
❌ streamlit_quill           - Editor Avançado (Word-like) [FALTANDO]

⚠️  ATENÇÃO: Dependências críticas faltando!

Para instalar as dependências críticas:

  pip install streamlit-quill

Ou reinstale todas as dependências:

  pip install -r requirements.txt
```

### Opção 2: Verificar Python

```bash
# Ver se o Python está instalado:
python --version
# Deve mostrar: Python 3.8.x ou superior

# Se não funcionar, tente:
python3 --version
```

## Passo 4: Instalar Dependências (Primeira Vez)

```bash
pip install -r requirements.txt

# Se não funcionar, tente:
pip3 install -r requirements.txt
```

**Saída esperada:**
```
Successfully installed streamlit-1.51.0 streamlit-quill-0.0.3 ...
```

## Passo 5: Executar o Aplicativo

### Opção 1: Comando Direto
```bash
streamlit run app_editor.py
```

### Opção 2: Usando o Script (Mac/Linux)
```bash
./run.sh
```

### Opção 3: Usando o Script (Windows)
```bash
run.bat
```

### Opção 4: Com Python
```bash
python -m streamlit run app_editor.py
```

## O Que Você Verá no Terminal

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📝 Adapta ONE - Editor Profissional com Interface Word-like
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Passo 6: Acessar no Navegador

O navegador deve abrir automaticamente em:
```
http://localhost:8501
```

Se não abrir:
1. Copie o endereço `http://localhost:8501`
2. Cole na barra de endereços do navegador
3. Pressione Enter

## Interface do Aplicativo

Você verá a seguinte interface:

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│          Adapta ONE - Editor Profissional ✒️                     │
│                                                                  │
│  A evolução da preparação de manuscritos. Carregue seu texto,   │
│  faça ajustes e, com um clique, obtenha um manuscrito           │
│  profissional e revisado.                                        │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ABAS (clique para navegar):                                    │
│                                                                  │
│  ┌──────────────────┬──────────────────┬──────────────────┐    │
│  │ 1. Escrever &    │ ✍️ Editor       │ 2. FastFormat    │    │
│  │    Editar        │    Avançado     │    (Formatação)  │    │
│  └──────────────────┴──────────────────┴──────────────────┘    │
│                                                                  │
│  ┌──────────────────┬──────────────────┐                       │
│  │ 3. Sugestões     │ 4. Finalizar &   │                       │
│  │    de Estilo     │    Baixar        │                       │
│  └──────────────────┴──────────────────┘                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Usando o Editor Avançado (Word-like)

### 1. Carregar Texto (Aba 1)

```
┌────────────────────────────────────────┐
│ Cole ou Faça o Upload do seu Manuscrito│
│                                        │
│ [Escolher arquivo] manuscrito.txt      │
│                                        │
│ ┌────────────────────────────────────┐ │
│ │ Editor Principal                   │ │
│ │                                    │ │
│ │ Era uma vez...                     │ │
│ │                                    │ │
│ └────────────────────────────────────┘ │
│                                        │
│ [📤 Enviar para Editor Avançado]      │
└────────────────────────────────────────┘
```

### 2. Editar com Toolbar (Aba 2)

```
┌───────────────────────────────────────────────────────────┐
│ ✍️ Editor Avançado - Interface estilo Word                │
│                                                           │
│ BARRA DE FERRAMENTAS:                                     │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ [B] [I] [U] [S] │ ["] [</>] │ [H1] [H2] │ [•] [1.] │ │
│ │ [🎨] [🖼️] [🔗] [≡] │ ... e muito mais!                │ │
│ └───────────────────────────────────────────────────────┘ │
│                                                           │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ ÁREA DE EDIÇÃO                                        │ │
│ │                                                       │ │
│ │ Era uma vez, em uma terra distante...                │ │
│ │                                                       │ │
│ │ [Edite aqui com formatação visual]                   │ │
│ │                                                       │ │
│ └───────────────────────────────────────────────────────┘ │
│                                                           │
│ [💾 Salvar para Texto Principal]  [🔄 Recarregar]        │
│                                                           │
│ 📊 Contagem de palavras: 142 palavras                    │
└───────────────────────────────────────────────────────────┘
```

### 3. Salvar e Continuar

Após editar:
1. Clique em **"💾 Salvar para Texto Principal"**
2. Vá para outras abas para:
   - **FastFormat** (Aba 3) - Formatação tipográfica
   - **Sugestões de IA** (Aba 4) - Análise de estilo
   - **Finalizar** (Aba 5) - Download do manuscrito

## Comandos Úteis

### Parar o Servidor
```
Pressione: Ctrl + C no terminal
```

### Reiniciar o Servidor
```bash
# Pare (Ctrl + C) e execute novamente:
streamlit run app_editor.py
```

### Limpar Cache
```bash
streamlit cache clear
streamlit run app_editor.py
```

### Ver em Outra Porta
```bash
streamlit run app_editor.py --server.port 8502
```

### Acessar de Outro Dispositivo
```bash
# Use o Network URL mostrado no terminal
# Exemplo: http://192.168.1.100:8501
```

## Solução de Problemas Visuais

### ⚠️ Editor Avançado não aparece / mostra erro

**O que você vê:**
```
┌────────────────────────────────────────┐
│ ⚠️ Editor Avançado não disponível      │
│                                        │
│ O módulo streamlit-quill não está     │
│ instalado.                             │
│                                        │
│ Para ativar o Editor Avançado:         │
│ 1. Pare o aplicativo (Ctrl+C)         │
│ 2. Execute: pip install streamlit-quill│
│ 3. Reinicie: streamlit run app_editor.py│
└────────────────────────────────────────┘
```

**Solução 1 - Executar diagnóstico:**
```bash
python check_dependencies.py
```

**Solução 2 - Instalar dependência específica:**
```bash
pip install streamlit-quill
```

**Solução 3 - Reinstalar tudo:**
```bash
pip install -r requirements.txt
```

Depois reinicie o app:
```bash
streamlit run app_editor.py
```

### ❌ Erro: "streamlit: command not found"

**Terminal mostra:**
```
bash: streamlit: command not found
```

**Solução:**
```bash
pip install streamlit streamlit-quill
```

### ❌ Erro: "Address already in use"

**Terminal mostra:**
```
OSError: Address already in use
```

**Solução 1 - Usar outra porta:**
```bash
streamlit run app_editor.py --server.port 8502
```

**Solução 2 - Matar processo:**
```bash
# Windows:
netstat -ano | findstr :8501
taskkill /PID <número> /F

# Mac/Linux:
lsof -ti:8501 | xargs kill -9
```

### ❌ Página em Branco no Navegador

**Solução:**
1. Aguarde alguns segundos (carregamento)
2. Recarregue a página (F5)
3. Limpe o cache: `Ctrl + Shift + R`
4. Tente outro navegador

### ❌ Editor Avançado Não Aparece

**Verifique:**
1. Dependência instalada: `pip show streamlit-quill`
2. Versão correta no requirements.txt
3. Reinstale: `pip install --upgrade streamlit-quill`

## Atalhos de Teclado Úteis

No navegador com o app aberto:

| Atalho | Ação |
|--------|------|
| `R` | Recarregar app |
| `C` | Limpar cache e recarregar |
| `⋮` menu | Configurações, tema, etc. |

## Estrutura de Arquivos

```
editor-literario-ia/
├── app_editor.py          ← ARQUIVO PRINCIPAL
├── requirements.txt       ← Dependências
├── run.sh                 ← Script de inicialização (Mac/Linux)
├── COMO_USAR.md          ← Este guia
├── WORD_INTERFACE_GUIDE.md ← Guia do editor avançado
└── ...
```

## Próximos Passos

1. ✅ Execute: `streamlit run app_editor.py`
2. ✅ Carregue um manuscrito na Aba 1
3. ✅ Clique "📤 Enviar para Editor Avançado"
4. ✅ Vá para Aba 2 e edite com a toolbar
5. ✅ Salve e continue o workflow

## 📞 Precisa de Ajuda?

- 📚 Leia: **WORD_INTERFACE_GUIDE.md**
- 📸 Veja: **VISUAL_REFERENCE.md**
- 📖 Consulte: **README.md**

---

**Desenvolvido com ❤️ por Manus AI**

**Versão 2.0** | Novembro 2025
