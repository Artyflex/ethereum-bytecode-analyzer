"""
Tests for validator module.
Tests are organized by function and validation rule.
"""

from bytecode_analyzer.validator import (
    # Main functions
    validate_bytecode,
    clean_bytecode,
    # Validation functions
    _validate_is_string,
    _validate_not_empty,
    _validate_starts_with_0x,
    _validate_only_hex_characters,
    _validate_even_length,
    _remove_whitespace,
    _strip_edges,
    _convert_to_lowercase,
    _extract_hex_data,
)

# ============================================================================
# TESTS FOR ATOMIC VALIDATION FUNCTIONS
# ============================================================================


class TestValidateIsString:
    """Test _validate_is_string function."""

    def test_valid_string(self):
        """Test that string type passes."""
        is_valid, msg = _validate_is_string("0x6080")
        assert is_valid is True
        assert msg == ""

    def test_invalid_int(self):
        """Test that integer fails."""
        is_valid, msg = _validate_is_string(12345)
        assert is_valid is False
        assert "must be a string" in msg.lower()
        assert "int" in msg

    def test_invalid_bytes(self):
        """Test that bytes fails."""
        is_valid, msg = _validate_is_string(b"6080")
        assert is_valid is False
        assert "must be a string" in msg.lower()
        assert "bytes" in msg

    def test_invalid_none(self):
        """Test that None fails."""
        is_valid, msg = _validate_is_string(None)
        assert is_valid is False
        assert "must be a string" in msg.lower()
        assert "nonetype" in msg.lower()

    def test_invalid_list(self):
        """Test that list fails."""
        is_valid, msg = _validate_is_string(["0x6080"])
        assert is_valid is False
        assert "must be a string" in msg.lower()


class TestValidateNotEmpty:
    """Test _validate_not_empty function."""

    def test_valid_non_empty(self):
        """Test that non-empty string passes."""
        is_valid, msg = _validate_not_empty("0x6080")
        assert is_valid is True
        assert msg == ""

    def test_invalid_empty_string(self):
        """Test that empty string fails."""
        is_valid, msg = _validate_not_empty("")
        assert is_valid is False
        assert "empty" in msg.lower()

    def test_invalid_whitespace_only(self):
        """Test that whitespace-only string fails."""
        is_valid, msg = _validate_not_empty("   ")
        assert is_valid is False
        assert "empty" in msg.lower()

    def test_invalid_tabs_only(self):
        """Test that tabs-only string fails."""
        is_valid, msg = _validate_not_empty("\t\t")
        assert is_valid is False
        assert "empty" in msg.lower()


class TestValidateStartsWith0x:
    """Test _validate_starts_with_0x function."""

    def test_valid_with_0x_lowercase(self):
        """Test that string starting with '0x' passes."""
        is_valid, msg = _validate_starts_with_0x("0x6080")
        assert is_valid is True
        assert msg == ""

    def test_valid_with_0x_uppercase(self):
        """Test that string starting with '0X' passes."""
        is_valid, msg = _validate_starts_with_0x("0X6080")
        assert is_valid is True
        assert msg == ""

    def test_invalid_without_0x(self):
        """Test that string without '0x' fails."""
        is_valid, msg = _validate_starts_with_0x("6080604052")
        assert is_valid is False
        assert "must start with '0x'" in msg.lower()

    def test_invalid_0x_in_middle(self):
        """Test that '0x' in middle doesn't count."""
        is_valid, msg = _validate_starts_with_0x("aa0x6080")
        assert is_valid is False
        assert "must start with '0x'" in msg.lower()

    def test_valid_with_leading_whitespace(self):
        """Test that leading whitespace is stripped."""
        is_valid, msg = _validate_starts_with_0x("  0x6080")
        assert is_valid is True
        assert msg == ""


class TestValidateOnlyHexCharacters:
    """Test _validate_only_hex_characters function."""

    def test_valid_lowercase_hex(self):
        """Test that lowercase hex characters pass."""
        is_valid, msg = _validate_only_hex_characters("6080abcdef")
        assert is_valid is True
        assert msg == ""

    def test_valid_uppercase_hex(self):
        """Test that uppercase hex characters pass."""
        is_valid, msg = _validate_only_hex_characters("6080ABCDEF")
        assert is_valid is True
        assert msg == ""

    def test_valid_mixed_case_hex(self):
        """Test that mixed case hex characters pass."""
        is_valid, msg = _validate_only_hex_characters("60aB40cD")
        assert is_valid is True
        assert msg == ""

    def test_invalid_with_g(self):
        """Test that 'g' character fails."""
        is_valid, msg = _validate_only_hex_characters("60G0")
        assert is_valid is False
        assert "invalid characters" in msg.lower()
        assert "hexadecimal" in msg.lower()

    def test_invalid_with_special_chars(self):
        """Test that special characters fail."""
        invalid_chars = ["60@80", "60!80", "60-80", "60_80", "60 80"]
        for bytecode in invalid_chars:
            is_valid, msg = _validate_only_hex_characters(bytecode)
            assert is_valid is False, f"Should reject: {bytecode}"
            assert "invalid characters" in msg.lower()


