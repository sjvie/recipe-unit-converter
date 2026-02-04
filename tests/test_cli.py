import pytest
import sys
from io import StringIO
from recipe_unit_converter.cli import main, format_output


class TestCLIFormatting:
    """Test CLI output formatting."""

    def test_format_simple(self):
        from recipe_unit_converter.models import ConversionResult
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
        from recipe_unit_converter.models import ConversionResult
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
        from recipe_unit_converter.models import ConversionResult
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

    def test_format_verbose_without_ingredient(self):
        """Test verbose format without ingredient."""
        from recipe_unit_converter.models import ConversionResult
        result = ConversionResult(
            original_query="1 cup",
            source_unit="cup",
            target_unit="ml",
            result_value=236.588,
            result_unit="ml",
            ingredient=None,
            explanation="Direct conversion"
        )
        output = format_output(result, "verbose")
        assert "236.588 ml" in output
        assert "Direct conversion" in output

    def test_format_invalid_type(self):
        """Test that invalid format type raises ValueError."""
        from recipe_unit_converter.models import ConversionResult
        result = ConversionResult(
            original_query="1 cup",
            source_unit="cup",
            target_unit="ml",
            result_value=236.588,
            result_unit="ml",
            ingredient=None,
            explanation="test"
        )
        with pytest.raises(ValueError, match="Unknown format type"):
            format_output(result, "invalid")


class TestCLIIntegration:
    """Test CLI main function integration."""

    def test_main_success_simple(self, monkeypatch, capsys):
        """Test successful conversion with simple format."""
        import sys
        monkeypatch.setattr(sys, 'argv', ['recipe-convert', '1 cup', '--to', 'ml'])

        try:
            main()
        except SystemExit as e:
            assert e.code == 0

        captured = capsys.readouterr()
        assert "236.588" in captured.out
        assert "ml" in captured.out

    def test_main_success_verbose(self, monkeypatch, capsys):
        """Test successful conversion with verbose format."""
        import sys
        monkeypatch.setattr(sys, 'argv', ['recipe-convert', '2 cups flour', '--to', 'g', '--format', 'verbose'])

        try:
            main()
        except SystemExit as e:
            assert e.code == 0

        captured = capsys.readouterr()
        assert "g" in captured.out
        assert "flour" in captured.out.lower()

    def test_main_success_json(self, monkeypatch, capsys):
        """Test successful conversion with JSON format."""
        import sys
        import json
        monkeypatch.setattr(sys, 'argv', ['recipe-convert', '1 cup water', '--to', 'g', '--format', 'json'])

        try:
            main()
        except SystemExit as e:
            assert e.code == 0

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "result_value" in data
        assert data["result_unit"] == "g"

    def test_main_parsing_error(self, monkeypatch, capsys):
        """Test CLI with invalid query format."""
        import sys
        monkeypatch.setattr(sys, 'argv', ['recipe-convert', 'invalid', '--to', 'g'])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err

    def test_main_unit_not_found(self, monkeypatch, capsys):
        """Test CLI with unknown unit."""
        import sys
        monkeypatch.setattr(sys, 'argv', ['recipe-convert', '1 cup', '--to', 'unknownunit'])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
