"""
Command-line interface for bytecode analyzer.
Interactive mode for analyzing EVM bytecode.
"""

from .validator import validate_bytecode, clean_bytecode
from .parser import parse_bytecode
from .formatter import format_output

# ============================================================================
# CONSTANTS
# ============================================================================

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
# MAIN CLI FUNCTION
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


def main():
    """
    Entry point for CLI.

    Runs the interactive mode.
    """
    try:
        run_interactive()
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}\n")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())