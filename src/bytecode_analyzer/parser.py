"""
EVM bytecode parser.

Converts raw bytecode into structured opcode data.

Current implementation (Phase 2):
- All PUSH1-PUSH32 opcodes extract arguments correctly
- All other opcodes recognized without argument extraction

Key functions:
- parse_bytecode(bytecode): Main parser (returns dict)
- _handle_push(): Extract PUSH1-PUSH32 with arguments
- _handle_simple_opcode(): Process opcodes without arguments
- _handle_unknown_byte(): Handle invalid bytes

Uses dispatcher pattern with atomic handlers.
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


def _handle_push(bytecode_bytes: bytes, offset: int) -> tuple[int, dict, str | None]:
    """
    Handle PUSH1-PUSH32 opcodes with dynamic argument extraction.

    Extracts arguments for all PUSH opcodes:
    - PUSH1  (0x60): 1-byte  argument
    - PUSH2  (0x61): 2-byte  argument
    - ...
    - PUSH32 (0x7F): 32-byte argument

    Args:
        bytecode_bytes: Full bytecode as bytes
        offset: Current position in bytecode

    Returns:
        Tuple of (bytes_consumed, opcode_entry, error_message)
        - bytes_consumed: 1 + push_size (opcode + argument bytes)
        - opcode_entry: Dictionary with opcode details and argument
        - error_message: Error string if incomplete, None otherwise
    """
    byte = bytecode_bytes[offset]
    push_size = byte - 0x5F  # PUSH1=1, PUSH2=2, ..., PUSH32=32

    opcode_info = get_opcode_info(byte)

    # Build base opcode entry
    opcode_entry = {
        "offset": offset,
        "opcode": opcode_info["name"],
        "value": f"0x{byte:02x}",
        "description": opcode_info["description"],
    }

    # Check if all argument bytes are available
    if offset + push_size < len(bytecode_bytes):
        # Extract argument bytes
        arg_bytes = bytecode_bytes[offset + 1 : offset + 1 + push_size]
        opcode_entry["argument"] = f"0x{arg_bytes.hex()}"
        return 1 + push_size, opcode_entry, None
    else:
        # Incomplete PUSH (missing argument bytes)
        error = (
            f"PUSH{push_size} at offset {offset} is incomplete (missing {push_size}-byte argument)"
        )
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
        case byte if 0x60 <= byte <= 0x7F:  # PUSH1-PUSH32
            return _handle_push(bytecode_bytes, offset)

        case _:  # Default: no special handling needed
            return None


# ============================================================================
# SIMPLE HANDLERS
# ============================================================================


def _handle_simple_opcode(byte: int, offset: int) -> tuple[int, dict, None]:
    """
    Handle simple opcodes (no arguments).

    This includes all opcodes that do not require argument extraction:
    - Arithmetic, comparison, stack, memory, storage opcodes
    - All other opcodes

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
        "description": opcode_info["description"],
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
        "description": "Unknown byte (not an EVM opcode)",
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
    - Handles PUSH1-PUSH32 with full argument extraction
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
        >>> parse_bytecode("0x6112346080604052")
        {
            "bytecode": "0x6112346080604052",
            "length": 8,
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
        bytes_consumed, opcode_entry, _ = _handle_simple_opcode(byte, i)
        opcodes_list.append(opcode_entry)
        i += bytes_consumed

    # Build final result
    return {
        "bytecode": f"0x{hex_data}",
        "length": len(bytecode_bytes),
        "opcodes": opcodes_list,
        "metadata": {"total_opcodes": len(opcodes_list), "parsing_errors": errors},
    }
