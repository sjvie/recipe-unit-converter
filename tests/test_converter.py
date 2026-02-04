import pytest
from pathlib import Path
from src.repository import Repository
from src.converter import Converter
from src.exceptions import InvalidConversionError, ParsingError, IngredientNotFoundError


@pytest.fixture
def repo():
    """Create a repository with test data."""
    base_path = Path(__file__).parent.parent / "data"
    return Repository(base_path)


@pytest.fixture
def converter(repo):
    """Create a converter instance."""
    return Converter(repo)


class TestTemperatureConversions:
    """Test temperature conversion scenarios."""

    def test_celsius_to_fahrenheit(self, converter):
        result = converter.convert("100 c", "f")
        assert result.result_value == 212.0
        assert result.result_unit == "f"
        assert "Temperature converted" in result.explanation

    def test_fahrenheit_to_celsius(self, converter):
        result = converter.convert("32 f", "c")
        assert result.result_value == 0.0
        assert result.result_unit == "c"

    def test_celsius_to_kelvin(self, converter):
        result = converter.convert("0 c", "k")
        assert result.result_value == 273.15
        assert result.result_unit == "k"

    def test_kelvin_to_celsius(self, converter):
        result = converter.convert("273.15 k", "c")
        assert result.result_value == 0.0
        assert result.result_unit == "c"

    def test_fahrenheit_to_kelvin(self, converter):
        result = converter.convert("32 f", "k")
        assert abs(result.result_value - 273.15) < 0.01
        assert result.result_unit == "k"

    def test_temperature_to_weight_error(self, converter):
        """Temperature cannot be converted to weight."""
        with pytest.raises(InvalidConversionError):
            converter.convert("100 c", "g")

    def test_weight_to_temperature_error(self, converter):
        """Weight cannot be converted to temperature."""
        with pytest.raises(InvalidConversionError):
            converter.convert("100 g flour", "f")


class TestSameCategoryConversions:
    """Test linear conversions within the same category."""

    def test_cups_to_ml(self, converter):
        """Convert cups to milliliters."""
        result = converter.convert("1 cup", "ml")
        # 1 cup = 236.588 ml
        assert abs(result.result_value - 236.588) < 0.01
        assert result.result_unit == "ml"
        assert result.ingredient is None

    def test_tbsp_to_tsp(self, converter):
        """Convert tablespoons to teaspoons."""
        result = converter.convert("1 tbsp", "tsp")
        # 1 tbsp = 3 tsp
        assert result.result_value == 3.0
        assert result.result_unit == "tsp"

    def test_grams_to_kg(self, converter):
        """Convert grams to kilograms."""
        result = converter.convert("1000 g", "kg")
        assert result.result_value == 1.0
        assert result.result_unit == "kg"

    def test_oz_to_lb(self, converter):
        """Convert ounces to pounds."""
        result = converter.convert("16 oz", "lb")
        assert result.result_value == 1.0
        assert result.result_unit == "lb"

    def test_liters_to_cups(self, converter):
        """Convert liters to cups."""
        result = converter.convert("1 l", "cup")
        # 1 L = 1000 ml, 1 cup = 236.588 ml
        expected = 1000 / 236.588
        assert abs(result.result_value - expected) < 0.01
        assert result.result_unit == "cup"


class TestCrossCategoryConversions:
    """Test conversions requiring density (volume to weight, weight to volume)."""

    def test_cups_flour_to_grams(self, converter):
        """Convert cups of flour to grams."""
        result = converter.convert("1 cup flour", "g")
        # 1 cup = 236.588 ml, flour density varies but should be reasonable
        assert result.result_value > 0
        assert result.result_unit == "g"
        assert result.ingredient == "flour"
        assert "density" in result.explanation.lower()

    def test_ml_water_to_grams(self, converter):
        """Convert milliliters of water to grams."""
        result = converter.convert("100 ml water", "g")
        # Water density = 0.997 g/ml (actual density in database)
        expected = 100.0 * 0.997
        assert abs(result.result_value - expected) < 0.1
        assert result.result_unit == "g"
        assert result.ingredient == "water"

    def test_grams_sugar_to_cups(self, converter):
        """Convert grams of sugar to cups."""
        result = converter.convert("200 g sugar", "cup")
        assert result.result_value > 0
        assert result.result_unit == "cup"
        assert result.ingredient == "sugar"

    def test_cross_category_without_ingredient_error(self, converter):
        """Cross-category conversion requires ingredient."""
        with pytest.raises(InvalidConversionError, match="Ingredient must be specified"):
            converter.convert("100 ml", "g")

    def test_cross_category_unknown_ingredient_error(self, converter):
        """Unknown ingredient should raise error."""
        with pytest.raises(IngredientNotFoundError):
            converter.convert("100 ml unknownfooditem", "g")


class TestParsingAndEdgeCases:
    """Test parsing and edge cases."""

    def test_decimal_quantities(self, converter):
        """Handle decimal quantities."""
        result = converter.convert("2.5 cup", "ml")
        expected = 2.5 * 236.588
        assert abs(result.result_value - expected) < 0.01

    def test_parse_with_of_keyword(self, converter):
        """Handle 'of' keyword in query."""
        # When converting within same category (cup to ml), ingredient is parsed but not used
        result = converter.convert("1 cup of water", "ml")
        assert result.result_value > 0
        # For same-category conversions, ingredient is not preserved in result
        assert result.ingredient is None

        # Test cross-category conversion with 'of' keyword
        result2 = converter.convert("1 cup of water", "g")
        assert result2.ingredient == "water"

    def test_invalid_query_format(self, converter):
        """Invalid query format should raise ParsingError."""
        with pytest.raises(ParsingError):
            converter.convert("invalid query", "g")

    def test_case_insensitive_units(self, converter):
        """Units should be case insensitive."""
        result1 = converter.convert("1 CUP", "ML")
        result2 = converter.convert("1 cup", "ml")
        assert abs(result1.result_value - result2.result_value) < 0.01

    def test_result_rounding(self, converter):
        """Results should be rounded to 4 decimal places."""
        result = converter.convert("1 cup", "ml")
        # Check that result has at most 4 decimal places
        decimal_places = len(str(result.result_value).split('.')[-1])
        assert decimal_places <= 4


class TestConversionResultModel:
    """Test that conversion results contain expected data."""

    def test_result_contains_original_query(self, converter):
        query = "2 cups flour"
        result = converter.convert(query, "g")
        assert result.original_query == query

    def test_result_contains_units(self, converter):
        result = converter.convert("1 cup", "ml")
        assert result.source_unit == "cup"
        assert result.target_unit == "ml"

    def test_result_contains_explanation(self, converter):
        result = converter.convert("1 cup", "ml")
        assert len(result.explanation) > 0
        assert isinstance(result.explanation, str)
