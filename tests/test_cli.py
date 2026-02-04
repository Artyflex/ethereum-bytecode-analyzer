"""
Tests for CLI module.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest
from bytecode_analyzer.cli import (
    display_welcome,
    display_result,
    display_error,
    display_validation_success,
    get_bytecode_input,
    read_bytecode_from_file,
    write_output_to_file,
    create_argument_parser,
    parse_arguments,
    process_bytecode,
    run_cli_mode,
    run_interactive,
    main,
    VERSION,
)

# ============================================================================
# Display, Input, Interactive
# ============================================================================


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

        assert mock_input.call_count == 2
        assert "EVM Bytecode Analyzer" in captured.out
        assert "Interactive Mode" in captured.out
        assert "Thank you for using" in captured.out

    @patch("builtins.input", side_effect=["quit"])
    def test_run_interactive_quit_command(self, mock_input, capsys):
        """Test quitting with 'quit' command."""
        run_interactive()
        captured = capsys.readouterr()

        assert mock_input.call_count == 1
        assert "Thank you for using" in captured.out

    @patch("builtins.input", side_effect=["exit"])
    def test_run_interactive_exit_command(self, mock_input, capsys):
        """Test quitting with 'exit' command."""
        run_interactive()
        captured = capsys.readouterr()

        assert "Thank you for using" in captured.out

    @patch("builtins.input", side_effect=["q"])
    def test_run_interactive_q_command(self, mock_input, capsys):
        """Test quitting with 'q' command."""
        run_interactive()
        captured = capsys.readouterr()

        assert "Thank you for using" in captured.out

    @patch("builtins.input", side_effect=["", "quit"])
    def test_run_interactive_empty_input(self, mock_input, capsys):
        """Test handling of empty input."""
        run_interactive()
        captured = capsys.readouterr()

        assert "Error" in captured.out
        assert "empty" in captured.out.lower()

    @patch("builtins.input", side_effect=["invalid", "quit"])
    def test_run_interactive_invalid_bytecode(self, mock_input, capsys):
        """Test handling of invalid bytecode."""
        run_interactive()
        captured = capsys.readouterr()

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

        assert "Thank you for using" in captured.out

    @patch("builtins.input", side_effect=["0x6080604052", "0x00", "quit"])
    def test_run_interactive_multiple_analyses(self, mock_input, capsys):
        """Test multiple analyses in one session."""
        run_interactive()
        captured = capsys.readouterr()

        assert mock_input.call_count == 3
        assert captured.out.count("Analysis Result") == 2


# ============================================================================
# File I/O
# ============================================================================


class TestFileIO:
    """Test file input/output functions."""

    def test_read_bytecode_from_file(self):
        """Test reading bytecode from binary file."""
        # Create temporary binary file
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".bin") as f:
            f.write(bytes.fromhex("6080604052"))
            temp_path = f.name

        try:
            result = read_bytecode_from_file(temp_path)
            assert result == "0x6080604052"
        finally:
            Path(temp_path).unlink()

    def test_read_bytecode_from_file_not_found(self):
        """Test reading from non-existent file."""
        with pytest.raises(FileNotFoundError):
            read_bytecode_from_file("nonexistent.bin")

    def test_read_bytecode_from_empty_file(self):
        """Test reading from empty file."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".bin") as f:
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="empty"):
                read_bytecode_from_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_write_output_to_file(self):
        """Test writing output to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.json"
            content = '{"test": "data"}'

            write_output_to_file(str(output_path), content)

            assert output_path.exists()
            assert output_path.read_text() == content

    def test_write_output_creates_directories(self):
        """Test that write creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "subdir" / "output.json"
            content = '{"test": "data"}'

            write_output_to_file(str(output_path), content)

            assert output_path.exists()
            assert output_path.read_text() == content


# ============================================================================
# Argument Parsing
# ============================================================================


