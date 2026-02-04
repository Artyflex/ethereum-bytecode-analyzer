"""
Interactive command-line interface.

Terminal-based interface for analyzing EVM bytecode.

Features:
- Interactive loop for multiple analyses
- CLI mode with arguments (--bytecode, --file, --output, etc.)
- Quit commands (quit, exit, q, Ctrl+C)
- Input validation with error messages
- File I/O (read .bin files, write JSON)
- Formatted JSON output (normal or compact)

Key functions:
- run_interactive(): Interactive loop
- run_cli_mode(): CLI mode with arguments
- main(): Entry point (dispatcher)

Usage:
    Interactive: python -m bytecode_analyzer
    CLI: python -m bytecode_analyzer --bytecode "0x..."
"""

import argparse
from pathlib import Path
from .validator import validate_bytecode, clean_bytecode
from .parser import parse_bytecode
from .formatter import format_output

# ============================================================================
# CONSTANTS
# ============================================================================

VERSION = "0.1.1"

WELCOME_MESSAGE = """
================================================================================
                    EVM Bytecode Analyzer - Interactive Mode
================================================================================
"""

PROMPT_MESSAGE = "Enter EVM bytecode (or 'quit' to exit): "

QUIT_COMMANDS = {"quit", "exit", "q"}

GOODBYE_MESSAGE = "\nThank you for using EVM Bytecode Analyzer!\n"


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================


def display_welcome():
    """Display welcome message and instructions."""
    print(WELCOME_MESSAGE)
    print("Instructions:")
    print("  - Enter bytecode with or without '0x' prefix")
    print("  - Type 'quit', 'exit', or 'q' to exit")
    print("  - Press Ctrl+C to exit")
    print()


def display_result(json_output: str):
    """
    Display formatted analysis result.

    Args:
        json_output: JSON formatted string from formatter
    """
    print("\nAnalysis Result:")
    print("=" * 80)
    print(json_output)
    print("=" * 80)
    print()


def display_error(error_message: str):
    """
    Display error message to user.

    Args:
        error_message: Error description
    """
    print(f"\n❌ Error: {error_message}\n")


def display_validation_success():
    """Display validation success message."""
    print("✓ Bytecode validated successfully")


# ============================================================================
# INPUT FUNCTIONS
# ============================================================================


def get_bytecode_input() -> str:
    """
    Prompt user for bytecode input.

    Returns:
        Bytecode string entered by user
    """
    return input(PROMPT_MESSAGE).strip()


# ============================================================================
# FILE I/O FUNCTIONS
# ============================================================================


def read_bytecode_from_file(filepath: str) -> str:
    """
    Read bytecode from a binary file.

    Args:
        filepath: Path to .bin file

    Returns:
        Bytecode string with 0x prefix

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty or invalid
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if not path.is_file():
        raise ValueError(f"Not a file: {filepath}")

    # Read binary file
    with open(path, "rb") as f:
        bytecode_bytes = f.read()

    if not bytecode_bytes:
        raise ValueError(f"File is empty: {filepath}")

    # Convert to hex string with 0x prefix
    return "0x" + bytecode_bytes.hex()


def write_output_to_file(filepath: str, content: str) -> None:
    """
    Write JSON output to file.

    Args:
        filepath: Path to output file
        content: JSON string to write

    Raises:
        IOError: If cannot write to file
    """
    path = Path(filepath)

    # Create parent directories if they don't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write content to file
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================================
# ARGUMENT PARSING
# ============================================================================


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="bytecode_analyzer",
        description="EVM Bytecode Analyzer - Parse and analyze Ethereum bytecode",
        epilog="Use without arguments for interactive mode",
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "--bytecode", type=str, help="Bytecode string to analyze (with or without 0x prefix)"
    )
    input_group.add_argument(
        "--file", type=str, metavar="PATH", help="Path to binary file (.bin) containing bytecode"
    )

    # Output options
    parser.add_argument(
        "--output",
        type=str,
        metavar="PATH",
        help="Save output to file instead of stdout",
    )
    parser.add_argument("--compact", action="store_true", help="Output compact JSON (single line)")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed parsing information and warnings",
    )

    # Info options
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    return parser


def parse_arguments(args=None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: Arguments to parse (None = sys.argv)

    Returns:
        Parsed arguments namespace
    """
    parser = create_argument_parser()
    return parser.parse_args(args)


