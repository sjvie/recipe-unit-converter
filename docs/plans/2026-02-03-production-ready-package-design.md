# Production-Ready Package Design

**Date:** 2026-02-03
**Goal:** Make recipe-unit-converter production-ready, git-installable, with extensive tests and enhanced features

## Overview

Transform the current recipe unit converter into a production-ready Python package installable via git, with enhanced parsing capabilities, full type hints, comprehensive testing (95%+ coverage), and a clean CLI interface.

## Package Structure

```
recipe-unit-converter/
├── pyproject.toml          # Modern Python packaging config
├── README.md               # Minimal docs (install + example)
├── LICENSE                 # MIT License
├── src/
│   └── recipe_unit_converter/   # Renamed for pip compatibility (underscores)
│       ├── __init__.py     # Expose public API
│       ├── cli.py          # New CLI entry point
│       ├── converter.py    # Core conversion logic (with type hints)
│       ├── parser.py       # Enhanced with fraction & word number support
│       ├── matcher.py      # Ingredient matching (with type hints)
│       ├── repository.py   # Data loading (with type hints)
│       ├── models.py       # Pydantic models with full type hints
│       ├── exceptions.py   # Custom exceptions
│       └── data/           # Bundled data files
│           ├── units.json
│           └── ingredients.json
└── tests/
    ├── test_converter.py   # Expanded from existing
    ├── test_parser.py      # New: test parsing features
    ├── test_cli.py         # New: test CLI interface
    ├── test_matcher.py     # New: test ingredient matching
    ├── test_repository.py  # New: test data loading
    └── test_models.py      # New: test Pydantic models
```

**Key Changes:**
- Rename `src/` → `src/recipe_unit_converter/` (Python package naming convention)
- Move `data/` into package for bundling
- Remove `main.py`, replace with `cli.py`
- Add comprehensive test files for 95%+ coverage

## Enhanced Features

### 1. Parser Enhancements

**Supported Quantity Formats:**
- **Numeric**: `2`, `1.5`, `1/4`, `1 1/2` (mixed fractions)
- **Word numbers**: `one` through `twenty` (1-20)
- **Special fractions**: `quarter` (0.25), `half` (0.5), `half a` (0.5)

**Syntax Variations:**
- With/without "of": `2 cups water` or `2 cups of water`
- Natural language quantities (tested but not advertised in docs)

**Implementation Details:**
- Word-to-number mapping: `{"one": 1, "two": 2, ..., "twenty": 20, "quarter": 0.25, "half": 0.5}`
- Use Python's `fractions.Fraction` for accurate fraction conversion
- Multi-stage parsing: try numeric first, then word fallback
- Special case handling for "half a"

**Examples:**
```python
"1/4 cup flour" → ParsedQuery(quantity=0.25, unit="cup", ingredient="flour")
"quarter tsp salt" → ParsedQuery(quantity=0.25, unit="tsp", ingredient="salt")
"half a cup sugar" → ParsedQuery(quantity=0.5, unit="cup", ingredient="sugar")
"three tablespoons" → ParsedQuery(quantity=3.0, unit="tbsp", ingredient=None)
"1 1/2 cups" → ParsedQuery(quantity=1.5, unit="cup", ingredient=None)
```

### 2. Type Hints & Validation

**Full Type Hints:**
- All functions, methods, and classes fully type-annotated
- Use `typing` module: `Optional`, `Dict`, `List`, `Tuple`
- Strict mypy checking (`mypy --strict`)

**Enhanced Validation:**
- Input validation at all entry points
- Fail fast with clear error messages
- Runtime validation for JSON data files
- Type checking enforced in CI/dev workflow

