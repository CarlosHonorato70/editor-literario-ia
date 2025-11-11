# 🚀 Início Rápido - Editor Literário IA

## Acesso Imediato à Aplicação Streamlit

### Opção 1: Script Automático (Mais Fácil)

**🐧 Linux/Mac:**
```bash
./run_app.sh
```

**🪟 Windows:**
```cmd
run_app.bat
```

A aplicação será aberta automaticamente em: **http://localhost:8501**

### Opção 2: Comando Direto (Todos os sistemas)

```bash
streamlit run app_completo.py
```

### 🪟 Problemas no Windows?

Se você viu erros como:
- `'.' não é reconhecido como um comando interno`
- `File does not exist: app_completo.py`

**👉 Consulte o guia completo:** [GUIA_WINDOWS.md](GUIA_WINDOWS.md)

**Solução rápida:**
1. Certifique-se de estar no diretório correto
2. Use `run_app.bat` em vez de `./run_app.sh`
3. Ou use: `streamlit run app_completo.py`

---

## 📱 Três Modos de Operação

### 1. 📝 Editor Rápido

**Melhor para:** Edições rápidas e formatação profissional

**Funcionalidades:**
- Upload de arquivos TXT/DOCX
- Editor de texto integrado
- FastFormat para tipografia profissional
- Sugestões de IA (requer API OpenAI)
- Export para DOCX formatado

**Passos:**
1. Carregue ou cole seu texto
2. Aplique FastFormat (aspas curvas, travessões, etc.)
3. Use IA para sugestões (opcional)
4. Baixe o DOCX profissional

### 2. 🔄 Workflow Completo (14 Fases)

**Melhor para:** Publicação completa do manuscrito bruto até a gráfica

**Funcionalidades:**
- Análise estrutural completa
- Aprimoramento de conteúdo
- Formatação profissional
- Revisão editorial automática
- Geração de ISBN-13 e CIP
- Design de capas (5 conceitos)
- Diagramação profissional
- Arquivos print-ready (300 DPI, CMYK)

**Passos:**
1. Preencha os metadados (título, autor, editora, etc.)
2. Faça upload do manuscrito (PDF, DOCX, TXT, MD)
3. Clique em "Iniciar Processamento Completo"
4. Aguarde o processamento (4-6 horas para livro completo)
5. Baixe todos os arquivos gerados

**O que você recebe:**
- ✅ Manuscrito editado e revisado
- ✅ ISBN-13 válido com código de barras
- ✅ Ficha CIP (Catalogação na Publicação)
- ✅ 5 conceitos de capa profissionais
- ✅ PDF do miolo diagramado (300 DPI, CMYK)
- ✅ PDF da capa com lombada calculada
- ✅ Especificações técnicas para gráfica
- ✅ Pacote completo pronto para impressão

### 3. 📊 Análise e Relatórios

**Melhor para:** Avaliação de qualidade sem processamento completo

**Funcionalidades:**
- Análise estrutural (capítulos, seções)
- Métricas de qualidade (0-100%)
- Contagem de palavras e páginas
- Avaliação de legibilidade
- Recomendações de melhoria

**Passos:**
1. Faça upload do manuscrito
2. Clique em "Analisar Manuscrito"
3. Visualize as métricas e recomendações

---

## ⚙️ Configuração Rápida

### Configurações Básicas (Barra Lateral)

**Informações do Manuscrito:**
- Título do Livro
- Nome do Autor(a)
- Email ou Contato
- Gênero (Ficção, Romance, Acadêmico, etc.)

**Para Workflow Completo (adicional):**
- Editora
- Número de Páginas (estimado)
- Edição (ex: "1ª edição")
- Ano de Publicação

**FastFormat:**
- ✅ Marque para ativar tipografia profissional
- Transforma aspas retas em curvas
- Adiciona travessões em diálogos
- Normaliza reticências e espaçamentos

**OpenAI API Key (Opcional):**
- Necessária apenas para recursos de IA
- Sugestões de estilo
- Análise avançada de conteúdo

---

## 🎯 Exemplos de Uso

### Exemplo 1: Formatação Rápida

```
1. Abra a aplicação
2. Modo: "Editor Rápido"
3. Cole seu texto no editor
4. Vá para aba "FastFormat"
5. Escolha preset "PT-BR (Ficção)"
6. Clique em "Prévia da Formatação"
7. Revise as mudanças
8. Clique em "Aplicar ao Texto"
9. Vá para aba "Finalizar & Baixar"
10. Baixe o DOCX formatado
```

**Resultado:** Manuscrito com tipografia profissional em minutos!

### Exemplo 2: Publicação Completa

```
1. Abra a aplicação
2. Modo: "Workflow Completo (14 Fases)"
3. Preencha todos os metadados na barra lateral:
   - Título: "Meu Romance"
   - Autor: "João Silva"
   - Editora: "Minha Editora"
   - Páginas: 250
   - Gênero: "Ficção"
4. Faça upload do manuscrito (PDF ou DOCX)
5. Clique em "Iniciar Processamento Completo"
6. Aguarde o processamento (barras de progresso)
7. Baixe o pacote completo para gráfica
```

**Resultado:** Livro completamente pronto para impressão!

### Exemplo 3: Análise de Qualidade

```
1. Abra a aplicação
2. Modo: "Análise e Relatórios"
3. Faça upload do manuscrito
4. Clique em "Analisar Manuscrito"
5. Visualize:
   - Métricas de qualidade
   - Estrutura (capítulos/seções)
   - Recomendações de melhoria
```

