from .models import ConversionResult
from .repository import Repository
from .parser import Parser
from .matcher import IngredientMatcher
from .exceptions import InvalidConversionError


class Converter:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.parser = Parser()
        self.matcher = IngredientMatcher(repo)


    def _convert_temp(self, value: float, from_unit: str, to_unit: str) -> float:
        """Affine temperature conversion."""
        # Normalize to Celsius
        if from_unit == 'f':
            c_val = (value - 32) * 5/9
        elif from_unit == 'k':
            c_val = value - 273.15
        else:
            c_val = value  # assumed c

        # Convert to Target
        if to_unit == 'f':
            return (c_val * 9/5) + 32
        elif to_unit == 'k':
            return c_val + 273.15
        else:
            return c_val


    def convert(self, query_text: str, target_unit: str) -> ConversionResult:
        # 1. Parse
        parsed = self.parser.parse(query_text)
        
        target_unit = target_unit.lower()
        source_unit = parsed.unit

        # 2. Validate Types
        source_type = self.repo.get_unit_type(source_unit)
        target_type = self.repo.get_unit_type(target_unit)

        final_value = 0.0
        explanation = ""
        ingredient = None

        # 3. Route Logic
        
        # --- Scenario 1: Temperature ---
        if source_type == 'temperature' or target_type == 'temperature':
            if source_type != target_type:
                raise InvalidConversionError("Cannot convert between Temperature and other categories.")
            
            final_value = self._convert_temp(parsed.quantity, source_unit, target_unit)
            explanation = f"Temperature converted from {source_unit.upper()} to {target_unit.upper()}."

        # --- Scenario 2: Same Category (Linear) ---
        elif source_type == target_type:
            source_factor = self.repo.get_factor(source_unit)
            target_factor = self.repo.get_factor(target_unit)
            
            base_qty = parsed.quantity * source_factor
            final_value = base_qty / target_factor
            explanation = f"Direct conversion ({source_type})."

        # --- Scenario 3: Cross Category (Density Required) ---
        else:
            if parsed.ingredient is None:
                raise InvalidConversionError(
                    "Ingredient must be specified for conversions between volume and weight."
                )
            # Need an ingredient
            ingredient_entry = self.matcher.match(parsed.ingredient)
            density = ingredient_entry.density  # g/ml
            
            # Convert Source to Base (ml or g)
            source_factor = self.repo.get_factor(source_unit)
            base_source_qty = parsed.quantity * source_factor
            
            base_target_qty = 0.0

            # Vol -> Weight (Mass = Vol * Density)
            if source_type == 'volume' and target_type == 'weight':
                # base_source_qty is ml
                # result is g
                base_target_qty = base_source_qty * density
                explanation = f"Volume to Weight using density of {ingredient_entry.names[0]} ({density} g/ml)."

            # Weight -> Vol (Vol = Mass / Density)
            elif source_type == 'weight' and target_type == 'volume':
                # base_source_qty is g
                # result is ml
                base_target_qty = base_source_qty / density
                explanation = f"Weight to Volume using density of {ingredient_entry.names[0]} ({density} g/ml)."
            
            ingredient = ingredient_entry.names[0]

            # Convert Base Target -> Final Unit
            target_factor = self.repo.get_factor(target_unit)
            final_value = base_target_qty / target_factor

        return ConversionResult(
            original_query=query_text,
            source_unit=source_unit,
            target_unit=target_unit,
            result_value=round(final_value, 4),
            result_unit=target_unit,
            ingredient=ingredient,
            explanation=explanation
        )
