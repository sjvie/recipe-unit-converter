import re
from fractions import Fraction
from typing import Optional
from .models import ParsedQuery
from .exceptions import ParsingError


class Parser:
    # Word-to-number mapping for natural language quantities
    WORD_NUMBERS = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
        "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
        "quarter": 0.25, "half": 0.5
    }

    # Regex for numeric quantities (integers, decimals, fractions, mixed fractions)
    # Matches: "2", "1.5", "1/4", "1 1/2"
    NUMERIC_PATTERN = re.compile(
        r"^(?:(\d+)\s+)?(\d+)/(\d+)|(\d+(?:\.\d+)?)"
    )

    # Main pattern for query: quantity + unit + optional "of" + optional ingredient
    PATTERN = re.compile(
        r"^(.+?)\s+([a-zA-Z°_]+)\s*(?:of)?\s*(?:of\s+)?(.*)?$"
    )

    @staticmethod
    def _parse_quantity(qty_str: str) -> float:
        """
        Parse quantity string into float.
        Supports: integers, decimals, fractions (1/4), mixed fractions (1 1/2),
        word numbers (one-twenty, quarter, half).
        """
        qty_str = qty_str.strip().lower()

        # Handle special case: "half a" → 0.5
        if qty_str == "half a":
            return 0.5

        # Try word number first
        if qty_str in Parser.WORD_NUMBERS:
            return float(Parser.WORD_NUMBERS[qty_str])

        # Try numeric parsing
        match = Parser.NUMERIC_PATTERN.match(qty_str)
        if not match:
            raise ParsingError(
                f"Invalid quantity: '{qty_str}'. "
                f"Expected format: number (e.g., 2, 1.5, 1/4, 1 1/2)"
            )

        whole_part, numerator, denominator, decimal_num = match.groups()

        # Mixed fraction: "1 1/2"
        if numerator and denominator:
            whole = int(whole_part) if whole_part else 0
            frac = Fraction(int(numerator), int(denominator))
            return float(whole + frac)

        # Simple decimal or integer: "2" or "1.5"
        if decimal_num:
            return float(decimal_num)

        raise ParsingError(f"Could not parse quantity: '{qty_str}'")

    @staticmethod
    def parse(query_text: str) -> ParsedQuery:
        """
        Parse recipe query into structured components.

        Examples:
            "2 cups flour" → ParsedQuery(quantity=2.0, unit="cup", ingredient="flour")
            "1/4 tsp salt" → ParsedQuery(quantity=0.25, unit="tsp", ingredient="salt")
            "half a cup sugar" → ParsedQuery(quantity=0.5, unit="cup", ingredient="sugar")
        """
        cleaned = query_text.strip()
        match = Parser.PATTERN.match(cleaned)

        if not match:
            raise ParsingError(
                f"Could not parse query: '{query_text}'. "
                f"Expected format: '<number> <unit> [ingredient]' (e.g., '2 cups flour')"
            )

        qty_str, unit_str, ingredient_str = match.groups()

        # Parse quantity (supports fractions, decimals, word numbers)
        try:
            quantity = Parser._parse_quantity(qty_str)
        except ParsingError:
            raise
        except Exception as e:
            raise ParsingError(f"Invalid quantity '{qty_str}': {e}")

        return ParsedQuery(
            quantity=quantity,
            unit=unit_str.lower(),
            ingredient=ingredient_str.strip() if ingredient_str else None
        )