**Resultado:** Relatório completo de qualidade do manuscrito!

---

## ✨ Recursos Especiais

### FastFormat - Tipografia Profissional

**Presets Disponíveis:**

1. **PT-BR (Ficção)**
   - Aspas curvas: "texto"
   - Travessões em diálogos: — Olá
   - Reticências: …
   - Ideal para romances e narrativas

2. **Acadêmico/Técnico**
   - Mantém formatação original
   - Normaliza espaços
   - Ideal para teses e artigos

3. **Personalizado**
   - Configure cada opção individualmente
   - Controle total sobre a formatação

### Assistente de IA

**Requer:** OpenAI API Key

**O que faz:**
- Analisa estilo e clareza
- Sugere melhorias
- Identifica inconsistências
- Avalia qualidade geral

**Como usar:**
1. Insira API Key na barra lateral
2. Escreva ou carregue texto
3. Vá para aba "Sugestões de IA"
4. Clique em "Analisar Estilo"
5. Receba 3-5 sugestões específicas

---

## 📦 Arquivos Gerados

### Editor Rápido
```
{Título}_ManuscritoProfissional.docx
```

### Workflow Completo
```
projects/{Projeto}_{Timestamp}/
├── received/              # Manuscrito original
├── edited/                # Versões editadas
├── reviewed/              # Com revisões
├── approved/              # Aprovado
├── layout/                # Diagramação
├── covers/                # 5 conceitos de capa
│   ├── conceito_1.png
│   ├── conceito_2.png
│   ├── conceito_3.png
│   ├── conceito_4.png
│   └── conceito_5.png
├── isbn_cip/              
│   ├── isbn.png          # Código de barras
│   └── ficha_cip.txt     # Ficha catalográfica
├── print_ready/           # Arquivos finais
│   ├── miolo.pdf         # Interior (300 DPI, CMYK)
│   ├── capa.pdf          # Capa completa (300 DPI, CMYK)
│   └── especificacoes.txt # Dados técnicos
└── resultados.json        # Resumo do processo
```

### Análise e Relatórios
```
Relatório exibido na tela (sem arquivos)
```

---

## 🔧 Solução Rápida de Problemas

### Erro: "Porta 8501 já em uso"
```bash
# Use outra porta
streamlit run app_completo.py --server.port=8502
```

### Erro: "Módulo não encontrado"
```bash
# Instale dependências
pip install -r requirements.txt
```

### Erro: "language_tool_python falhou"
```bash
# Instale Java (necessário)
# Ubuntu/Debian:
sudo apt-get install default-jre

# macOS:
brew install java
```

### API Key não funciona
1. Verifique se a chave está correta
2. Confirme créditos na conta OpenAI
3. Teste em https://platform.openai.com/

---

## 💡 Dicas Profissionais

### Para Melhores Resultados

1. **Sempre use FastFormat**
   - Garante tipografia profissional
   - Padrão da indústria editorial

2. **Preencha todos os metadados**
   - Especialmente no Workflow Completo
   - Dados corretos geram ISBN/CIP válidos

3. **Revise os resultados**
   - Sempre revise o manuscrito final
   - IA é assistente, não substituto

4. **Salve versões intermediárias**
   - Faça download após cada etapa importante
   - Mantenha backups

### Workflow Recomendado

```
1. Editor Rápido
   ↓ (ajustes iniciais)
2. FastFormat
   ↓ (tipografia)
3. Sugestões de IA
   ↓ (refinamento)
4. Workflow Completo
   ↓ (publicação)
5. Download e envio para gráfica
```

---

## 📊 Economia e Eficiência

### Comparação com Processo Tradicional

| Aspecto | Tradicional | Com Sistema |
|---------|-------------|-------------|
| **Tempo** | 4-8 semanas | 4-6 horas |
| **Custo** | R$ 14k-33k | R$ 650-2.5k |
| **Qualidade** | Variável | Consistente |
| **Revisões** | Limitadas | Ilimitadas |

### ROI (Retorno sobre Investimento)

- **Economia de tempo:** 97-99%
- **Economia de custo:** 85-92%
- **Qualidade:** Profissional garantida

---

## 🆘 Precisa de Ajuda?

### Documentação Completa
- **COMO_EXECUTAR_STREAMLIT.md** - Guia detalhado de execução
- **WORKFLOW_COMPLETO.md** - Detalhes das 14 fases
- **FASTFORMAT_DOCS.md** - Guia do FastFormat
- **README.md** - Documentação geral

### Suporte
- 📖 Consulte a documentação no repositório
- 🐛 Abra issues no GitHub para bugs
- 💬 Use GitHub Discussions para dúvidas

---

## ✅ Checklist de Primeira Execução

- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] (Opcional) API Key da OpenAI configurada
- [ ] Manuscrito preparado para upload
- [ ] Metadados do livro em mãos (título, autor, etc.)
- [ ] Navegador moderno instalado

**Tudo pronto?** Execute: `./run_app.sh` 🚀

---

## 🎉 Pronto para Começar!

```bash
# Comando mais simples
./run_app.sh

# Ou
streamlit run app_completo.py
```

**Acesse:** http://localhost:8501

**Bom trabalho! 📚✨**

---

*Desenvolvido com ❤️ por Manus AI - Novembro 2025*
