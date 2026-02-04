import re
from .models import ParsedQuery
from .exceptions import ParsingError


class Parser:
    # Regex Strategy per plan:
    # Group 1 (Qty): integers or decimals
    # Group 2 (Unit): Unit string
    # Group 3 (Ing): Optional remainder
    PATTERN = re.compile(r"^(\d+(?:\.\d+)?)\s*([a-zA-Z°_]+)\s*(of)?\s*(?:of\s+)?(.*)?$")

    @staticmethod
    def parse(query_text: str) -> ParsedQuery:
        cleaned = query_text.strip()
        match = Parser.PATTERN.match(cleaned)
        
        if not match:
            raise ParsingError(f"Could not parse query: '{query_text}'. Format expected: 'QTY UNIT [of] INGREDIENT'")
        
        qty_str, unit_str, _, ingredient_str = match.groups()
        
        print(f"Parsed Query - Quantity: {qty_str}, Unit: {unit_str}, Ingredient: {ingredient_str}")
        
        return ParsedQuery(
            quantity=float(qty_str),
            unit=unit_str.lower(),
            # Convert empty string matches to None
            ingredient=ingredient_str.strip() if ingredient_str else None
        )
