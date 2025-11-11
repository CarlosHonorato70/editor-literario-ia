# Testes - Sistema de Preparação de Manuscritos

Este diretório contém a suite de testes do sistema.

## Estrutura

- `test_modules.py` - Testes unitários dos módulos principais
- `test_workflow.py` - Testes de integração do workflow completo
- `test_templates.py` - Testes dos templates
- `test_production.py` - Testes dos módulos de produção

## Executar Testes

### Todos os testes
```bash
python -m pytest tests/ -v
```

ou

```bash
python -m unittest discover tests/
```

### Testes específicos
```bash
python tests/test_modules.py
python tests/test_workflow.py
```

### Com cobertura
```bash
pip install pytest-cov
python -m pytest tests/ --cov=modules --cov-report=html
```

## Estrutura dos Testes

### Testes Unitários (`test_modules.py`)
Testa cada módulo individualmente:
- ✅ Config - Configurações do sistema
- ✅ Analyzer - Análise de manuscritos
- ✅ Enhancer - Aprimoramento de conteúdo
- ✅ Formatter - Formatação de documentos
- ✅ Elements - Geração de elementos
- ✅ Reviewer - Revisão editorial
- ✅ Exporter - Exportação de publicações
- ✅ Templates - Validação de templates

### Testes de Integração (`test_workflow.py`)
Testa o fluxo completo:
- ✅ Workflow Orchestrator - Orquestração das 14 fases
- ✅ ISBN/CIP Generator - Geração de ISBN e ficha catalográfica
- ✅ Print Ready Generator - Preparação para impressão
- ✅ Complete Workflow - Fluxo de ponta a ponta

### Testes de Produção (`test_production.py`)
Testa módulos de produção editorial:
- ✅ Cover Designer - Design de capas
- ✅ Layout Engine - Diagramação
- ✅ Materials Generator - Materiais adicionais
- ✅ Proof Checker - Revisão de provas

## Convenções

### Nomenclatura
- Classes de teste: `Test<NomeDoModulo>`
- Métodos de teste: `test_<funcionalidade>`
- Setup: `setUp()` e `tearDown()` para preparação/limpeza

### Estrutura de Teste
```python
class TestModulo(unittest.TestCase):
    def setUp(self):
        """Prepara ambiente de teste."""
        pass
    
    def tearDown(self):
        """Limpa ambiente de teste."""
        pass
    
    def test_funcionalidade(self):
        """Testa funcionalidade específica."""
        # Arrange
        # Act
        # Assert
        pass
```

## Dependências de Teste

```bash
pip install pytest pytest-cov
```

## Cobertura Esperada

- **Módulos principais**: > 80%
- **Workflow**: > 75%
- **Produção**: > 70%
- **Total**: > 75%

## Continuous Integration

Os testes são executados automaticamente em:
- Push para branch principal
- Pull requests
- Releases

## Dados de Teste

Arquivos de teste ficam em `tests/fixtures/`:
- `sample_manuscript.md` - Manuscrito de exemplo
- `sample_config.yaml` - Configuração de teste
- `sample_output/` - Saídas esperadas

## Troubleshooting

### Erro: ModuleNotFoundError
```bash
# Adicione o diretório raiz ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Erro: Dependências faltando
```bash
pip install -r requirements.txt
```

### Testes lentos
```bash
# Execute apenas testes rápidos
python -m pytest tests/ -v -m "not slow"
```

## Contribuindo

Ao adicionar novos recursos:
1. Escreva testes primeiro (TDD)
2. Mantenha cobertura > 75%
3. Use nomenclatura consistente
4. Documente testes complexos
5. Execute suite completa antes de commit
