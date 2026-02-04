"""Recipe Unit Converter - Convert between recipe measurement units."""

from .converter import Converter
from .repository import Repository
from .parser import Parser
from .models import (
    ParsedQuery,
    ConversionResult,
    IngredientEntry,
)
from .exceptions import (
    ConverterError,
    ParsingError,
    InvalidConversionError,
    UnitNotFoundError,
    IngredientNotFoundError,
    IngredientAmbiguousError,
)

__version__ = "0.1.0"

__all__ = [
    # Core classes
    "Converter",
    "Repository",
    "Parser",
    # Models
    "ParsedQuery",
    "ConversionResult",
    "IngredientEntry",
    # Exceptions
    "ConverterError",
    "ParsingError",
    "InvalidConversionError",
    "UnitNotFoundError",
    "IngredientNotFoundError",
    "IngredientAmbiguousError",
]
