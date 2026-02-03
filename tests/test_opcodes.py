"""
Tests for opcodes module.
"""

from bytecode_analyzer.opcodes import (
    get_opcode_info,
    OPCODES_MAP,
    get_total_opcodes,
    is_push_opcode,
    get_push_size,
    EVM_VERSION,
)


class TestOpcodesMap:
    """Test the OPCODES_MAP dictionary."""

    def test_opcodes_map_exists(self):
        """Test that OPCODES_MAP is defined."""
        assert OPCODES_MAP is not None
        assert isinstance(OPCODES_MAP, dict)

    def test_opcodes_map_complete(self):
        """Test that we have a comprehensive set of opcodes."""
        # Should have around 140+ opcodes
        assert len(OPCODES_MAP) >= 140

    def test_opcodes_have_required_fields(self):
        """Test that all opcodes have name and description."""
        for opcode_byte, info in OPCODES_MAP.items():
            assert "name" in info, f"Opcode 0x{opcode_byte:02x} missing 'name'"
            assert "description" in info, f"Opcode 0x{opcode_byte:02x} missing 'description'"
            assert isinstance(info["name"], str)
            assert isinstance(info["description"], str)
            assert len(info["name"]) > 0
            assert len(info["description"]) > 0

    def test_evm_version_defined(self):
        """Test that EVM version is defined."""
        assert EVM_VERSION is not None
        assert isinstance(EVM_VERSION, str)
        assert len(EVM_VERSION) > 0


class TestGetOpcodeInfo:
    """Test the get_opcode_info function."""

    def test_arithmetic_opcodes(self):
        """Test arithmetic opcodes."""
        assert get_opcode_info(0x00)["name"] == "STOP"
        assert get_opcode_info(0x01)["name"] == "ADD"
        assert get_opcode_info(0x02)["name"] == "MUL"
        assert get_opcode_info(0x03)["name"] == "SUB"
        assert get_opcode_info(0x04)["name"] == "DIV"

    def test_comparison_opcodes(self):
        """Test comparison opcodes."""
        assert get_opcode_info(0x10)["name"] == "LT"
        assert get_opcode_info(0x11)["name"] == "GT"
        assert get_opcode_info(0x14)["name"] == "EQ"
        assert get_opcode_info(0x15)["name"] == "ISZERO"

    def test_environmental_opcodes(self):
        """Test environmental opcodes."""
        assert get_opcode_info(0x30)["name"] == "ADDRESS"
        assert get_opcode_info(0x33)["name"] == "CALLER"
        assert get_opcode_info(0x3A)["name"] == "GASPRICE"

    def test_block_opcodes(self):
        """Test block information opcodes."""
        assert get_opcode_info(0x40)["name"] == "BLOCKHASH"
        assert get_opcode_info(0x42)["name"] == "TIMESTAMP"
        assert get_opcode_info(0x43)["name"] == "NUMBER"

    def test_storage_opcodes(self):
        """Test storage opcodes."""
        assert get_opcode_info(0x54)["name"] == "SLOAD"
        assert get_opcode_info(0x55)["name"] == "SSTORE"

    def test_push_opcodes(self):
        """Test PUSH opcodes."""
        assert get_opcode_info(0x5F)["name"] == "PUSH0"
        assert get_opcode_info(0x60)["name"] == "PUSH1"
        assert get_opcode_info(0x7F)["name"] == "PUSH32"

    def test_dup_opcodes(self):
        """Test DUP opcodes."""
        assert get_opcode_info(0x80)["name"] == "DUP1"
        assert get_opcode_info(0x8F)["name"] == "DUP16"

    def test_swap_opcodes(self):
        """Test SWAP opcodes."""
        assert get_opcode_info(0x90)["name"] == "SWAP1"
        assert get_opcode_info(0x9F)["name"] == "SWAP16"

    def test_log_opcodes(self):
        """Test LOG opcodes."""
        assert get_opcode_info(0xA0)["name"] == "LOG0"
        assert get_opcode_info(0xA4)["name"] == "LOG4"

    def test_system_opcodes(self):
        """Test system opcodes."""
        assert get_opcode_info(0xF0)["name"] == "CREATE"
        assert get_opcode_info(0xF1)["name"] == "CALL"
        assert get_opcode_info(0xF3)["name"] == "RETURN"
        assert get_opcode_info(0xFD)["name"] == "REVERT"
        assert get_opcode_info(0xFF)["name"] == "SELFDESTRUCT"

    def test_unknown_opcode(self):
        """Test that truly unknown opcodes return None."""
        # Test some unused opcodes
        assert get_opcode_info(0x0C) is None
        assert get_opcode_info(0x0D) is None
        assert get_opcode_info(0x21) is None


class TestGetTotalOpcodes:
    """Test the get_total_opcodes function."""

    def test_returns_correct_count(self):
        """Test that total count matches OPCODES_MAP length."""
        assert get_total_opcodes() == len(OPCODES_MAP)

    def test_count_is_reasonable(self):
        """Test that we have a reasonable number of opcodes."""
        total = get_total_opcodes()
        assert total >= 140
        assert total <= 160  # Shouldn't exceed this


class TestIsPushOpcode:
    """Test the is_push_opcode function."""

    def test_push0(self):
        """Test PUSH0 detection."""
        assert is_push_opcode(0x5F) is True

    def test_push1_to_push32(self):
        """Test PUSH1-PUSH32 detection."""
        for i in range(0x60, 0x80):
            assert is_push_opcode(i) is True, f"0x{i:02x} should be detected as PUSH"

    def test_non_push_opcodes(self):
        """Test that non-PUSH opcodes return False."""
        non_push = [0x00, 0x01, 0x50, 0x80, 0x90, 0xF0, 0xFF]
        for opcode in non_push:
            assert is_push_opcode(opcode) is False


class TestGetPushSize:
    """Test the get_push_size function."""

    def test_push0_size(self):
        """Test PUSH0 size."""
        assert get_push_size(0x5F) == 0

    def test_push1_size(self):
        """Test PUSH1 size."""
        assert get_push_size(0x60) == 1

    def test_push32_size(self):
        """Test PUSH32 size."""
        assert get_push_size(0x7F) == 32

    def test_all_push_sizes(self):
        """Test all PUSH opcode sizes."""
        for i in range(1, 33):
            opcode = 0x5F + i
            expected_size = i
            assert get_push_size(opcode) == expected_size

    def test_non_push_returns_zero(self):
        """Test that non-PUSH opcodes return 0."""
        non_push = [0x00, 0x01, 0x50, 0x80, 0x90, 0xF0]
        for opcode in non_push:
            assert get_push_size(opcode) == 0
