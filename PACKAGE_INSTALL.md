# Installation Guide - Blackbelt Platform

## Overview

The Blackbelt Platform (@CarlosHonorato70/blackbelt-platform) is now available as a Python package that can be installed using pip.

## Requirements

- Python 3.11 or higher
- pip (Python package manager)

## Installation Methods

### 1. Install from Source (Development)

Clone the repository and install in editable mode:

```bash
# Clone the repository
git clone https://github.com/CarlosHonorato70/editor-literario-ia.git
cd editor-literario-ia

# Install in editable mode
pip install -e .
```

### 2. Install from PyPI (Coming Soon)

Once published to PyPI, you'll be able to install with:

```bash
pip install blackbelt-platform
```

## Verify Installation

After installation, verify that the package is working:

```bash
# Check command-line tools
manuscript-publisher --help
complete-workflow --help

# Test Python import
python -c "import blackbelt_platform; print(f'Version: {blackbelt_platform.__version__}')"
```

Expected output:
```
Version: 2.0.0
```

## Using the Package

### Command-Line Interface

#### 1. Manuscript Publisher

Process a manuscript with the complete editorial workflow:

```bash
manuscript-publisher manuscrito.pdf -o output/
```

With custom configuration:
```bash
manuscript-publisher manuscrito.docx -o output/ -c configs/academic.yaml
```

Interactive mode:
```bash
manuscript-publisher --interactive
```

#### 2. Complete Workflow

Run the complete 14-phase workflow from manuscript to print:

```bash
complete-workflow manuscrito.pdf \
  --title "Meu Livro" \
  --author "Nome do Autor" \
  --genre "Ficção" \
  --pages 300
```

### Python API

Use the package in your Python code:

```python
from blackbelt_platform import ManuscriptPublisher
from modules.config import Config

# Create publisher with default config
publisher = ManuscriptPublisher()

# Or with custom config
config = Config()
config.openai_model = "gpt-4"
publisher = ManuscriptPublisher(config)

# Process manuscript
results = publisher.process_manuscript(
    input_path="manuscrito.pdf",
    output_path="output/"
)

# Check results
if "error" not in results:
    print("Success!")
    print(f"Word count: {results['analysis']['word_count']}")
```

### Streamlit App

Run the Streamlit web interface:

```bash
streamlit run blackbelt_platform/app_editor.py
```

Or from the repository root:
```bash
streamlit run app_editor.py
```

## Package Structure

```
blackbelt-platform/
├── blackbelt_platform/      # Main package
│   ├── __init__.py
│   ├── main.py             # Manuscript publisher
│   ├── complete_workflow.py # Complete workflow script
│   ├── app_editor.py       # Streamlit app
│   └── fastformat.py       # Typography tools
├── modules/                # Core modules
│   ├── analyzer.py
│   ├── enhancer.py
│   ├── formatter.py
│   ├── elements.py
│   ├── reviewer.py
│   ├── exporter.py
│   └── production/        # Production modules
│       ├── cover_designer.py
│       ├── layout_engine.py
│       └── materials_generator.py
├── configs/               # Configuration templates
├── examples/              # Usage examples
└── templates/             # Document templates
```

## Dependencies

The package automatically installs all required dependencies:

- streamlit>=1.25.0 - Web interface
- python-docx>=0.8.11 - DOCX processing
- PyPDF2>=3.0.0 - PDF processing
- openai>=1.0.0 - AI enhancement
- WeasyPrint>=60.0 - Professional PDF generation
- reportlab>=4.0.0 - PDF creation
- And more...

See `pyproject.toml` for the complete list.

## Development Installation

For development with additional tools:

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

This includes:
- pytest - Testing framework
- black - Code formatter
- flake8 - Code linter
- mypy - Type checker

## Troubleshooting

### Import Errors

If you get import errors, ensure you installed the package:

```bash
pip install -e .
```

### Command Not Found

If commands are not found, ensure pip's bin directory is in your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### Missing Dependencies

If dependencies are missing:

```bash
pip install -r requirements.txt
```

## Next Steps

- Read the [README.md](README.md) for feature overview
- Check [WORKFLOW_COMPLETO.md](WORKFLOW_COMPLETO.md) for the complete workflow guide
- See [QUICKSTART.md](QUICKSTART.md) for quick start examples
- Review [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) for system architecture

## Publishing to PyPI (For Maintainers)

To publish the package to PyPI:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI (requires credentials)
python -m twine upload dist/*
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/CarlosHonorato70/editor-literario-ia/issues
- Documentation: See the `docs/` directory

## License

MIT License - See [LICENSE](LICENSE) for details
