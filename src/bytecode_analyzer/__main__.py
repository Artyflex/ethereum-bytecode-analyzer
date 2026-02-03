"""
Entry point for running bytecode_analyzer as a module.
Allows: python -m bytecode_analyzer
"""

from .cli import main

if __name__ == "__main__":
    exit(main())