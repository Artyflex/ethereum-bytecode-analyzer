"""
Integration tests for bytecode analyzer.
Tests the complete workflow across all modules.
"""

from bytecode_analyzer.validator import validate_bytecode, clean_bytecode
from bytecode_analyzer.parser import parse_bytecode
from bytecode_analyzer.formatter import format_output
import json


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""

    def test_complete_workflow_simple_bytecode(self):
        """Test complete workflow with simple bytecode."""
        # Given
        user_input = "  0x60 80 60 40 52  "

        # When - Step 1: Clean
        cleaned = clean_bytecode(user_input)
        assert cleaned == "0x6080604052"

        # When - Step 2: Validate
        is_valid, error_msg = validate_bytecode(cleaned)
        assert is_valid is True
        assert error_msg == ""

        # When - Step 3: Parse
        parsed = parse_bytecode(cleaned)
        assert parsed["bytecode"] == "0x6080604052"
        assert parsed["length"] == 5
        assert len(parsed["opcodes"]) == 3
        assert parsed["metadata"]["total_opcodes"] == 3

        # When - Step 4: Format
        json_output = format_output(parsed)
        assert isinstance(json_output, str)

        # Then - Verify JSON is valid
        reparsed = json.loads(json_output)
        assert reparsed["bytecode"] == "0x6080604052"

    def test_complete_workflow_with_push1(self):
        """Test complete workflow with PUSH1 opcodes."""
        # Given
        bytecode = "0x60425f525f3560ab145f515500"

        # When
        cleaned = clean_bytecode(bytecode)
        is_valid, _ = validate_bytecode(cleaned)
        parsed = parse_bytecode(cleaned)
        format_output(parsed)

        # Then
        assert is_valid is True
        assert len(parsed["opcodes"]) > 0

        # Verify PUSH1 opcodes have arguments
        push1_opcodes = [op for op in parsed["opcodes"] if op["opcode"] == "PUSH1"]
        assert len(push1_opcodes) > 0
        for push1 in push1_opcodes:
            assert "argument" in push1

    def test_complete_workflow_with_errors(self):
        """Test complete workflow with bytecode containing errors."""
        # Given - Incomplete PUSH1
        bytecode = "0x6001606000"

        # When
        cleaned = clean_bytecode(bytecode)
        is_valid, _ = validate_bytecode(cleaned)
        parsed = parse_bytecode(cleaned)
        json_output = format_output(parsed)

        # Then
        assert is_valid is True
        assert parsed["length"] == 5

        # Should have parsed some opcodes
        assert len(parsed["opcodes"]) > 0

        # JSON should be valid
        reparsed = json.loads(json_output)
        assert "metadata" in reparsed

    def test_complete_workflow_invalid_bytes(self):
        """Test complete workflow with invalid bytes."""
        # Given
        bytecode = "0x0c0d0e"

        # When
        cleaned = clean_bytecode(bytecode)
        is_valid, _ = validate_bytecode(cleaned)
        parsed = parse_bytecode(cleaned)
        format_output(parsed)

        # Then
        assert is_valid is True
        assert parsed["length"] == 3

        # All should be marked as UNKNOWN
        for opcode in parsed["opcodes"]:
            assert opcode["opcode"] == "UNKNOWN"

        # Should have errors in metadata
        assert len(parsed["metadata"]["parsing_errors"]) == 3

    def test_complete_workflow_empty_bytecode(self):
        """Test complete workflow with empty bytecode."""
        # Given
        bytecode = "0x"

        # When
        cleaned = clean_bytecode(bytecode)
        is_valid, error_msg = validate_bytecode(cleaned)

        # Then - Validation should fail
        assert is_valid is False
        assert "empty" in error_msg.lower()


class TestModuleIntegration:
    """Test integration between specific modules."""

    def test_validator_to_parser_integration(self):
        """Test that validator output is compatible with parser input."""
        # Given
        bytecode = "0x6080604052"

        # When
        cleaned = clean_bytecode(bytecode)
        is_valid, _ = validate_bytecode(cleaned)

        # Then - Parser should accept validated bytecode without errors
        if is_valid:
            parsed = parse_bytecode(cleaned)
            assert "bytecode" in parsed
            assert "opcodes" in parsed
            assert "metadata" in parsed

    def test_parser_to_formatter_integration(self):
        """Test that parser output is compatible with formatter input."""
        # Given
        bytecode = "0x6080604052"

        # When
        parsed = parse_bytecode(bytecode)
        json_output = format_output(parsed)

        # Then - Should produce valid JSON
        reparsed = json.loads(json_output)
        assert reparsed == parsed

    def test_all_modules_together(self):
        """Test all modules working together in sequence."""
        # Given
        user_input = "  0X60 80 60 40 52  "  # Uppercase X, spaces

        # When - Complete pipeline
        cleaned = clean_bytecode(user_input)
        is_valid, error_msg = validate_bytecode(cleaned)

        assert is_valid is True

        parsed = parse_bytecode(cleaned)
        json_output = format_output(parsed)
        final_result = json.loads(json_output)

        # Then - Verify complete transformation
        assert final_result["bytecode"] == "0x6080604052"
        assert final_result["length"] == 5
        assert len(final_result["opcodes"]) == 3
        assert final_result["metadata"]["total_opcodes"] == 3


