import difflib
from .repository import Repository
from .models import IngredientEntry
from .exceptions import IngredientNotFoundError, IngredientAmbiguousError


class IngredientMatcher:
    def __init__(self, repo: Repository):
        self.repo = repo


    def match(self, input_name: str) -> IngredientEntry:
        if not input_name:
            raise IngredientNotFoundError("No ingredient specified for density conversion.")

        cleaned_input = input_name.lower().strip()

        # 1. Exact Match
        exact = self.repo.get_ingredient_by_name(cleaned_input)
        if exact is not None:
            return exact

        # 2. Fuzzy Match
        all_names = self.repo.get_all_ingredient_names()
        matches = difflib.get_close_matches(cleaned_input, all_names, n=3, cutoff=0.6)

        if not matches:
            raise IngredientNotFoundError(f"Ingredient '{input_name}' not found in database.")
        
        ingredient_entries = [self.repo.get_ingredient_by_name(name) for name in matches]
        
        # check if multiple distinct ingredients matched
        if len(set(ie.id for ie in ingredient_entries if ie is not None)) > 1:
            raise IngredientAmbiguousError(
                f"Ambiguous ingredient '{input_name}'. Close matches: {', '.join(matches)}"
            )
        ingredient_entry = ingredient_entries[0]
        if ingredient_entry is None:
            raise IngredientNotFoundError(f"Ingredient '{input_name}' not found in database.")
        return ingredient_entry
