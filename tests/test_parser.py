"""
Tests for parser module.
"""
import pytest
from bytecode_analyzer.parser import (
    parse_bytecode,
    _is_opcode,
    _handle_push1,
    _handle_simple_opcode,
    _handle_unknown_byte,
    _requires_special_handling,
)
from bytecode_analyzer.opcodes import OPCODES_MAP


# ============================================================================
# TESTS FOR ATOMIC FUNCTIONS
# ============================================================================

class TestIsOpcode:
    """Test _is_opcode function."""

    def test_is_opcode_true_for_valid_opcodes(self):
        """Test that valid EVM opcodes return True."""
        assert _is_opcode(0x00) is True  # STOP
        assert _is_opcode(0x01) is True  # ADD
        assert _is_opcode(0x60) is True  # PUSH1
        assert _is_opcode(0x80) is True  # DUP1
        assert _is_opcode(0xF3) is True  # RETURN

    def test_is_opcode_false_for_invalid_bytes(self):
        """Test that invalid bytes return False."""
        assert _is_opcode(0x0C) is False
        assert _is_opcode(0x0D) is False
        assert _is_opcode(0x0E) is False
        assert _is_opcode(0x0F) is False


class TestHandlePush1:
    """Test _handle_push1 function."""

    def test_handle_push1_complete(self):
        """Test handling complete PUSH1 with argument."""
        bytecode_bytes = bytes.fromhex("6080")
        bytes_consumed, opcode_entry, error = _handle_push1(bytecode_bytes, 0)

        assert bytes_consumed == 2
        assert opcode_entry["offset"] == 0
        assert opcode_entry["opcode"] == "PUSH1"
        assert opcode_entry["value"] == "0x60"
        assert opcode_entry["argument"] == "0x80"
        assert error is None

    def test_handle_push1_different_argument(self):
        """Test PUSH1 with different argument values."""
        bytecode_bytes = bytes.fromhex("60ff")
        bytes_consumed, opcode_entry, error = _handle_push1(bytecode_bytes, 0)

        assert bytes_consumed == 2
        assert opcode_entry["argument"] == "0xff"
        assert error is None

    def test_handle_push1_incomplete(self):
        """Test handling incomplete PUSH1 (missing argument)."""
        bytecode_bytes = bytes.fromhex("60")
        bytes_consumed, opcode_entry, error = _handle_push1(bytecode_bytes, 0)

        assert bytes_consumed == 1
        assert opcode_entry["opcode"] == "PUSH1"
        assert "argument" not in opcode_entry
        assert error is not None
        assert "incomplete" in error.lower()


class TestHandleSimpleOpcode:
    """Test _handle_simple_opcode function."""

    def test_handle_simple_opcode(self):
        """Test handling simple opcode without arguments."""
        bytes_consumed, opcode_entry, error = _handle_simple_opcode(0x00, 0)

        assert bytes_consumed == 1
        assert opcode_entry["offset"] == 0
        assert opcode_entry["opcode"] == "STOP"
        assert opcode_entry["value"] == "0x00"
        assert "argument" not in opcode_entry
        assert error is None

    def test_handle_simple_opcode_add(self):
        """Test handling ADD opcode."""
        bytes_consumed, opcode_entry, error = _handle_simple_opcode(0x01, 5)

        assert bytes_consumed == 1
        assert opcode_entry["offset"] == 5
        assert opcode_entry["opcode"] == "ADD"


class TestHandleUnknownByte:
    """Test _handle_unknown_byte function."""

    def test_handle_unknown_byte(self):
        """Test handling invalid byte."""
        bytes_consumed, entry, warning = _handle_unknown_byte(0x0C, 0)

        assert bytes_consumed == 1
        assert entry["offset"] == 0
        assert entry["opcode"] == "UNKNOWN"
        assert entry["value"] == "0x0c"
        assert "not an EVM opcode" in entry["description"]
        assert warning is not None
        assert "invalid byte" in warning.lower()


