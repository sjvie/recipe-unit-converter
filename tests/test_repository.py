import pytest
from pathlib import Path
from recipe_unit_converter.repository import Repository
from recipe_unit_converter.exceptions import UnitNotFoundError


@pytest.fixture
def repo():
    """Create a repository with test data."""
    base_path = Path(__file__).parent.parent / "src" / "recipe_unit_converter" / "data"
    return Repository(base_path)


class TestDataLoading:
    """Test data loading and initialization."""

    def test_repository_initializes(self, repo):
        """Repository should load data successfully."""
        assert repo.units_db is not None
        assert len(repo.ingredients) > 0

    def test_units_db_has_volume(self, repo):
        """Units database should contain volume units."""
        assert "cup" in repo.units_db.volume.units
        assert "ml" in repo.units_db.volume.units

    def test_units_db_has_weight(self, repo):
        """Units database should contain weight units."""
        assert "g" in repo.units_db.weight.units
        assert "kg" in repo.units_db.weight.units

    def test_units_db_has_temperature(self, repo):
        """Units database should contain temperature units."""
        assert "c" in repo.units_db.temperature.units
        assert "f" in repo.units_db.temperature.units

    def test_ingredients_loaded(self, repo):
        """Ingredients should be loaded."""
        assert len(repo.ingredients) > 0
        # Check for common ingredient
        names = repo.get_all_ingredient_names()
        assert "water" in names or "flour" in names


class TestUnitResolution:
    """Test unit alias resolution."""

    def test_canonical_unit(self, repo):
        """Canonical unit names should resolve."""
        assert repo.get_unit_type("cup") == "volume"
        assert repo.get_unit_type("g") == "weight"

    def test_unit_alias(self, repo):
        """Unit aliases should resolve to canonical form."""
        # "cups" is alias for "cup"
        assert repo.get_unit_type("cups") == "volume"

    def test_case_insensitive(self, repo):
        """Unit resolution should be case-insensitive."""
        assert repo.get_unit_type("CUP") == "volume"
        assert repo.get_unit_type("Cup") == "volume"

    def test_unknown_unit_error(self, repo):
        """Unknown units should raise error."""
        with pytest.raises(UnitNotFoundError):
            repo.get_unit_type("unknownunit")


class TestFactorRetrieval:
    """Test conversion factor retrieval."""

    def test_get_factor_volume(self, repo):
        """Should retrieve volume unit factors."""
        factor = repo.get_factor("cup")
        assert factor > 0
        # 1 cup = 236.588 ml
        assert abs(factor - 236.588) < 0.01

    def test_get_factor_weight(self, repo):
        """Should retrieve weight unit factors."""
        factor = repo.get_factor("kg")
        assert factor == 1000.0  # 1 kg = 1000 g

    def test_get_factor_temperature_error(self, repo):
        """Temperature units should not have linear factors."""
        with pytest.raises(UnitNotFoundError):
            repo.get_factor("c")


class TestIngredientLookup:
    """Test ingredient lookup functionality."""

    def test_get_ingredient_exact_match(self, repo):
        """Should find ingredient by exact name."""
        ingredient = repo.get_ingredient_by_name("water")
        assert ingredient is not None
        assert "water" in ingredient.names

    def test_get_ingredient_case_insensitive(self, repo):
        """Ingredient lookup should be case-insensitive."""
        ing1 = repo.get_ingredient_by_name("water")
        ing2 = repo.get_ingredient_by_name("WATER")
        assert ing1 == ing2

    def test_get_ingredient_not_found(self, repo):
        """Should return None for unknown ingredients."""
        ingredient = repo.get_ingredient_by_name("unknowningredient123")
        assert ingredient is None

    def test_get_all_ingredient_names(self, repo):
        """Should return all ingredient name aliases."""
        names = repo.get_all_ingredient_names()
        assert len(names) > 0
        assert all(isinstance(name, str) for name in names)
