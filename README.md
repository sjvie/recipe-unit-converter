# Recipe Unit Converter

Convert between recipe measurement units (cups, grams, tablespoons, etc.)

## Installation

```bash
pip install git+https://github.com/sjvie/recipe-unit-converter.git
```

## Usage

### Command Line

```bash
# Simple conversion
recipe-convert "2 cups flour" --to grams

# With different output formats
recipe-convert "100 ml water" --to g --format verbose
recipe-convert "1/4 tsp salt" --to ml --format json
```

Supported quantity formats:
- Numeric: `2`, `1.5`, `1/4`, `1 1/2`
- Natural language: `two cups`, `quarter tsp`, `half a cup`

### Python API

```python
from recipe_unit_converter import Converter, Repository
from pathlib import Path
from importlib.resources import files

# Load data from package
data_path = files('recipe_unit_converter') / 'data'

repo = Repository(data_path)
converter = Converter(repo)
result = converter.convert("2 cups flour", "grams")
print(f"{result.result_value} {result.result_unit}")
```

## Development

```bash
# Clone repository
git clone https://github.com/sjvie/recipe-unit-converter.git
cd recipe-unit-converter

# Install with dev dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Type check
mypy src/recipe_unit_converter/ --strict
```

## License

MIT