class TestRequiresSpecialHandling:
    """Test _requires_special_handling dispatcher function."""

    def test_push1_requires_special_handling(self):
        """Test that PUSH1 is dispatched to special handler."""
        bytecode_bytes = bytes.fromhex("6080")
        result = _requires_special_handling(0x60, bytecode_bytes, 0)

        assert result is not None
        bytes_consumed, opcode_entry, error = result
        assert bytes_consumed == 2
        assert opcode_entry["opcode"] == "PUSH1"
        assert opcode_entry["argument"] == "0x80"

    def test_simple_opcode_no_special_handling(self):
        """Test that simple opcodes return None."""
        bytecode_bytes = bytes.fromhex("00")
        result = _requires_special_handling(0x00, bytecode_bytes, 0)

        assert result is None

    def test_push2_no_special_handling(self):
        """Test that PUSH2 has no special handling (Sprint 4)."""
        bytecode_bytes = bytes.fromhex("61")
        result = _requires_special_handling(0x61, bytecode_bytes, 0)

        assert result is None


# ============================================================================
# TESTS FOR MAIN PARSING FUNCTION
# ============================================================================

class TestParseSimpleOpcodes:
    """Test parsing of simple opcodes (no arguments)."""

    def test_parse_single_stop(self):
        """Test parsing single STOP opcode."""
        result = parse_bytecode("0x00")

        assert result["length"] == 1
        assert len(result["opcodes"]) == 1
        assert result["opcodes"][0]["opcode"] == "STOP"
        assert result["opcodes"][0]["offset"] == 0
        assert result["opcodes"][0]["value"] == "0x00"

    def test_parse_single_add(self):
        """Test parsing single ADD opcode."""
        result = parse_bytecode("0x01")

        assert result["opcodes"][0]["opcode"] == "ADD"
        assert result["opcodes"][0]["offset"] == 0

    def test_parse_multiple_simple_opcodes(self):
        """Test parsing multiple simple opcodes."""
        result = parse_bytecode("0x000102")

        assert result["length"] == 3
        assert len(result["opcodes"]) == 3
        assert result["opcodes"][0]["opcode"] == "STOP"
        assert result["opcodes"][1]["opcode"] == "ADD"
        assert result["opcodes"][2]["opcode"] == "MUL"

    def test_parse_opcodes_offsets(self):
        """Test that offsets are correctly calculated."""
        result = parse_bytecode("0x000102")

        assert result["opcodes"][0]["offset"] == 0
        assert result["opcodes"][1]["offset"] == 1
        assert result["opcodes"][2]["offset"] == 2

    def test_parse_dup1(self):
        """Test parsing DUP1 opcode."""
        result = parse_bytecode("0x80")

        assert result["opcodes"][0]["opcode"] == "DUP1"
        assert result["opcodes"][0]["value"] == "0x80"

    def test_parse_swap1(self):
        """Test parsing SWAP1 opcode."""
        result = parse_bytecode("0x90")

        assert result["opcodes"][0]["opcode"] == "SWAP1"
        assert result["opcodes"][0]["value"] == "0x90"

    def test_parse_return(self):
        """Test parsing RETURN opcode."""
        result = parse_bytecode("0xf3")

        assert result["opcodes"][0]["opcode"] == "RETURN"

    def test_parse_revert(self):
        """Test parsing REVERT opcode."""
        result = parse_bytecode("0xfd")

        assert result["opcodes"][0]["opcode"] == "REVERT"