class TestArgumentParsing:
    """Test argument parsing."""

    def test_create_argument_parser(self):
        """Test that argument parser is created correctly."""
        parser = create_argument_parser()
        assert parser.prog == "bytecode_analyzer"

    def test_parse_arguments_bytecode(self):
        """Test parsing --bytecode argument."""
        args = parse_arguments(["--bytecode", "0x6080"])
        assert args.bytecode == "0x6080"
        assert args.file is None

    def test_parse_arguments_file(self):
        """Test parsing --file argument."""
        args = parse_arguments(["--file", "contract.bin"])
        assert args.file == "contract.bin"
        assert args.bytecode is None

    def test_parse_arguments_output(self):
        """Test parsing --output argument."""
        args = parse_arguments(["--bytecode", "0x6080", "--output", "result.json"])
        assert args.output == "result.json"

    def test_parse_arguments_compact(self):
        """Test parsing --compact flag."""
        args = parse_arguments(["--bytecode", "0x6080", "--compact"])
        assert args.compact is True

    def test_parse_arguments_verbose(self):
        """Test parsing --verbose flag."""
        args = parse_arguments(["--bytecode", "0x6080", "--verbose"])
        assert args.verbose is True

    def test_parse_arguments_no_args(self):
        """Test parsing with no arguments."""
        args = parse_arguments([])
        assert args.bytecode is None
        assert args.file is None

    def test_parse_arguments_bytecode_and_file_mutually_exclusive(self):
        """Test that --bytecode and --file are mutually exclusive."""
        with pytest.raises(SystemExit):
            parse_arguments(["--bytecode", "0x6080", "--file", "contract.bin"])


# ============================================================================
# Processing
# ============================================================================


class TestProcessBytecode:
    """Test bytecode processing function."""

    def test_process_bytecode_valid(self):
        """Test processing valid bytecode."""
        result = process_bytecode("0x6080604052")
        assert "0x6080604052" in result
        assert "opcodes" in result

    def test_process_bytecode_compact(self):
        """Test processing with compact output."""
        result = process_bytecode("0x6080604052", compact=True)
        # Compact should have no/minimal newlines
        assert result.count("\n") <= 1

    def test_process_bytecode_verbose(self):
        """Test processing with verbose output."""
        result = process_bytecode("0x6080604052", verbose=True)
        assert "verbose_info" in result

    def test_process_bytecode_invalid_raises_error(self):
        """Test that invalid bytecode raises ValueError."""
        with pytest.raises(ValueError):
            process_bytecode("invalid")


# ============================================================================
# CLI Mode
# ============================================================================


