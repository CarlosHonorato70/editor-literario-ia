# Como Usar o Editor com Interface Word-like

## 🚀 Guia Rápido de Instalação e Uso

### Passo 1: Instalar Dependências

Primeiro, certifique-se de que todas as dependências estão instaladas:

```bash
# No diretório do projeto
pip install -r requirements.txt
```

Isso irá instalar:
- `streamlit` - Framework da interface
- `streamlit-quill` - Editor de texto rico (NOVO)
- Todas as outras dependências necessárias

### Passo 2: Executar o Aplicativo

Execute o aplicativo com Streamlit:

```bash
streamlit run app_editor.py
```

O aplicativo será aberto automaticamente no seu navegador em:
```
http://localhost:8501
```

Se não abrir automaticamente, copie e cole esse endereço no navegador.

### Passo 3: Usar o Editor Avançado

1. **Carregue seu manuscrito:**
   - Na primeira aba "1. Escrever & Editar"
   - Faça upload de um arquivo (.txt ou .docx)
   - OU cole o texto diretamente

2. **Envie para o Editor Avançado:**
   - Clique no botão **"📤 Enviar para Editor Avançado"**
   - Uma mensagem de sucesso aparecerá

3. **Edite com ferramentas profissionais:**
   - Vá para a aba **"✍️ Editor Avançado (Word-like)"**
   - Use a barra de ferramentas para formatar:
     - **Negrito, itálico, sublinhado**
     - **Títulos** (H1, H2, H3, etc.)
     - **Listas** (numeradas ou com marcadores)
     - **Cores** de texto e fundo
     - **Alinhamento** do texto
     - E muito mais!

4. **Salve suas alterações:**
   - Clique em **"💾 Salvar para Texto Principal"**
   - Seu texto será atualizado no editor simples

5. **Continue o workflow:**
   - Use **FastFormat** para formatação tipográfica
   - Use **Sugestões de IA** para melhorias
   - **Finalize e baixe** seu manuscrito profissional

## 📋 Comandos Úteis

### Iniciar o aplicativo
```bash
streamlit run app_editor.py
```

### Iniciar com porta personalizada
```bash
streamlit run app_editor.py --server.port 8502
```

### Iniciar e abrir automaticamente no navegador
```bash
streamlit run app_editor.py --server.headless false
```

### Ver logs detalhados
```bash
streamlit run app_editor.py --logger.level=debug
```

## 🖥️ Requisitos do Sistema

- **Python:** 3.8 ou superior
- **RAM:** Mínimo 2GB recomendado
- **Navegador:** Chrome, Firefox, Safari ou Edge (versão recente)
- **Conexão:** Internet necessária apenas para sugestões de IA (opcional)

## 🎯 Fluxo de Trabalho Completo

```
1. Abra terminal/prompt de comando
2. Navegue até a pasta do projeto
3. Execute: streamlit run app_editor.py
4. Aguarde o navegador abrir
5. Carregue seu manuscrito (Aba 1)
6. Clique "📤 Enviar para Editor Avançado"
7. Edite visualmente (Aba 2)
8. Salve com "💾 Salvar para Texto Principal"
9. Continue com FastFormat (Aba 3)
10. Use IA se desejar (Aba 4)
11. Finalize e baixe (Aba 5)
```

## 💡 Dicas

### Primeira Vez Usando Streamlit?

O Streamlit abre automaticamente no navegador. Se não abrir:
1. Veja no terminal a URL (geralmente `http://localhost:8501`)
2. Copie e cole no navegador
3. Pronto!

### Parou de Responder?

Se o app travar:
1. No terminal, pressione `Ctrl+C` para parar
2. Execute novamente: `streamlit run app_editor.py`

### Quer Compartilhar?

Para acessar de outros dispositivos na mesma rede:
```bash
streamlit run app_editor.py --server.address 0.0.0.0
```

Depois acesse pelo IP da máquina (ex: `http://192.168.1.100:8501`)

## 📸 Interface

Quando o app abrir, você verá:

```
┌────────────────────────────────────────────┐
│ Adapta ONE - Editor Profissional ✒️        │
├────────────────────────────────────────────┤
│                                            │
│ [1. Escrever & Editar] ← Comece aqui      │
│ [✍️ Editor Avançado] ← NOVO!              │
│ [2. FastFormat]                            │
│ [3. Sugestões de IA]                       │
│ [4. Finalizar & Baixar]                    │
│                                            │
└────────────────────────────────────────────┘
```

## 🔧 Solução de Problemas

### Erro: "streamlit: command not found"
```bash
# Instale o streamlit
pip install streamlit
```

### Erro: "No module named 'streamlit_quill'"
```bash
# Instale as dependências
pip install -r requirements.txt
```

### Porta já em uso
```bash
# Use outra porta
streamlit run app_editor.py --server.port 8502
```

### App não abre no navegador
```bash
# Abra manualmente
# Terminal mostrará: "You can now view your Streamlit app in your browser."
# Copie a URL e cole no navegador
```

## 📚 Documentação Completa

Para mais detalhes, consulte:
- **WORD_INTERFACE_GUIDE.md** - Guia completo do editor avançado
- **VISUAL_REFERENCE.md** - Referência visual da interface
- **IMPLEMENTATION_SUMMARY.md** - Resumo técnico
- **README.md** - Visão geral do sistema

## ✅ Checklist de Verificação

Antes de começar, verifique:
- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Navegador moderno disponível
- [ ] Porta 8501 disponível (ou use outra)

## 🎉 Pronto!

Agora você está pronto para usar o Editor Avançado com interface Word-like!

Execute `streamlit run app_editor.py` e comece a editar! 🚀

---

**Desenvolvido com ❤️ por Manus AI**

**Versão 2.0** | Novembro 2025