class TestParsePush1:
    """Test parsing of PUSH1 opcode with arguments."""

    def test_parse_push1_with_argument(self):
        """Test parsing PUSH1 with its argument."""
        result = parse_bytecode("0x6060")

        assert len(result["opcodes"]) == 1
        assert result["opcodes"][0]["opcode"] == "PUSH1"
        assert result["opcodes"][0]["offset"] == 0
        assert result["opcodes"][0]["value"] == "0x60"
        assert result["opcodes"][0]["argument"] == "0x60"

    def test_parse_push1_different_argument(self):
        """Test PUSH1 with different argument values."""
        result = parse_bytecode("0x6080")

        assert result["opcodes"][0]["argument"] == "0x80"

    def test_parse_push1_zero_argument(self):
        """Test PUSH1 with 0x00 argument."""
        result = parse_bytecode("0x6000")

        assert result["opcodes"][0]["argument"] == "0x00"

    def test_parse_push1_max_argument(self):
        """Test PUSH1 with 0xFF argument."""
        result = parse_bytecode("0x60ff")

        assert result["opcodes"][0]["argument"] == "0xff"

    def test_parse_multiple_push1(self):
        """Test parsing multiple PUSH1 opcodes."""
        result = parse_bytecode("0x60806040")

        assert len(result["opcodes"]) == 2
        assert result["opcodes"][0]["opcode"] == "PUSH1"
        assert result["opcodes"][0]["argument"] == "0x80"
        assert result["opcodes"][1]["opcode"] == "PUSH1"
        assert result["opcodes"][1]["argument"] == "0x40"

    def test_parse_push1_incomplete(self):
        """Test PUSH1 without argument (incomplete bytecode)."""
        result = parse_bytecode("0x60")

        assert len(result["opcodes"]) == 1
        assert result["opcodes"][0]["opcode"] == "PUSH1"
        assert "argument" not in result["opcodes"][0]
        assert len(result["metadata"]["parsing_errors"]) == 1
        assert "incomplete" in result["metadata"]["parsing_errors"][0].lower()
        assert "PUSH1" in result["metadata"]["parsing_errors"][0]

    def test_parse_push1_offset_calculation(self):
        """Test that offset skips PUSH1 argument correctly."""
        result = parse_bytecode("0x606000")

        assert result["opcodes"][0]["offset"] == 0
        assert result["opcodes"][1]["offset"] == 2
        assert result["opcodes"][1]["opcode"] == "STOP"


class TestParseInvalidBytes:
    """Test parsing of invalid bytes (not EVM opcodes)."""

    def test_parse_invalid_byte(self):
        """Test that invalid bytes are detected."""
        result = parse_bytecode("0x0c")

        assert len(result["opcodes"]) == 1
        assert result["opcodes"][0]["opcode"] == "UNKNOWN"
        assert result["opcodes"][0]["value"] == "0x0c"
        assert len(result["metadata"]["parsing_errors"]) == 1
        assert "invalid byte" in result["metadata"]["parsing_errors"][0].lower()

    def test_parse_multiple_invalid_bytes(self):
        """Test parsing multiple invalid bytes."""
        result = parse_bytecode("0x0c0d0e")

        assert len(result["opcodes"]) == 3
        assert all(op["opcode"] == "UNKNOWN" for op in result["opcodes"])
        assert len(result["metadata"]["parsing_errors"]) == 3


class TestParseMixedBytecode:
    """Test parsing of mixed bytecode with different opcode types."""

    def test_parse_simple_and_push1(self):
        """Test parsing mix of simple opcodes and PUSH1."""
        result = parse_bytecode("0x60600100")

        assert len(result["opcodes"]) == 3
        assert result["opcodes"][0]["opcode"] == "PUSH1"
        assert result["opcodes"][0]["argument"] == "0x60"
        assert result["opcodes"][1]["opcode"] == "ADD"
        assert result["opcodes"][2]["opcode"] == "STOP"

    def test_parse_real_bytecode_fragment(self):
        """Test parsing realistic bytecode fragment."""
        result = parse_bytecode("0x608060405200")

        assert len(result["opcodes"]) == 4
        assert result["opcodes"][0]["opcode"] == "PUSH1"
        assert result["opcodes"][0]["argument"] == "0x80"
        assert result["opcodes"][1]["opcode"] == "PUSH1"
        assert result["opcodes"][1]["argument"] == "0x40"
        assert result["opcodes"][2]["opcode"] == "MSTORE"
        assert result["opcodes"][3]["opcode"] == "STOP"
        assert len(result["metadata"]["parsing_errors"]) == 0


class TestParseMetadata:
    """Test metadata in parsing results."""

    def test_metadata_total_opcodes(self):
        """Test that total opcodes count is correct."""
        result = parse_bytecode("0x000102")

        assert result["metadata"]["total_opcodes"] == 3

    def test_metadata_no_errors(self):
        """Test that parsing_errors is empty for valid bytecode."""
        result = parse_bytecode("0x6060604052")

        assert result["metadata"]["parsing_errors"] == []

    def test_metadata_with_errors(self):
        """Test that errors are recorded in metadata."""
        result = parse_bytecode("0x60")

        assert len(result["metadata"]["parsing_errors"]) == 1
        assert isinstance(result["metadata"]["parsing_errors"], list)

    def test_bytecode_in_result(self):
        """Test that bytecode is included in result with 0x prefix."""
        result = parse_bytecode("0x6080")

        assert result["bytecode"] == "0x6080"

    def test_bytecode_length(self):
        """Test that length is correctly calculated."""
        result = parse_bytecode("0x6080604052")

        assert result["length"] == 5