**Improved Error Messages:**
- Keep numeric examples only (don't advertise word number support)
- Include context and suggestions:
  - `"Invalid conversion between temperature and weight"`
  - `"Ingredient not found: 'xyz'. Did you mean 'xyx'?"` (fuzzy suggestion)
  - `"Missing unit. Expected format: '<number> <unit> [ingredient]'"`

### 3. CLI Interface

**Command:** `recipe-convert "QUERY" --to TARGET_UNIT [--format FORMAT]`

**Arguments:**
- Positional: Query string (e.g., `"2 cups flour"`)
- Required flag: `--to TARGET_UNIT` (e.g., `grams`, `ml`, `tsp`)
- Optional flag: `--format {simple,verbose,json}` (default: simple)

**Output Formats:**

1. **Simple (default)**: Just value and unit
   ```
   473.176 g
   ```

2. **Verbose**: Include ingredient and explanation
   ```
   473.176 g of flour (Volume to Weight using density of flour (0.593 g/ml))
   ```

3. **JSON**: Full machine-readable output
   ```json
   {
     "original_query": "2 cups flour",
     "source_unit": "cup",
     "target_unit": "g",
     "result_value": 473.176,
     "result_unit": "g",
     "ingredient": "flour",
     "explanation": "Volume to Weight using density of flour (0.593 g/ml)"
   }
   ```

**Error Handling:**
- Print errors to stderr
- Exit with code 1 on error
- Exit with code 0 on success

**Entry Point:**
- Defined in `pyproject.toml`: `recipe-convert = "recipe_unit_converter.cli:main"`
- Available after `pip install`

### 4. Package Configuration (pyproject.toml)

**Build System:**
- Modern `setuptools` backend
- PEP 621 compliant metadata

**Dependencies:**
- Runtime: `pydantic>=2.0.0`
- Dev: `pytest>=7.0.0`, `pytest-cov>=4.0.0`, `mypy>=1.0.0`

**Package Data:**
- Bundle `data/*.json` files with package
- Automatically included in distribution

**Tool Configuration:**
- pytest: testpaths, file patterns
- coverage: 95% minimum, branch coverage enabled, show missing lines
- mypy: strict mode enabled

**Installation:**
```bash
# User installation
pip install git+https://github.com/username/recipe-unit-converter.git

# Development installation
git clone https://github.com/username/recipe-unit-converter.git
cd recipe-unit-converter
pip install -e .[dev]
```

## Testing Strategy (95%+ Coverage)

### Test Coverage by Module

**1. test_parser.py** (covers parser.py)
- All numeric formats: integers, decimals, fractions (1/4), mixed fractions (1 1/2)
- Word numbers: one-twenty, quarter, half, "half a"
- Syntax: with/without "of", with/without ingredient
- Edge cases: invalid fractions (0/0, 1/0), negative numbers, empty input
- Error messages: verify specific error text

**2. test_converter.py** (covers converter.py) - expand existing tests
- All conversion scenarios: temperature, same-category, cross-category
- All error paths: missing ingredient, type mismatches, unknown units
- Edge cases: zero quantities, very large numbers, precision
- Temperature: absolute zero, extreme temps, all unit combinations

**3. test_matcher.py** (covers matcher.py)
- Exact matches, fuzzy matches
- Case sensitivity, plurals, synonyms
- Not found scenarios with suggestions
- Edge cases: empty strings, special characters

**4. test_repository.py** (covers repository.py)
- Successful data loading
- Invalid JSON handling
- Missing data files
- Unit type lookups, factor retrieval
- Edge cases: malformed data

**5. test_cli.py** (covers cli.py)
- All three output formats (simple, verbose, json)
- Argument parsing: valid and invalid inputs
- Error handling and exit codes
- Integration: end-to-end conversions via CLI

**6. test_models.py** (covers models.py)
- Pydantic model validation
- Required vs optional fields
- Type coercion and validation errors
- Edge cases: boundary values

### Coverage Configuration
- Target: 95% minimum (fail build if below)
- Branch coverage enabled
- Show missing lines in reports
- Exclude test files from coverage

## Documentation

### README.md (Minimal)

```markdown
# Recipe Unit Converter

Convert between recipe measurement units (cups, grams, tablespoons, etc.)

## Installation

```bash
pip install git+https://github.com/yourusername/recipe-unit-converter.git
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

### Python API

```python
from recipe_unit_converter import Converter, Repository
from pathlib import Path

# Assuming data is in package
from importlib.resources import files
data_path = files('recipe_unit_converter') / 'data'

repo = Repository(data_path)
converter = Converter(repo)
result = converter.convert("2 cups flour", "grams")
print(f"{result.result_value} {result.result_unit}")
```

## License

MIT
```

### Other Documentation
- Docstrings for all public functions/classes
- Type hints serve as inline documentation
- No extensive API docs (keep it simple for now)

## License

MIT License - permissive, widely compatible

## Implementation Notes

### Word Number Support Philosophy
- Word numbers (one-twenty, quarter, half) are **tested but not advertised**
- Keep error messages and docs focused on numeric input (1, 1.5, 1/4)
- This encourages best practices while supporting natural language input
- Users who discover it naturally will find it works

### Data File Handling
- Move `data/` into `src/recipe_unit_converter/data/`
- Use `importlib.resources` for cross-platform data access
- Bundle data files in package distribution via `package-data` in pyproject.toml

### Backwards Compatibility
- Maintain existing test suite (all tests must still pass)
- Parser changes are additive (existing formats still work)
- API signatures unchanged (Converter, Repository interfaces)

### Migration Path
1. Restructure package (rename src directory)
2. Add pyproject.toml and LICENSE
3. Enhance parser with new features
4. Add full type hints to all modules
5. Create new test files for uncovered modules
6. Implement CLI with output formats
7. Move and bundle data files
8. Write minimal README
9. Verify all tests pass with 95%+ coverage

## Success Criteria

- ✅ Installable via `pip install git+https://...`
- ✅ CLI works: `recipe-convert "2 cups flour" --to grams`
- ✅ Fractions supported: `1/4`, `1 1/2`
- ✅ Word numbers work but not advertised
- ✅ All output formats functional (simple, verbose, json)
- ✅ 95%+ test coverage
- ✅ Full type hints, passes `mypy --strict`
- ✅ Clean error messages
- ✅ Minimal README with examples
- ✅ All existing tests still pass
