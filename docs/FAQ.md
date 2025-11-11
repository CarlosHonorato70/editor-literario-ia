# FAQ - Perguntas Frequentes

## Geral

### O que é este sistema?
É um sistema automatizado completo para preparação de manuscritos para publicação, que executa as 14 fases do processo editorial, desde o recebimento do manuscrito até a geração dos arquivos prontos para a gráfica.

### Quanto custa?
O sistema é gratuito e open-source. Você pode ter custos com:
- API OpenAI (se usar recursos de IA): ~$2-10 por livro
- Servidor/hospedagem (se necessário)

### Funciona sem internet?
Sim! A maior parte das funcionalidades funciona offline. Apenas os recursos de IA (opcionais) requerem internet.

## Instalação

### Qual versão do Python preciso?
Python 3.8 ou superior. Recomendamos Python 3.10+.

### Posso usar no Windows?
Sim! O sistema funciona em Windows, Linux e macOS.

### Como instalo as dependências?
```bash
pip install -r requirements.txt
```

### O WeasyPrint não instala no Windows
No Windows, use a versão pré-compilada:
```bash
pip install weasyprint --prefer-binary
```

## Uso

### Como processo um manuscrito simples?
```bash
python main.py manuscrito.pdf -o output/
```

### Como uso o workflow completo (14 fases)?
```bash
python complete_workflow.py manuscrito.pdf \
  --title "Título" --author "Autor"
```

### Que formatos de entrada são aceitos?
- PDF (.pdf)
- Microsoft Word (.docx)
- Markdown (.md)
- Texto (.txt)

### Que formatos de saída são gerados?
- Markdown (.md) - sempre
- DOCX (.docx) - se configurado
- PDF (.pdf) - se configurado

### Como customizo o processamento?
Edite ou crie um arquivo YAML em `configs/`:
```yaml
project_name: "Meu Projeto"
enable_ai_enhancement: true
default_format: "A5"
```

## Recursos de IA

### Preciso usar IA?
Não! Os recursos de IA são opcionais. O sistema funciona sem IA, mas com capacidades reduzidas.

### Como configuro a API da OpenAI?
```bash
export OPENAI_API_KEY="sua-chave-aqui"
```

### Quanto custa usar a IA?
Depende do tamanho do manuscrito:
- Livro pequeno (50k palavras): ~$2-5
- Livro médio (100k palavras): ~$5-10
- Livro grande (200k palavras): ~$10-20

### Posso usar outra IA?
Atualmente apenas OpenAI é suportada, mas você pode adaptar o código para outras APIs.

## FastFormat

### O que é FastFormat?
Sistema de tipografia profissional que:
- Converte aspas para aspas tipográficas
- Substitui hífens por travessões corretos
- Padroniza reticências
- Normaliza espaçamento

### Como ativo/desativo FastFormat?
No arquivo de configuração:
```yaml
enable_fastformat: true  # ou false
```

### FastFormat funciona para português?
Sim! Foi desenvolvido especificamente para PT-BR.

## Workflow de 14 Fases

### Quais são as 14 fases?
1. Recebimento do manuscrito
2. Análise estrutural
3. Edição de conteúdo
4. Revisão técnica
5. Formatação tipográfica
6. Aprovação editorial
7. Diagramação
8. Design de capa (5 conceitos)
9. Revisão de provas
10. Geração ISBN e CIP
11. Finalização PDF (miolo)
12. Finalização PDF (capa)
13. Preparação especificações técnicas
14. Pacote para gráfica

### Posso pular fases?
Sim, mas não recomendado. Para pular, use:
```bash
python main.py manuscrito.pdf --skip-phases 3,5,7
```

### Quanto tempo leva o workflow completo?
- Sem IA: 2-4 horas
- Com IA: 4-6 horas
(Depende do tamanho do manuscrito)

## Produção Editorial

### O sistema gera capas automaticamente?
Sim! Gera 5 conceitos de capa profissionais.

### Como funciona a diagramação?
O sistema cria PDF profissional com:
- 300 DPI
- CMYK
- Sangria correta
- Margens padronizadas

### O PDF está pronto para gráfica?
Sim! Inclui:
- PDF do miolo (CMYK, 300 DPI)
- PDF da capa com lombada
- Especificações técnicas
- Arquivo de marcação

### Como personalizo o design?
Edite templates em `templates/` ou ajuste configurações:
```yaml
cover_style: "modern"  # modern, classic, minimalist
layout_style: "elegant"  # elegant, clean, academic
```

## ISBN e CIP

