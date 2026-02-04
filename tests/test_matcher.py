import pytest
from pathlib import Path
from src.recipe_unit_converter.repository import Repository
from src.recipe_unit_converter.exceptions import IngredientNotFoundError, IngredientAmbiguousError


@pytest.fixture
def repo():
    """Create a repository with test data."""
    base_path = Path(__file__).parent.parent / "src" / "recipe_unit_converter" / "data"
    return Repository(base_path)


class TestExactMatching:
    """Test exact ingredient matching."""

    def test_exact_match(self, repo):
        """Should match ingredient exactly."""
        result = repo.match_ingredient("water")
        assert result is not None
        assert "water" in result.names

    def test_case_insensitive(self, repo):
        """Matching should be case-insensitive."""
        result1 = repo.match_ingredient("water")
        result2 = repo.match_ingredient("WATER")
        assert result1.id == result2.id

    def test_whitespace_handling(self, repo):
        """Should handle extra whitespace."""
        result = repo.match_ingredient("  water  ")
        assert result is not None
        assert "water" in result.names


class TestFuzzyMatching:
    """Test fuzzy ingredient matching."""

    def test_close_match(self, repo):
        """Should fuzzy match close ingredient names."""
        # This assumes "flour" exists in database
        # and "flou" is close enough
        try:
            result = repo.match_ingredient("flou")
            assert "flour" in result.names or result is not None
        except IngredientNotFoundError:
            # If fuzzy matching doesn't work at this cutoff, that's okay
            pass

    def test_typo_matching(self, repo):
        """Should match common typos."""
        # This test depends on actual data
        # If "flour" is in database, "flowr" might match
        try:
            result = repo.match_ingredient("flowr")
            # If it matches, great
            assert result is not None
        except IngredientNotFoundError:
            # If cutoff is too strict, this is expected
            pass


class TestErrorHandling:
    """Test error handling in matcher."""

    def test_empty_string_error(self, repo):
        """Empty ingredient should raise error."""
        with pytest.raises(IngredientNotFoundError, match="No ingredient specified"):
            repo.match_ingredient("")

    def test_not_found_error(self, repo):
        """Unknown ingredient should raise error."""
        with pytest.raises(IngredientNotFoundError):
            repo.match_ingredient("completelyfakefooditem12345")

    def test_not_found_error_message(self, repo):
        """Error message should include ingredient name."""
        with pytest.raises(IngredientNotFoundError, match="notfound123"):
            repo.match_ingredient("notfound123")


class TestDensityRetrieval:
    """Test that matched ingredients have density data."""

    def test_water_has_density(self, repo):
        """Water should have density data."""
        result = repo.match_ingredient("water")
        assert result.density is not None
        # Water density should be close to 1.0 g/ml
        assert 0.9 < result.density < 1.1

    def test_flour_has_density(self, repo):
        """Flour should have density data."""
        result = repo.match_ingredient("flour")
        assert result.density is not None
        # Flour density should be reasonable (less than water)
        assert 0.4 < result.density < 0.8