class TestRunCLIMode:
    """Test CLI mode execution."""

    def test_run_cli_mode_with_bytecode(self, capsys):
        """Test CLI mode with --bytecode argument."""
        args = parse_arguments(["--bytecode", "0x6080604052"])
        result = run_cli_mode(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "0x6080604052" in captured.out

    def test_run_cli_mode_with_file(self, capsys):
        """Test CLI mode with --file argument."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".bin") as f:
            f.write(bytes.fromhex("6080604052"))
            temp_path = f.name

        try:
            args = parse_arguments(["--file", temp_path])
            result = run_cli_mode(args)

            assert result == 0
            captured = capsys.readouterr()
            assert "0x6080604052" in captured.out
        finally:
            Path(temp_path).unlink()

    def test_run_cli_mode_with_output_file(self, capsys):
        """Test CLI mode with --output argument."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "result.json"
            args = parse_arguments(["--bytecode", "0x6080604052", "--output", str(output_path)])
            result = run_cli_mode(args)

            assert result == 0
            assert output_path.exists()
            content = output_path.read_text()
            assert "0x6080604052" in content

    def test_run_cli_mode_compact(self, capsys):
        """Test CLI mode with --compact flag."""
        args = parse_arguments(["--bytecode", "0x6080604052", "--compact"])
        result = run_cli_mode(args)

        assert result == 0
        captured = capsys.readouterr()
        # Compact output should have minimal newlines
        assert captured.out.strip().count("\n") <= 2

    def test_run_cli_mode_verbose(self, capsys):
        """Test CLI mode with --verbose flag."""
        args = parse_arguments(["--bytecode", "0x6080604052", "--verbose"])
        result = run_cli_mode(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "verbose_info" in captured.out

    def test_run_cli_mode_file_not_found(self, capsys):
        """Test CLI mode with non-existent file."""
        args = parse_arguments(["--file", "nonexistent.bin"])
        result = run_cli_mode(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_run_cli_mode_invalid_bytecode(self, capsys):
        """Test CLI mode with invalid bytecode."""
        args = parse_arguments(["--bytecode", "invalid"])
        result = run_cli_mode(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.out


# ============================================================================
# Main Dispatcher
# ============================================================================


class TestMainDispatcher:
    """Test main function dispatching."""

    @patch("bytecode_analyzer.cli.run_cli_mode")
    def test_main_with_bytecode_calls_cli_mode(self, mock_cli):
        """Test that main calls CLI mode when bytecode argument provided."""
        mock_cli.return_value = 0

        with patch("sys.argv", ["prog", "--bytecode", "0x6080"]):
            result = main()

        mock_cli.assert_called_once()
        assert result == 0

    @patch("bytecode_analyzer.cli.run_cli_mode")
    def test_main_with_file_calls_cli_mode(self, mock_cli):
        """Test that main calls CLI mode when file argument provided."""
        mock_cli.return_value = 0

        with patch("sys.argv", ["prog", "--file", "contract.bin"]):
            result = main()

        mock_cli.assert_called_once()
        assert result == 0

    @patch("bytecode_analyzer.cli.run_interactive")
    def test_main_without_args_calls_interactive(self, mock_interactive):
        """Test that main calls interactive mode when no arguments."""
        with patch("sys.argv", ["prog"]):
            result = main()

        mock_interactive.assert_called_once()
        assert result == 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestCLIIntegration:
    """Integration tests for CLI with other modules."""

    @patch("builtins.input", side_effect=["0x6080604052", "quit"])
    def test_cli_complete_workflow(self, mock_input, capsys):
        """Test complete workflow: input -> validate -> parse -> format -> display."""
        run_interactive()
        captured = capsys.readouterr()

        assert "validated successfully" in captured.out.lower()
        assert "Analysis Result" in captured.out
        assert "0x6080604052" in captured.out
        assert "PUSH1" in captured.out or "opcodes" in captured.out.lower()

    @patch("builtins.input", side_effect=["0x6080604052", "quit"])
    def test_cli_accepts_bytecode_with_0x(self, mock_input, capsys):
        """Test that CLI accepts bytecode with 0x prefix."""
        run_interactive()
        captured = capsys.readouterr()

        assert "validated successfully" in captured.out.lower()
        assert "Analysis Result" in captured.out

    @patch("builtins.input", side_effect=["0x60", "quit"])
    def test_cli_handles_parsing_errors(self, mock_input, capsys):
        """Test CLI handles bytecode with parsing errors (incomplete PUSH1)."""
        run_interactive()
        captured = capsys.readouterr()

        assert "Analysis Result" in captured.out
        assert "PUSH1" in captured.out


class TestVersion:
    """Test version information."""

    def test_version_constant_exists(self):
        """Test that VERSION constant is defined."""
        assert VERSION == "0.1.1"

    def test_version_in_help(self, capsys):
        """Test that --version displays version."""
        with pytest.raises(SystemExit):
            parse_arguments(["--version"])

        captured = capsys.readouterr()
        assert VERSION in captured.out


# ============================================================================
# COVERAGE TESTS (Edge cases and error paths)
# ============================================================================


class TestEdgeCasesAndErrors:
    """Test edge cases and error handling paths."""

    def test_read_bytecode_from_directory_raises_error(self):
        """Test that reading from a directory raises ValueError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="Not a file"):
                read_bytecode_from_file(temp_dir)

    def test_write_output_io_error(self, monkeypatch):
        """Test handling of IOError when writing to file."""

        def mock_open(*args, **kwargs):
            raise IOError("Permission denied")

        monkeypatch.setattr("builtins.open", mock_open)

        args = parse_arguments(["--bytecode", "0x6080604052", "--output", "test.json"])
        result = run_cli_mode(args)

        assert result == 1

    def test_run_cli_mode_unexpected_error(self, monkeypatch):
        """Test handling of unexpected errors in CLI mode."""

        def mock_process(*args, **kwargs):
            raise RuntimeError("Unexpected error")

        monkeypatch.setattr("bytecode_analyzer.cli.process_bytecode", mock_process)

        args = parse_arguments(["--bytecode", "0x6080604052"])
        result = run_cli_mode(args)

        assert result == 1

    def test_main_fatal_error(self, monkeypatch):
        """Test handling of fatal errors in main."""

        def mock_parse_args(*args, **kwargs):
            raise RuntimeError("Fatal error")

        monkeypatch.setattr("bytecode_analyzer.cli.parse_arguments", mock_parse_args)

        result = main()

        assert result == 1

    def test_run_cli_mode_no_input_error(self, monkeypatch, capsys):
        """Test error when no input provided to CLI mode (should not happen)."""
        # Create args manually without bytecode or file
        import argparse
        args = argparse.Namespace(
            bytecode=None,
            file=None,
            output=None,
            compact=False,
            verbose=False
        )

        result = run_cli_mode(args)
        captured = capsys.readouterr()

        assert result == 1
        assert "No input provided" in captured.out
