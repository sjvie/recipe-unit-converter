import pytest
import sys
from io import StringIO
from src.recipe_unit_converter.cli import main, format_output


class TestCLIFormatting:
    """Test CLI output formatting."""

    def test_format_simple(self):
        from src.recipe_unit_converter.models import ConversionResult
        result = ConversionResult(
            original_query="2 cups flour",
            source_unit="cup",
            target_unit="g",
            result_value=473.176,
            result_unit="g",
            ingredient="flour",
            explanation="Volume to Weight using density"
        )
        output = format_output(result, "simple")
        assert output == "473.176 g"

    def test_format_verbose(self):
        from src.recipe_unit_converter.models import ConversionResult
        result = ConversionResult(
            original_query="2 cups flour",
            source_unit="cup",
            target_unit="g",
            result_value=473.176,
            result_unit="g",
            ingredient="flour",
            explanation="Volume to Weight using density of flour (0.593 g/ml)"
        )
        output = format_output(result, "verbose")
        assert "473.176 g" in output
        assert "flour" in output
        assert "density" in output.lower()

    def test_format_json(self):
        import json
        from src.recipe_unit_converter.models import ConversionResult
        result = ConversionResult(
            original_query="2 cups flour",
            source_unit="cup",
            target_unit="g",
            result_value=473.176,
            result_unit="g",
            ingredient="flour",
            explanation="Volume to Weight using density"
        )
        output = format_output(result, "json")
        data = json.loads(output)
        assert data["result_value"] == 473.176
        assert data["result_unit"] == "g"
        assert data["ingredient"] == "flour"
