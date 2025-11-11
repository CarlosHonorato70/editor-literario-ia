# Template: Diagrama de Fluxo

```mermaid
graph TD
    A[{{start_node}}] --> B{{{decision_node}}}
    B -->|Sim| C[{{yes_path}}]
    B -->|Não| D[{{no_path}}]
    C --> E[{{end_node}}]
    D --> E
```

## Informações de Uso

Este template é utilizado para gerar diagramas de fluxo usando Mermaid.

### Variáveis Disponíveis:
- `{{start_node}}` - Nó inicial
- `{{decision_node}}` - Ponto de decisão
- `{{yes_path}}` - Caminho positivo
- `{{no_path}}` - Caminho negativo
- `{{end_node}}` - Nó final

### Exemplo de Uso:
```python
template_vars = {
    'start_node': 'Receber Manuscrito',
    'decision_node': 'Formato Adequado?',
    'yes_path': 'Processar',
    'no_path': 'Converter Formato',
    'end_node': 'Manuscrito Processado'
}
```

### Notas:
- Utiliza sintaxe Mermaid para diagramas
- Pode ser renderizado em PNG, SVG ou PDF
- Suporta diagramas complexos com múltiplos níveis
