# Templates de Documentos

Este diretório contém templates para os elementos pré-textuais, pós-textuais e diagramas do sistema de preparação de manuscritos.

## Estrutura

### `pre_textual/`
Templates para elementos que aparecem antes do conteúdo principal:
- `folha_rosto.md` - Folha de rosto do livro
- `dedicatoria.md` - Página de dedicatória
- `agradecimentos.md` - Página de agradecimentos
- `prefacio.md` - Prefácio da obra
- `ficha_catalografica.md` - Ficha catalográfica (CIP)
- `sumario.md` - Sumário/Índice

### `post_textual/`
Templates para elementos que aparecem após o conteúdo principal:
- `glossario.md` - Glossário de termos (40+ entradas)
- `indice_remissivo.md` - Índice remissivo (200+ entradas)
- `referencias.md` - Referências bibliográficas (ABNT)
- `apendices.md` - Apêndices
- `sobre_autor.md` - Biografia do autor

### `diagrams/`
Templates para diagramas e elementos visuais:
- Diagramas de fluxo
- Organogramas
- Gráficos
- Tabelas formatadas

## Como Usar

Os templates utilizam a sintaxe Jinja2 para substituição de variáveis:

```python
from jinja2 import Template

# Carregar template
with open('templates/pre_textual/folha_rosto.md', 'r') as f:
    template = Template(f.read())

# Renderizar com dados
output = template.render(
    title="Meu Livro",
    author="Nome do Autor",
    publisher="Minha Editora",
    city="São Paulo",
    year=2025
)
```

## Personalização

Todos os templates podem ser personalizados:

1. Edite os arquivos `.md` diretamente
2. Adicione novas variáveis `{{variable_name}}`
3. Ajuste a formatação conforme necessário
4. O sistema detectará automaticamente as mudanças

## Padrões de Formatação

- **Markdown** para estrutura e conteúdo
- **HTML/CSS** para formatação avançada (quando necessário)
- **Variáveis Jinja2** para dados dinâmicos: `{{variable}}`
- **ABNT** para referências bibliográficas

## Validação

O sistema valida automaticamente:
- Presença de todas as variáveis requeridas
- Formatação correta dos templates
- Consistência entre templates
- Padrões ABNT para referências