### O sistema gera ISBN real?
Gera um ISBN-13 válido em formato, mas você precisa registrar oficialmente na Câmara Brasileira do Livro (CBL).

### Como obtenho ISBN oficial?
1. Cadastre-se na CBL
2. Solicite ISBN para seu livro
3. Use o ISBN gerado pelo sistema como referência

### O que é CIP?
Catalogação na Publicação - ficha catalográfica que deve ser feita por bibliotecário profissional.

### O sistema gera CIP oficial?
Gera um template de CIP. Para versão oficial, contrate um bibliotecário.

## Elementos Textuais

### O sistema cria glossário automaticamente?
Sim! Extrai 40+ termos do texto e gera definições.

### Como funciona o índice remissivo?
Gera automaticamente 200+ entradas com referências de página.

### Posso editar elementos gerados?
Sim! Todos os arquivos `.md` podem ser editados.

### Como adiciono meus próprios elementos?
Edite templates em `templates/pre_textual/` ou `templates/post_textual/`.

## Configuração

### Onde ficam as configurações?
Em `configs/`:
- `default.yaml` - Padrão
- `academic.yaml` - Livros acadêmicos
- `fiction.yaml` - Ficção/romance
- `technical.yaml` - Manuais técnicos

### Como crio configuração customizada?
```yaml
# configs/minha_config.yaml
project_name: "Meu Projeto"
default_format: "A5"
default_font: "Garamond"
# ... outras configurações
```

Use:
```bash
python main.py manuscrito.pdf -c configs/minha_config.yaml
```

## Testes

### Como testo o sistema?
```bash
python -m unittest discover tests/
```

### Há exemplos de uso?
Sim! Veja `examples/`:
- `example_usage.py`
- `fastformat_example.py`
- `production_example.py`

## Erros Comuns

### "ModuleNotFoundError: No module named X"
```bash
pip install -r requirements.txt
```

### "Error: OpenAI API key not found"
Configure a chave:
```bash
export OPENAI_API_KEY="sua-chave"
```
Ou desabilite IA:
```yaml
enable_ai_enhancement: false
```

### "Permission denied"
Use ambiente virtual ou `--user`:
```bash
pip install -r requirements.txt --user
```

### PDF não gera corretamente
Instale dependências do WeasyPrint:
```bash
# Linux
sudo apt install libcairo2 libpango-1.0-0

# Windows
pip install weasyprint --prefer-binary
```

### Sistema muito lento
1. Desabilite IA se não necessária
2. Reduza qualidade de imagens
3. Processe em partes menores

## Performance

### Como acelero o processamento?
- Desabilite recursos de IA
- Use configuração minimalista
- Processe em paralelo (se múltiplos livros)

### Quanto de RAM preciso?
- Mínimo: 4GB
- Recomendado: 8GB+
- Para livros grandes (500+ páginas): 16GB

## Customização

### Posso modificar o código?
Sim! É open-source. Contribuições são bem-vindas.

### Como adiciono novo módulo?
1. Crie `modules/meu_modulo.py`
2. Implemente funcionalidade
3. Integre em `main.py`

### Como adiciono novo template?
1. Crie arquivo em `templates/`
2. Use sintaxe Jinja2 para variáveis
3. Sistema detecta automaticamente

## Suporte

### Onde obtenho ajuda?
1. Leia documentação em `docs/`
2. Veja exemplos em `examples/`
3. Consulte este FAQ
4. Abra issue no GitHub

### Como reporto bug?
1. Verifique se é problema conhecido
2. Prepare exemplo mínimo reproduzível
3. Abra issue com detalhes:
   - Sistema operacional
   - Versão do Python
   - Mensagem de erro completa
   - Passos para reproduzir

### Como sugiro nova funcionalidade?
Abra issue no GitHub com:
- Descrição detalhada
- Casos de uso
- Benefícios esperados

## Licença e Uso

### Posso usar comercialmente?
Sim! O sistema pode ser usado para projetos comerciais.

### Preciso dar crédito?
Apreciamos crédito, mas não é obrigatório.

### Posso redistribuir?
Sim, mantendo a licença original.

## Roadmap

### Quais novos recursos virão?
- Suporte para mais formatos de entrada
- Mais estilos de capa
- Integração com serviços de impressão
- API REST
- Interface web melhorada

### Como contribuo?
1. Fork o repositório
2. Crie branch para feature
3. Faça commit das mudanças
4. Abra Pull Request

---

**Não encontrou sua pergunta?**

- Consulte documentação completa em `docs/`
- Abra issue no GitHub
- Contate os desenvolvedores
