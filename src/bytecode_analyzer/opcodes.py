"""
EVM opcodes mapping and utilities.

Provides comprehensive mapping of 140+ EVM opcodes (Shanghai/Cancun).
Maps opcode bytes to their names and descriptions.

Key functions:
- get_opcode_info(byte): Get opcode information
- is_push_opcode(byte): Check if byte is PUSH opcode
- get_push_size(byte): Get PUSH argument size

Reference: https://evm.codes
"""

# Complete EVM opcodes mapping
OPCODES_MAP = {
    # 0x0s: Stop and Arithmetic Operations
    0x00: {"name": "STOP", "description": "Halts execution"},
    0x01: {"name": "ADD", "description": "Addition operation"},
    0x02: {"name": "MUL", "description": "Multiplication operation"},
    0x03: {"name": "SUB", "description": "Subtraction operation"},
    0x04: {"name": "DIV", "description": "Integer division operation"},
    0x05: {"name": "SDIV", "description": "Signed integer division operation"},
    0x06: {"name": "MOD", "description": "Modulo remainder operation"},
    0x07: {"name": "SMOD", "description": "Signed modulo remainder operation"},
    0x08: {"name": "ADDMOD", "description": "Modulo addition operation"},
    0x09: {"name": "MULMOD", "description": "Modulo multiplication operation"},
    0x0A: {"name": "EXP", "description": "Exponential operation"},
    0x0B: {"name": "SIGNEXTEND", "description": "Extend length of two's complement signed integer"},
    # 0x10s: Comparison & Bitwise Logic Operations
    0x10: {"name": "LT", "description": "Less-than comparison"},
    0x11: {"name": "GT", "description": "Greater-than comparison"},
    0x12: {"name": "SLT", "description": "Signed less-than comparison"},
    0x13: {"name": "SGT", "description": "Signed greater-than comparison"},
    0x14: {"name": "EQ", "description": "Equality comparison"},
    0x15: {"name": "ISZERO", "description": "Simple not operator"},
    0x16: {"name": "AND", "description": "Bitwise AND operation"},
    0x17: {"name": "OR", "description": "Bitwise OR operation"},
    0x18: {"name": "XOR", "description": "Bitwise XOR operation"},
    0x19: {"name": "NOT", "description": "Bitwise NOT operation"},
    0x1A: {"name": "BYTE", "description": "Retrieve single byte from word"},
    0x1B: {"name": "SHL", "description": "Shift left operation"},
    0x1C: {"name": "SHR", "description": "Logical shift right operation"},
    0x1D: {"name": "SAR", "description": "Arithmetic shift right operation"},
    # 0x20s: SHA3
    0x20: {"name": "SHA3", "description": "Compute Keccak-256 hash"},
    # 0x30s: Environmental Information
    0x30: {"name": "ADDRESS", "description": "Get address of currently executing account"},
    0x31: {"name": "BALANCE", "description": "Get balance of the given account"},
    0x32: {"name": "ORIGIN", "description": "Get execution origination address"},
    0x33: {"name": "CALLER", "description": "Get caller address"},
    0x34: {
        "name": "CALLVALUE",
        "description": "Get deposited value by the instruction/transaction",
    },
    0x35: {"name": "CALLDATALOAD", "description": "Get input data of current environment"},
    0x36: {"name": "CALLDATASIZE", "description": "Get size of input data"},
    0x37: {"name": "CALLDATACOPY", "description": "Copy input data to memory"},
    0x38: {"name": "CODESIZE", "description": "Get size of code running in current environment"},
    0x39: {"name": "CODECOPY", "description": "Copy code running in current environment to memory"},
    0x3A: {"name": "GASPRICE", "description": "Get price of gas in current environment"},
    0x3B: {"name": "EXTCODESIZE", "description": "Get size of an account's code"},
    0x3C: {"name": "EXTCODECOPY", "description": "Copy an account's code to memory"},
    0x3D: {
        "name": "RETURNDATASIZE",
        "description": "Get size of output data from the previous call",
    },
    0x3E: {
        "name": "RETURNDATACOPY",
        "description": "Copy output data from the previous call to memory",
    },
    0x3F: {"name": "EXTCODEHASH", "description": "Get hash of an account's code"},
    # 0x40s: Block Information
    0x40: {
        "name": "BLOCKHASH",
        "description": "Get the hash of one of the 256 most recent complete blocks",
    },
    0x41: {"name": "COINBASE", "description": "Get the block's beneficiary address"},
    0x42: {"name": "TIMESTAMP", "description": "Get the block's timestamp"},
    0x43: {"name": "NUMBER", "description": "Get the block's number"},
    0x44: {
        "name": "DIFFICULTY",
        "description": "Get the block's difficulty (pre-merge) or PREVRANDAO (post-merge)",
    },
    0x45: {"name": "GASLIMIT", "description": "Get the block's gas limit"},
    0x46: {"name": "CHAINID", "description": "Get the chain ID"},
    0x47: {"name": "SELFBALANCE", "description": "Get balance of currently executing account"},
    0x48: {"name": "BASEFEE", "description": "Get the base fee"},
    # 0x50s: Stack, Memory, Storage and Flow Operations
    0x50: {"name": "POP", "description": "Remove item from stack"},
    0x51: {"name": "MLOAD", "description": "Load word from memory"},
    0x52: {"name": "MSTORE", "description": "Save word to memory"},
    0x53: {"name": "MSTORE8", "description": "Save byte to memory"},
    0x54: {"name": "SLOAD", "description": "Load word from storage"},
    0x55: {"name": "SSTORE", "description": "Save word to storage"},
    0x56: {"name": "JUMP", "description": "Alter the program counter"},
    0x57: {"name": "JUMPI", "description": "Conditionally alter the program counter"},
    0x58: {"name": "PC", "description": "Get the value of the program counter"},
    0x59: {"name": "MSIZE", "description": "Get the size of active memory in bytes"},
    0x5A: {"name": "GAS", "description": "Get the amount of available gas"},
    0x5B: {"name": "JUMPDEST", "description": "Mark a valid destination for jumps"},
    0x5F: {"name": "PUSH0", "description": "Place 0 on stack"},
    # 0x60s & 0x70s: Push Operations
    0x60: {"name": "PUSH1", "description": "Place 1 byte item on stack"},
    0x61: {"name": "PUSH2", "description": "Place 2 bytes item on stack"},
    0x62: {"name": "PUSH3", "description": "Place 3 bytes item on stack"},
    0x63: {"name": "PUSH4", "description": "Place 4 bytes item on stack"},
    0x64: {"name": "PUSH5", "description": "Place 5 bytes item on stack"},
    0x65: {"name": "PUSH6", "description": "Place 6 bytes item on stack"},
    0x66: {"name": "PUSH7", "description": "Place 7 bytes item on stack"},
    0x67: {"name": "PUSH8", "description": "Place 8 bytes item on stack"},
    0x68: {"name": "PUSH9", "description": "Place 9 bytes item on stack"},
    0x69: {"name": "PUSH10", "description": "Place 10 bytes item on stack"},
    0x6A: {"name": "PUSH11", "description": "Place 11 bytes item on stack"},
    0x6B: {"name": "PUSH12", "description": "Place 12 bytes item on stack"},
    0x6C: {"name": "PUSH13", "description": "Place 13 bytes item on stack"},
    0x6D: {"name": "PUSH14", "description": "Place 14 bytes item on stack"},
    0x6E: {"name": "PUSH15", "description": "Place 15 bytes item on stack"},
    0x6F: {"name": "PUSH16", "description": "Place 16 bytes item on stack"},
    0x70: {"name": "PUSH17", "description": "Place 17 bytes item on stack"},
    0x71: {"name": "PUSH18", "description": "Place 18 bytes item on stack"},
    0x72: {"name": "PUSH19", "description": "Place 19 bytes item on stack"},
    0x73: {"name": "PUSH20", "description": "Place 20 bytes item on stack"},
    0x74: {"name": "PUSH21", "description": "Place 21 bytes item on stack"},
    0x75: {"name": "PUSH22", "description": "Place 22 bytes item on stack"},
    0x76: {"name": "PUSH23", "description": "Place 23 bytes item on stack"},
    0x77: {"name": "PUSH24", "description": "Place 24 bytes item on stack"},
    0x78: {"name": "PUSH25", "description": "Place 25 bytes item on stack"},
    0x79: {"name": "PUSH26", "description": "Place 26 bytes item on stack"},
    0x7A: {"name": "PUSH27", "description": "Place 27 bytes item on stack"},
    0x7B: {"name": "PUSH28", "description": "Place 28 bytes item on stack"},
    0x7C: {"name": "PUSH29", "description": "Place 29 bytes item on stack"},
    0x7D: {"name": "PUSH30", "description": "Place 30 bytes item on stack"},
    0x7E: {"name": "PUSH31", "description": "Place 31 bytes item on stack"},
    0x7F: {"name": "PUSH32", "description": "Place 32 bytes item on stack"},
    # 0x80s: Duplication Operations
    0x80: {"name": "DUP1", "description": "Duplicate 1st stack item"},
    0x81: {"name": "DUP2", "description": "Duplicate 2nd stack item"},
    0x82: {"name": "DUP3", "description": "Duplicate 3rd stack item"},
    0x83: {"name": "DUP4", "description": "Duplicate 4th stack item"},
    0x84: {"name": "DUP5", "description": "Duplicate 5th stack item"},
    0x85: {"name": "DUP6", "description": "Duplicate 6th stack item"},
    0x86: {"name": "DUP7", "description": "Duplicate 7th stack item"},
    0x87: {"name": "DUP8", "description": "Duplicate 8th stack item"},
    0x88: {"name": "DUP9", "description": "Duplicate 9th stack item"},
    0x89: {"name": "DUP10", "description": "Duplicate 10th stack item"},
    0x8A: {"name": "DUP11", "description": "Duplicate 11th stack item"},
    0x8B: {"name": "DUP12", "description": "Duplicate 12th stack item"},
    0x8C: {"name": "DUP13", "description": "Duplicate 13th stack item"},
    0x8D: {"name": "DUP14", "description": "Duplicate 14th stack item"},
    0x8E: {"name": "DUP15", "description": "Duplicate 15th stack item"},
    0x8F: {"name": "DUP16", "description": "Duplicate 16th stack item"},
    # 0x90s: Exchange Operations
    0x90: {"name": "SWAP1", "description": "Exchange 1st and 2nd stack items"},
    0x91: {"name": "SWAP2", "description": "Exchange 1st and 3rd stack items"},
    0x92: {"name": "SWAP3", "description": "Exchange 1st and 4th stack items"},
    0x93: {"name": "SWAP4", "description": "Exchange 1st and 5th stack items"},
    0x94: {"name": "SWAP5", "description": "Exchange 1st and 6th stack items"},
    0x95: {"name": "SWAP6", "description": "Exchange 1st and 7th stack items"},
    0x96: {"name": "SWAP7", "description": "Exchange 1st and 8th stack items"},
    0x97: {"name": "SWAP8", "description": "Exchange 1st and 9th stack items"},
    0x98: {"name": "SWAP9", "description": "Exchange 1st and 10th stack items"},
    0x99: {"name": "SWAP10", "description": "Exchange 1st and 11th stack items"},
    0x9A: {"name": "SWAP11", "description": "Exchange 1st and 12th stack items"},
    0x9B: {"name": "SWAP12", "description": "Exchange 1st and 13th stack items"},
    0x9C: {"name": "SWAP13", "description": "Exchange 1st and 14th stack items"},
    0x9D: {"name": "SWAP14", "description": "Exchange 1st and 15th stack items"},
    0x9E: {"name": "SWAP15", "description": "Exchange 1st and 16th stack items"},
    0x9F: {"name": "SWAP16", "description": "Exchange 1st and 17th stack items"},
    # 0xa0s: Logging Operations
    0xA0: {"name": "LOG0", "description": "Append log record with 0 topics"},
    0xA1: {"name": "LOG1", "description": "Append log record with 1 topic"},
    0xA2: {"name": "LOG2", "description": "Append log record with 2 topics"},
    0xA3: {"name": "LOG3", "description": "Append log record with 3 topics"},
    0xA4: {"name": "LOG4", "description": "Append log record with 4 topics"},
    # 0xf0s: System Operations
    0xF0: {"name": "CREATE", "description": "Create a new account with associated code"},
    0xF1: {"name": "CALL", "description": "Message-call into an account"},
    0xF2: {
        "name": "CALLCODE",
        "description": "Message-call into this account with alternative account's code",
    },
    0xF3: {"name": "RETURN", "description": "Halt execution returning output data"},
    0xF4: {
        "name": "DELEGATECALL",
        "description": "Message-call into this account with alternative account's code (preserving sender and value)",
    },
    0xF5: {
        "name": "CREATE2",
        "description": "Create a new account with associated code at a predictable address",
    },
    0xFA: {"name": "STATICCALL", "description": "Static message-call into an account"},
    0xFD: {"name": "REVERT", "description": "Halt execution reverting state changes"},
    0xFE: {"name": "INVALID", "description": "Designated invalid instruction"},
    0xFF: {
        "name": "SELFDESTRUCT",
        "description": "Halt execution and register account for later deletion",
    },
}

