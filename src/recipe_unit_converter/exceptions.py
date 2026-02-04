class ConverterError(Exception):
    """Base exception for the converter."""
    pass


class UnitNotFoundError(ConverterError):
    """Raised when source or target unit is unknown."""
    pass


class IngredientAmbiguousError(ConverterError):
    """Raised when fuzzy matching returns multiple close results."""
    pass


class IngredientNotFoundError(ConverterError):
    """Raised when no density data is found for a specific conversion."""
    pass


class InvalidConversionError(ConverterError):
    """Raised when trying to convert incompatible types (e.g., Temp to Weight)."""
    pass


class ParsingError(ConverterError):
    """Raised when the input string cannot be parsed."""
    pass
