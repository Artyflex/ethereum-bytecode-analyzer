"""
Tests for CLI module.
"""

from unittest.mock import patch
from bytecode_analyzer.cli import (
    display_welcome,
    display_result,
    display_error,
    display_validation_success,
    get_bytecode_input,
    run_interactive,
    main,
)


class TestDisplayFunctions:
    """Test display functions."""

    def test_display_welcome(self, capsys):
        """Test that welcome message is displayed."""
        display_welcome()
        captured = capsys.readouterr()

        assert "EVM Bytecode Analyzer" in captured.out
        assert "Interactive Mode" in captured.out
        assert "Instructions:" in captured.out

    def test_display_result(self, capsys):
        """Test that result is displayed with formatting."""
        json_output = '{"bytecode": "0x6080604052"}'
        display_result(json_output)
        captured = capsys.readouterr()

        assert "Analysis Result:" in captured.out
        assert json_output in captured.out
        assert "=" in captured.out

    def test_display_error(self, capsys):
        """Test that error message is displayed."""
        error_msg = "Invalid bytecode format"
        display_error(error_msg)
        captured = capsys.readouterr()

        assert "Error" in captured.out
        assert error_msg in captured.out

    def test_display_validation_success(self, capsys):
        """Test that validation success message is displayed."""
        display_validation_success()
        captured = capsys.readouterr()

        assert "validated successfully" in captured.out.lower()


class TestInputFunctions:
    """Test input functions."""

    @patch("builtins.input", return_value="0x6080604052")
    def test_get_bytecode_input_valid(self, mock_input):
        """Test getting valid bytecode input."""
        result = get_bytecode_input()

        assert result == "0x6080604052"
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="quit")
    def test_get_bytecode_input_quit(self, mock_input):
        """Test getting quit command."""
        result = get_bytecode_input()

        assert result == "quit"

    @patch("builtins.input", return_value="  0x6080604052  ")
    def test_get_bytecode_input_strips_whitespace(self, mock_input):
        """Test that input is stripped of whitespace."""
        result = get_bytecode_input()

        assert result == "0x6080604052"


class TestRunInteractive:
    """Test run_interactive function."""

    @patch("builtins.input", side_effect=["0x6080604052", "quit"])
    def test_run_interactive_single_analysis(self, mock_input, capsys):
        """Test interactive mode with single analysis then quit."""
        run_interactive()
        captured = capsys.readouterr()

        # Verify input was called
        assert mock_input.call_count == 2

        # Verify welcome message was displayed
        assert "EVM Bytecode Analyzer" in captured.out
        assert "Interactive Mode" in captured.out

        # Verify goodbye message was displayed
        assert "Thank you for using" in captured.out

    @patch("builtins.input", side_effect=["quit"])
    def test_run_interactive_immediate_quit(self, mock_input, capsys):
        """Test quitting immediately."""
        run_interactive()
        captured = capsys.readouterr()

        assert mock_input.call_count == 1

        # Verify goodbye message was displayed
        assert "Thank you for using" in captured.out

    @patch("builtins.input", side_effect=["exit"])
    def test_run_interactive_exit_command(self, mock_input, capsys):
        """Test exit command."""
        run_interactive()
        captured = capsys.readouterr()

        assert "Thank you for using" in captured.out

    @patch("builtins.input", side_effect=["q"])
    def test_run_interactive_q_command(self, mock_input, capsys):
        """Test 'q' command."""
        run_interactive()
        captured = capsys.readouterr()

        assert "Thank you for using" in captured.out

    @patch("builtins.input", side_effect=["", "quit"])
    def test_run_interactive_empty_input(self, mock_input, capsys):
        """Test handling of empty input."""
        run_interactive()
        captured = capsys.readouterr()

        # Should display error for empty input
        assert "Error" in captured.out
        assert "empty" in captured.out.lower()

    @patch("builtins.input", side_effect=["invalid", "quit"])
    def test_run_interactive_invalid_bytecode(self, mock_input, capsys):
        """Test handling of invalid bytecode."""
        run_interactive()
        captured = capsys.readouterr()

        # Should display error for invalid bytecode
        assert "Error" in captured.out

    @patch("builtins.input", side_effect=["0x60G0", "quit"])
    def test_run_interactive_invalid_hex_characters(self, mock_input, capsys):
        """Test handling of invalid hex characters."""
        run_interactive()
        captured = capsys.readouterr()

        assert "Error" in captured.out
        assert "invalid" in captured.out.lower()

    @patch("builtins.input", side_effect=KeyboardInterrupt())
    def test_run_interactive_keyboard_interrupt(self, mock_input, capsys):
        """Test handling of Ctrl+C (KeyboardInterrupt)."""
        run_interactive()
        captured = capsys.readouterr()

        # Should display goodbye message
        assert "Thank you for using" in captured.out

    @patch("builtins.input", side_effect=["0x6080604052", "0x00", "quit"])
    def test_run_interactive_multiple_analyses(self, mock_input, capsys):
        """Test multiple analyses in one session."""
        run_interactive()
        captured = capsys.readouterr()

        assert mock_input.call_count == 3

        # Verify analysis results were displayed multiple times
        assert captured.out.count("Analysis Result") == 2


class TestMainEntryPoint:
    """Test main entry point."""

    @patch("bytecode_analyzer.cli.run_interactive")
    def test_main_calls_run_interactive(self, mock_run):
        """Test that main calls run_interactive."""
        result = main()

        mock_run.assert_called_once()
        assert result == 0

    @patch("bytecode_analyzer.cli.run_interactive", side_effect=Exception("Test error"))
    def test_main_handles_exceptions(self, mock_run, capsys):
        """Test that main handles exceptions gracefully."""
        result = main()
        captured = capsys.readouterr()

        assert result == 1

        # Verify error was printed
        assert "Fatal error" in captured.out


class TestCLIIntegration:
    """Integration tests for CLI with other modules."""

    @patch("builtins.input", side_effect=["0x6080604052", "quit"])
    def test_cli_complete_workflow(self, mock_input, capsys):
        """Test complete workflow: input -> validate -> parse -> format -> display."""
        run_interactive()
        captured = capsys.readouterr()

        # Verify workflow steps
        assert "validated successfully" in captured.out.lower()
        assert "Analysis Result" in captured.out
        assert "0x6080604052" in captured.out
        assert "PUSH1" in captured.out or "opcodes" in captured.out.lower()

    @patch("builtins.input", side_effect=["0x6080604052", "quit"])
    def test_cli_accepts_bytecode_with_0x(self, mock_input, capsys):
        """Test that CLI accepts bytecode with 0x prefix."""
        run_interactive()
        captured = capsys.readouterr()

        # Should work with 0x prefix
        assert "validated successfully" in captured.out.lower()
        assert "Analysis Result" in captured.out

    @patch("builtins.input", side_effect=["0x60", "quit"])
    def test_cli_handles_parsing_errors(self, mock_input, capsys):
        """Test CLI handles bytecode with parsing errors (incomplete PUSH1)."""
        run_interactive()
        captured = capsys.readouterr()

        # Should display result even with errors
        assert "Analysis Result" in captured.out
        assert "PUSH1" in captured.out