# EVM version supported
EVM_VERSION = "Shanghai/Cancun"


def get_opcode_info(byte: int) -> dict | None:
    """
    Get information about an opcode.

    Args:
        byte: The opcode byte value (0x00 to 0xFF)

    Returns:
        Dictionary with opcode information or None if unknown

    Example:
        >>> get_opcode_info(0x00)
        {'name': 'STOP', 'description': 'Halts execution'}
        >>> get_opcode_info(0xFF)
        {'name': 'SELFDESTRUCT', 'description': 'Halt execution and register account for later deletion'}
    """
    return OPCODES_MAP.get(byte)


def get_total_opcodes() -> int:
    """
    Get the total number of opcodes supported.

    Returns:
        Total count of opcodes in OPCODES_MAP
    """
    return len(OPCODES_MAP)


def is_push_opcode(byte: int) -> bool:
    """
    Check if an opcode is a PUSH operation.

    Args:
        byte: The opcode byte value

    Returns:
        True if the opcode is PUSH0-PUSH32, False otherwise
    """
    return byte == 0x5F or (0x60 <= byte <= 0x7F)


def get_push_size(byte: int) -> int:
    """
    Get the number of bytes a PUSH opcode pushes.

    Args:
        byte: The opcode byte value

    Returns:
        Number of bytes (0-32), or 0 if not a PUSH opcode

    Example:
        >>> get_push_size(0x60)
        1
        >>> get_push_size(0x7F)
        32
        >>> get_push_size(0x5F)
        0
        >>> get_push_size(0x00)
        0
    """
    if byte == 0x5F:  # PUSH0
        return 0
    elif 0x60 <= byte <= 0x7F:  # PUSH1-PUSH32
        return byte - 0x5F
    return 0
