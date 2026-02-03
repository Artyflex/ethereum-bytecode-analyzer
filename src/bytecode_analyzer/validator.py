"""
Bytecode validation and cleaning utilities.

Validates EVM bytecode format with 5 atomic checks:
1. Type is string
2. Not empty
3. Starts with '0x' (mandatory)
4. Only hex characters (0-9, a-f, A-F)
5. Even length (2 chars per byte)

Key functions:
- validate_bytecode(bytecode): Validate format
- clean_bytecode(bytecode): Normalize (remove spaces, lowercase)
"""

import re

# ============================================================================
# VALIDATION FUNCTIONS (Atomic checks)
# ============================================================================


def _validate_is_string(bytecode) -> tuple[bool, str]:
    """
    Check if bytecode is a string type.

    Args:
        bytecode: Value to check

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(bytecode, str):
        return False, f"Bytecode must be a string, got {type(bytecode).__name__}"
    return True, ""


def _validate_not_empty(bytecode: str) -> tuple[bool, str]:
    """
    Check if bytecode is not empty after stripping whitespace.

    Args:
        bytecode: String to check

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not bytecode or not bytecode.strip():
        return False, "Bytecode cannot be empty"
    return True, ""


def _validate_starts_with_0x(bytecode: str) -> tuple[bool, str]:
    """
    Check if bytecode starts with '0x' prefix (mandatory).

    Args:
        bytecode: String to check (after strip)

    Returns:
        Tuple of (is_valid, error_message)
    """
    cleaned = bytecode.strip()
    if not cleaned.lower().startswith("0x"):
        return False, "Bytecode must start with '0x' prefix"
    return True, ""


def _validate_only_hex_characters(bytecode: str) -> tuple[bool, str]:
    """
    Check if bytecode contains only valid hexadecimal characters (0-9, a-f, A-F).
    Assumes 0x prefix has been removed.

    Args:
        bytecode: String to check (without 0x prefix)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not re.match(r"^[0-9a-fA-F]+$", bytecode):
        return False, "Bytecode contains invalid characters (must be hexadecimal: 0-9, a-f, A-F)"
    return True, ""


def _validate_even_length(bytecode: str) -> tuple[bool, str]:
    """
    Check if bytecode has even length (each byte = 2 hex characters).
    Assumes 0x prefix has been removed.

    Args:
        bytecode: String to check (without 0x prefix)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(bytecode) % 2 != 0:
        return False, "Bytecode must have even length (each byte = 2 hex characters)"
    return True, ""


# ============================================================================
# MAIN VALIDATION FUNCTION (Orchestrator)
# ============================================================================


def validate_bytecode(bytecode) -> tuple[bool, str]:
    """
    Validate EVM bytecode format using 5 atomic validation rules.

    Validation rules (in order):
    1. Must be a string type
    2. Cannot be empty (after strip)
    3. Must start with '0x' prefix (mandatory)
    4. Must contain only hexadecimal characters (0-9, a-f, A-F)
    5. Must have even length (each byte = 2 hex characters)

    Args:
        bytecode: Value to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if all validations pass, False otherwise
        - error_message: Empty string if valid, error description if invalid

    Examples:
        >>> validate_bytecode("0x6080604052")
        (True, '')
        >>> validate_bytecode("6080604052")
        (False, "Bytecode must start with '0x' prefix")
        >>> validate_bytecode("0xinvalid")
        (False, 'Bytecode contains invalid characters...')
    """
    # Rule 1: Type check
    is_valid, error = _validate_is_string(bytecode)
    if not is_valid:
        return is_valid, error

    # Rule 2: Not empty
    is_valid, error = _validate_not_empty(bytecode)
    if not is_valid:
        return is_valid, error

    # Rule 3: Must start with 0x
    is_valid, error = _validate_starts_with_0x(bytecode)
    if not is_valid:
        return is_valid, error

    # Prepare for remaining validations (remove 0x prefix)
    cleaned = bytecode.strip().lower()[2:]  # Remove '0x'

    # Check if empty after removing 0x
    if not cleaned:
        return False, "Bytecode cannot be empty (only '0x' provided)"

    # Rule 4: Only hex characters
    is_valid, error = _validate_only_hex_characters(cleaned)
    if not is_valid:
        return is_valid, error

    # Rule 5: Even length
    is_valid, error = _validate_even_length(cleaned)
    if not is_valid:
        return is_valid, error

    # All validations passed
    return True, ""


# ============================================================================
# CLEANING FUNCTIONS (Atomic operations)
# ============================================================================


def _remove_whitespace(bytecode: str) -> str:
    """
    Remove all whitespace characters (spaces, tabs, newlines).

    Args:
        bytecode: String to clean

    Returns:
        String without any whitespace
    """
    return re.sub(r"\s+", "", bytecode)


def _strip_edges(bytecode: str) -> str:
    """
    Strip leading and trailing whitespace.

    Args:
        bytecode: String to clean

    Returns:
        String without leading/trailing whitespace
    """
    return bytecode.strip()


def _convert_to_lowercase(bytecode: str) -> str:
    """
    Convert all characters to lowercase.

    Args:
        bytecode: String to convert

    Returns:
        Lowercase string
    """
    return bytecode.lower()


def _extract_hex_data(bytecode: str) -> str:
    """
    Extract hex data without 0x prefix.
    Used internally by parser after validation.

    Args:
        bytecode: Cleaned bytecode with 0x prefix

    Returns:
        Hex data without 0x prefix

    Example:
        >>> _extract_hex_data("0x6080604052")
        '6080604052'
    """
    if bytecode.lower().startswith("0x"):
        return bytecode[2:]
    return bytecode


# ============================================================================
# MAIN CLEANING FUNCTION (Orchestrator)
# ============================================================================


def clean_bytecode(bytecode: str) -> str:
    """
    Clean and normalize bytecode string using atomic cleaning operations.

    Operations performed (in order):
    1. Strip leading/trailing whitespace
    2. Remove all internal whitespace (spaces, tabs, newlines)
    3. Convert to lowercase

    Args:
        bytecode: Raw bytecode string

    Returns:
        Cleaned bytecode string (lowercase hex without whitespace)

    Examples:
        >>> clean_bytecode("  0x6080604052  ")
        '6080604052'
        >>> clean_bytecode("0x60 80 60 40 52")
        '0x6080604052'
        >>> clean_bytecode("0x60A0\\n6040")
        '60a06040'
    """
    # Step 1: Strip edges
    cleaned = _strip_edges(bytecode)

    # Step 2: Remove all whitespace
    cleaned = _remove_whitespace(cleaned)

    # Step 3: Convert to lowercase
    cleaned = _convert_to_lowercase(cleaned)

    return cleaned
