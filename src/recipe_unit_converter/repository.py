import json
import logging
import difflib
from pathlib import Path
from typing import List, Dict, Any

from .models import UnitsDb, IngredientEntry
from .exceptions import UnitNotFoundError, IngredientNotFoundError, IngredientAmbiguousError

logger = logging.getLogger(__name__)


class Repository:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir: Path = data_dir
        self.units_db: UnitsDb
        self.ingredients: List[IngredientEntry]
        self._alias_map: Dict[str, IngredientEntry]
        self._unit_alias_map: Dict[str, str]

        self._load_data()
        self._build_unit_alias_map()


    def _load_data(self) -> None:
        # Load Units
        try:
            with open(self.data_dir / "units.json", "r") as f:
                raw_data: Any = json.load(f)
                self.units_db = UnitsDb(**raw_data)
        except FileNotFoundError:
            logger.error("units.json not found")
            raise

        # Load Ingredients
        try:
            with open(self.data_dir / "ingredients.json", "r") as f:
                raw_data = json.load(f)
                self.ingredients = [IngredientEntry(**i) for i in raw_data["ingredients"]]
        except FileNotFoundError:
            logger.error("ingredients.json not found")
            raise

        # Build O(1) Alias Map
        self._alias_map = {}
        for ing in self.ingredients:
            for name in ing.names:
                self._alias_map[name.lower()] = ing

    def _build_unit_alias_map(self) -> None:
        """Build a master lookup index mapping all unit aliases to their canonical keys."""
        self._unit_alias_map = {}

        # Process volume units
        for canonical_key, unit_detail in self.units_db.volume.units.items():
            # Add canonical key pointing to itself
            normalized_key: str = canonical_key.lower().strip()
            self._unit_alias_map[normalized_key] = canonical_key

            # Add all aliases pointing to canonical key
            for alias in unit_detail.aliases:
                normalized_alias: str = alias.lower().strip()
                if normalized_alias in self._unit_alias_map:
                    collision_key: str = self._unit_alias_map[normalized_alias]
                    logger.warning(
                        f"Alias collision: '{normalized_alias}' already mapped to '{collision_key}' "
                        f"(volume), now also found in volume unit '{canonical_key}'. "
                        f"Using first occurrence."
                    )
                else:
                    self._unit_alias_map[normalized_alias] = canonical_key
        
        # Process weight units
        for canonical_key, unit_detail in self.units_db.weight.units.items():
            # Add canonical key pointing to itself
            normalized_key = canonical_key.lower().strip()
            if normalized_key in self._unit_alias_map:
                collision_key = self._unit_alias_map[normalized_key]
                logger.warning(
                    f"Alias collision: '{normalized_key}' already mapped to '{collision_key}' "
                    f"(volume), now also found in weight unit '{canonical_key}'. "
                    f"Using first occurrence."
                )
            else:
                self._unit_alias_map[normalized_key] = canonical_key

            # Add all aliases pointing to canonical key
            for alias in unit_detail.aliases:
                normalized_alias = alias.lower().strip()
                if normalized_alias in self._unit_alias_map:
                    collision_key = self._unit_alias_map[normalized_alias]
                    logger.warning(
                        f"Alias collision: '{normalized_alias}' already mapped to '{collision_key}', "
                        f"now also found in weight unit '{canonical_key}'. "
                        f"Using first occurrence."
                    )
                else:
                    self._unit_alias_map[normalized_alias] = canonical_key
        
        # Process temperature units
        for canonical_key, temp_unit_detail in self.units_db.temperature.units.items():
            normalized_key = canonical_key.lower().strip()
            if normalized_key in self._unit_alias_map:
                collision_key = self._unit_alias_map[normalized_key]
                logger.warning(
                    f"Alias collision: '{normalized_key}' already mapped to '{collision_key}', "
                    f"now also found in temperature unit '{canonical_key}'. "
                    f"Using first occurrence."
                )
            else:
                self._unit_alias_map[normalized_key] = canonical_key

            for alias in temp_unit_detail.aliases:
                normalized_alias = alias.lower().strip()
                if normalized_alias in self._unit_alias_map:
                    collision_key = self._unit_alias_map[normalized_alias]
                    logger.warning(
                        f"Alias collision: '{normalized_alias}' already mapped to '{collision_key}', "
                        f"now also found in temperature unit '{canonical_key}'. "
                        f"Using first occurrence."
                    )
                else:
                    self._unit_alias_map[normalized_alias] = canonical_key

    def _resolve_unit(self, raw_input: str) -> str:
        """
        Resolve a user input string to its canonical unit key.

        Args:
            raw_input: User-provided unit string (e.g., "Grams", "tbsp")

        Returns:
            Canonical unit key (e.g., "g", "tbsp")

        Raises:
            UnitNotFoundError: If the input cannot be resolved to a known unit
        """
        normalized: str = raw_input.lower().strip()
        if normalized in self._unit_alias_map:
            return self._unit_alias_map[normalized]
        raise UnitNotFoundError(f"Unit '{raw_input}' is not recognized.")

    def get_unit_type(self, unit_name: str) -> str:
        """
        Returns 'volume', 'weight', 'temperature' or raises UnitNotFoundError.

        Args:
            unit_name: User-provided unit name (supports aliases)

        Returns:
            The type of unit: 'volume', 'weight', or 'temperature'
        """
        canonical_key: str = self._resolve_unit(unit_name)

        if canonical_key in self.units_db.volume.units:
            return "volume"
        if canonical_key in self.units_db.weight.units:
            return "weight"
        if canonical_key in self.units_db.temperature.units:
            return "temperature"

        raise UnitNotFoundError(f"Unit '{unit_name}' type could not be determined.")

    def get_factor(self, unit_name: str) -> float:
        """
        Returns conversion factor to base unit.

        Args:
            unit_name: User-provided unit name (supports aliases)

        Returns:
            The conversion factor to the base unit
        """
        canonical_key: str = self._resolve_unit(unit_name)

        if canonical_key in self.units_db.volume.units:
            return self.units_db.volume.units[canonical_key].factor
        if canonical_key in self.units_db.weight.units:
            return self.units_db.weight.units[canonical_key].factor

        # Temperature does not use simple factors
        raise UnitNotFoundError(f"No linear factor for unit '{unit_name}'.")

    def get_all_ingredient_names(self) -> List[str]:
        return list(self._alias_map.keys())

    def get_ingredient_by_name(self, name: str) -> IngredientEntry | None:
        return self._alias_map.get(name.lower())

    def match_ingredient(self, input_name: str) -> IngredientEntry:
        """
        Match an ingredient name using exact or fuzzy matching.

        Args:
            input_name: User-provided ingredient name

        Returns:
            Matched IngredientEntry

        Raises:
            IngredientNotFoundError: If no match found
            IngredientAmbiguousError: If multiple distinct ingredients match
        """
        if not input_name:
            raise IngredientNotFoundError("No ingredient specified for density conversion.")

        cleaned_input: str = input_name.lower().strip()

        # 1. Exact Match
        exact: IngredientEntry | None = self.get_ingredient_by_name(cleaned_input)
        if exact is not None:
            return exact

        # 2. Fuzzy Match
        all_names: List[str] = self.get_all_ingredient_names()
        matches: List[str] = difflib.get_close_matches(cleaned_input, all_names, n=3, cutoff=0.6)

        if not matches:
            raise IngredientNotFoundError(f"Ingredient '{input_name}' not found in database.")

        ingredient_entries: List[IngredientEntry | None] = [self.get_ingredient_by_name(name) for name in matches]

        # check if multiple distinct ingredients matched
        if len(set(ie.id for ie in ingredient_entries if ie is not None)) > 1:
            raise IngredientAmbiguousError(
                f"Ambiguous ingredient '{input_name}'. Close matches: {', '.join(matches)}"
            )
        ingredient_entry: IngredientEntry | None = ingredient_entries[0]
        if ingredient_entry is None:
            raise IngredientNotFoundError(f"Ingredient '{input_name}' not found in database.")
        return ingredient_entry
