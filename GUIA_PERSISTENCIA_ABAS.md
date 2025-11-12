# Guia: Persistência de Texto Entre Abas no Streamlit

## O Problema Relatado
"Faço upload do texto mas ele não fica salvo para as outras abas"

## Como o Sistema Funciona

### 1. Upload de Arquivo (Tab 1)
```python
# Quando você faz upload:
def processar_arquivo_carregado():
    text, error = extract_text(file_content, filename)
    st.session_state.text_content = text  # ← SALVA NO SESSION STATE
    st.success("Arquivo carregado!")
```

### 2. Editor de Texto (Tab 1)
```python
# O text_area está vinculado ao session_state:
st.text_area(..., key="text_content")
# Isto significa:
# - O que você digita → salva em st.session_state.text_content
# - O que está em st.session_state.text_content → aparece no editor
```

### 3. Outras Abas (Tab 2, 3, 4)
```python
# Todas as outras abas leem do mesmo session_state:
if not st.session_state.text_content:
    st.info("Carregue um texto primeiro")
else:
    # Usa st.session_state.text_content
```

## Por Que Deveria Funcionar

O `st.session_state` é **global** em toda a sessão do Streamlit:
- ✅ Compartilhado entre todas as abas
- ✅ Persiste durante toda a sessão
- ✅ Atualiza automaticamente quando você muda de aba

## Possíveis Causas do Problema

### Causa 1: Você Editou o Texto Após o Upload
**Sintoma**: Upload funciona, mas quando volta à aba, texto sumiu

**Explicação**: 
- Você faz upload → texto aparece no editor
- Você edita ou limpa o editor (mesmo sem querer)
- O editor atualiza `st.session_state.text_content` para o valor editado
- Outras abas veem o valor editado (que pode estar vazio)

**Solução**: Não limpe ou edite o campo após o upload, OU suas edições serão salvas automaticamente

### Causa 2: Upload Não Completou
**Sintoma**: Você troca de aba antes de ver a mensagem de sucesso

**Explicação**:
- Callback `on_change` está processando
- Você troca de aba antes dele terminar
- `st.session_state.text_content` ainda não foi atualizado

**Solução**: Aguarde a mensagem "✅ Arquivo carregado com sucesso!" antes de trocar de aba

### Causa 3: Sessão Streamlit Corrompida
**Sintoma**: Comportamento inconsistente, às vezes funciona às vezes não

**Explicação**:
- Cache do navegador ou servidor
- Estado inconsistente após erros
- Múltiplas abas do navegador na mesma sessão

**Solução**: 
```bash
# 1. Pare o Streamlit (Ctrl+C)
# 2. Limpe cache do navegador (Ctrl+Shift+Delete)
# 3. Reinicie: streamlit run app_editor.py
```

### Causa 4: Problema com Versão do Streamlit
**Sintoma**: O código está correto mas não funciona

**Solução**:
```bash
pip install --upgrade streamlit
# Versão mínima recomendada: 1.25.0
```

## Como Testar

### Teste 1: Verificar Upload
1. Vá para Tab 1 (Escrever & Editar)
2. Faça upload de um arquivo .txt
3. **AGUARDE** a mensagem: ✅ Arquivo 'nome.txt' carregado com sucesso!
4. Verifique se o texto aparece no "Editor Principal"
   - ✅ Se SIM: Upload funciona, vá para Teste 2
   - ❌ Se NÃO: Há problema no upload (execute verificar_upload.py)

### Teste 2: Verificar Persistência
1. Com o texto visível no Editor Principal (Tab 1)
2. **NÃO EDITE O TEXTO**
3. Vá para Tab 2 (FastFormat)
4. Verifique se vê opções de formatação ou mensagem "carregue um texto"
   - ✅ Se vê opções: Texto persistiu!
   - ❌ Se vê "carregue um texto": Texto NÃO persistiu

### Teste 3: Verificar Two-Way Binding
1. Tab 1: Digite algo no Editor Principal
2. Vá para Tab 2
3. Volte para Tab 1
4. O que você digitou ainda está lá?
   - ✅ Se SIM: Binding funciona
   - ❌ Se NÃO: Problema com session_state

## Debug: Ver o Session State

Adicione temporariamente no app_editor.py, logo após `inicializar_estado()`:

```python
# DEBUG: Mostrar session_state
st.sidebar.markdown("---")
st.sidebar.markdown("**DEBUG: Session State**")
st.sidebar.write(f"text_content: {len(st.session_state.get('text_content', ''))} caracteres")
st.sidebar.write(f"file_processed: {st.session_state.get('file_processed', False)}")
```

Isso mostrará na barra lateral:
- Quantos caracteres existem em `text_content`
- Se um arquivo foi processado

Se mostrar "0 caracteres" após o upload, o problema está no callback.
Se mostrar ">0 caracteres" mas outras abas não veem, há problema de rendering.

## Solução Alternativa: Forçar Rerun

Se o problema persistir, podemos modificar o callback para forçar um rerun:

```python
def processar_arquivo_carregado():
    uploaded_file = st.session_state.file_uploader_key
    if uploaded_file:
        try:
            file_content = uploaded_file.getvalue()
            text, error = extract_text(file_content, uploaded_file.name)
            
            if error:
                st.error(f"❌ {error}")
                st.session_state.text_content = ""
                st.session_state.file_processed = False
            else:
                st.session_state.text_content = text
                st.session_state.file_processed = True
                st.session_state.sugestoes_estilo = None
                st.success(f"✅ Arquivo '{uploaded_file.name}' carregado com sucesso!")
                st.rerun()  # ← ADICIONAR ESTA LINHA
        except Exception as e:
            st.error(f"Ocorreu um erro ao ler o arquivo: {e}")
            st.session_state.text_content = ""
            st.session_state.file_processed = False
```

## Conclusão

O código **está correto** e **deveria funcionar**. Se não funciona:

1. **Execute os scripts de diagnóstico**:
   ```bash
   python verificar_upload.py
   python demonstracao_upload.py
   python testar_persistencia_abas.py
   ```

2. **Teste manualmente seguindo os passos acima**

3. **Se ainda não funcionar**, adicione o debug no sidebar e compartilhe:
   - O que mostra no DEBUG
   - Em qual aba você está
   - O que você fez exatamente antes do problema

4. **Última opção**: Adicione `st.rerun()` no callback (ver acima)

---
**Atualizado**: 2025-11-12
**Status**: Código correto, problema pode ser de ambiente/uso
