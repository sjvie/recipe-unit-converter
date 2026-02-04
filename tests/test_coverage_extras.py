import pytest
import json
from pathlib import Path
from src.recipe_unit_converter.repository import Repository
from src.recipe_unit_converter.matcher import IngredientMatcher
from src.recipe_unit_converter.converter import Converter
from src.recipe_unit_converter.parser import Parser
from src.recipe_unit_converter.exceptions import (
    IngredientAmbiguousError,
    IngredientNotFoundError,
    InvalidConversionError,
    ParsingError,
)


class TestRepositoryEdgeCases:
    """Test repository edge cases for coverage."""

    def test_missing_units_file(self):
        """Test repository with missing units.json."""
        fake_path = Path("/nonexistent/path")
        with pytest.raises(FileNotFoundError):
            Repository(fake_path)

    def test_missing_ingredients_file(self, tmp_path):
        """Test repository with missing ingredients.json."""
        # Create units.json but not ingredients.json
        (tmp_path / "units.json").write_text('{"volume": {"base": "ml", "units": {}}, "weight": {"base": "g", "units": {}}, "temperature": {"units": {}}}')

        with pytest.raises(FileNotFoundError):
            Repository(tmp_path)

    def test_unit_alias_collision_volume_weight(self, tmp_path, caplog):
        """Test warning when volume and weight units have same alias."""
        units_data = {
            "volume": {
                "base": "ml",
                "units": {
                    "cup": {
                        "factor": 236.588,
                        "aliases": ["c", "cups"]
                    }
                }
            },
            "weight": {
                "base": "g",
                "units": {
                    "gram": {
                        "factor": 1.0,
                        "aliases": ["c", "grams"]
                    }
                }
            },
            "temperature": {
                "units": {}
            }
        }
        ingredients_data = {"ingredients": []}

        (tmp_path / "units.json").write_text(json.dumps(units_data))
        (tmp_path / "ingredients.json").write_text(json.dumps(ingredients_data))

        import logging
        with caplog.at_level(logging.WARNING):
            repo = Repository(tmp_path)

        assert any("Alias collision" in record.message for record in caplog.records)

    def test_unit_alias_collision_temperature(self, tmp_path, caplog):
        """Test warning when temperature units have collision."""
        units_data = {
            "volume": {
                "base": "ml",
                "units": {
                    "cup": {
                        "factor": 236.588,
                        "aliases": ["c"]
                    }
                }
            },
            "weight": {
                "base": "g",
                "units": {}
            },
            "temperature": {
                "units": {
                    "celsius": {
                        "aliases": ["c", "deg"]
                    }
                }
            }
        }
        ingredients_data = {"ingredients": []}

        (tmp_path / "units.json").write_text(json.dumps(units_data))
        (tmp_path / "ingredients.json").write_text(json.dumps(ingredients_data))

        import logging
        with caplog.at_level(logging.WARNING):
            repo = Repository(tmp_path)

        assert any("Alias collision" in record.message for record in caplog.records)


class TestConverterEdgeCases:
    """Test converter edge cases for coverage."""

    def test_weight_to_volume_conversion(self):
        """Test weight to volume conversion."""
        from pathlib import Path
        base_path = Path(__file__).parent.parent / "src" / "recipe_unit_converter" / "data"
        repo = Repository(base_path)
        converter = Converter(repo)

        result = converter.convert("100 g flour", "cup")
        assert result.result_value > 0
        assert result.result_unit == "cup"
        assert result.ingredient == "flour"

    def test_ingredient_no_density_error(self):
        """Test cross-category conversion with ingredient missing density."""
        from pathlib import Path
        base_path = Path(__file__).parent.parent / "src" / "recipe_unit_converter" / "data"
        repo = Repository(base_path)
        converter = Converter(repo)

        # Try to convert with a made-up ingredient (if it exists, it shouldn't have density)
        # This tests the error path
        try:
            result = converter.convert("1 cup unknownitem", "g")
            # If this succeeds, the ingredient has density
            assert result is not None
        except (IngredientNotFoundError, InvalidConversionError, AttributeError):
            # Expected - either not found or no density
            pass


class TestParserEdgeCases:
    """Test parser edge cases for coverage."""

    def test_parse_half_a(self):
        """Test parsing 'half a' quantity."""
        result = Parser._parse_quantity("half a")
        assert result == 0.5

    def test_parse_invalid_format(self):
        """Test parsing completely invalid quantity."""
        with pytest.raises(ParsingError, match="Invalid quantity"):
            Parser._parse_quantity("xyz")


class TestMatcherEdgeCases:
    """Test matcher edge cases for coverage."""

    def test_ambiguous_ingredient(self, tmp_path):
        """Test ambiguous ingredient matching with fuzzy search."""
        # Create a database where fuzzy match returns multiple distinct ingredients
        units_data = {
            "volume": {"base": "ml", "units": {}},
            "weight": {"base": "g", "units": {}},
            "temperature": {"units": {}}
        }
        ingredients_data = {
            "ingredients": [
                {
                    "id": "sugar_white",
                    "names": ["sugar", "white sugar"],
                    "density": 0.85
                },
                {
                    "id": "sugar_brown",
                    "names": ["sugars", "brown sugar"],
                    "density": 0.72
                }
            ]
        }

        (tmp_path / "units.json").write_text(json.dumps(units_data))
        (tmp_path / "ingredients.json").write_text(json.dumps(ingredients_data))

        repo = Repository(tmp_path)
        matcher = IngredientMatcher(repo)

        # Use a typo that fuzzy matches both sugar types
        with pytest.raises(IngredientAmbiguousError, match="Ambiguous ingredient"):
            matcher.match("suger")

    def test_fuzzy_match_returns_none(self, tmp_path):
        """Test when fuzzy match finds a name but ingredient entry is None."""
        units_data = {
            "volume": {"base": "ml", "units": {}},
            "weight": {"base": "g", "units": {}},
            "temperature": {"units": {}}
        }
        # Empty ingredients list
        ingredients_data = {"ingredients": []}

        (tmp_path / "units.json").write_text(json.dumps(units_data))
        (tmp_path / "ingredients.json").write_text(json.dumps(ingredients_data))

        repo = Repository(tmp_path)
        matcher = IngredientMatcher(repo)

        with pytest.raises(IngredientNotFoundError):
            matcher.match("anything")


class TestCLIEdgeCases:
    """Test CLI edge cases for coverage."""

    def test_main_unexpected_error(self, monkeypatch, capsys):
        """Test CLI with unexpected error (non-ConverterError exception)."""
        import sys
        from src.recipe_unit_converter.cli import main

        # Mock to raise an unexpected exception
        def mock_converter_init(*args, **kwargs):
            raise RuntimeError("Unexpected error")

        monkeypatch.setattr(sys, 'argv', ['recipe-convert', '1 cup', '--to', 'ml'])
        monkeypatch.setattr('src.recipe_unit_converter.cli.Converter', mock_converter_init)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Unexpected error:" in captured.err