class TestValidateEvenLength:
    """Test _validate_even_length function."""

    def test_valid_even_length(self):
        """Test that even length passes."""
        is_valid, msg = _validate_even_length("6080604052")
        assert is_valid is True
        assert msg == ""

    def test_valid_two_chars(self):
        """Test that 2 characters (minimum) pass."""
        is_valid, msg = _validate_even_length("60")
        assert is_valid is True
        assert msg == ""

    def test_invalid_odd_length(self):
        """Test that odd length fails."""
        is_valid, msg = _validate_even_length("608")
        assert is_valid is False
        assert "even length" in msg.lower()

    def test_invalid_single_char(self):
        """Test that single character fails."""
        is_valid, msg = _validate_even_length("6")
        assert is_valid is False
        assert "even length" in msg.lower()


# ============================================================================
# TESTS FOR MAIN VALIDATION FUNCTION
# ============================================================================


class TestValidateBytecode:
    """Test the main validate_bytecode function."""

    def test_valid_bytecode_complete(self):
        """Test completely valid bytecode."""
        is_valid, msg = validate_bytecode("0x6080604052")
        assert is_valid is True
        assert msg == ""

    def test_valid_bytecode_uppercase(self):
        """Test valid bytecode with uppercase."""
        is_valid, msg = validate_bytecode("0x60A0B0C0")
        assert is_valid is True
        assert msg == ""

    def test_invalid_not_string(self):
        """Test that non-string input fails at first check."""
        is_valid, msg = validate_bytecode(12345)
        assert is_valid is False
        assert "must be a string" in msg.lower()

    def test_invalid_empty(self):
        """Test that empty string fails at second check."""
        is_valid, msg = validate_bytecode("")
        assert is_valid is False
        assert "empty" in msg.lower()

    def test_invalid_no_0x_prefix(self):
        """Test that missing 0x prefix fails at third check."""
        is_valid, msg = validate_bytecode("6080604052")
        assert is_valid is False
        assert "must start with '0x'" in msg.lower()

    def test_invalid_only_0x(self):
        """Test that only '0x' fails."""
        is_valid, msg = validate_bytecode("0x")
        assert is_valid is False
        assert "empty" in msg.lower()

    def test_invalid_hex_characters(self):
        """Test that invalid hex fails at fourth check."""
        is_valid, msg = validate_bytecode("0x60G0")
        assert is_valid is False
        assert "invalid characters" in msg.lower()

    def test_invalid_odd_length(self):
        """Test that odd length fails at fifth check."""
        is_valid, msg = validate_bytecode("0x608")
        assert is_valid is False
        assert "even length" in msg.lower()

    def test_valid_with_whitespace_before_validation(self):
        """Test that leading/trailing whitespace is handled."""
        is_valid, msg = validate_bytecode("  0x6080604052  ")
        assert is_valid is True
        assert msg == ""


# ============================================================================
# TESTS FOR ATOMIC CLEANING FUNCTIONS
# ============================================================================


class TestRemoveWhitespace:
    """Test _remove_whitespace function."""

    def test_remove_spaces(self):
        """Test removal of spaces."""
        result = _remove_whitespace("60 80 60 40")
        assert result == "60806040"

    def test_remove_tabs(self):
        """Test removal of tabs."""
        result = _remove_whitespace("60\t80\t60")
        assert result == "608060"

    def test_remove_newlines(self):
        """Test removal of newlines."""
        result = _remove_whitespace("60\n80\n60")
        assert result == "608060"

    def test_remove_mixed_whitespace(self):
        """Test removal of mixed whitespace."""
        result = _remove_whitespace("60 \t\n80  60")
        assert result == "608060"

    def test_no_whitespace(self):
        """Test string without whitespace."""
        result = _remove_whitespace("6080")
        assert result == "6080"


class TestStripEdges:
    """Test _strip_edges function."""

    def test_strip_leading(self):
        """Test stripping leading whitespace."""
        result = _strip_edges("  0x6080")
        assert result == "0x6080"

    def test_strip_trailing(self):
        """Test stripping trailing whitespace."""
        result = _strip_edges("0x6080  ")
        assert result == "0x6080"

    def test_strip_both(self):
        """Test stripping both sides."""
        result = _strip_edges("  0x6080  ")
        assert result == "0x6080"

    def test_no_whitespace(self):
        """Test string without whitespace."""
        result = _strip_edges("0x6080")
        assert result == "0x6080"


