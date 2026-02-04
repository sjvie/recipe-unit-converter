import pytest
from pydantic import ValidationError
from src.recipe_unit_converter.models import (
    ParsedQuery,
    ConversionResult,
    IngredientEntry,
    UnitsDb,
    UnitDetail,
)


class TestParsedQuery:
    """Test ParsedQuery model."""

    def test_valid_parsed_query(self):
        """Valid ParsedQuery should initialize correctly."""
        query = ParsedQuery(
            quantity=2.0,
            unit="cup",
            ingredient="flour"
        )
        assert query.quantity == 2.0
        assert query.unit == "cup"
        assert query.ingredient == "flour"

    def test_parsed_query_without_ingredient(self):
        """ParsedQuery should work without ingredient."""
        query = ParsedQuery(
            quantity=1.0,
            unit="tsp"
        )
        assert query.ingredient is None

    def test_parsed_query_missing_required_field(self):
        """Missing required field should raise error."""
        with pytest.raises(ValidationError):
            ParsedQuery(unit="cup", ingredient="flour")  # Missing quantity


class TestConversionResult:
    """Test ConversionResult model."""

    def test_valid_conversion_result(self):
        """Valid ConversionResult should initialize correctly."""
        result = ConversionResult(
            original_query="2 cups flour",
            source_unit="cup",
            target_unit="g",
            result_value=473.176,
            result_unit="g",
            ingredient="flour",
            explanation="Volume to Weight conversion"
        )
        assert result.result_value == 473.176
        assert result.ingredient == "flour"

    def test_conversion_result_without_ingredient(self):
        """ConversionResult should work without ingredient."""
        result = ConversionResult(
            original_query="1 cup",
            source_unit="cup",
            target_unit="ml",
            result_value=236.588,
            result_unit="ml",
            ingredient=None,
            explanation="Direct conversion"
        )
        assert result.ingredient is None

    def test_conversion_result_missing_field(self):
        """Missing required field should raise error."""
        with pytest.raises(ValidationError):
            ConversionResult(
                original_query="2 cups",
                source_unit="cup",
                # Missing target_unit and other required fields
            )


class TestIngredientEntry:
    """Test IngredientEntry model."""

    def test_valid_ingredient(self):
        """Valid ingredient should initialize correctly."""
        ingredient = IngredientEntry(
            id="flour",
            names=["flour", "all-purpose flour"],
            density=0.593
        )
        assert ingredient.id == "flour"
        assert len(ingredient.names) == 2
        assert ingredient.density == 0.593

    def test_ingredient_without_density(self):
        """Ingredient without density should work."""
        ingredient = IngredientEntry(
            id="test",
            names=["test"]
        )
        assert ingredient.density is None

    def test_ingredient_empty_names_list(self):
        """Empty names list should be allowed (no validation constraint)."""
        ingredient = IngredientEntry(id="test", names=[])
        assert ingredient.names == []


class TestUnitDetail:
    """Test UnitDetail model."""

    def test_valid_unit_detail(self):
        """Valid UnitDetail should initialize correctly."""
        unit = UnitDetail(
            factor=236.588,
            aliases=["cup", "cups", "c"]
        )
        assert unit.factor == 236.588
        assert len(unit.aliases) == 3

    def test_unit_detail_type_validation(self):
        """Invalid types should raise error."""
        with pytest.raises(ValidationError):
            UnitDetail(factor="not a number", aliases=["cup"])


class TestUnitsDb:
    """Test UnitsDb model structure."""

    def test_units_db_structure(self):
        """UnitsDb should have required structure."""
        from src.recipe_unit_converter.models import VolumeDefinition, WeightDefinition, TempDefinition

        db = UnitsDb(
            volume=VolumeDefinition(
                base="ml",
                units={"ml": UnitDetail(factor=1.0, aliases=["ml", "milliliter"])}
            ),
            weight=WeightDefinition(
                base="g",
                units={"g": UnitDetail(factor=1.0, aliases=["g", "gram"])}
            ),
            temperature=TempDefinition(
                units={"c": {"aliases": ["c", "celsius"]}}
            )
        )
        assert db.volume.base == "ml"
        assert db.weight.base == "g"