# ============================================================================
# PROCESSING FUNCTIONS
# ============================================================================


def process_bytecode(bytecode: str, compact: bool = False, verbose: bool = False) -> str:
    """
    Process bytecode through full pipeline.

    Args:
        bytecode: Raw bytecode string
        compact: Output compact JSON
        verbose: Include verbose information

    Returns:
        JSON formatted string

    Raises:
        ValueError: If bytecode is invalid
    """
    # Clean bytecode
    cleaned = clean_bytecode(bytecode)

    # Validate
    is_valid, error_msg = validate_bytecode(cleaned)
    if not is_valid:
        raise ValueError(error_msg)

    # Parse
    parsed = parse_bytecode(cleaned)

    # Add verbose information if requested
    if verbose:
        # Verbose mode: add extra metadata section
        parsed["metadata"]["verbose_info"] = {
            "original_bytecode": bytecode,
            "cleaned_bytecode": cleaned,
            "has_errors": len(parsed["metadata"]["parsing_errors"]) > 0,
        }

    # Format
    indent = None if compact else 2
    return format_output(parsed, indent=indent)


def run_cli_mode(args: argparse.Namespace) -> int:
    """
    Run CLI mode with parsed arguments.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        # Get bytecode from --bytecode or --file
        if args.bytecode:
            bytecode = args.bytecode
        elif args.file:
            bytecode = read_bytecode_from_file(args.file)
        else:
            # Should not happen (argparse validates)
            print("❌ Error: No input provided. Use --bytecode or --file")
            return 1

        # Process bytecode
        output = process_bytecode(bytecode, args.compact, args.verbose)

        # Write to file or stdout
        if args.output:
            write_output_to_file(args.output, output)
            print(f"✓ Output saved to {args.output}")
        else:
            print(output)

        return 0

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except IOError as e:
        print(f"❌ Error: Cannot write to file: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


# ============================================================================
# INTERACTIVE MODE
# ============================================================================


def run_interactive():
    """
    Run interactive CLI mode.

    Main loop:
    1. Prompt for bytecode
    2. Check if user wants to quit
    3. Clean bytecode
    4. Validate bytecode
    5. Parse bytecode
    6. Format output
    7. Display result
    8. Repeat
    """
    display_welcome()

    while True:
        try:
            # Get user input
            bytecode = get_bytecode_input()

            # Check for empty input
            if not bytecode:
                display_error("Bytecode cannot be empty")
                continue

            # Check if user wants to quit
            if bytecode.lower() in QUIT_COMMANDS:
                print(GOODBYE_MESSAGE)
                break

            # Clean bytecode (remove spaces, normalize)
            cleaned = clean_bytecode(bytecode)

            # Validate bytecode
            is_valid, error_msg = validate_bytecode(cleaned)
            if not is_valid:
                display_error(error_msg)
                continue

            # Display validation success
            display_validation_success()

            # Parse bytecode
            parsed = parse_bytecode(cleaned)

            # Format output to JSON
            json_output = format_output(parsed)

            # Display result
            display_result(json_output)

        except KeyboardInterrupt:
            print(GOODBYE_MESSAGE)
            break
        except Exception as e:
            display_error(f"Unexpected error: {str(e)}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def main():
    """
    Entry point for CLI.

    Behavior:
    - If arguments provided → CLI mode
    - If no arguments → Interactive mode

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        # Parse arguments
        args = parse_arguments()

        # Check if any CLI argument was provided
        if args.bytecode or args.file:
            # CLI mode
            return run_cli_mode(args)
        else:
            # Interactive mode (default)
            run_interactive()
            return 0

    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}\n")
        return 1


if __name__ == "__main__":
    exit(main())