class TestParseEdgeCases:
    """Test edge cases and error conditions."""

    def test_parse_empty_bytecode(self):
        """Test parsing empty bytecode (after 0x removal)."""
        result = parse_bytecode("0x")

        assert result["length"] == 0
        assert len(result["opcodes"]) == 0
        assert result["metadata"]["total_opcodes"] == 0

    def test_parse_single_byte(self):
        """Test parsing single byte."""
        result = parse_bytecode("0x00")

        assert result["length"] == 1
        assert len(result["opcodes"]) == 1

    def test_parse_without_0x_prefix(self):
        """Test parsing bytecode without 0x prefix."""
        result = parse_bytecode("6080604052")

        assert result["bytecode"] == "0x6080604052"
        assert len(result["opcodes"]) == 3

    def test_parse_long_bytecode(self):
        """Test parsing longer bytecode."""
        bytecode = "0x" + "01" * 20
        result = parse_bytecode(bytecode)

        assert result["length"] == 20
        assert len(result["opcodes"]) == 20
        assert all(op["opcode"] == "ADD" for op in result["opcodes"])


class TestParseOpcodeDetails:
    """Test that opcode details are correctly extracted."""

    def test_opcode_has_all_required_fields(self):
        """Test that each opcode entry has all required fields."""
        result = parse_bytecode("0x00")

        opcode = result["opcodes"][0]
        assert "offset" in opcode
        assert "opcode" in opcode
        assert "value" in opcode
        assert "description" in opcode

    def test_push1_has_argument_field(self):
        """Test that PUSH1 has argument field."""
        result = parse_bytecode("0x6080")

        opcode = result["opcodes"][0]
        assert "argument" in opcode

    def test_simple_opcode_no_argument_field(self):
        """Test that simple opcodes don't have argument field."""
        result = parse_bytecode("0x00")

        opcode = result["opcodes"][0]
        assert "argument" not in opcode

    def test_description_comes_from_opcodes_map(self):
        """Test that descriptions match OPCODES_MAP."""
        result = parse_bytecode("0x00")

        opcode = result["opcodes"][0]
        assert opcode["description"] == OPCODES_MAP[0x00]["description"]


class TestParseIntegration:
    """Integration tests with validator and opcodes modules."""

    def test_parse_after_validation_and_cleaning(self):
        """Test complete workflow: validate, clean, parse."""
        from bytecode_analyzer.validator import validate_bytecode, clean_bytecode

        user_input = "  0x60 80 60 40 52  "

        cleaned = clean_bytecode(user_input)
        assert cleaned == "0x6080604052"

        is_valid, msg = validate_bytecode(cleaned)
        assert is_valid is True

        result = parse_bytecode(cleaned)
        assert len(result["opcodes"]) == 3
        assert result["opcodes"][0]["opcode"] == "PUSH1"
        assert result["opcodes"][2]["opcode"] == "MSTORE"

    def test_parse_uses_opcodes_map(self):
        """Test that parser uses OPCODES_MAP from opcodes module."""
        result = parse_bytecode("0x010203")

        assert result["opcodes"][0]["opcode"] == "ADD"
        assert result["opcodes"][1]["opcode"] == "MUL"
        assert result["opcodes"][2]["opcode"] == "SUB"


class TestParsePush2ToPush32:
    """Test that PUSH2-PUSH32 are recognized but not specially handled (Sprint 4)."""

    def test_parse_push2_as_simple_opcode(self):
        """Test that PUSH2 is recognized but treated as simple opcode."""
        result = parse_bytecode("0x61")

        assert len(result["opcodes"]) == 1
        assert result["opcodes"][0]["opcode"] == "PUSH2"
        assert result["opcodes"][0]["value"] == "0x61"
        assert "argument" not in result["opcodes"][0]

    def test_parse_push32_as_simple_opcode(self):
        """Test that PUSH32 is recognized but treated as simple opcode."""
        result = parse_bytecode("0x7f")

        assert result["opcodes"][0]["opcode"] == "PUSH32"
        assert "argument" not in result["opcodes"][0]