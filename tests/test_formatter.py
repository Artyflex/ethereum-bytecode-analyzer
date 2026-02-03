"""
Tests for formatter module.
"""
import json
import pytest
from bytecode_analyzer.formatter import format_output
from bytecode_analyzer.parser import parse_bytecode


class TestFormatOutput:
    """Test format_output function."""

    def test_format_output_valid_data(self):
        """Test formatting valid parsed data."""
        parsed_data = {
            "bytecode": "0x6080604052",
            "length": 5,
            "opcodes": [
                {
                    "offset": 0,
                    "opcode": "PUSH1",
                    "value": "0x60",
                    "argument": "0x80",
                    "description": "Place 1 byte item on stack"
                }
            ],
            "metadata": {
                "total_opcodes": 1,
                "parsing_errors": []
            }
        }

        output = format_output(parsed_data)

        assert isinstance(output, str)
        assert len(output) > 0

    def test_format_output_default_indent(self):
        """Test that default indentation is 2 spaces."""
        parsed_data = {
            "bytecode": "0x00",
            "opcodes": []
        }

        output = format_output(parsed_data)

        # Check that indentation is applied (contains newlines)
        assert "\n" in output
        # Check for 2-space indentation pattern
        assert '  "bytecode"' in output or '  "opcodes"' in output

    def test_format_output_custom_indent(self):
        """Test formatting with custom indentation."""
        parsed_data = {
            "bytecode": "0x00",
            "opcodes": []
        }

        output = format_output(parsed_data, indent=4)

        # Check for 4-space indentation pattern
        assert '    "bytecode"' in output or '    "opcodes"' in output

    def test_format_output_no_indent(self):
        """Test formatting with no indentation (compact)."""
        parsed_data = {
            "bytecode": "0x00",
            "opcodes": []
        }

        output = format_output(parsed_data, indent=None)

        # Compact format should have no newlines (or very few)
        assert output.count("\n") <= 1

    def test_format_output_is_valid_json(self):
        """Test that output is valid JSON that can be parsed back."""
        parsed_data = {
            "bytecode": "0x6080604052",
            "length": 5,
            "opcodes": [
                {
                    "offset": 0,
                    "opcode": "PUSH1",
                    "value": "0x60",
                    "argument": "0x80"
                }
            ],
            "metadata": {
                "total_opcodes": 1,
                "parsing_errors": []
            }
        }

        output = format_output(parsed_data)

        # Should be able to parse it back
        reparsed = json.loads(output)
        assert reparsed == parsed_data

    def test_format_output_preserves_data_structure(self):
        """Test that formatting preserves all data."""
        parsed_data = {
            "bytecode": "0x6080604052",
            "length": 5,
            "opcodes": [
                {"offset": 0, "opcode": "PUSH1", "value": "0x60", "argument": "0x80"},
                {"offset": 2, "opcode": "PUSH1", "value": "0x60", "argument": "0x40"},
                {"offset": 4, "opcode": "MSTORE", "value": "0x52"}
            ],
            "metadata": {
                "total_opcodes": 3,
                "parsing_errors": []
            }
        }

        output = format_output(parsed_data)
        reparsed = json.loads(output)

        assert reparsed["bytecode"] == parsed_data["bytecode"]
        assert reparsed["length"] == parsed_data["length"]
        assert len(reparsed["opcodes"]) == len(parsed_data["opcodes"])
        assert reparsed["metadata"]["total_opcodes"] == parsed_data["metadata"]["total_opcodes"]

    def test_format_output_with_unicode(self):
        """Test that unicode characters are preserved."""
        parsed_data = {
            "bytecode": "0x00",
            "metadata": {
                "note": "Test with unicode: émojis 🚀 and special chars: é, à, ü"
            }
        }

        output = format_output(parsed_data)

        # ensure_ascii=False should preserve unicode
        assert "🚀" in output
        assert "é" in output

    def test_format_output_empty_opcodes(self):
        """Test formatting data with empty opcodes list."""
        parsed_data = {
            "bytecode": "0x",
            "length": 0,
            "opcodes": [],
            "metadata": {
                "total_opcodes": 0,
                "parsing_errors": []
            }
        }

        output = format_output(parsed_data)
        reparsed = json.loads(output)

        assert reparsed["opcodes"] == []
        assert reparsed["length"] == 0


class TestFormatterIntegration:
    """Integration tests with parser module."""

    def test_format_after_parse(self):
        """Test formatting output from parse_bytecode."""
        bytecode = "0x6080604052"

        parsed = parse_bytecode(bytecode)
        output = format_output(parsed)

        assert isinstance(output, str)
        assert bytecode in output

        # Verify it's valid JSON
        reparsed = json.loads(output)
        assert reparsed["bytecode"] == bytecode

    def test_format_with_real_bytecode(self):
        """Test complete workflow with realistic bytecode."""
        bytecode = "0x608060405234801561001057600080fd5b50"

        parsed = parse_bytecode(bytecode)
        output = format_output(parsed)

        # Verify structure
        reparsed = json.loads(output)
        assert "bytecode" in reparsed
        assert "length" in reparsed
        assert "opcodes" in reparsed
        assert "metadata" in reparsed
        assert len(reparsed["opcodes"]) > 0

    def test_format_with_errors(self):
        """Test formatting bytecode with parsing errors."""
        bytecode = "0x60"  # Incomplete PUSH1

        parsed = parse_bytecode(bytecode)
        output = format_output(parsed)

        reparsed = json.loads(output)
        assert len(reparsed["metadata"]["parsing_errors"]) > 0

    def test_format_with_invalid_bytes(self):
        """Test formatting bytecode with invalid bytes."""
        bytecode = "0x0c"  # Invalid opcode

        parsed = parse_bytecode(bytecode)
        output = format_output(parsed)

        reparsed = json.loads(output)
        assert reparsed["opcodes"][0]["opcode"] == "UNKNOWN"

    def test_format_multiple_times_same_result(self):
        """Test that formatting is idempotent."""
        bytecode = "0x6080604052"
        parsed = parse_bytecode(bytecode)

        output1 = format_output(parsed)
        output2 = format_output(parsed)

        assert output1 == output2