"""
JSON formatter for analysis results.

Converts parsed bytecode data to formatted JSON string.

Key function:
- format_output(parsed_data, indent=2): Format to JSON

Simple implementation for Phase 1.
Future: YAML/XML support, validation, advanced options (Phase 5).
"""

import json


def format_output(parsed_data: dict, indent: int = 2) -> str:
    """
    Format parsed bytecode data to JSON string.

    Args:
        parsed_data: Dictionary from parse_bytecode()
        indent: Number of spaces for indentation (default: 2)

    Returns:
        JSON formatted string

    Example:
        >>> result = parse_bytecode("0x6080604052")
        >>> json_output = format_output(result)
        >>> print(json_output)
        {
          "bytecode": "0x6080604052",
          "length": 5,
          "opcodes": [...],
          "metadata": {...}
        }
    """
    return json.dumps(parsed_data, indent=indent, ensure_ascii=False)
