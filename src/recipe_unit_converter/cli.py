import sys
import argparse
import json
from pathlib import Path
from typing import NoReturn
from importlib.resources import files

from .repository import Repository
from .converter import Converter
from .models import ConversionResult
from .exceptions import ConverterError


def format_output(result: ConversionResult, format_type: str) -> str:
    """
    Format conversion result for output.

    Args:
        result: The conversion result
        format_type: Output format ('simple', 'verbose', or 'json')

    Returns:
        Formatted string for output
    """
    if format_type == "simple":
        return f"{result.result_value} {result.result_unit}"

    elif format_type == "verbose":
        output = f"{result.result_value} {result.result_unit}"
        if result.ingredient:
            output += f" of {result.ingredient}"
        output += f" ({result.explanation})"
        return output

    elif format_type == "json":
        data = {
            "original_query": result.original_query,
            "source_unit": result.source_unit,
            "target_unit": result.target_unit,
            "result_value": result.result_value,
            "result_unit": result.result_unit,
            "ingredient": result.ingredient,
            "explanation": result.explanation
        }
        return json.dumps(data, indent=2)

    else:
        raise ValueError(f"Unknown format type: {format_type}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert between recipe measurement units",
        epilog="Example: recipe-convert '2 cups flour' --to grams"
    )
    parser.add_argument(
        "query",
        help="Recipe query (e.g., '2 cups flour', '1/4 tsp salt')"
    )
    parser.add_argument(
        "--to",
        required=True,
        dest="target_unit",
        help="Target unit (e.g., grams, ml, tsp)"
    )
    parser.add_argument(
        "--format",
        choices=["simple", "verbose", "json"],
        default="simple",
        help="Output format (default: simple)"
    )

    args = parser.parse_args()

    try:
        # Load data from package
        data_path = Path(str(files('recipe_unit_converter') / 'data'))

        # Initialize converter
        repo = Repository(data_path)
        converter = Converter(repo)

        # Perform conversion
        result = converter.convert(args.query, args.target_unit)

        # Format and print output
        output = format_output(result, args.format)
        print(output)
        sys.exit(0)

    except ConverterError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