class TestRealWorldBytecode:
    """Test with real-world bytecode examples."""

    def test_simple_contract_bytecode(self):
        """Test with simple contract bytecode."""
        # Given - Simple contract initialization
        bytecode = "0x60425f525f3560ab145f515500"

        # When
        cleaned = clean_bytecode(bytecode)
        is_valid, _ = validate_bytecode(cleaned)
        parsed = parse_bytecode(cleaned)
        json_output = format_output(parsed)

        # Then
        assert is_valid is True
        assert parsed["length"] == 13
        assert len(parsed["opcodes"]) > 0

        # Verify it's valid JSON
        result = json.loads(json_output)
        assert result["bytecode"] == bytecode

    def test_bytecode_with_mixed_opcodes(self):
        """Test bytecode with mix of different opcode types."""
        # Given - Mix of PUSH1, arithmetic, stack, and control opcodes
        bytecode = "0x6001600201600380910400"

        # When
        parsed = parse_bytecode(bytecode)

        # Then - Should parse all opcodes
        assert len(parsed["opcodes"]) > 0

        # Should have PUSH1 with arguments
        push1_count = sum(1 for op in parsed["opcodes"] if op["opcode"] == "PUSH1")
        assert push1_count > 0

        # Should have arithmetic opcodes
        opcodes = [op["opcode"] for op in parsed["opcodes"]]
        assert any(op in ["ADD", "MUL", "DIV", "SWAP1"] for op in opcodes)

    def test_bytecode_with_incomplete_push1(self):
        """Test bytecode ending with incomplete PUSH1."""
        # Given - Ends with PUSH1 without argument
        bytecode = "0x600160"

        # When
        parsed = parse_bytecode(bytecode)

        # Then
        assert len(parsed["metadata"]["parsing_errors"]) > 0
        assert any("incomplete" in err.lower() for err in parsed["metadata"]["parsing_errors"])

        # Should still parse the complete PUSH1
        complete_push1 = [
            op for op in parsed["opcodes"] if op["opcode"] == "PUSH1" and "argument" in op
        ]
        assert len(complete_push1) >= 1


class TestErrorHandling:
    """Test error handling across modules."""

    def test_invalid_format_caught_by_validator(self):
        """Test that invalid format is caught by validator."""
        # Given
        invalid_inputs = [
            "not hex",
            "0xGGGG",
            "0x123",  # Odd length
            "123",  # No 0x prefix
        ]

        # When/Then
        for invalid in invalid_inputs:
            cleaned = clean_bytecode(invalid)
            is_valid, error_msg = validate_bytecode(cleaned)
            assert is_valid is False
            assert len(error_msg) > 0

    def test_parser_handles_all_unknown_bytes(self):
        """Test that parser handles bytecode with all unknown bytes."""
        # Given
        bytecode = "0x0c0d0e0f"

        # When
        parsed = parse_bytecode(bytecode)

        # Then
        assert len(parsed["opcodes"]) == 4
        assert all(op["opcode"] == "UNKNOWN" for op in parsed["opcodes"])
        assert len(parsed["metadata"]["parsing_errors"]) == 4

    def test_formatter_handles_empty_opcodes(self):
        """Test that formatter handles empty opcodes list."""
        # Given
        parsed_data = {
            "bytecode": "0x",
            "length": 0,
            "opcodes": [],
            "metadata": {"total_opcodes": 0, "parsing_errors": []},
        }

        # When
        json_output = format_output(parsed_data)

        # Then
        result = json.loads(json_output)
        assert result["opcodes"] == []
        assert result["length"] == 0


class TestDataConsistency:
    """Test data consistency across transformations."""

    def test_bytecode_preserved_through_pipeline(self):
        """Test that original bytecode is preserved."""
        # Given
        original = "0x6080604052"

        # When
        cleaned = clean_bytecode(original)
        parsed = parse_bytecode(cleaned)
        json_output = format_output(parsed)
        result = json.loads(json_output)

        # Then
        assert result["bytecode"] == original

    def test_opcode_count_matches_length(self):
        """Test that opcode count is consistent with metadata."""
        # Given
        bytecode = "0x6080604052"

        # When
        parsed = parse_bytecode(bytecode)

        # Then
        assert len(parsed["opcodes"]) == parsed["metadata"]["total_opcodes"]

    def test_json_roundtrip_preserves_data(self):
        """Test that JSON serialization/deserialization preserves data."""
        # Given
        bytecode = "0x6080604052"

        # When
        parsed = parse_bytecode(bytecode)
        json_output = format_output(parsed)
        reparsed = json.loads(json_output)
        json_output2 = format_output(reparsed)

        # Then - Second serialization should be identical
        assert json_output == json_output2