class TestConvertToLowercase:
    """Test _convert_to_lowercase function."""

    def test_uppercase_to_lowercase(self):
        """Test conversion of uppercase."""
        result = _convert_to_lowercase("0X60A0B0C0")
        assert result == "0x60a0b0c0"

    def test_mixed_case_to_lowercase(self):
        """Test conversion of mixed case."""
        result = _convert_to_lowercase("0x60aB40cD")
        assert result == "0x60ab40cd"

    def test_already_lowercase(self):
        """Test already lowercase string."""
        result = _convert_to_lowercase("0x6080abcd")
        assert result == "0x6080abcd"


# ============================================================================
# TESTS FOR MAIN CLEANING FUNCTION
# ============================================================================


class TestCleanBytecode:
    """Test the main clean_bytecode function."""

    def test_clean_preserves_0x_prefix(self):
        """Test that 0x prefix is preserved."""
        result = clean_bytecode("0x6080604052")
        assert result == "0x6080604052"

    def test_clean_with_spaces_keeps_0x(self):
        """Test cleaning with spaces keeps 0x."""
        result = clean_bytecode("0x60 80 60 40 52")
        assert result == "0x6080604052"

    def test_clean_uppercase_x_to_lowercase(self):
        """Test that 0X becomes 0x."""
        result = clean_bytecode("0X6080604052")
        assert result == "0x6080604052"

    def test_clean_mixed_whitespace_keeps_0x(self):
        """Test cleaning with mixed whitespace keeps 0x."""
        result = clean_bytecode("  0x60 \t80\n60  40  ")
        assert result == "0x60806040"

    def test_clean_without_0x_unchanged(self):
        """Test that bytecode without 0x is unchanged (no prefix added)."""
        result = clean_bytecode("6080604052")
        assert result == "6080604052"
        # Note: This would fail validation, but clean doesn't add 0x


# ============================================================================
# Hex Data Extraction TESTS
# ============================================================================


class TestExtractHexData:
    """Test the _extract_hex_data utility function."""

    def test_extract_with_0x(self):
        """Test extracting hex data with 0x prefix."""
        result = _extract_hex_data("0x6080604052")
        assert result == "6080604052"

    def test_extract_without_0x(self):
        """Test extracting hex data without 0x prefix."""
        result = _extract_hex_data("6080604052")
        assert result == "6080604052"

    def test_extract_uppercase_0x(self):
        """Test extracting with uppercase 0X."""
        result = _extract_hex_data("0X6080604052")
        assert result == "6080604052"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestValidationCleaningIntegration:
    """Test validation and cleaning together."""

    def test_clean_then_validate_workflow_with_spaces(self):
        """Test typical workflow: clean bytecode with spaces, then validate."""
        bytecode = "  0x60 80 60 40 52  "

        # Clean first
        cleaned = clean_bytecode(bytecode)
        assert cleaned == "0x6080604052"

        # Then validate
        is_valid, msg = validate_bytecode(cleaned)
        assert is_valid is True
        assert msg == ""

    def test_clean_then_validate_workflow_uppercase(self):
        """Test workflow with uppercase."""
        bytecode = "0X60A0B0C0"

        cleaned = clean_bytecode(bytecode)
        assert cleaned == "0x60a0b0c0"

        is_valid, msg = validate_bytecode(cleaned)
        assert is_valid is True

    def test_validate_fails_without_0x_even_after_clean(self):
        """Test that bytecode without 0x fails validation even if cleaned."""
        bytecode = "6080604052"  # No 0x

        cleaned = clean_bytecode(bytecode)
        assert cleaned == "6080604052"  # Still no 0x

        is_valid, msg = validate_bytecode(cleaned)
        assert is_valid is False
        assert "must start with '0x'" in msg.lower()

    def test_complete_user_workflow(self):
        """Test complete realistic user workflow."""
        # User copies bytecode from Etherscan with spaces
        user_input = "  0x60 80 60 40 52 34 80 15 60 0f 57 60 00 80 fd 5b 50  "

        # Step 1: Clean
        cleaned = clean_bytecode(user_input)
        assert "  " not in cleaned  # No spaces
        assert "\t" not in cleaned  # No tabs
        assert cleaned.startswith("0x")  # Has prefix

        # Step 2: Validate
        is_valid, msg = validate_bytecode(cleaned)
        assert is_valid is True
        assert msg == ""

        # Step 3: Extract hex for parsing (internal use)
        hex_data = _extract_hex_data(cleaned)
        assert hex_data == "6080604052348015600f57600080fd5b50"
        assert not hex_data.startswith("0x")
