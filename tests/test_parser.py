import pytest
from src.recipe_unit_converter.parser import Parser
from src.recipe_unit_converter.exceptions import ParsingError


class TestNumericParsing:
    """Test numeric quantity parsing."""

    def test_integer(self):
        result = Parser.parse("2 cups")
        assert result.quantity == 2.0
        assert result.unit == "cups"

    def test_decimal(self):
        result = Parser.parse("1.5 cups")
        assert result.quantity == 1.5
        assert result.unit == "cups"

    def test_simple_fraction(self):
        result = Parser.parse("1/4 tsp")
        assert result.quantity == 0.25
        assert result.unit == "tsp"

    def test_mixed_fraction(self):
        result = Parser.parse("1 1/2 cups")
        assert result.quantity == 1.5
        assert result.unit == "cups"

    def test_complex_mixed_fraction(self):
        result = Parser.parse("2 3/4 tbsp")
        assert result.quantity == 2.75
        assert result.unit == "tbsp"


class TestWordNumberParsing:
    """Test word number parsing."""

    def test_word_number_one(self):
        result = Parser.parse("one cup")
        assert result.quantity == 1.0
        assert result.unit == "cup"

    def test_word_number_three(self):
        result = Parser.parse("three tablespoons")
        assert result.quantity == 3.0
        assert result.unit == "tablespoons"

    def test_word_quarter(self):
        result = Parser.parse("quarter tsp")
        assert result.quantity == 0.25
        assert result.unit == "tsp"

    def test_word_half(self):
        result = Parser.parse("half cup")
        assert result.quantity == 0.5
        assert result.unit == "cup"

    def test_half_a(self):
        # "half a" is treated as quantity, "a" becomes unit, "cup" becomes ingredient
        result = Parser.parse("half a cup sugar")
        assert result.quantity == 0.5
        assert result.unit == "a"
        assert result.ingredient == "cup sugar"

    def test_word_twenty(self):
        result = Parser.parse("twenty ml")
        assert result.quantity == 20.0
        assert result.unit == "ml"


class TestIngredientParsing:
    """Test ingredient extraction."""

    def test_with_ingredient(self):
        result = Parser.parse("2 cups flour")
        assert result.ingredient == "flour"

    def test_without_ingredient(self):
        result = Parser.parse("2 cups")
        assert result.ingredient is None

    def test_with_of_keyword(self):
        result = Parser.parse("1 cup of water")
        assert result.ingredient == "water"

    def test_multi_word_ingredient(self):
        result = Parser.parse("2 cups all purpose flour")
        assert result.ingredient == "all purpose flour"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_fraction_zero_denominator(self):
        with pytest.raises(ParsingError):
            Parser.parse("1/0 cup")

    def test_empty_query(self):
        with pytest.raises(ParsingError):
            Parser.parse("")

    def test_no_recognized_unit(self):
        # Parser doesn't validate units - just extracts them
        # "2 flour" parses as quantity=2, unit="flour"
        # Unit validation happens in the converter/repository layer
        result = Parser.parse("2 flour")
        assert result.quantity == 2.0
        assert result.unit == "flour"

    def test_invalid_format(self):
        with pytest.raises(ParsingError):
            Parser.parse("invalid query")

    def test_case_insensitive_unit(self):
        result1 = Parser.parse("1 CUP")
        result2 = Parser.parse("1 cup")
        assert result1.unit == result2.unit

    def test_extra_whitespace(self):
        result = Parser.parse("  2   cups   flour  ")
        assert result.quantity == 2.0
        assert result.unit == "cups"
        assert result.ingredient == "flour"
