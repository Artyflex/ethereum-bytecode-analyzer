"""
EVM bytecode parser.
Converts bytecode into structured opcode data.
"""
from .opcodes import get_opcode_info
from .validator import _extract_hex_data


# ============================================================================
# OPCODE CHECKING FUNCTIONS
# ============================================================================

def _is_opcode(byte: int) -> bool:
    """
    Check if byte is a valid EVM opcode.

    Args:
        byte: Byte value to check

    Returns:
        True if byte is an EVM opcode (exists in OPCODES_MAP), False otherwise
    """
    return get_opcode_info(byte) is not None


# ============================================================================
# SPECIAL OPCODE HANDLERS
# ============================================================================

def _handle_push1(bytecode_bytes: bytes, offset: int) -> tuple[int, dict, str | None]:
    """
    Handle PUSH1 opcode (reads 1-byte argument).

    Args:
        bytecode_bytes: Full bytecode as bytes
        offset: Current position in bytecode

    Returns:
        Tuple of (bytes_consumed, opcode_entry, error_message)
        - bytes_consumed: Number of bytes this opcode uses (2 for PUSH1)
        - opcode_entry: Dictionary with opcode details
        - error_message: Error string if any, None otherwise
    """
    byte = bytecode_bytes[offset]
    opcode_info = get_opcode_info(byte)

    # Build base opcode entry
    opcode_entry = {
        "offset": offset,
        "opcode": opcode_info["name"],
        "value": f"0x{byte:02x}",
        "description": opcode_info["description"]
    }

    # Check if argument is available
    if offset + 1 < len(bytecode_bytes):
        arg_byte = bytecode_bytes[offset + 1]
        opcode_entry["argument"] = f"0x{arg_byte:02x}"
        return 2, opcode_entry, None  # Consumed 2 bytes (opcode + argument)
    else:
        # Incomplete PUSH1 (malformed bytecode)
        error = f"PUSH1 at offset {offset} is incomplete (missing 1-byte argument)"
        return 1, opcode_entry, error


def _requires_special_handling(
    byte: int, bytecode_bytes: bytes, offset: int
) -> tuple[int, dict, str | None] | None:
    """
    Check if opcode requires special handling and handle it.

    This function acts as a dispatcher for opcodes that need special processing.
    Returns the handler result if special handling is needed, None otherwise.

    Args:
        byte: Opcode byte value
        bytecode_bytes: Full bytecode as bytes
        offset: Current position in bytecode

    Returns:
        If special handling required: Tuple of (bytes_consumed, opcode_entry, error_message)
        If no special handling: None

    """
    # Switch-case pattern for special handlers
    match byte:
        case 0x60:  # PUSH1
            return _handle_push1(bytecode_bytes, offset)

        # Other OPCODES will be added here

        case _:  # Default: no special handling needed
            return None


# ============================================================================
# SIMPLE HANDLERS
# ============================================================================

def _handle_simple_opcode(byte: int, offset: int) -> tuple[int, dict, None]:
    """
    Handle simple opcodes (no arguments).

    Args:
        byte: Opcode byte value
        offset: Current position in bytecode

    Returns:
        Tuple of (bytes_consumed, opcode_entry, None)
    """
    opcode_info = get_opcode_info(byte)

    opcode_entry = {
        "offset": offset,
        "opcode": opcode_info["name"],
        "value": f"0x{byte:02x}",
        "description": opcode_info["description"]
    }

    return 1, opcode_entry, None


def _handle_unknown_byte(byte: int, offset: int) -> tuple[int, dict, str | None]:
    """
    Handle unknown bytes (not a valid EVM opcode).

    Args:
        byte: Byte value (NOT an opcode)
        offset: Current position in bytecode

    Returns:
        Tuple of (bytes_consumed, entry, warning_message)
    """
    entry = {
        "offset": offset,
        "opcode": "UNKNOWN",
        "value": f"0x{byte:02x}",
        "description": "Unknown byte (not an EVM opcode)"
    }

    warning = f"Invalid byte 0x{byte:02x} at offset {offset} (not a valid EVM opcode)"

    return 1, entry, warning


# ============================================================================
# MAIN PARSING FUNCTION (Orchestrator)
# ============================================================================

def parse_bytecode(bytecode: str) -> dict:
    """
    Parse EVM bytecode into structured format.

    Current implementation :
    - Parses all EVM opcodes
    - Handles PUSH1 with 1-byte argument extraction
    - Detects invalid bytes (not EVM opcodes)
    - Tracks parsing errors and warnings

    Args:
        bytecode: Cleaned hexadecimal bytecode (with or without 0x prefix)

    Returns:
        Dictionary containing:
        - bytecode: Original bytecode with 0x prefix
        - length: Number of bytes
        - opcodes: List of parsed opcodes/bytes with details
        - metadata: Parsing statistics and errors

    Example:
        >>> parse_bytecode("0x6060604052")
        {
            "bytecode": "0x6060604052",
            "length": 5,
            "opcodes": [...],
            "metadata": {"total_opcodes": 3, "parsing_errors": []}
        }
    """
    # Extract hex data (remove 0x if present)
    hex_data = _extract_hex_data(bytecode)

    # Convert to bytes
    bytecode_bytes = bytes.fromhex(hex_data)

    # Initialize result structures
    opcodes_list = []
    errors = []

    # Parse bytecode byte by byte
    i = 0
    while i < len(bytecode_bytes):
        byte = bytecode_bytes[i]

        # Check if byte is a valid EVM opcode
        if not _is_opcode(byte):
            # Invalid byte (not an EVM opcode)
            bytes_consumed, entry, warning = _handle_unknown_byte(byte, i)
            opcodes_list.append(entry)
            if warning:
                errors.append(warning)
            i += bytes_consumed
            continue

        # Check if opcode requires special handling
        special_result = _requires_special_handling(byte, bytecode_bytes, i)

        if special_result is not None:
            # Special handling was applied
            bytes_consumed, opcode_entry, error = special_result
            opcodes_list.append(opcode_entry)
            if error:
                errors.append(error)
            i += bytes_consumed
            continue

        # Simple opcode (no special handling needed)
        bytes_consumed, opcode_entry, error = _handle_simple_opcode(byte, i)
        opcodes_list.append(opcode_entry)
        if error:
            errors.append(error)
        i += bytes_consumed

    # Build final result
    return {
        "bytecode": f"0x{hex_data}",
        "length": len(bytecode_bytes),
        "opcodes": opcodes_list,
        "metadata": {
            "total_opcodes": len(opcodes_list),
            "parsing_errors": errors
        }
    }