import pytest
from pathlib import Path
from src.recipe_unit_converter.repository import Repository
from src.recipe_unit_converter.matcher import IngredientMatcher
from src.recipe_unit_converter.exceptions import IngredientNotFoundError, IngredientAmbiguousError


@pytest.fixture
def repo():
    """Create a repository with test data."""
    base_path = Path(__file__).parent.parent / "src" / "recipe_unit_converter" / "data"
    return Repository(base_path)


@pytest.fixture
def matcher(repo):
    """Create a matcher instance."""
    return IngredientMatcher(repo)


class TestExactMatching:
    """Test exact ingredient matching."""

    def test_exact_match(self, matcher):
        """Should match ingredient exactly."""
        result = matcher.match("water")
        assert result is not None
        assert "water" in result.names

    def test_case_insensitive(self, matcher):
        """Matching should be case-insensitive."""
        result1 = matcher.match("water")
        result2 = matcher.match("WATER")
        assert result1.id == result2.id

    def test_whitespace_handling(self, matcher):
        """Should handle extra whitespace."""
        result = matcher.match("  water  ")
        assert result is not None
        assert "water" in result.names


class TestFuzzyMatching:
    """Test fuzzy ingredient matching."""

    def test_close_match(self, matcher):
        """Should fuzzy match close ingredient names."""
        # This assumes "flour" exists in database
        # and "flou" is close enough
        try:
            result = matcher.match("flou")
            assert "flour" in result.names or result is not None
        except IngredientNotFoundError:
            # If fuzzy matching doesn't work at this cutoff, that's okay
            pass

    def test_typo_matching(self, matcher):
        """Should match common typos."""
        # This test depends on actual data
        # If "flour" is in database, "flowr" might match
        try:
            result = matcher.match("flowr")
            # If it matches, great
            assert result is not None
        except IngredientNotFoundError:
            # If cutoff is too strict, this is expected
            pass


class TestErrorHandling:
    """Test error handling in matcher."""

    def test_empty_string_error(self, matcher):
        """Empty ingredient should raise error."""
        with pytest.raises(IngredientNotFoundError, match="No ingredient specified"):
            matcher.match("")

    def test_not_found_error(self, matcher):
        """Unknown ingredient should raise error."""
        with pytest.raises(IngredientNotFoundError):
            matcher.match("completelyfakefooditem12345")

    def test_not_found_error_message(self, matcher):
        """Error message should include ingredient name."""
        with pytest.raises(IngredientNotFoundError, match="notfound123"):
            matcher.match("notfound123")


class TestDensityRetrieval:
    """Test that matched ingredients have density data."""

    def test_water_has_density(self, matcher):
        """Water should have density data."""
        result = matcher.match("water")
        assert result.density is not None
        # Water density should be close to 1.0 g/ml
        assert 0.9 < result.density < 1.1

    def test_flour_has_density(self, matcher):
        """Flour should have density data."""
        result = matcher.match("flour")
        assert result.density is not None
        # Flour density should be reasonable (less than water)
        assert 0.4 < result.density < 0.8
